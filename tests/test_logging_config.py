"""Logging configuration coverage for ``atlantis.core.logging``."""

from __future__ import annotations

import logging

import pytest

from atlantis.core.logging import configure_logging, default_log_path

pytestmark = pytest.mark.usefixtures("reset_root_logging")


def test_default_log_path_uses_writable_location(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        "atlantis.core.logging.QStandardPaths.writableLocation",
        lambda _location: str(tmp_path),
    )
    path = default_log_path()
    assert path == tmp_path / "atlantis.log"
    assert path.parent.is_dir()


def test_configure_logging_writes_file_and_sets_level(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(
        "atlantis.core.logging.QStandardPaths.writableLocation",
        lambda _location: str(tmp_path),
    )
    configure_logging(logging.DEBUG)
    logging.getLogger().info("coverage probe")
    for handler in logging.getLogger().handlers:
        handler.flush()
    log_path = tmp_path / "atlantis.log"
    assert log_path.is_file()
    assert "coverage probe" in log_path.read_text(encoding="utf-8")
    assert logging.getLogger().level == logging.DEBUG
