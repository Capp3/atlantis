"""Phase 2 window and render-loop tests."""

from __future__ import annotations

import os
from pathlib import Path

from atlantis.core.app import create_application
from atlantis.ui.main_window import MainWindow

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["ATLANTIS_HEADLESS"] = "1"
_APP = create_application()


def _create_window() -> MainWindow:
    return MainWindow()


def test_main_window_has_editor_preview_splitter() -> None:
    """Phase 2 should provide the expected split editor/preview shell."""
    window = _create_window()
    assert window.splitter.count() == 2
    assert window.editor is not None
    assert window.preview is not None
    window.editor.document().setModified(False)
    window.close()


def test_render_error_keeps_last_good_preview() -> None:
    """Failed renders must retain the last successful preview."""
    window = _create_window()

    window.editor.setPlainText("flowchart TD\nA-->B")
    window._render_current_source()
    first_svg = window.preview.last_svg
    assert first_svg

    window.editor.setPlainText("this is not mermaid")
    window._render_current_source()
    assert window.preview.last_svg == first_svg
    assert "Unable to render Mermaid source." in window.statusBar().currentMessage()
    window.editor.document().setModified(False)
    window.close()


def test_save_and_load_mermaid_file_roundtrip(tmp_path: Path) -> None:
    """Phase 2 file actions should persist and restore editor content."""
    window = _create_window()
    sample = "graph LR\nA-->B"
    target = tmp_path / "diagram.mmd"

    window.editor.setPlainText(sample)
    window.save_to_path(target)
    assert target.read_text(encoding="utf-8") == sample

    window.editor.setPlainText("")
    window.load_from_path(target)
    assert window.editor.toPlainText() == sample
    window.editor.document().setModified(False)
    window.close()
