"""In-process plugin registry (manifest registration only; no dynamic loader)."""

from __future__ import annotations

from atlantis.plugins.manifest import (
    Contribution,
    ContributionKind,
    PluginManifest,
    PluginManifestError,
)


class PluginRegistry:
    """Register plugin manifests and query contributions.

    Plugins must not register Mermaid dialect hooks. Export contributions are
    expected to use the renderer facade only when a loader exists (future).
    """

    def __init__(self) -> None:
        self._plugins: dict[str, PluginManifest] = {}

    def register(self, manifest: PluginManifest) -> None:
        """Register a plugin manifest."""
        manifest.validate()
        if manifest.id in self._plugins:
            msg = f"duplicate plugin id: {manifest.id!r}"
            raise PluginManifestError(msg)
        self._plugins[manifest.id] = manifest

    def list_plugins(self) -> list[PluginManifest]:
        """Return registered manifests sorted by plugin id."""
        return [self._plugins[key] for key in sorted(self._plugins)]

    def contributions(self, kind: ContributionKind | None = None) -> list[Contribution]:
        """Return all contributions, optionally filtered by kind."""
        result: list[Contribution] = []
        for manifest in self.list_plugins():
            for contribution in manifest.contributions:
                if kind is None or contribution.kind is kind:
                    result.append(contribution)
        return result

    def clear(self) -> None:
        """Remove all registered plugins (for tests)."""
        self._plugins.clear()
