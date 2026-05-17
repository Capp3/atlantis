"""Mermaid preview asset paths and script URL resolution."""

from __future__ import annotations

import logging
import os
from contextlib import ExitStack
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

from PyQt6.QtCore import QUrl

from atlantis.renderer.logging_events import ASSETS_LOGGER, log_event

MERMAID_VERSION = "10.9.3"
MERMAID_CDN = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js"
MERMAID_VENDOR_RELATIVE = "../vendor/mermaid/mermaid.min.js"
_PREVIEW_SHELL_NAME = "preview_shell.html"
_USE_CDN_ENV = "ATLANTIS_USE_MERMAID_CDN"


def use_mermaid_cdn() -> bool:
    """Return True when the CDN fallback is requested via environment."""
    return os.environ.get(_USE_CDN_ENV, "").strip().lower() in {"1", "true", "yes"}


def mermaid_script_src(*, use_cdn: bool | None = None) -> str:
    """Return the Mermaid ``<script src=…>`` target (relative or absolute URL)."""
    if use_cdn if use_cdn is not None else use_mermaid_cdn():
        log_event(ASSETS_LOGGER, logging.DEBUG, "mermaid_src_cdn")
        return MERMAID_CDN
    return MERMAID_VENDOR_RELATIVE


def _assets_root() -> Traversable:
    return resources.files("atlantis.assets")


def preview_shell_template() -> str:
    """Load the preview HTML shell template from package assets."""
    return (_assets_root() / "preview" / _PREVIEW_SHELL_NAME).read_text(encoding="utf-8")


def mermaid_version_file() -> str:
    """Read the vendored VERSION file (trimmed)."""
    return (_assets_root() / "vendor" / "mermaid" / "VERSION").read_text(encoding="utf-8").strip()


class PreviewAssetSession:
    """Hold extracted asset directories alive for the lifetime of a WebEngine shell."""

    def __init__(self) -> None:
        self._stack = ExitStack()
        preview = self._stack.enter_context(resources.as_file(_assets_root() / "preview"))
        self.preview_dir = Path(preview)
        self.base_url = QUrl.fromLocalFile(f"{self.preview_dir.resolve()}/")
        log_event(
            ASSETS_LOGGER,
            logging.DEBUG,
            "assets_session_open",
            preview_dir=self.preview_dir.name,
        )

    def close(self) -> None:
        self._stack.close()
