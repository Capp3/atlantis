"""Phase 3 persistence and recovery tests."""

from __future__ import annotations

import os
from pathlib import Path

from atlantis.core.app import create_application
from atlantis.ui.main_window import MainWindow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["ATLANTIS_HEADLESS"] = "1"
_APP = create_application()


def _create_window(tmp_path: Path) -> MainWindow:
    os.environ["ATLANTIS_AUTOSAVE_DIR"] = str(tmp_path)
    return MainWindow()


def test_autosave_writes_rolling_file(tmp_path: Path) -> None:
    """Autosave should write current editor content to rolling file."""
    window = _create_window(tmp_path)
    window.editor.setPlainText("flowchart TD\nA-->B")
    window._autosave_current_document()
    autosave_path = window.current_autosave_path()
    assert autosave_path.exists()
    assert "flowchart TD" in autosave_path.read_text(encoding="utf-8")
    window.editor.document().setModified(False)
    window.close()


def test_recovery_restores_unsaved_work_in_headless(tmp_path: Path) -> None:
    """Startup should restore autosave in headless mode."""
    os.environ["ATLANTIS_AUTOSAVE_DIR"] = str(tmp_path)
    recovery = tmp_path / "untitled.mmd.autosave"
    recovery.write_text("graph LR\nA-->B", encoding="utf-8")

    window = MainWindow()
    assert "graph LR" in window.editor.toPlainText()
    window.editor.document().setModified(False)
    window.close()


def test_external_file_change_reload_when_clean(tmp_path: Path) -> None:
    """Watcher callback should reload changed files when editor is clean."""
    window = _create_window(tmp_path)
    target = tmp_path / "external.mmd"
    target.write_text("graph LR\nA-->B", encoding="utf-8")
    window.load_from_path(target)
    window.editor.document().setModified(False)

    target.write_text("graph LR\nA-->C", encoding="utf-8")
    window._on_external_file_changed(str(target))
    assert "A-->C" in window.editor.toPlainText()
    window.editor.document().setModified(False)
    window.close()


def test_recent_files_persisted(tmp_path: Path) -> None:
    """Loading/saving files should update recent file list."""
    window = _create_window(tmp_path)
    first = tmp_path / "one.mmd"
    second = tmp_path / "two.mmd"
    first.write_text("graph LR\nA-->B", encoding="utf-8")
    second.write_text("graph LR\nB-->C", encoding="utf-8")

    window.load_from_path(first)
    window.load_from_path(second)
    recent = window.recent_files()
    assert recent[0].endswith("two.mmd")
    assert any(item.endswith("one.mmd") for item in recent)
    window.editor.document().setModified(False)
    window.close()
