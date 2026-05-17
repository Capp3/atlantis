"""Tests for structured renderer logging events."""

from __future__ import annotations

import logging

import pytest
from PyQt6.QtCore import QObject, QUrl, pyqtSignal

from atlantis.renderer.logging_events import (
    BRIDGE_LOGGER,
    log_event,
    mermaid_src_label,
    truncate_error,
)
from atlantis.renderer.webengine_bridge import WebEngineMermaidBridge


class _FakePage(QObject):
    loadFinished = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.html_calls: list[tuple[str, QUrl]] = []
        self.js_calls: list[str] = []
        self._web_channel: object | None = None

    def setWebChannel(self, channel: object) -> None:
        self._web_channel = channel

    def setHtml(self, html: str, base_url: QUrl) -> None:
        self.html_calls.append((html, base_url))

    def runJavaScript(self, script: str) -> None:
        self.js_calls.append(script)


@pytest.fixture
def bridge_log(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    with caplog.at_level(logging.DEBUG, logger="atlantis.renderer.bridge"):
        yield caplog


def test_log_event_message_and_extra(caplog: pytest.LogCaptureFixture) -> None:
    test_logger = logging.getLogger("test.atlantis.log_event")
    with caplog.at_level(logging.DEBUG, logger="test.atlantis.log_event"):
        log_event(test_logger, logging.INFO, "render_success", elapsed_ms=10.0, source_chars=5)
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.message == "event=render_success elapsed_ms=10.0 source_chars=5"
    assert record.event == "render_success"  # type: ignore[attr-defined]
    assert record.source_chars == 5  # type: ignore[attr-defined]


def test_truncate_error() -> None:
    assert truncate_error("short") == "short"
    long_text = "x" * 250
    assert truncate_error(long_text).endswith("...")
    assert len(truncate_error(long_text)) == 200


def test_mermaid_src_label() -> None:
    assert mermaid_src_label("../vendor/mermaid/mermaid.min.js") == "local"
    assert mermaid_src_label("https://cdn.jsdelivr.net/npm/mermaid@10.9.3/dist/mermaid.min.js") == "cdn"


def test_bridge_logger_name() -> None:
    assert BRIDGE_LOGGER.name == "atlantis.renderer.bridge"


def test_shell_load_failed_logged(bridge_log: pytest.LogCaptureFixture) -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0)
    bridge.render("flowchart TD\nA-->B\n")
    page.loadFinished.emit(False)
    warnings = [r for r in bridge_log.records if r.levelno == logging.WARNING]
    assert any("event=shell_load_failed" in r.message for r in warnings)


def test_render_success_logged(bridge_log: pytest.LogCaptureFixture, qtbot) -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0)
    page.loadFinished.emit(True)
    bridge.render("flowchart TD\nA-->B\n")
    bridge._inner.rendered.emit(True, "<svg></svg>")
    qtbot.wait(10)
    assert any("event=render_success" in r.message for r in bridge_log.records)
    assert not any("flowchart TD" in r.message for r in bridge_log.records)


def test_render_error_logged(bridge_log: pytest.LogCaptureFixture, qtbot) -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=0)
    page.loadFinished.emit(True)
    bridge.render("flowchart TD\nA-->B\n")
    bridge._inner.rendered.emit(False, "Parse error on line 1")
    qtbot.wait(10)
    assert any("event=render_error" in r.message for r in bridge_log.records)
    assert any("error=Parse error on line 1" in r.message for r in bridge_log.records)


def test_render_timeout_logged(bridge_log: pytest.LogCaptureFixture, qtbot) -> None:
    page = _FakePage()
    bridge = WebEngineMermaidBridge(page, timeout_ms=50)
    bridge.render("flowchart TD\nA-->B\n")
    qtbot.wait(150)
    assert any("event=render_timeout" in r.message for r in bridge_log.records)


def test_shell_install_logged_at_debug(bridge_log: pytest.LogCaptureFixture) -> None:
    page = _FakePage()
    WebEngineMermaidBridge(page, timeout_ms=0)
    assert any("event=shell_install" in r.message and "mermaid_src=local" in r.message for r in bridge_log.records)
