"""CLI and entrypoint coverage for ``atlantis.main``."""

from __future__ import annotations

import argparse
import logging

import pytest

from atlantis.main import _LOG_LEVELS, _resolve_log_level, build_parser, main

pytestmark = pytest.mark.usefixtures("reset_root_logging")


def test_build_parser_exposes_smoke_test_and_log_level() -> None:
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)
    args = parser.parse_args(["--smoke-test", "--log-level", "DEBUG"])
    assert args.smoke_test is True
    assert args.log_level == "DEBUG"
    assert set(_LOG_LEVELS) == {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def test_resolve_log_level_cli_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATLANTIS_LOG_LEVEL", "ERROR")
    args = build_parser().parse_args(["--log-level", "DEBUG"])
    assert _resolve_log_level(args) == logging.DEBUG


def test_resolve_log_level_uses_env_when_cli_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATLANTIS_LOG_LEVEL", "INFO")
    args = build_parser().parse_args([])
    assert _resolve_log_level(args) == logging.INFO


def test_resolve_log_level_defaults_to_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ATLANTIS_LOG_LEVEL", raising=False)
    args = build_parser().parse_args([])
    assert _resolve_log_level(args) == logging.WARNING


def test_resolve_log_level_invalid_env_falls_back_to_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATLANTIS_LOG_LEVEL", "NOT_A_LEVEL")
    args = build_parser().parse_args([])
    assert _resolve_log_level(args) == logging.WARNING


def test_main_smoke_test_exits_zero() -> None:
    assert main(["--smoke-test"]) == 0


def test_main_non_smoke_returns_exec_code(monkeypatch: pytest.MonkeyPatch) -> None:
    class _StubWindow:
        def show(self) -> None:
            return None

        def close(self) -> None:
            return None

    class _StubApp:
        def exec(self) -> int:
            return 7

        def quit(self) -> None:
            return None

    monkeypatch.setattr("atlantis.main.create_application", lambda: _StubApp())
    monkeypatch.setattr("atlantis.main.MainWindow", _StubWindow)
    assert main([]) == 7
