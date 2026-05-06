"""Core diagram model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DiagramDocument:
    """Represents a single Mermaid document."""

    source: str = ""
    front_matter: str = ""
