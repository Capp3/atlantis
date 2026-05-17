"""Tests for the plugin manifest and registry scaffold."""

from __future__ import annotations

import pytest

from atlantis.plugins import (
    Contribution,
    ContributionKind,
    PluginManifest,
    PluginManifestError,
    PluginRegistry,
    core_plugin_manifest,
)
from atlantis.plugins.manifest import SUPPORTED_API_VERSIONS


def test_supported_api_versions_includes_v1() -> None:
    assert "1" in SUPPORTED_API_VERSIONS


def test_register_and_list_plugins() -> None:
    registry = PluginRegistry()
    manifest = core_plugin_manifest()
    registry.register(manifest)
    listed = registry.list_plugins()
    assert len(listed) == 1
    assert listed[0].id == "atlantis.core"


def test_duplicate_plugin_id_raises() -> None:
    registry = PluginRegistry()
    registry.register(core_plugin_manifest())
    with pytest.raises(PluginManifestError, match="duplicate"):
        registry.register(core_plugin_manifest())


def test_unsupported_api_version_rejected() -> None:
    registry = PluginRegistry()
    bad = PluginManifest(
        id="bad.api",
        name="Bad",
        version="0",
        description="",
        api_version="99",
    )
    with pytest.raises(PluginManifestError, match="api_version"):
        registry.register(bad)


def test_contributions_filter_by_kind() -> None:
    registry = PluginRegistry()
    manifest = PluginManifest(
        id="mixed",
        name="Mixed",
        version="1",
        description="",
        api_version="1",
        contributions=(
            Contribution(kind=ContributionKind.MENU_ACTION, id="a", label="A"),
            Contribution(kind=ContributionKind.EXPORT, id="b", label="B"),
        ),
    )
    registry.register(manifest)
    assert len(registry.contributions()) == 2
    assert len(registry.contributions(ContributionKind.EXPORT)) == 1
    assert registry.contributions(ContributionKind.EXPORT)[0].id == "b"


def test_empty_plugin_id_rejected() -> None:
    with pytest.raises(PluginManifestError, match="plugin id"):
        PluginManifest(
            id="  ",
            name="X",
            version="1",
            description="",
            api_version="1",
        ).validate()


def test_registry_clear() -> None:
    registry = PluginRegistry()
    registry.register(core_plugin_manifest())
    registry.clear()
    assert registry.list_plugins() == []


def test_contribution_kinds_exclude_mermaid_dialect() -> None:
    """Guardrail: only documented contribution kinds exist (no dialect hook)."""
    kinds = {member.value for member in ContributionKind}
    assert kinds == {"menu_action", "export", "editor_panel"}
    assert "mermaid_dialect" not in kinds
    assert "syntax_extension" not in kinds
