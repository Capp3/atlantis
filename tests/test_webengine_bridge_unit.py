"""Unit tests for ``WebEngineMermaidBridge`` using a minimal fake page."""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import QObject, QUrl, pyqtSignal

from atlantis.renderer.mermaid_assets import MERMAID_CDN, MERMAID_VENDOR_RELATIVE
from atlantis.renderer.webengine_bridge import BridgeRenderResult, WebEngineMermaidBridge


class _FakePage(QObject):
    loadFinished = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.html_calls: list[tuple[str, QUrl]] = []
        self.js_calls: list[str] = []
        self._web_channel: Any = None

    def setWebChannel(self, channel: Any) -> None:
        self._web_channel = channel

    def setHtml(self, html: str, base_url: QUrl) -> None:
        self.html_calls.append((html, base_url))

    def runJavaScript(self, script: str) -> None:
        self.js_calls.append(script)


def test_bridge_render_result_dataclass() -> None:
    result = BridgeRenderResult(ok=True, payload="<svg></svg>", elapsed_ms=1.5)
    assert result.ok is True
    assert result.payload == "<svg></svg>"
    assert result.elapsed_ms == 1.5


def test_build_shell_html_uses_local_mermaid_and_theme() -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0)
    html = bridge._build_shell_html()
    assert MERMAID_VENDOR_RELATIVE in html
    assert "cdn.jsdelivr.net" not in html
    assert '"default"' in html
    bridge.set_theme("dark")
    assert '"dark"' in bridge._build_shell_html()


def test_install_shell_uses_file_base_url() -> None:
    page = _FakePage()
    WebEngineMermaidBridge(page, timeout_ms=0)
    _, base_url = page.html_calls[0]
    assert base_url.scheme() == "file"


def test_cdn_script_override_via_parameter() -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0, cdn_url=MERMAID_CDN)
    assert MERMAID_CDN in bridge._build_shell_html()


def test_render_dispatches_immediately_when_page_ready() -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0)
    bridge._page_ready = True
    bridge.render("flowchart TD\nA-->B\n")
    assert len(page.js_calls) == 1


def test_render_queues_until_load_finished(qtbot) -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0)
    bridge.render("flowchart TD\nA-->B\n")
    assert page.js_calls == []
    page.loadFinished.emit(True)
    assert len(page.js_calls) == 1
    assert "atlantisRender" in page.js_calls[0]


def test_load_finished_failure_does_not_dispatch_js() -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0)
    bridge.render("flowchart TD\nA-->B\n")
    page.loadFinished.emit(False)
    assert page.js_calls == []


def test_on_rendered_emits_bridge_result(qtbot) -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0)
    results: list[BridgeRenderResult] = []
    bridge.renderFinished.connect(results.append)
    page.loadFinished.emit(True)
    bridge._inner.rendered.emit(True, "<svg></svg>")
    qtbot.wait(10)
    assert len(results) == 1
    assert results[0].ok is True
    assert "<svg" in results[0].payload
    assert results[0].elapsed_ms >= 0.0


def test_on_timeout_emits_failure_result(qtbot) -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=50)
    results: list[BridgeRenderResult] = []
    bridge.renderFinished.connect(results.append)
    bridge.render("flowchart TD\nA-->B\n")
    qtbot.wait(150)
    assert len(results) == 1
    assert results[0].ok is False
    assert results[0].payload == "Render timed out"
    assert results[0].elapsed_ms >= 0.0
