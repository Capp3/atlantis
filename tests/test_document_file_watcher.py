"""Unit tests for DocumentFileWatcher."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from atlantis.model.file_session import FileSession
from atlantis.model.file_watch import DocumentFileWatcher, FileChangeAction


def _watcher_with_session(path: Path | None = None) -> tuple[MagicMock, FileSession, DocumentFileWatcher]:
    qt_watcher = MagicMock()
    qt_watcher.files.return_value = []
    session = FileSession()
    if path is not None:
        session.bind(path)
    doc_watcher = DocumentFileWatcher(qt_watcher, session)
    return qt_watcher, session, doc_watcher


def test_set_path_adds_and_replaces_watch(tmp_path: Path) -> None:
    qt_watcher, _, doc_watcher = _watcher_with_session()
    target = tmp_path / "watch.mmd"
    target.write_text("x", encoding="utf-8")
    doc_watcher.set_path(target)
    qt_watcher.addPath.assert_called_once_with(str(target))

    other = tmp_path / "other.mmd"
    other.write_text("y", encoding="utf-8")
    qt_watcher.files.return_value = [str(target)]
    doc_watcher.set_path(other)
    qt_watcher.removePaths.assert_called_once()
    qt_watcher.addPath.assert_called_with(str(other))

    doc_watcher.set_path(None)
    assert qt_watcher.removePaths.call_count >= 2


def test_handle_change_ignore_when_no_session_path(tmp_path: Path) -> None:
    _, _, doc_watcher = _watcher_with_session()
    target = tmp_path / "other.mmd"
    target.write_text("x", encoding="utf-8")
    assert doc_watcher.handle_change(str(target), is_modified=False) == FileChangeAction.IGNORE


def test_handle_change_ignore_wrong_path(tmp_path: Path) -> None:
    bound = tmp_path / "bound.mmd"
    bound.write_text("x", encoding="utf-8")
    other = tmp_path / "other.mmd"
    other.write_text("y", encoding="utf-8")
    _, _, doc_watcher = _watcher_with_session(bound)
    assert doc_watcher.handle_change(str(other), is_modified=False) == FileChangeAction.IGNORE


def test_handle_change_removed(tmp_path: Path) -> None:
    bound = tmp_path / "bound.mmd"
    _, _, doc_watcher = _watcher_with_session(bound)
    assert doc_watcher.handle_change(str(bound), is_modified=False) == FileChangeAction.REMOVED


def test_handle_change_warn_dirty(tmp_path: Path) -> None:
    bound = tmp_path / "bound.mmd"
    bound.write_text("x", encoding="utf-8")
    qt_watcher, _, doc_watcher = _watcher_with_session(bound)
    assert doc_watcher.handle_change(str(bound), is_modified=True) == FileChangeAction.WARN_DIRTY
    qt_watcher.addPath.assert_called_with(str(bound))


def test_handle_change_reload_when_clean(tmp_path: Path) -> None:
    bound = tmp_path / "bound.mmd"
    bound.write_text("x", encoding="utf-8")
    _, _, doc_watcher = _watcher_with_session(bound)
    assert doc_watcher.handle_change(str(bound), is_modified=False) == FileChangeAction.RELOAD
