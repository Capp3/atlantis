"""Plugin manifest and registry (v1 scaffold; no dynamic loader)."""

from atlantis.plugins.builtin import core_plugin_manifest
from atlantis.plugins.manifest import (
    SUPPORTED_API_VERSIONS,
    Contribution,
    ContributionKind,
    PluginManifest,
    PluginManifestError,
)
from atlantis.plugins.registry import PluginRegistry

__all__ = [
    "SUPPORTED_API_VERSIONS",
    "Contribution",
    "ContributionKind",
    "PluginManifest",
    "PluginManifestError",
    "PluginRegistry",
    "core_plugin_manifest",
]
