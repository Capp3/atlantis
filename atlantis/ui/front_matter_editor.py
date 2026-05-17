"""Dialog for viewing and editing document front matter."""

from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from atlantis.utils.frontmatter import (
    FrontMatterFormat,
    FrontMatterParseResult,
    format_toml_front_matter,
    format_toml_front_matter_from_inner,
    strip_front_matter_inner,
    validate_toml_inner,
)

_DEFAULT_TOML_METADATA: dict[str, Any] = {"title": ""}


class _KeyValueRow(QWidget):
    """Single key/value row in the front matter form."""

    def __init__(self, parent: QWidget | None = None, *, key: str = "", value: str = "") -> None:
        super().__init__(parent)
        self._key_edit = QLineEdit(key)
        self._value_edit = QLineEdit(value)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._key_edit, 1)
        layout.addWidget(self._value_edit, 2)

    @property
    def key(self) -> str:
        return self._key_edit.text().strip()

    @property
    def value_text(self) -> str:
        return self._value_edit.text()

    def set_value_text(self, text: str) -> None:
        self._value_edit.setText(text)


def _value_to_display(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value
    return str(value)


def _display_to_scalar(text: str) -> Any:
    stripped = text.strip()
    lowered = stripped.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if stripped.isdigit() or (stripped.startswith("-") and stripped[1:].isdigit()):
        return int(stripped)
    try:
        if "." in stripped:
            return float(stripped)
    except ValueError:
        pass
    return stripped


def _metadata_to_form_parts(metadata: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    scalars: dict[str, Any] = {}
    tables: dict[str, dict[str, Any]] = {}
    for key, value in metadata.items():
        if isinstance(value, dict):
            table: dict[str, Any] = {}
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, (dict, list)):
                    continue
                table[str(sub_key)] = sub_value
            if table:
                tables[str(key)] = table
        elif not isinstance(value, (list, dict)):
            scalars[str(key)] = value
    return scalars, tables


def _form_parts_to_metadata(scalars: dict[str, Any], tables: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = dict(scalars)
    for table_name, table_data in tables.items():
        if table_name:
            result[table_name] = table_data
    return result


class FrontMatterEditorDialog(QDialog):
    """Edit TOML front matter as a dict, or view YAML read-only."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        parsed: FrontMatterParseResult,
        metadata: dict[str, Any] | None = None,
        warning: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Front Matter")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self._parsed = parsed
        self._result_front_matter: str | None = None
        self._scalar_rows: list[_KeyValueRow] = []
        self._table_groups: list[tuple[str, QGroupBox, list[_KeyValueRow]]] = []

        layout = QVBoxLayout(self)
        self._notice_label = QLabel()
        self._notice_label.setWordWrap(True)
        layout.addWidget(self._notice_label)

        self._form_host = QWidget()
        self._form_layout = QVBoxLayout(self._form_host)
        self._form_layout.setContentsMargins(0, 0, 0, 0)

        self._raw_edit = QPlainTextEdit()
        self._raw_edit.setPlaceholderText('title = "My diagram"')

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._form_host)

        self._add_row_button = QPushButton("Add field")
        self._add_row_button.clicked.connect(self._add_scalar_row)

        self._buttons = QDialogButtonBox()
        layout.addWidget(scroll)
        layout.addWidget(self._raw_edit)
        layout.addWidget(self._add_row_button)
        layout.addWidget(self._buttons)

        if parsed.format is FrontMatterFormat.YAML:
            self._build_yaml_readonly()
        elif parsed.format is FrontMatterFormat.TOML and metadata is None:
            self._build_invalid_toml(warning)
        elif parsed.format is FrontMatterFormat.TOML:
            self._build_toml_form(metadata or {})
        else:
            self._build_create_toml()

        self._buttons.rejected.connect(self.reject)

    @property
    def result_front_matter(self) -> str | None:
        """Fenced front matter block after accept, or ``None`` when unchanged."""
        return self._result_front_matter

    def _build_yaml_readonly(self) -> None:
        self._notice_label.setText(
            "YAML front matter is preserved as-is. Edit it in the source editor; "
            "Atlantis does not ship a YAML parser for structured editing."
        )
        self._form_host.hide()
        self._raw_edit.setReadOnly(True)
        self._raw_edit.setPlainText(self._parsed.front_matter)
        self._raw_edit.show()
        self._add_row_button.hide()
        self._buttons.addButton(QDialogButtonBox.StandardButton.Close)

    def _build_invalid_toml(self, warning: str | None) -> None:
        self._notice_label.setText(
            warning or "Front matter could not be parsed. Fix the TOML below or edit in the source."
        )
        self._form_host.hide()
        self._raw_edit.show()
        self._add_row_button.hide()
        self._raw_edit.setPlainText(strip_front_matter_inner(self._parsed.front_matter).rstrip("\n"))
        self._buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self._buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._buttons.accepted.connect(self._accept_raw_toml)

    def _build_toml_form(self, metadata: dict[str, Any]) -> None:
        self._notice_label.setText(
            "Editing TOML via this dialog re-emits the block; comments and key order may change. "
            "For full control, edit the source directly."
        )
        self._raw_edit.hide()
        scalars, tables = _metadata_to_form_parts(metadata)
        for key, value in scalars.items():
            self._add_scalar_row(key=key, value=_value_to_display(value))
        for table_name, table_data in tables.items():
            self._add_table_group(table_name, table_data)
        if not self._scalar_rows and not self._table_groups:
            self._add_scalar_row(key="title", value="")
        self._buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self._buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._buttons.accepted.connect(self._accept_toml_form)

    def _build_create_toml(self) -> None:
        self._notice_label.setText("This document has no front matter. Add a TOML block below.")
        self._raw_edit.hide()
        self._add_scalar_row(key="title", value="")
        self._buttons.addButton(QDialogButtonBox.StandardButton.Ok)
        self._buttons.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._buttons.accepted.connect(self._accept_toml_form)

    def _add_scalar_row(self, *, key: str = "", value: str = "") -> None:
        row = _KeyValueRow(self._form_host, key=key, value=value)
        self._scalar_rows.append(row)
        self._form_layout.addWidget(row)

    def _add_table_group(self, table_name: str, table_data: dict[str, Any]) -> None:
        group = QGroupBox(f"[{table_name}]")
        form = QFormLayout(group)
        rows: list[_KeyValueRow] = []
        for sub_key, sub_value in table_data.items():
            row = _KeyValueRow(group, key=sub_key, value=_value_to_display(sub_value))
            rows.append(row)
            form.addRow(sub_key, row)
        self._table_groups.append((table_name, group, rows))
        self._form_layout.addWidget(group)

    def _collect_metadata(self) -> dict[str, Any]:
        scalars: dict[str, Any] = {}
        for row in self._scalar_rows:
            key = row.key
            if not key:
                continue
            scalars[key] = _display_to_scalar(row.value_text)
        tables: dict[str, dict[str, Any]] = {}
        for table_name, _group, rows in self._table_groups:
            table_data: dict[str, Any] = {}
            for row in rows:
                key = row.key
                if not key:
                    continue
                table_data[key] = _display_to_scalar(row.value_text)
            if table_data:
                tables[table_name] = table_data
        return _form_parts_to_metadata(scalars, tables)

    def _accept_toml_form(self) -> None:
        metadata = self._collect_metadata() or _DEFAULT_TOML_METADATA
        self._result_front_matter = format_toml_front_matter(metadata)
        self.accept()

    def _accept_raw_toml(self) -> None:
        inner = self._raw_edit.toPlainText()
        error = validate_toml_inner(inner)
        if error:
            QMessageBox.warning(self, "Invalid TOML", error)
            return
        self._result_front_matter = format_toml_front_matter_from_inner(inner)
        self.accept()
