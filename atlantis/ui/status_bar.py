"""Status bar helpers."""

from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow


def initialize_status_bar(window: QMainWindow) -> None:
    """Set initial status bar text for a newly created window."""
    window.statusBar().showMessage("Ready")
