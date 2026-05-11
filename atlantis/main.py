"""CLI and application entrypoint."""

from __future__ import annotations

import argparse
import logging
import os
from collections.abc import Sequence

from atlantis.core.app import create_application
from atlantis.core.logging import configure_logging
from atlantis.ui.main_window import MainWindow

_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level argument parser."""
    parser = argparse.ArgumentParser(description="Atlantis Mermaid desktop editor")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Create the app and window, then exit without starting the event loop.",
    )
    parser.add_argument(
        "--log-level",
        choices=_LOG_LEVELS,
        default=None,
        help="Override log level (also honored via ATLANTIS_LOG_LEVEL env var).",
    )
    return parser


def _resolve_log_level(args: argparse.Namespace) -> int:
    raw = args.log_level or os.environ.get("ATLANTIS_LOG_LEVEL", "WARNING")
    return getattr(logging, raw.upper(), logging.WARNING)


def main(argv: Sequence[str] | None = None) -> int:
    """Run Atlantis and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.smoke_test:
        os.environ["ATLANTIS_HEADLESS"] = "1"

    configure_logging(_resolve_log_level(args))

    app = create_application()
    window = MainWindow()
    window.show()

    if args.smoke_test:
        window.close()
        app.quit()
        return 0

    return app.exec()
