"""Hygiene tests for packaging targets and PyInstaller spec."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAKE = shutil.which("make")
assert MAKE is not None


def test_pyinstaller_spec_exists() -> None:
    spec = REPO_ROOT / "packaging" / "pyinstaller" / "atlantis.spec"
    assert spec.is_file()
    text = spec.read_text(encoding="utf-8")
    assert "atlantis/assets" in text
    assert "PyQt6.QtWebEngineWidgets" in text


def test_makefile_defines_bundle_smoke() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert re.search(r"^bundle-smoke:", makefile, re.MULTILINE) is not None
    assert re.search(r"^bundle:", makefile, re.MULTILINE) is not None


def test_packaging_dependency_group_in_pyproject() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "packaging" in pyproject
    assert "pyinstaller" in pyproject.lower()
