#!/usr/bin/env python3
"""Technology validation: Mermaid.js inside PyQt6 QWebEngineView with QWebChannel.

Run interactively (recommended on macOS) so WebEngine can use the native display
server — do not set ``QT_QPA_PLATFORM=offscreen`` for this PoC unless you accept
that rendering may fail on some hosts.

Example::

    uv run python scripts/tech_validation_mermaid_webengine.py

Exit codes: 0 on success, 1 on failure or timeout.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication

from atlantis.renderer.mermaid_assets import (
    PreviewAssetSession,
    mermaid_script_src,
)


class TechValidationPage(QWebEnginePage):
    """QWebEnginePage subclass so we can log JS console output (PoC diagnostics)."""

    def javaScriptConsoleMessage(
        self,
        level: QWebEnginePage.JavaScriptConsoleMessageLevel,
        message: str,
        line_number: int,
        source_id: str,
    ) -> None:
        print(
            f"[js console {int(level)}] {message} (line {line_number}, {source_id})",
            file=sys.stderr,
        )
        super().javaScriptConsoleMessage(level, message, line_number, source_id)


SAMPLE_SOURCE = """flowchart TD
    A[Start] --> B{Is it ok?}
    B -->|Yes| C[Great]
    B -->|No| D[Worry]
"""


class Bridge(QObject):
    """Minimal JS bridge: Mermaid success/error paths call into Python."""

    rendered = pyqtSignal(bool, str)

    def __init__(self) -> None:
        super().__init__()

    @pyqtSlot(str)
    def report_svg(self, svg: str) -> None:
        self.rendered.emit(True, svg)

    @pyqtSlot(str)
    def report_error(self, message: str) -> None:
        self.rendered.emit(False, message)


def _build_html(*, script_src: str) -> str:
    source_json = json.dumps(SAMPLE_SOURCE)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Atlantis tech validation</title>
  <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
  <script src="{script_src}"></script>
</head>
<body>
<script>
const MERMAID_SOURCE = {source_json};

function sendError(msg) {{
  if (window.bridge) {{
    window.bridge.report_error(String(msg));
  }} else {{
    console.error("bridge missing:", msg);
  }}
}}

document.addEventListener("DOMContentLoaded", function () {{
  new QWebChannel(qt.webChannelTransport, function (channel) {{
    window.bridge = channel.objects.bridge;
    (async function () {{
      try {{
        await mermaid.initialize({{ startOnLoad: false, securityLevel: "loose" }});
        const id = "mermaid-" + Math.random().toString(36).slice(2);
        const result = await mermaid.render(id, MERMAID_SOURCE);
        window.bridge.report_svg(result.svg);
      }} catch (e) {{
        sendError(e && e.message ? e.message : String(e));
      }}
    }})();
  }});
}});
</script>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=45_000,
        help="Abort if Mermaid does not report within this time (default: 45000).",
    )
    parser.add_argument(
        "--no-window",
        action="store_true",
        help="Do not call show(); still runs the event loop (for automated smoke).",
    )
    parser.add_argument(
        "--cdn",
        action="store_true",
        help="Load Mermaid from jsDelivr CDN instead of the vendored bundle (default: offline).",
    )
    args = parser.parse_args(argv)

    app = QApplication(sys.argv)
    view = QWebEngineView()
    page = TechValidationPage(view)
    view.setPage(page)

    bridge = Bridge()
    channel = QWebChannel(view)
    channel.registerObject("bridge", bridge)
    page.setWebChannel(channel)

    outcome: dict[str, Any] = {"done": False, "ok": False, "payload": ""}

    def finish(ok: bool, payload: str, elapsed_ms: float) -> None:
        if outcome["done"]:
            return
        outcome["done"] = True
        outcome["ok"] = ok
        outcome["payload"] = payload
        status = "OK" if ok else "FAIL"
        print(f"{status}: first Mermaid callback after {elapsed_ms:.1f} ms (payload length {len(payload)})")
        if ok and "<svg" not in payload.lower():
            print("WARN: expected <svg in payload", file=sys.stderr)
        QTimer.singleShot(0, app.quit)

    t0 = time.perf_counter()

    def on_rendered(ok: bool, payload: str) -> None:
        elapsed_ms = (time.perf_counter() - t0) * 1000
        finish(ok, payload, elapsed_ms)

    bridge.rendered.connect(on_rendered)

    def on_timeout() -> None:
        if outcome["done"]:
            return
        elapsed_ms = (time.perf_counter() - t0) * 1000
        print(f"FAIL: timeout after {elapsed_ms:.1f} ms", file=sys.stderr)
        finish(False, "timeout", elapsed_ms)

    QTimer.singleShot(args.timeout_ms, on_timeout)

    asset_session = PreviewAssetSession()
    script_src = mermaid_script_src(use_cdn=args.cdn)
    view.setHtml(_build_html(script_src=script_src), asset_session.base_url)
    view.destroyed.connect(asset_session.close)
    view.resize(900, 700)
    if not args.no_window:
        view.show()

    app.exec()
    return 0 if outcome.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
