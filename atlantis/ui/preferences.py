"""Preferences dialogs for Atlantis."""

from __future__ import annotations

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from atlantis.core.settings import AUTOSAVE_ENABLED_KEY, AUTOSAVE_INTERVAL_KEY, get_settings

_MIN_INTERVAL_MS = 5_000
_MAX_INTERVAL_MS = 600_000


class AutosavePreferencesDialog(QDialog):
    """Dialog for editing autosave enable flag and interval."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        settings: QSettings | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Autosave Preferences")
        self._settings: QSettings = settings if settings is not None else get_settings()

        self._enabled_checkbox = QCheckBox("Enable autosave")
        self._enabled_checkbox.setChecked(self._settings.value(AUTOSAVE_ENABLED_KEY, True, type=bool))

        self._interval_spinbox = QSpinBox()
        self._interval_spinbox.setRange(_MIN_INTERVAL_MS // 1000, _MAX_INTERVAL_MS // 1000)
        self._interval_spinbox.setSuffix(" s")
        current_ms = self._settings.value(AUTOSAVE_INTERVAL_KEY, 60_000, type=int)
        self._interval_spinbox.setValue(max(_MIN_INTERVAL_MS, current_ms) // 1000)

        form = QFormLayout()
        form.addRow(self._enabled_checkbox)
        form.addRow("Autosave interval", self._interval_spinbox)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

    @property
    def autosave_enabled(self) -> bool:
        """Current value of the enable checkbox."""
        return self._enabled_checkbox.isChecked()

    @property
    def autosave_interval_ms(self) -> int:
        """Current value of the interval spinbox in milliseconds."""
        return int(self._interval_spinbox.value()) * 1000

    def _on_accept(self) -> None:
        self._settings.setValue(AUTOSAVE_ENABLED_KEY, self.autosave_enabled)
        self._settings.setValue(AUTOSAVE_INTERVAL_KEY, self.autosave_interval_ms)
        self.accept()
