"""Application factory utilities."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from atlantis.core.settings import APP_NAME, ORG_NAME


def create_application() -> QApplication:
    """Return an existing QApplication instance or create a new one."""
    app = QApplication.instance()
    if app is not None:
        return app

    created_app = QApplication(sys.argv)
    created_app.setApplicationName(APP_NAME)
    created_app.setOrganizationName(ORG_NAME)
    return created_app
