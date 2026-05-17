"""Tests for vendored Mermaid assets and path resolution."""

from __future__ import annotations

from importlib import resources

import pytest

from atlantis.renderer.mermaid_assets import (
    MERMAID_CDN,
    MERMAID_VENDOR_RELATIVE,
    MERMAID_VERSION,
    mermaid_script_src,
    mermaid_version_file,
    preview_shell_template,
    use_mermaid_cdn,
)


def test_vendored_mermaid_file_exists_and_is_large() -> None:
    data = (resources.files("atlantis.assets") / "vendor" / "mermaid" / "mermaid.min.js").read_bytes()
    assert len(data) > 100_000


def test_version_file_matches_constant() -> None:
    assert mermaid_version_file() == MERMAID_VERSION


def test_default_script_src_is_local_relative() -> None:
    assert mermaid_script_src(use_cdn=False) == MERMAID_VENDOR_RELATIVE
    assert "cdn.jsdelivr.net" not in mermaid_script_src(use_cdn=False)


def test_cdn_script_src_when_env_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ATLANTIS_USE_MERMAID_CDN", "1")
    assert use_mermaid_cdn() is True
    assert mermaid_script_src() == MERMAID_CDN


def test_preview_shell_template_has_placeholders() -> None:
    template = preview_shell_template()
    assert "{{MERMAID_SCRIPT_SRC}}" in template
    assert "{{THEME_JSON}}" in template
    assert "atlantisRender" in template
