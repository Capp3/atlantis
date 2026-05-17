"""Phase 4 window polish tests: recent files prune, autosave prefs, error cycle, theme."""

from __future__ import annotations

import os
from pathlib import Path

from atlantis.core.settings import (
    AUTOSAVE_ENABLED_KEY,
    AUTOSAVE_INTERVAL_KEY,
    RECENT_FILES_KEY,
    get_settings,
)
from atlantis.model.recovery import build_recovery_diff
from atlantis.ui.main_window import MainWindow
from atlantis.ui.preferences import AutosavePreferencesDialog


def _create_window(tmp_path: Path) -> MainWindow:
    os.environ["ATLANTIS_AUTOSAVE_DIR"] = str(tmp_path)
    return MainWindow()


def test_recovery_diff_contains_disk_and_recovery_lines() -> None:
    """Unified diff includes both sides with default 3 lines of context."""
    diff = build_recovery_diff("flowchart TD\nA-->B\n", "flowchart TD\nA-->C\n")
    assert "--- disk" in diff
    assert "+++ recovery" in diff
    assert "-A-->B" in diff
    assert "+A-->C" in diff


def test_recovery_diff_empty_when_identical() -> None:
    assert build_recovery_diff("x", "x") == ""


def test_recent_files_stale_entries_are_pruned(tmp_path: Path) -> None:
    """Startup should drop recent-file entries whose files no longer exist."""
    real = tmp_path / "real.mmd"
    real.write_text("graph LR\nA-->B", encoding="utf-8")
    ghost = tmp_path / "ghost.mmd"
    settings = get_settings()
    settings.setValue(RECENT_FILES_KEY, [str(real), str(ghost)])

    window = _create_window(tmp_path)
    recent = window.recent_files()
    assert str(real) in recent
    assert str(ghost) not in recent
    window.editor.document().setModified(False)
    window.close()


def test_autosave_preferences_dialog_persists_values(tmp_path: Path) -> None:
    """Dialog should round-trip enable+interval through QSettings on accept."""
    os.environ["ATLANTIS_AUTOSAVE_DIR"] = str(tmp_path)
    settings = get_settings()
    settings.setValue(AUTOSAVE_ENABLED_KEY, False)
    settings.setValue(AUTOSAVE_INTERVAL_KEY, 90_000)

    dialog = AutosavePreferencesDialog(settings=settings)
    assert dialog.autosave_enabled is False
    assert dialog.autosave_interval_ms == 90_000

    dialog._enabled_checkbox.setChecked(True)
    dialog._interval_spinbox.setValue(45)
    dialog._on_accept()

    assert settings.value(AUTOSAVE_ENABLED_KEY, type=bool) is True
    assert settings.value(AUTOSAVE_INTERVAL_KEY, type=int) == 45_000


def test_render_error_cycle_action_enabled_with_multiple_messages(tmp_path: Path) -> None:
    """View → Cycle Render Errors enables when >1 message present and rotates the status bar."""
    window = _create_window(tmp_path)
    window._set_render_errors(["first problem", "second problem", "third problem"])
    assert window._cycle_errors_action.isEnabled()

    window.cycle_render_errors()
    assert "second problem" in window.statusBar().currentMessage()
    window.cycle_render_errors()
    assert "third problem" in window.statusBar().currentMessage()
    window.cycle_render_errors()
    assert "first problem" in window.statusBar().currentMessage()
    window.editor.document().setModified(False)
    window.close()


def test_render_with_invalid_toml_front_matter_warns_but_renders(tmp_path: Path) -> None:
    """Invalid TOML front matter should not block render; warning lands in errors."""
    window = _create_window(tmp_path)
    window.editor.setPlainText("+++\nnot toml at all\n+++\nflowchart TD\nA-->B\n")
    window._render_current_source()
    assert window.preview.last_svg
    assert any("TOML" in msg for msg in window.render_error_messages())
    window.editor.document().setModified(False)
    window.close()
