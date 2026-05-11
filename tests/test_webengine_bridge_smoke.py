"""Opt-in WebEngine bridge smoke test.

This test boots a real ``QWebEngineView`` plus the production
:class:`~atlantis.renderer.webengine_bridge.WebEngineMermaidBridge` and waits for
a successful Mermaid render. It is skipped by default; set
``ATLANTIS_WEBENGINE_TESTS=1`` and run on a host with a working WebEngine stack
(typically a desktop macOS/Linux session, not headless CI) to enable it.
"""

from __future__ import annotations

import os
from typing import Any

import pytest


@pytest.mark.webengine
def test_webengine_bridge_renders_simple_flowchart() -> None:
    """End-to-end: bridge installs the shell, JS renders, Python receives SVG."""
    if os.environ.get("ATLANTIS_HEADLESS") == "1":
        os.environ.pop("ATLANTIS_HEADLESS", None)

    from PyQt6.QtCore import QEventLoop, QTimer
    from PyQt6.QtWebEngineWidgets import QWebEngineView

    from atlantis.renderer.webengine_bridge import BridgeRenderResult, WebEngineMermaidBridge

    view = QWebEngineView()
    bridge = WebEngineMermaidBridge(view.page(), timeout_ms=10_000)
    received: list[BridgeRenderResult] = []

    loop = QEventLoop()

    def _on_finished(result: Any) -> None:
        received.append(result)
        loop.quit()

    bridge.renderFinished.connect(_on_finished)
    QTimer.singleShot(0, lambda: bridge.render("flowchart TD\nA-->B\n"))
    QTimer.singleShot(15_000, loop.quit)
    loop.exec()

    view.close()

    assert received, "Bridge produced no result within the timeout."
    result = received[0]
    assert result.ok, f"Render reported failure: {result.payload!r}"
    assert "<svg" in result.payload
