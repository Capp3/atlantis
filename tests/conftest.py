"""Shared pytest harness for Atlantis.

Centralises the Qt offscreen / headless bootstrap so individual test modules
stay focused on behaviour. Also registers the opt-in ``webengine`` marker that
gates tests requiring the real ``QWebEngineView`` runtime.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("ATLANTIS_HEADLESS", "1")

_WEBENGINE_ENV_VAR = "ATLANTIS_WEBENGINE_TESTS"


@pytest.fixture(scope="session")
def qapp():
    """Return the singleton ``QApplication`` used by GUI tests."""
    from atlantis.core.app import create_application

    return create_application()


@pytest.fixture(autouse=True)
def _qapp_autouse(qapp):
    """Ensure every test sees a live ``QApplication`` without asking for it."""
    return qapp


@pytest.fixture
def reset_root_logging() -> Iterator[None]:
    """Clear root handlers so ``logging.basicConfig`` can run again in tests."""
    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    for handler in saved_handlers:
        root.removeHandler(handler)
    root.setLevel(logging.WARNING)
    yield
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    for handler in saved_handlers:
        root.addHandler(handler)
    root.setLevel(saved_level)


@pytest.fixture
def autosave_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Point ``ATLANTIS_AUTOSAVE_DIR`` at an isolated temp directory."""
    monkeypatch.setenv("ATLANTIS_AUTOSAVE_DIR", str(tmp_path))
    yield tmp_path


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip ``@pytest.mark.webengine`` tests unless explicitly enabled."""
    if os.environ.get(_WEBENGINE_ENV_VAR) == "1":
        return
    skip_marker = pytest.mark.skip(
        reason=f"Set {_WEBENGINE_ENV_VAR}=1 to run real WebEngine tests.",
    )
    for item in items:
        if "webengine" in item.keywords:
            item.add_marker(skip_marker)
