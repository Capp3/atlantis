"""Phase 4 front matter parsing tests."""

from __future__ import annotations

from atlantis.utils.frontmatter import FrontMatterFormat, split_front_matter, try_parse_metadata


def test_no_front_matter_round_trips() -> None:
    raw = "flowchart TD\nA-->B\n"
    result = split_front_matter(raw)
    assert result.front_matter == ""
    assert result.body == raw
    assert result.format is None
    assert not result.has_front_matter


def test_yaml_front_matter_is_preserved_verbatim() -> None:
    raw = "---\ntitle: My Diagram\nconfig:\n  theme: default\n---\nflowchart TD\nA-->B\n"
    result = split_front_matter(raw)
    assert result.format is FrontMatterFormat.YAML
    assert result.front_matter == "---\ntitle: My Diagram\nconfig:\n  theme: default\n---\n"
    assert result.body == "flowchart TD\nA-->B\n"
    assert result.front_matter + result.body == raw


def test_toml_front_matter_parses_to_dict() -> None:
    raw = '+++\ntitle = "X"\n+++\nflowchart TD\nA-->B\n'
    result = split_front_matter(raw)
    assert result.format is FrontMatterFormat.TOML
    data, warning = try_parse_metadata(result)
    assert warning is None
    assert data is not None
    assert data["title"] == "X"


def test_invalid_toml_returns_warning_not_exception() -> None:
    raw = "+++\nnot toml at all\n+++\nflowchart TD\n"
    result = split_front_matter(raw)
    assert result.format is FrontMatterFormat.TOML
    data, warning = try_parse_metadata(result)
    assert data is None
    assert warning is not None
    assert "TOML" in warning


def test_yaml_metadata_warns_when_no_parser() -> None:
    raw = "---\ntitle: X\n---\nflowchart\n"
    result = split_front_matter(raw)
    data, warning = try_parse_metadata(result)
    assert data is None
    assert warning is not None


def test_unterminated_fence_treated_as_no_front_matter() -> None:
    raw = "---\ntitle: only opener\nflowchart TD\n"
    result = split_front_matter(raw)
    assert result.format is None
    assert result.front_matter == ""
    assert result.body == raw
