"""Unit tests for FileSession."""

from __future__ import annotations

from pathlib import Path

import pytest

from atlantis.model.file_session import FileSession


def test_bind_and_clear(tmp_path: Path) -> None:
    session = FileSession()
    assert session.path is None
    path = tmp_path / "example.mmd"
    session.bind(path)
    assert session.path == path
    session.clear()
    assert session.path is None


def test_window_title_untitled_and_named(tmp_path: Path) -> None:
    session = FileSession()
    assert session.window_title() == "Atlantis"
    session.bind(tmp_path / "diagram.mmd")
    assert session.window_title() == "Atlantis - diagram.mmd"


def test_matches_respects_bound_path(tmp_path: Path) -> None:
    session = FileSession()
    target = tmp_path / "a.mmd"
    session.bind(target)
    assert session.matches(target)
    assert not session.matches(tmp_path / "b.mmd")


def test_autosave_path_uses_file_handler(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATLANTIS_AUTOSAVE_DIR", str(tmp_path))
    session = FileSession()
    untitled = session.autosave_path()
    assert untitled.name == "untitled.mmd.autosave"

    doc = tmp_path / "doc.mmd"
    session.bind(doc)
    named = session.autosave_path()
    assert named != untitled
    assert named.parent == tmp_path


def test_read_disk_text_returns_content_and_handles_missing(tmp_path: Path) -> None:
    session = FileSession()
    assert session.read_disk_text() == ""

    doc = tmp_path / "on_disk.mmd"
    doc.write_text("graph LR\nA-->B", encoding="utf-8")
    session.bind(doc)
    assert "A-->B" in session.read_disk_text()

    session.bind(tmp_path / "missing.mmd")
    assert session.read_disk_text() == ""
