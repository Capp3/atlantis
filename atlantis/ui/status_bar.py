"""Status bar helpers."""

from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow

from atlantis.ui.qt_accessors import require_status_bar


def initialize_status_bar(window: QMainWindow) -> None:
    """Set initial status bar text for a newly created window."""
    require_status_bar(window).showMessage("Ready")
