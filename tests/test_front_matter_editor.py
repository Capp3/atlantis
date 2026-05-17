"""Tests for the front matter editor dialog."""

from __future__ import annotations

from atlantis.ui.front_matter_editor import FrontMatterEditorDialog
from atlantis.utils.frontmatter import FrontMatterFormat, split_front_matter, try_parse_metadata


def test_toml_form_dialog_accepts_updated_title() -> None:
    raw = '+++\ntitle = "Old"\n+++\nflowchart TD\n'
    parsed = split_front_matter(raw)
    data, warning = try_parse_metadata(parsed)
    assert warning is None
    assert data is not None

    dialog = FrontMatterEditorDialog(parsed=parsed, metadata=data, warning=warning)
    assert dialog._scalar_rows
    dialog._scalar_rows[0].set_value_text("New")
    dialog._accept_toml_form()

    assert dialog.result_front_matter is not None
    assert 'title = "New"' in dialog.result_front_matter


def test_yaml_dialog_is_read_only_and_does_not_emit_result() -> None:
    raw = "---\ntitle: X\n---\nflowchart\n"
    parsed = split_front_matter(raw)
    data, warning = try_parse_metadata(parsed)

    dialog = FrontMatterEditorDialog(parsed=parsed, metadata=data, warning=warning)
    assert parsed.format is FrontMatterFormat.YAML
    assert dialog._raw_edit.isReadOnly()
    assert dialog.result_front_matter is None


def test_create_toml_dialog_emits_default_block() -> None:
    raw = "flowchart TD\nA-->B\n"
    parsed = split_front_matter(raw)
    assert not parsed.has_front_matter

    dialog = FrontMatterEditorDialog(parsed=parsed, metadata=None, warning=None)
    dialog._accept_toml_form()

    assert dialog.result_front_matter is not None
    assert dialog.result_front_matter.startswith("+++")
    assert 'title = ""' in dialog.result_front_matter or "title" in dialog.result_front_matter


def test_invalid_toml_raw_editor_accepts_fixed_inner() -> None:
    raw = "+++\nnot valid\n+++\nflowchart\n"
    parsed = split_front_matter(raw)
    data, warning = try_parse_metadata(parsed)
    assert data is None

    dialog = FrontMatterEditorDialog(parsed=parsed, metadata=data, warning=warning)
    dialog._raw_edit.setPlainText('title = "Fixed"')
    dialog._accept_raw_toml()

    assert dialog.result_front_matter == '+++\ntitle = "Fixed"\n+++\n'
