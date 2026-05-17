"""External file change detection for the active document."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from PyQt6.QtCore import QFileSystemWatcher

from atlantis.model.file_session import FileSession


class FileChangeAction(StrEnum):
    """Strategy result when a watched file changes on disk."""

    IGNORE = "ignore"
    REMOVED = "removed"
    WARN_DIRTY = "warn_dirty"
    RELOAD = "reload"


class DocumentFileWatcher:
    """Sync QFileSystemWatcher membership with a FileSession."""

    def __init__(self, watcher: QFileSystemWatcher, session: FileSession) -> None:
        self._watcher = watcher
        self._session = session

    def set_path(self, path: Path | None) -> None:
        """Replace watched paths with a single document path, or none."""
        existing = self._watcher.files()
        if existing:
            self._watcher.removePaths(existing)
        if path is not None:
            self._watcher.addPath(str(path))

    def handle_change(self, path: str, *, is_modified: bool) -> FileChangeAction:
        """Classify an external file change without mutating the editor."""
        changed_path = Path(path)
        if self._session.path is None or not self._session.matches(changed_path):
            return FileChangeAction.IGNORE
        if not changed_path.exists():
            return FileChangeAction.REMOVED
        self._watcher.addPath(path)
        if is_modified:
            return FileChangeAction.WARN_DIRTY
        return FileChangeAction.RELOAD
