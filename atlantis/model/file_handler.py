"""File I/O helpers for .mmd files."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from PyQt6.QtCore import QStandardPaths


def read_mermaid_file(path: Path) -> str:
    """Read a Mermaid file and return its text."""
    return path.read_text(encoding="utf-8")


def write_mermaid_file(path: Path, content: str) -> None:
    """Write Mermaid content to disk."""
    path.write_text(content, encoding="utf-8")


def autosave_dir() -> Path:
    """Return autosave directory, overridable for tests."""
    override = os.environ.get("ATLANTIS_AUTOSAVE_DIR")
    if override:
        target = Path(override)
    else:
        base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.TempLocation)
        target = Path(base) / "atlantis-autosave"
    target.mkdir(parents=True, exist_ok=True)
    return target


def autosave_path_for(document_path: Path | None) -> Path:
    """Return deterministic autosave path for a document."""
    if document_path is None:
        return autosave_dir() / "untitled.mmd.autosave"
    key = hashlib.sha256(str(document_path).encode("utf-8")).hexdigest()[:16]
    return autosave_dir() / f"{key}.mmd.autosave"


def write_autosave(document_path: Path | None, content: str) -> Path:
    """Write rolling autosave content and return path."""
    target = autosave_path_for(document_path)
    target.write_text(content, encoding="utf-8")
    return target


def read_autosave(document_path: Path | None) -> str | None:
    """Read autosave content if present."""
    target = autosave_path_for(document_path)
    if not target.exists():
        return None
    return target.read_text(encoding="utf-8")


def clear_autosave(document_path: Path | None) -> None:
    """Delete autosave file for a document if present."""
    target = autosave_path_for(document_path)
    if target.exists():
        target.unlink()
