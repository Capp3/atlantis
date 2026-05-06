"""CLI and application entrypoint."""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence

from atlantis.core.app import create_application
from atlantis.ui.main_window import MainWindow


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level argument parser."""
    parser = argparse.ArgumentParser(description="Atlantis Mermaid desktop editor")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Create the app and window, then exit without starting the event loop.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run Atlantis and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.smoke_test:
        os.environ["ATLANTIS_HEADLESS"] = "1"

    app = create_application()
    window = MainWindow()
    window.show()

    if args.smoke_test:
        window.close()
        app.quit()
        return 0

    return app.exec()
