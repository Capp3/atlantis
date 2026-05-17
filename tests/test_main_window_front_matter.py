"""Main window integration tests for front matter editing."""

from __future__ import annotations

import os
from pathlib import Path

from PyQt6.QtGui import QAction

from atlantis.ui.front_matter_editor import FrontMatterEditorDialog
from atlantis.ui.main_window import MainWindow


def _create_window(tmp_path: Path) -> MainWindow:
    os.environ["ATLANTIS_AUTOSAVE_DIR"] = str(tmp_path)
    return MainWindow()


def test_open_front_matter_editor_updates_toml_document(tmp_path: Path, monkeypatch) -> None:
    window = _create_window(tmp_path)
    raw = '+++\ntitle = "Before"\n+++\nflowchart TD\nA-->B\n'
    window.editor.setPlainText(raw)

    class _StubDialog:
        DialogCode = FrontMatterEditorDialog.DialogCode

        def __init__(self, parent, *, parsed, metadata, warning) -> None:
            del parent, parsed, metadata, warning
            self._result = '+++\ntitle = "After"\n+++\n'

        def exec(self) -> int:
            return self.DialogCode.Accepted

        @property
        def result_front_matter(self) -> str:
            return self._result

    monkeypatch.setattr("atlantis.ui.main_window.FrontMatterEditorDialog", _StubDialog)
    window.open_front_matter_editor()

    assert 'title = "After"' in window.editor.toPlainText()
    assert "flowchart TD" in window.editor.toPlainText()
    window.editor.document().setModified(False)
    window.close()


def test_view_menu_has_edit_front_matter_action(tmp_path: Path) -> None:
    window = _create_window(tmp_path)
    texts = [action.text() for action in window.findChildren(QAction)]
    assert any("Edit Front Matter" in text for text in texts)
    window.editor.document().setModified(False)
    window.close()
