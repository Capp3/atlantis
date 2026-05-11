"""Main application window."""

from __future__ import annotations

import difflib
import logging
import os
from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher, Qt, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent, QKeySequence, QPalette
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMenu, QMessageBox, QSplitter

from atlantis.core.settings import (
    AUTOSAVE_ENABLED_KEY,
    AUTOSAVE_INTERVAL_KEY,
    RECENT_FILES_KEY,
    SPLITTER_STATE_KEY,
    WINDOW_GEOMETRY_KEY,
    WINDOW_STATE_KEY,
    get_settings,
)
from atlantis.model.file_handler import (
    autosave_path_for,
    clear_autosave,
    read_autosave,
    read_mermaid_file,
    write_autosave,
    write_mermaid_file,
)
from atlantis.renderer.mermaid_renderer import MermaidRenderer
from atlantis.renderer.webengine_bridge import BridgeRenderResult
from atlantis.ui.editor import MermaidEditor
from atlantis.ui.preferences import AutosavePreferencesDialog
from atlantis.ui.preview import create_preview_widget
from atlantis.ui.status_bar import initialize_status_bar
from atlantis.utils.debounce import Debouncer
from atlantis.utils.frontmatter import split_front_matter, try_parse_metadata

logger = logging.getLogger(__name__)

_RECENT_FILES_LIMIT = 10
_RECOVERY_DIFF_CONTEXT = 3


