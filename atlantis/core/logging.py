"""Logging configuration for Atlantis."""

from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QStandardPaths


def default_log_path() -> Path:
    """Return a user-accessible log path."""
    log_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "atlantis.log"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging for the application process."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.FileHandler(default_log_path()), logging.StreamHandler()],
        force=True,
    )
