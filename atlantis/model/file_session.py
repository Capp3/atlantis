"""Active document path session (no Qt dependencies)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from atlantis.model.file_handler import autosave_path_for


@dataclass(slots=True)
class FileSession:
    """Owns the on-disk path for the editor's current document."""

    path: Path | None = None

    def bind(self, path: Path | None) -> None:
        """Associate this session with a document path (or None for untitled)."""
        self.path = path

    def clear(self) -> None:
        """Reset to an untitled document."""
        self.path = None

    def autosave_path(self) -> Path:
        """Return the rolling autosave path for the current document."""
        return autosave_path_for(self.path)

    def window_title(self, base: str = "Atlantis") -> str:
        """Return a window title for the current document."""
        if self.path is None:
            return base
        return f"{base} - {self.path.name}"

    def matches(self, candidate: Path) -> bool:
        """Return True when candidate is the bound document path."""
        return self.path is not None and candidate == self.path

    def read_disk_text(self) -> str:
        """Read on-disk document text, or empty string when unavailable."""
        if self.path is None or not self.path.exists():
            return ""
        try:
            return self.path.read_text(encoding="utf-8")
        except OSError:
            return ""
