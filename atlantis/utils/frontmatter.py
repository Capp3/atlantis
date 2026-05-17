"""Front matter parsing utilities for Mermaid documents.

Atlantis preserves the original front matter text verbatim on save so user-written
YAML or TOML metadata round-trips cleanly. Higher-level dict parsing is best-effort
and only emits warnings (never blocks editing).
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import tomli_w


class FrontMatterFormat(StrEnum):
    """Recognized front matter formats."""

    YAML = "yaml"
    TOML = "toml"


_YAML_FENCE = "---"
_TOML_FENCE = "+++"


@dataclass(slots=True)
class FrontMatterParseResult:
    """Parsed front matter result preserving original text segments."""

    front_matter: str
    body: str
    format: FrontMatterFormat | None = None

    @property
    def has_front_matter(self) -> bool:
        """Return True when a front matter block was detected."""
        return self.format is not None


def split_front_matter(raw_text: str) -> FrontMatterParseResult:
    """Split a Mermaid document into its front matter (if any) and body.

    The detection only fires when the first non-empty line is one of the supported
    fences (``---`` or ``+++``) on its own line. The front matter text returned
    includes the opening fence, content lines, the closing fence, and the trailing
    newline so saving back ``front_matter + body`` reproduces the input exactly.
    """
    if not raw_text:
        return FrontMatterParseResult(front_matter="", body="")

    lines = raw_text.splitlines(keepends=True)
    if not lines:
        return FrontMatterParseResult(front_matter="", body=raw_text)

    first = lines[0].rstrip("\r\n")
    fence: str | None
    fmt: FrontMatterFormat | None
    if first == _YAML_FENCE:
        fence = _YAML_FENCE
        fmt = FrontMatterFormat.YAML
    elif first == _TOML_FENCE:
        fence = _TOML_FENCE
        fmt = FrontMatterFormat.TOML
    else:
        return FrontMatterParseResult(front_matter="", body=raw_text)

    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r\n") == fence:
            front_matter = "".join(lines[: idx + 1])
            body = "".join(lines[idx + 1 :])
            return FrontMatterParseResult(front_matter=front_matter, body=body, format=fmt)

    return FrontMatterParseResult(front_matter="", body=raw_text)


def try_parse_metadata(result: FrontMatterParseResult) -> tuple[dict[str, Any] | None, str | None]:
    """Best-effort decode of a parsed front matter block into a dict.

    Returns ``(data, warning)``. ``data`` is ``None`` and ``warning`` is a short
    user-facing message when the block cannot be parsed (e.g. YAML without
    optional dependency, or invalid TOML). Successful parses return ``(dict, None)``.
    """
    if not result.has_front_matter or not result.front_matter:
        return None, None

    inner = _strip_fences(result.front_matter)
    if result.format is FrontMatterFormat.TOML:
        try:
            return tomllib.loads(inner), None
        except tomllib.TOMLDecodeError as exc:
            return None, f"Invalid TOML front matter: {exc}"
    return None, "YAML front matter preserved as-is (no parser installed)."


def strip_front_matter_inner(front_matter: str) -> str:
    """Return front matter content between opening and closing fences."""
    return _strip_fences(front_matter)


def _strip_fences(front_matter: str) -> str:
    lines = front_matter.splitlines()
    if len(lines) <= 2:
        return ""
    return "\n".join(lines[1:-1]) + "\n"


def serialize_toml_inner(data: dict[str, Any]) -> str:
    """Serialize a metadata dict to TOML inner text (no fences)."""
    return tomli_w.dumps(data)


def format_toml_front_matter(data: dict[str, Any]) -> str:
    """Format a metadata dict as a fenced TOML front matter block."""
    inner = serialize_toml_inner(data).strip()
    if inner:
        return f"+++\n{inner}\n+++\n"
    return "+++\n+++\n"


def format_toml_front_matter_from_inner(inner: str) -> str:
    """Wrap raw TOML inner text with ``+++`` fences."""
    stripped = inner.strip()
    if stripped:
        return f"+++\n{stripped}\n+++\n"
    return "+++\n+++\n"


def replace_front_matter(raw: str, new_front_matter: str) -> str:
    """Replace an existing front matter block, preserving the document body."""
    parsed = split_front_matter(raw)
    if not parsed.has_front_matter:
        return new_front_matter + raw
    fm = new_front_matter if new_front_matter.endswith("\n") else f"{new_front_matter}\n"
    return fm + parsed.body


def insert_toml_front_matter(body: str, data: dict[str, Any]) -> str:
    """Prepend a new TOML front matter block to a document body."""
    return format_toml_front_matter(data) + body


def validate_toml_inner(inner: str) -> str | None:
    """Return a user-facing error when *inner* is not valid TOML, else ``None``."""
    try:
        tomllib.loads(inner if inner.endswith("\n") else f"{inner}\n")
    except tomllib.TOMLDecodeError as exc:
        return f"Invalid TOML: {exc}"
    return None
