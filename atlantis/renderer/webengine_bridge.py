"""WebEngine-backed Mermaid render bridge.

Owns a small ``QObject`` exposed over ``QWebChannel`` so the embedded JavaScript
can call back into Python with rendered SVG or error text. The bridge does not
own a widget; it attaches to an existing :class:`~PyQt6.QtWebEngineCore.QWebEnginePage`
provided by the caller (typically the production preview widget).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from atlantis.renderer.logging_events import (
    BRIDGE_LOGGER,
    log_event,
    mermaid_src_label,
    truncate_error,
)
from atlantis.renderer.mermaid_assets import (
    MERMAID_CDN,
    MERMAID_VERSION,
    PreviewAssetSession,
    mermaid_script_src,
    preview_shell_template,
)

_RENDER_TIMEOUT_MS = 15_000


@dataclass(slots=True)
class BridgeRenderResult:
    """Async render outcome reported from the WebEngine JS side."""

    ok: bool
    payload: str
    elapsed_ms: float


class _BridgeChannel(QObject):
    """Inner ``QObject`` exposed to JS via ``QWebChannel``."""

    rendered = pyqtSignal(bool, str)

    @pyqtSlot(str)
    def report_svg(self, svg: str) -> None:
        self.rendered.emit(True, svg)

    @pyqtSlot(str)
    def report_error(self, message: str) -> None:
        self.rendered.emit(False, message)

    @pyqtSlot()
    def report_ready(self) -> None:
        """Optional signal from JS that mermaid.initialize finished."""
        # JS path uses an explicit poll instead — kept for forward compatibility.


class WebEngineMermaidBridge(QObject):
    """Render Mermaid source via a ``QWebEnginePage`` and emit results back to Python.

    Callers construct the bridge with an existing page (already attached to a view)
    and a theme hint. The bridge installs an HTML shell on first use and serializes
    render requests so only the latest request completes when the user types quickly.
    """

    renderFinished = pyqtSignal(object)

    def __init__(
        self,
        page: Any,
        *,
        theme: str = "default",
        cdn_url: str | None = None,
        timeout_ms: int = _RENDER_TIMEOUT_MS,
    ) -> None:
        super().__init__(page)
        from PyQt6.QtWebChannel import QWebChannel

        self._page = page
        self._theme = theme
        self._mermaid_script_src = cdn_url if cdn_url is not None else mermaid_script_src()
        self._timeout_ms = timeout_ms
        self._asset_session = PreviewAssetSession()
        self.destroyed.connect(self._asset_session.close)

        self._channel = QWebChannel(self)
        self._inner = _BridgeChannel(self)
        self._channel.registerObject("bridge", self._inner)
        self._page.setWebChannel(self._channel)

        self._pending_source: str | None = None
        self._render_start: float | None = None
        self._page_ready = False
        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_timeout)

        self._inner.rendered.connect(self._on_rendered)
        self._page.loadFinished.connect(self._on_load_finished)
        self._install_shell()

    def render(self, source: str) -> None:
        """Request rendering of ``source``; emit ``renderFinished`` when JS responds."""
        self._pending_source = source
        self._render_start = time.perf_counter()
        if self._timeout_ms > 0:
            self._timeout_timer.start(self._timeout_ms)
        if self._page_ready:
            log_event(
                BRIDGE_LOGGER,
                logging.DEBUG,
                "render_dispatch",
                source_chars=len(source),
                page_ready=True,
            )
            self._dispatch_render(source)

    def set_theme(self, theme: str) -> None:
        """Update preferred Mermaid theme; takes effect on next render."""
        self._theme = theme

    def _install_shell(self) -> None:
        self._page_ready = False
        log_event(
            BRIDGE_LOGGER,
            logging.DEBUG,
            "shell_install",
            mermaid_src=mermaid_src_label(self._mermaid_script_src),
            theme=self._theme,
        )
        html = self._build_shell_html()
        self._page.setHtml(html, self._asset_session.base_url)

    def _build_shell_html(self) -> str:
        theme_json = json.dumps(self._theme)
        return (
            preview_shell_template()
            .replace("{{MERMAID_SCRIPT_SRC}}", self._mermaid_script_src)
            .replace("{{THEME_JSON}}", theme_json)
        )

    def _on_load_finished(self, ok: bool) -> None:
        self._page_ready = bool(ok)
        if not ok:
            log_event(BRIDGE_LOGGER, logging.WARNING, "shell_load_failed", page_ready=False)
            return
        if self._pending_source is not None:
            log_event(
                BRIDGE_LOGGER,
                logging.DEBUG,
                "render_dispatch",
                source_chars=len(self._pending_source),
                page_ready=True,
            )
            self._dispatch_render(self._pending_source)

    def _dispatch_render(self, source: str) -> None:
        encoded = json.dumps(source)
        self._page.runJavaScript(f"atlantisRender({encoded});")

    def _on_rendered(self, ok: bool, payload: str) -> None:
        elapsed_ms = 0.0 if self._render_start is None else (time.perf_counter() - self._render_start) * 1000.0
        source_chars = len(self._pending_source) if self._pending_source else 0
        self._render_start = None
        self._pending_source = None
        if self._timeout_timer.isActive():
            self._timeout_timer.stop()
        if ok:
            log_event(
                BRIDGE_LOGGER,
                logging.INFO,
                "render_success",
                elapsed_ms=elapsed_ms,
                source_chars=source_chars,
            )
        else:
            log_event(
                BRIDGE_LOGGER,
                logging.WARNING,
                "render_error",
                elapsed_ms=elapsed_ms,
                source_chars=source_chars,
                error=truncate_error(payload),
            )
        self.renderFinished.emit(BridgeRenderResult(ok=ok, payload=payload, elapsed_ms=elapsed_ms))

    def _on_timeout(self) -> None:
        if self._render_start is None:
            return
        elapsed_ms = (time.perf_counter() - self._render_start) * 1000.0
        self._render_start = None
        self._pending_source = None
        log_event(BRIDGE_LOGGER, logging.WARNING, "render_timeout", elapsed_ms=elapsed_ms)
        self.renderFinished.emit(
            BridgeRenderResult(ok=False, payload="Render timed out", elapsed_ms=elapsed_ms),
        )


__all__ = [
    "MERMAID_CDN",
    "MERMAID_VERSION",
    "BridgeRenderResult",
    "WebEngineMermaidBridge",
]
