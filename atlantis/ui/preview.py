"""Diagram preview widget."""

from __future__ import annotations

import os

from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover - fallback only used when deps are missing
    QWebEngineView = None  # type: ignore[assignment]


class PreviewPane(QWidget):
    """Preview container that supports both web and headless backends."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._last_svg = ""
        self._use_webengine = os.environ.get("ATLANTIS_HEADLESS") != "1" and QWebEngineView is not None

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        if self._use_webengine:
            self._backend: QWebEngineView | QTextEdit = QWebEngineView(self)
        else:
            backend = QTextEdit(self)
            backend.setReadOnly(True)
            self._backend = backend
        self._layout.addWidget(self._backend)
        self.show_placeholder("Phase 2 preview ready.")

    @property
    def last_svg(self) -> str:
        """Expose the currently retained SVG for tests and state checks."""
        return self._last_svg

    def show_placeholder(self, message: str) -> None:
        """Display a placeholder message in the preview pane."""
        html = f"<h3>Atlantis Preview</h3><p>{message}</p>"
        self._set_html(html)

    def render_svg(self, svg: str) -> None:
        """Render SVG output and retain it as last good preview."""
        self._last_svg = svg
        self._set_html(svg)

    def _set_html(self, html: str) -> None:
        if isinstance(self._backend, QTextEdit):
            self._backend.setHtml(html)
            return
        self._backend.setHtml(html)


def create_preview_widget(parent: QWidget | None = None) -> PreviewPane:
    """Create the preview widget with backend fallback support."""
    if os.environ.get("ATLANTIS_HEADLESS") == "1":
        wrapper = PreviewPane(parent)
        wrapper.show_placeholder("Headless mode: preview backend uses text view.")
        return wrapper

    if QWebEngineView is None:
        wrapper = PreviewPane(parent)
        wrapper.show_placeholder("PyQt6-WebEngine is not installed. Preview unavailable.")
        return wrapper

    return PreviewPane(parent)
