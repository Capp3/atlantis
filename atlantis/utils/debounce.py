"""Debounce helpers."""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QObject, QTimer


class Debouncer(QObject):
    """Invoke a callback once after no new triggers for a delay."""

    def __init__(self, delay_ms: int, callback: Callable[[], None]) -> None:
        super().__init__()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(delay_ms)
        self._timer.timeout.connect(callback)

    def trigger(self) -> None:
        """Start or restart the delay window."""
        self._timer.start()
