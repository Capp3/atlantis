"""Application settings helpers."""

from __future__ import annotations

from PyQt6.QtCore import QSettings

APP_NAME = "Atlantis"
ORG_NAME = "capp3"

WINDOW_GEOMETRY_KEY = "window/geometry"
WINDOW_STATE_KEY = "window/state"
SPLITTER_STATE_KEY = "window/splitter_state"
AUTOSAVE_ENABLED_KEY = "autosave/enabled"
AUTOSAVE_INTERVAL_KEY = "autosave/interval_ms"
RECENT_FILES_KEY = "files/recent"


def get_settings() -> QSettings:
    """Return the app QSettings store."""
    return QSettings(ORG_NAME, APP_NAME)
