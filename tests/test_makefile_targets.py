"""Regression tests for the Atlantis development Makefile."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAKE = shutil.which("make")
assert MAKE is not None, "make must be on PATH for Makefile regression tests"


def test_make_help_exits_zero() -> None:
    result = subprocess.run(  # noqa: S603
        [MAKE, "help"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "check" in result.stdout


def test_make_format_check_exits_zero() -> None:
    result = subprocess.run(  # noqa: S603
        [MAKE, "format-check"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_makefile_check_target_includes_ci_gates() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    match = re.search(r"^check:\s*(.+)$", makefile, re.MULTILINE)
    assert match is not None
    prerequisites = match.group(1)
    for target in ("format-check", "lint", "typecheck", "test-cov"):
        assert target in prerequisites


def test_makefile_check_all_includes_docs() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    match = re.search(r"^check-all:\s*(.+)$", makefile, re.MULTILINE)
    assert match is not None
    assert "check" in match.group(1)
    assert "docs" in match.group(1)
