"""Tests for TOML front matter serialization and document composition."""

from __future__ import annotations

import tomllib

from atlantis.utils.frontmatter import (
    FrontMatterFormat,
    format_toml_front_matter,
    format_toml_front_matter_from_inner,
    insert_toml_front_matter,
    replace_front_matter,
    serialize_toml_inner,
    split_front_matter,
    try_parse_metadata,
    validate_toml_inner,
)


def test_serialize_toml_inner_round_trips() -> None:
    data = {"title": "X", "config": {"theme": "dark"}}
    inner = serialize_toml_inner(data)
    parsed = tomllib.loads(inner)
    assert parsed["title"] == "X"
    assert parsed["config"]["theme"] == "dark"


def test_format_toml_front_matter_has_fences() -> None:
    block = format_toml_front_matter({"title": "A"})
    assert block.startswith("+++\n")
    assert block.endswith("+++\n")
    assert 'title = "A"' in block


def test_replace_front_matter_preserves_body() -> None:
    raw = '+++\ntitle = "old"\n+++\nflowchart TD\nA-->B\n'
    updated = replace_front_matter(raw, '+++\ntitle = "new"\n+++\n')
    assert updated.startswith('+++\ntitle = "new"')
    assert updated.endswith("flowchart TD\nA-->B\n")
    assert split_front_matter(updated).body == "flowchart TD\nA-->B\n"


def test_insert_toml_front_matter_prepends_block() -> None:
    body = "flowchart TD\nA-->B\n"
    result = insert_toml_front_matter(body, {"title": "New"})
    assert result.startswith("+++")
    assert result.endswith(body)
    parsed = split_front_matter(result)
    assert parsed.format is FrontMatterFormat.TOML
    data, warning = try_parse_metadata(parsed)
    assert warning is None
    assert data is not None
    assert data["title"] == "New"


def test_format_toml_from_inner_and_validate() -> None:
    inner = 'title = "X"'
    assert validate_toml_inner(inner) is None
    block = format_toml_front_matter_from_inner(inner)
    assert block == '+++\ntitle = "X"\n+++\n'


def test_validate_toml_inner_reports_errors() -> None:
    assert validate_toml_inner("not valid =") is not None
