"""Plugin manifest types for Atlantis extension contributions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PluginManifestError(ValueError):
    """Raised when a manifest or contribution is invalid."""


class ContributionKind(StrEnum):
    """Supported plugin contribution kinds (v1 API)."""

    MENU_ACTION = "menu_action"
    EXPORT = "export"
    EDITOR_PANEL = "editor_panel"


SUPPORTED_API_VERSIONS: frozenset[str] = frozenset({"1"})

_ALLOWED_KINDS: frozenset[ContributionKind] = frozenset(ContributionKind)


@dataclass(frozen=True, slots=True)
class Contribution:
    """A single contribution from a plugin manifest."""

    kind: ContributionKind
    id: str
    label: str
    description: str = ""

    def validate(self) -> None:
        """Validate contribution fields."""
        if self.kind not in _ALLOWED_KINDS:
            msg = f"unsupported contribution kind: {self.kind!r}"
            raise PluginManifestError(msg)
        if not self.id.strip():
            msg = "contribution id must not be empty"
            raise PluginManifestError(msg)
        if not self.label.strip():
            msg = "contribution label must not be empty"
            raise PluginManifestError(msg)


@dataclass(frozen=True, slots=True)
class PluginManifest:
    """Declarative description of a plugin (no dynamic loading in v1)."""

    id: str
    name: str
    version: str
    description: str
    api_version: str
    contributions: tuple[Contribution, ...] = ()

    def validate(self) -> None:
        """Validate manifest fields."""
        if not self.id.strip():
            msg = "plugin id must not be empty"
            raise PluginManifestError(msg)
        if not self.name.strip():
            msg = "plugin name must not be empty"
            raise PluginManifestError(msg)
        if not self.version.strip():
            msg = "plugin version must not be empty"
            raise PluginManifestError(msg)
        if self.api_version not in SUPPORTED_API_VERSIONS:
            msg = f"unsupported api_version: {self.api_version!r}"
            raise PluginManifestError(msg)
        for contribution in self.contributions:
            contribution.validate()
