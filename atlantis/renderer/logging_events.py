"""Structured logging helpers for the Mermaid renderer package."""

from __future__ import annotations

import logging
from typing import Any

BRIDGE_LOGGER = logging.getLogger("atlantis.renderer.bridge")
ASSETS_LOGGER = logging.getLogger("atlantis.renderer.assets")

_ERROR_TRUNCATE = 200


def truncate_error(message: str, *, max_len: int = _ERROR_TRUNCATE) -> str:
    """Truncate error text for log lines."""
    text = message.replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return f"{text[: max_len - 3]}..."


def mermaid_src_label(script_src: str) -> str:
    """Return ``local`` or ``cdn`` for structured logs (not the full URL)."""
    return "cdn" if "cdn.jsdelivr.net" in script_src else "local"


def _format_message(event: str, fields: dict[str, Any]) -> str:
    parts = [f"event={event}"]
    for key in sorted(fields):
        if key == "event":
            continue
        value = fields[key]
        if isinstance(value, bool):
            parts.append(f"{key}={'true' if value else 'false'}")
        elif isinstance(value, float):
            parts.append(f"{key}={value:.1f}")
        else:
            parts.append(f"{key}={value}")
    return " ".join(parts)


def log_event(logger: logging.Logger, level: int, event: str, **fields: Any) -> None:
    """Log a renderer event with grep-friendly ``event=`` message and ``extra`` fields."""
    payload = {**fields, "event": event}
    message = _format_message(event, fields)
    logger.log(level, message, extra=payload)
