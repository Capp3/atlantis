"""Regression lock: mypy must pass on the atlantis package."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_mypy_atlantis_is_clean() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "atlantis"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
