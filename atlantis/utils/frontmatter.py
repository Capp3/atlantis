"""Front matter parsing placeholders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class FrontMatterParseResult:
    """Parsed front matter result."""

    front_matter: str
    body: str


def split_front_matter(raw_text: str) -> FrontMatterParseResult:
    """Return an unmodified split placeholder for Phase 1."""
    return FrontMatterParseResult(front_matter="", body=raw_text)
