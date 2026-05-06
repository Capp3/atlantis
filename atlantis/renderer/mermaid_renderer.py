"""Mermaid renderer facade."""

from __future__ import annotations

from dataclasses import dataclass
from re import search


@dataclass(slots=True)
class RenderResult:
    """Simple render result placeholder for early implementation phases."""

    ok: bool
    svg: str | None = None
    error: str | None = None


class MermaidRenderer:
    """Renderer placeholder with lightweight Mermaid text validation."""

    _SUPPORTED_PATTERNS = (
        r"\bflowchart\b",
        r"\bgraph\b",
        r"\bsequenceDiagram\b",
        r"\bclassDiagram\b",
        r"\bstateDiagram\b",
        r"\berDiagram\b",
    )

    def render(self, source: str) -> RenderResult:
        """Return a placeholder SVG for recognized Mermaid syntax."""
        if not source.strip():
            return RenderResult(ok=False, error="No Mermaid source provided.")

        if not any(search(pattern, source) for pattern in self._SUPPORTED_PATTERNS):
            return RenderResult(ok=False, error="Unable to render Mermaid source.")

        return RenderResult(ok=True, svg="<svg><!-- phase-1-placeholder --></svg>")
