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

from PyQt6.QtCore import QObject, QTimer, QUrl, pyqtSignal, pyqtSlot

logger = logging.getLogger(__name__)

MERMAID_VERSION = "10.9.3"
MERMAID_CDN = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js"

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
        cdn_url: str = MERMAID_CDN,
        timeout_ms: int = _RENDER_TIMEOUT_MS,
    ) -> None:
        super().__init__(page)
        from PyQt6.QtWebChannel import QWebChannel

        self._page = page
        self._theme = theme
        self._cdn_url = cdn_url
        self._timeout_ms = timeout_ms

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
            self._dispatch_render(source)

    def set_theme(self, theme: str) -> None:
        """Update preferred Mermaid theme; takes effect on next render."""
        self._theme = theme

    def _install_shell(self) -> None:
        self._page_ready = False
        html = self._build_shell_html()
        self._page.setHtml(html, QUrl("https://atlantis.local/preview"))

    def _build_shell_html(self) -> str:
        theme = json.dumps(self._theme)
        cdn = self._cdn_url
        return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\"/>
  <style>
    html, body {{ margin: 0; padding: 0; background: transparent; }}
    #atlantis-output {{ padding: 8px; font-family: -apple-system, system-ui, sans-serif; }}
    #atlantis-output svg {{ max-width: 100%; height: auto; }}
  </style>
  <script src=\"qrc:///qtwebchannel/qwebchannel.js\"></script>
  <script src=\"{cdn}\"></script>
</head>
<body>
<div id=\"atlantis-output\"></div>
<script>
const ATLANTIS_THEME = {theme};
let ATLANTIS_INITIALIZED = false;
let ATLANTIS_BRIDGE = null;

function atlantisInit() {{
  if (ATLANTIS_INITIALIZED) {{ return Promise.resolve(); }}
  try {{
    mermaid.initialize({{ startOnLoad: false, securityLevel: "loose", theme: ATLANTIS_THEME }});
    ATLANTIS_INITIALIZED = true;
    return Promise.resolve();
  }} catch (e) {{
    return Promise.reject(e);
  }}
}}

async function atlantisRender(source) {{
  try {{
    await atlantisInit();
    const id = "atlantis-" + Math.random().toString(36).slice(2);
    const result = await mermaid.render(id, source);
    document.getElementById("atlantis-output").innerHTML = result.svg;
    if (ATLANTIS_BRIDGE) {{ ATLANTIS_BRIDGE.report_svg(result.svg); }}
  }} catch (e) {{
    const msg = (e && e.message) ? e.message : String(e);
    if (ATLANTIS_BRIDGE) {{ ATLANTIS_BRIDGE.report_error(msg); }}
  }}
}}

document.addEventListener("DOMContentLoaded", function () {{
  new QWebChannel(qt.webChannelTransport, function (channel) {{
    ATLANTIS_BRIDGE = channel.objects.bridge;
    ATLANTIS_BRIDGE.report_ready();
  }});
}});
</script>
</body>
</html>
"""

    def _on_load_finished(self, ok: bool) -> None:
        self._page_ready = bool(ok)
        if not ok:
            logger.warning("WebEngine preview page failed to load shell")
            return
        if self._pending_source is not None:
            self._dispatch_render(self._pending_source)

    def _dispatch_render(self, source: str) -> None:
        encoded = json.dumps(source)
        self._page.runJavaScript(f"atlantisRender({encoded});")

    def _on_rendered(self, ok: bool, payload: str) -> None:
        elapsed_ms = 0.0 if self._render_start is None else (time.perf_counter() - self._render_start) * 1000.0
        self._render_start = None
        self._pending_source = None
        if self._timeout_timer.isActive():
            self._timeout_timer.stop()
        self.renderFinished.emit(BridgeRenderResult(ok=ok, payload=payload, elapsed_ms=elapsed_ms))

    def _on_timeout(self) -> None:
        if self._render_start is None:
            return
        elapsed_ms = (time.perf_counter() - self._render_start) * 1000.0
        self._render_start = None
        self._pending_source = None
        self.renderFinished.emit(
            BridgeRenderResult(ok=False, payload="Render timed out", elapsed_ms=elapsed_ms),
        )