class MainWindow(QMainWindow):
    """Primary Atlantis shell window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Atlantis")
        self.resize(1200, 760)
        self._current_path: Path | None = None
        self._renderer = MermaidRenderer()
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_external_file_changed)
        self._error_messages: list[str] = []
        self._error_cursor = 0
        self._last_render_ms: float | None = None

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.editor = MermaidEditor(self.splitter)
        self.preview = create_preview_widget(self.splitter, theme=self._preview_theme())
        if self.preview.uses_webengine:
            self.preview.sourceRendered.connect(self._on_preview_rendered)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.setCentralWidget(self.splitter)

        self._recent_menu: QMenu | None = None
        self._build_menus()
        initialize_status_bar(self)
        self._restore_window_state()
        self._render_debouncer = Debouncer(delay_ms=500, callback=self._render_current_source)
        self.editor.textChanged.connect(self._on_editor_text_changed)
        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave_current_document)
        self._configure_autosave()
        self._prune_stale_recent_files()
        self._refresh_recent_files_menu()
        self._restore_from_recovery_if_available()
        self._render_current_source()

    def _persist_window_state(self) -> None:
        settings = get_settings()
        settings.setValue(WINDOW_GEOMETRY_KEY, self.saveGeometry())
        settings.setValue(WINDOW_STATE_KEY, self.saveState())
        settings.setValue(SPLITTER_STATE_KEY, self.splitter.saveState())

    def _restore_window_state(self) -> None:
        settings = get_settings()
        geometry = settings.value(WINDOW_GEOMETRY_KEY)
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = settings.value(WINDOW_STATE_KEY)
        if state is not None:
            self.restoreState(state)

        splitter_state = settings.value(SPLITTER_STATE_KEY)
        if splitter_state is not None:
            self.splitter.restoreState(splitter_state)

    def _configure_autosave(self) -> None:
        settings = get_settings()
        enabled = settings.value(AUTOSAVE_ENABLED_KEY, True, type=bool)
        interval_ms = settings.value(AUTOSAVE_INTERVAL_KEY, 60000, type=int)
        self._autosave_timer.setInterval(max(1000, interval_ms))
        if enabled:
            if not self._autosave_timer.isActive():
                self._autosave_timer.start()
        elif self._autosave_timer.isActive():
            self._autosave_timer.stop()

    def current_autosave_path(self) -> Path:
        """Expose active autosave file path for tests and diagnostics."""
        return autosave_path_for(self._current_path)

    def _autosave_current_document(self) -> None:
        if not self.editor.toPlainText().strip():
            return
        path = write_autosave(self._current_path, self.editor.toPlainText())
        self.statusBar().showMessage(f"Autosaved to {path.name}")

    def _restore_from_recovery_if_available(self) -> None:
        recovery = read_autosave(self._current_path)
        if not recovery:
            return
        if self.editor.toPlainText().strip():
            return

        if self._headless_mode():
            self.editor.setPlainText(recovery)
            self.editor.document().setModified(True)
            self.statusBar().showMessage("Recovered unsaved work (headless mode).")
            return

        disk_text = ""
        if self._current_path is not None and self._current_path.exists():
            try:
                disk_text = self._current_path.read_text(encoding="utf-8")
            except OSError:
                disk_text = ""
        diff_text = build_recovery_diff(disk_text, recovery)

        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle("Restore recovery")
        box.setText("Unsaved recovery data was found. Restore it?")
        if diff_text:
            box.setDetailedText(diff_text)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setDefaultButton(QMessageBox.StandardButton.Yes)
        if box.exec() == QMessageBox.StandardButton.Yes:
            self.editor.setPlainText(recovery)
            self.editor.document().setModified(True)
            self.statusBar().showMessage("Recovered unsaved work.")

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        new_action = QAction("&New", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        self._recent_menu = file_menu.addMenu("Open &Recent")

        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()
        prefs_action = QAction("Autosave &Preferences...", self)
        prefs_action.triggered.connect(self.open_autosave_preferences)
        file_menu.addAction(prefs_action)

        file_menu.addSeparator()
        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        view_menu = menu_bar.addMenu("&View")
        wrap_group = QActionGroup(self)
        toggle_wrap = QAction("Toggle Soft Wrap", self, checkable=True)
        toggle_wrap.setChecked(True)
        toggle_wrap.triggered.connect(self._toggle_soft_wrap)
        wrap_group.addAction(toggle_wrap)
        view_menu.addAction(toggle_wrap)

        view_menu.addSeparator()
        self._cycle_errors_action = QAction("Cycle Render Errors", self)
        self._cycle_errors_action.setShortcut(QKeySequence("Ctrl+E"))
        self._cycle_errors_action.setEnabled(False)
        self._cycle_errors_action.triggered.connect(self.cycle_render_errors)
        view_menu.addAction(self._cycle_errors_action)

    def _on_editor_text_changed(self) -> None:
        self.statusBar().showMessage("Rendering scheduled...")
        self._render_debouncer.trigger()

    def _render_current_source(self) -> None:
        raw_source = self.editor.toPlainText()
        parsed = split_front_matter(raw_source)
        diagram_source = parsed.body if parsed.has_front_matter else raw_source
        fm_warning: str | None = None
        if parsed.has_front_matter:
            _, fm_warning = try_parse_metadata(parsed)

        result = self._renderer.render(diagram_source)
        if not result.ok or result.svg is None:
            messages = [result.error or "Render failed"]
            if fm_warning:
                messages.append(fm_warning)
            self._set_render_errors(messages)
            self.editor.set_error_lines([1] if diagram_source.strip() else [])
            self.statusBar().showMessage(messages[0])
            return

        self._set_render_errors([fm_warning] if fm_warning else [])
        self.editor.clear_error_lines()

        if self.preview.uses_webengine:
            self.statusBar().showMessage("Rendering…")
            self.preview.render_source(diagram_source)
            return

        self.preview.render_svg(result.svg)
        self.statusBar().showMessage(self._format_success_status(fm_warning))

    def _on_preview_rendered(self, result: BridgeRenderResult) -> None:
        self._last_render_ms = result.elapsed_ms
        if result.ok:
            self.statusBar().showMessage(f"Rendered in {result.elapsed_ms:.0f} ms")
            return
        existing = list(self._error_messages)
        existing.insert(0, result.payload)
        self._set_render_errors(existing)
        self.statusBar().showMessage(result.payload)

    def _set_render_errors(self, messages: list[str]) -> None:
        deduped: list[str] = []
        seen: set[str] = set()
        for raw in messages:
            text = (raw or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            deduped.append(text)
        self._error_messages = deduped
        self._error_cursor = 0
        self._cycle_errors_action.setEnabled(len(self._error_messages) > 1)

    def cycle_render_errors(self) -> None:
        """Status-bar cycle through known render/front-matter errors."""
        if not self._error_messages:
            return
        self._error_cursor = (self._error_cursor + 1) % len(self._error_messages)
        message = self._error_messages[self._error_cursor]
        self.statusBar().showMessage(f"[{self._error_cursor + 1}/{len(self._error_messages)}] {message}")

    def render_error_messages(self) -> list[str]:
        """Read-only snapshot of current render error messages (for tests)."""
        return list(self._error_messages)

    def last_render_ms(self) -> float | None:
        """Return the elapsed ms of the most recent WebEngine render, if any."""
        return self._last_render_ms

    def _format_success_status(self, fm_warning: str | None) -> str:
        if fm_warning:
            return f"Rendered preview ({fm_warning})"
        return "Rendered preview"

    def open_autosave_preferences(self) -> None:
        """Show the autosave preferences dialog and apply the chosen values."""
        dialog = AutosavePreferencesDialog(self)
        if dialog.exec() == AutosavePreferencesDialog.DialogCode.Accepted:
            self._configure_autosave()

    def _preview_theme(self) -> str:
        app = QApplication.instance()
        if app is None:
            return "default"
        palette = app.palette()
        background = palette.color(QPalette.ColorRole.Window)
        return "dark" if background.lightness() < 128 else "default"

    def _toggle_soft_wrap(self, enabled: bool) -> None:
        self.editor.setLineWrapMode(
            MermaidEditor.LineWrapMode.WidgetWidth if enabled else MermaidEditor.LineWrapMode.NoWrap
        )

    def new_file(self) -> None:
        self.editor.clear()
        self.editor.document().setModified(False)
        self._current_path = None
        self.setWindowTitle("Atlantis")
        self.statusBar().showMessage("New diagram")

    def open_file_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Mermaid File", "", "Mermaid (*.mmd);;All Files (*)")
        if not path:
            return
        self.load_from_path(Path(path))

    def load_from_path(self, path: Path) -> None:
        content = read_mermaid_file(path)
        self.editor.setPlainText(content)
        self.editor.document().setModified(False)
        self._current_path = path
        self._set_watched_file(path)
        self._add_recent_file(path)
        self._refresh_recent_files_menu()
        self.setWindowTitle(f"Atlantis - {path.name}")
        self.statusBar().showMessage(f"Opened {path.name}")

    def save_file(self) -> None:
        if self._current_path is None:
            self.save_file_as()
            return
        self.save_to_path(self._current_path)

    def save_file_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Mermaid File", "", "Mermaid (*.mmd);;All Files (*)")
        if not path:
            return
        target = Path(path)
        if target.suffix != ".mmd":
            target = target.with_suffix(".mmd")
        self.save_to_path(target)

    def save_to_path(self, path: Path) -> None:
        write_mermaid_file(path, self.editor.toPlainText())
        self.editor.document().setModified(False)
        self._current_path = path
        self._set_watched_file(path)
        self._add_recent_file(path)
        self._refresh_recent_files_menu()
        clear_autosave(path)
        self.setWindowTitle(f"Atlantis - {path.name}")
        self.statusBar().showMessage(f"Saved {path.name}")

    def _set_watched_file(self, path: Path) -> None:
        existing = self._watcher.files()
        if existing:
            self._watcher.removePaths(existing)
        self._watcher.addPath(str(path))

    def _on_external_file_changed(self, path: str) -> None:
        changed_path = Path(path)
        if self._current_path is None or changed_path != self._current_path:
            return
        if not changed_path.exists():
            self.statusBar().showMessage("Watched file was removed.")
            return
        self._watcher.addPath(path)
        if self.editor.document().isModified():
            self.statusBar().showMessage("File changed externally. Reload manually to avoid data loss.")
            return
        self.editor.setPlainText(read_mermaid_file(changed_path))
        self.editor.document().setModified(False)
        self.statusBar().showMessage("File reloaded after external change.")

    def _add_recent_file(self, path: Path) -> None:
        settings = get_settings()
        current = settings.value(RECENT_FILES_KEY, [], type=list) or []
        updated = [str(path), *[item for item in current if item != str(path)]]
        settings.setValue(RECENT_FILES_KEY, updated[:_RECENT_FILES_LIMIT])

    def recent_files(self) -> list[str]:
        """Return persisted recent file list (does not prune)."""
        settings = get_settings()
        return settings.value(RECENT_FILES_KEY, [], type=list) or []

    def _prune_stale_recent_files(self) -> int:
        """Drop entries whose path no longer exists. Returns count of removals."""
        settings = get_settings()
        current = settings.value(RECENT_FILES_KEY, [], type=list) or []
        existing = [item for item in current if Path(item).exists()]
        removed = len(current) - len(existing)
        if removed > 0:
            settings.setValue(RECENT_FILES_KEY, existing[:_RECENT_FILES_LIMIT])
        return removed

    def _refresh_recent_files_menu(self) -> None:
        if self._recent_menu is None:
            return
        self._recent_menu.clear()
        recent = self.recent_files()
        if not recent:
            empty = QAction("(No recent files)", self)
            empty.setEnabled(False)
            self._recent_menu.addAction(empty)
            return
        for raw_path in recent:
            path = Path(raw_path)
            action = QAction(path.name, self)
            action.setToolTip(str(path))
            action.triggered.connect(lambda _checked=False, p=path: self.load_from_path(p))
            self._recent_menu.addAction(action)
        self._recent_menu.addSeparator()
        clear_action = QAction("Clear Recent", self)
        clear_action.triggered.connect(self._clear_recent_files)
        self._recent_menu.addAction(clear_action)

    def _clear_recent_files(self) -> None:
        get_settings().setValue(RECENT_FILES_KEY, [])
        self._refresh_recent_files_menu()

    @staticmethod
    def _headless_mode() -> bool:
        return os.environ.get("ATLANTIS_HEADLESS") == "1"

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.editor.document().isModified():
            answer = QMessageBox.question(
                self,
                "Unsaved changes",
                "You have unsaved changes. Close without saving?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
        self._persist_window_state()
        clear_autosave(self._current_path)
        super().closeEvent(event)


def build_recovery_diff(disk_text: str, recovery_text: str, *, context: int = _RECOVERY_DIFF_CONTEXT) -> str:
    """Return a compact unified diff between the on-disk text and the recovery text."""
    disk_lines = disk_text.splitlines()
    recovery_lines = recovery_text.splitlines()
    diff_iter = difflib.unified_diff(
        disk_lines,
        recovery_lines,
        fromfile="disk",
        tofile="recovery",
        lineterm="",
        n=context,
    )
    return "\n".join(diff_iter)
