"""Persisted recent-files list backed by QSettings."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings

from atlantis.core.settings import RECENT_FILES_KEY, get_settings


class RecentFilesRegistry:
    """Tracks recently opened document paths in application settings."""

    def __init__(self, *, limit: int = 10, settings: QSettings | None = None) -> None:
        self._limit = limit
        self._settings = settings if settings is not None else get_settings()

    def add(self, path: Path) -> None:
        """Promote path to the front of the recent list."""
        current = self._settings.value(RECENT_FILES_KEY, [], type=list) or []
        updated = [str(path), *[item for item in current if item != str(path)]]
        self._settings.setValue(RECENT_FILES_KEY, updated[: self._limit])

    def paths(self) -> list[str]:
        """Return stored recent paths without pruning."""
        return self._settings.value(RECENT_FILES_KEY, [], type=list) or []

    def prune_missing(self) -> int:
        """Drop entries whose path no longer exists. Returns count removed."""
        current = self.paths()
        existing = [item for item in current if Path(item).exists()]
        removed = len(current) - len(existing)
        if removed > 0:
            self._settings.setValue(RECENT_FILES_KEY, existing[: self._limit])
        return removed

    def clear(self) -> None:
        """Remove all recent file entries."""
        self._settings.setValue(RECENT_FILES_KEY, [])
