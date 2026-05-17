"""Built-in plugin manifests used by tests and documentation."""

from __future__ import annotations

from atlantis.plugins.manifest import Contribution, ContributionKind, PluginManifest


def core_plugin_manifest() -> PluginManifest:
    """Return the built-in pseudo-plugin manifest for registry tests."""
    return PluginManifest(
        id="atlantis.core",
        name="Atlantis Core",
        version="0.0.1",
        description="Built-in placeholder; no user-facing contributions in v1.",
        api_version="1",
        contributions=(
            Contribution(
                kind=ContributionKind.MENU_ACTION,
                id="core.about",
                label="About Atlantis",
                description="Reserved for a future about dialog.",
            ),
        ),
    )
