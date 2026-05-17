"""Narrow Qt accessor return types for mypy (PyQt stubs often mark these as optional)."""

from __future__ import annotations

from PyQt6.QtGui import QTextDocument
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QPlainTextEdit, QStatusBar


def require_status_bar(window: QMainWindow) -> QStatusBar:
    """Return the window status bar, raising if the platform stub's ``None`` path occurs."""
    bar = window.statusBar()
    if bar is None:
        msg = "QMainWindow.statusBar() returned None"
        raise RuntimeError(msg)
    return bar


def require_menu(menu: QMenu | None) -> QMenu:
    """Return a menu instance, raising if the platform stub's ``None`` path occurs."""
    if menu is None:
        msg = "QMenuBar.addMenu() returned None"
        raise RuntimeError(msg)
    return menu


def require_menu_bar(window: QMainWindow) -> QMenuBar:
    """Return the window menu bar, raising if unavailable."""
    bar = window.menuBar()
    if bar is None:
        msg = "QMainWindow.menuBar() returned None"
        raise RuntimeError(msg)
    return bar


def require_text_document(editor: QPlainTextEdit) -> QTextDocument:
    """Return the editor document, raising if unavailable."""
    document = editor.document()
    if document is None:
        msg = "QPlainTextEdit.document() returned None"
        raise RuntimeError(msg)
    return document


def require_qapplication() -> QApplication:
    """Return the running ``QApplication`` instance."""
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        msg = "No QApplication instance is running"
        raise TypeError(msg)
    return app
