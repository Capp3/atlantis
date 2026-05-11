"""Diagram preview widget."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:  # pragma: no cover - fallback only used when deps are missing
    QWebEngineView = None  # type: ignore[assignment]

from atlantis.renderer.webengine_bridge import BridgeRenderResult, WebEngineMermaidBridge

logger = logging.getLogger(__name__)


class PreviewPane(QWidget):
    """Preview container that supports both web and headless backends."""

    sourceRendered = pyqtSignal(object)

    def __init__(self, parent: QWidget | None = None, *, theme: str = "default") -> None:
        super().__init__(parent)
        self._last_svg = ""
        self._theme = theme
        self._use_webengine = os.environ.get("ATLANTIS_HEADLESS") != "1" and QWebEngineView is not None
        self._bridge: WebEngineMermaidBridge | None = None

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        if self._use_webengine:
            view = QWebEngineView(self)
            self._backend: QWebEngineView | QTextEdit = view
            self._bridge = WebEngineMermaidBridge(view.page(), theme=self._theme)
            self._bridge.renderFinished.connect(self._on_bridge_finished)
        else:
            backend = QTextEdit(self)
            backend.setReadOnly(True)
            self._backend = backend
        self._layout.addWidget(self._backend)
        self.show_placeholder("Atlantis preview ready.")

    @property
    def last_svg(self) -> str:
        """Expose the currently retained SVG for tests and state checks."""
        return self._last_svg

    @property
    def uses_webengine(self) -> bool:
        """True when the WebEngine + Mermaid render path is active."""
        return self._use_webengine and self._bridge is not None

    def set_theme(self, theme: str) -> None:
        """Update the Mermaid theme used for subsequent renders."""
        self._theme = theme
        if self._bridge is not None:
            self._bridge.set_theme(theme)

    def show_placeholder(self, message: str) -> None:
        """Display a placeholder message in the preview pane."""
        html = f"<h3>Atlantis Preview</h3><p>{message}</p>"
        self._set_html(html)

    def render_svg(self, svg: str) -> None:
        """Render SVG output and retain it as last good preview.

        Used by the headless/text fallback and by callers that already have a
        rendered SVG (e.g. tests). The WebEngine path uses :meth:`render_source`.
        """
        self._last_svg = svg
        self._set_html(svg)

    def render_source(self, source: str, on_done: Callable[[BridgeRenderResult], None] | None = None) -> bool:
        """Render Mermaid source via the WebEngine bridge if available.

        Returns ``True`` when the request was dispatched to the bridge, ``False``
        otherwise (e.g. headless fallback in tests, missing WebEngine wheel).
        Callers should use :meth:`render_svg` plus their own validation for the
        ``False`` case.
        """
        if self._bridge is None:
            return False
        if on_done is not None:
            self._pending_callback: Callable[[BridgeRenderResult], None] | None = on_done
        else:
            self._pending_callback = None
        self._bridge.render(source)
        return True

    def _on_bridge_finished(self, result: BridgeRenderResult) -> None:
        if result.ok:
            self._last_svg = result.payload
        callback = getattr(self, "_pending_callback", None)
        if callback is not None:
            self._pending_callback = None
            callback(result)
        self.sourceRendered.emit(result)

    def _set_html(self, html: str) -> None:
        if isinstance(self._backend, QTextEdit):
            self._backend.setHtml(html)
            return
        # WebEngine path: render_svg() is only used as a fallback, e.g. before the
        # bridge has finished loading, so we still emit raw HTML in that case.
        self._backend.setHtml(html)


def create_preview_widget(parent: QWidget | None = None, *, theme: str = "default") -> PreviewPane:
    """Create the preview widget with backend fallback support."""
    if os.environ.get("ATLANTIS_HEADLESS") == "1":
        wrapper = PreviewPane(parent, theme=theme)
        wrapper.show_placeholder("Headless mode: preview backend uses text view.")
        return wrapper

    if QWebEngineView is None:
        wrapper = PreviewPane(parent, theme=theme)
        wrapper.show_placeholder("PyQt6-WebEngine is not installed. Preview unavailable.")
        return wrapper

    return PreviewPane(parent, theme=theme)
