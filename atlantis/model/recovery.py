"""Recovery diff helpers for autosave restore prompts."""

from __future__ import annotations

import difflib

_DEFAULT_RECOVERY_DIFF_CONTEXT = 3


def build_recovery_diff(
    disk_text: str,
    recovery_text: str,
    *,
    context: int = _DEFAULT_RECOVERY_DIFF_CONTEXT,
) -> str:
    """Return a compact unified diff between on-disk text and recovery text."""
    disk_lines = disk_text.splitlines()
    recovery_lines = recovery_text.splitlines()
    diff_iter = difflib.unified_diff(
        disk_lines,
        recovery_lines,
        fromfile="disk",
        tofile="recovery",
        lineterm="",
        n=context,
    )
    return "\n".join(diff_iter)
