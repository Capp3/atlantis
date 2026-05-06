"""Main application window."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher, Qt, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QCloseEvent
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QSplitter

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
from atlantis.ui.editor import MermaidEditor
from atlantis.ui.preview import create_preview_widget
from atlantis.ui.status_bar import initialize_status_bar
from atlantis.utils.debounce import Debouncer


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

        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.editor = MermaidEditor(self.splitter)
        self.preview = create_preview_widget(self.splitter)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.setCentralWidget(self.splitter)

        self._build_menus()
        initialize_status_bar(self)
        self._restore_window_state()
        self._render_debouncer = Debouncer(delay_ms=500, callback=self._render_current_source)
        self.editor.textChanged.connect(self._on_editor_text_changed)
        self._autosave_timer = QTimer(self)
        self._autosave_timer.timeout.connect(self._autosave_current_document)
        self._configure_autosave()
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
            self._autosave_timer.start()

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

        answer = QMessageBox.question(
            self,
            "Restore recovery",
            "Unsaved recovery data was found. Restore it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
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

        save_action = QAction("&Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

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

    def _on_editor_text_changed(self) -> None:
        self.statusBar().showMessage("Rendering scheduled...")
        self._render_debouncer.trigger()

    def _render_current_source(self) -> None:
        source = self.editor.toPlainText()
        result = self._renderer.render(source)
        if result.ok and result.svg is not None:
            self.preview.render_svg(result.svg)
            self.editor.clear_error_lines()
            self.statusBar().showMessage("Rendered preview")
            return

        self.editor.set_error_lines([1] if source.strip() else [])
        self.statusBar().showMessage(result.error or "Render failed")

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
        settings.setValue(RECENT_FILES_KEY, updated[:10])

    def recent_files(self) -> list[str]:
        """Return persisted recent file list."""
        settings = get_settings()
        return settings.value(RECENT_FILES_KEY, [], type=list) or []

    @staticmethod
    def _headless_mode() -> bool:
        import os

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
