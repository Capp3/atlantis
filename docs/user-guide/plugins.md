# Plugins (planned)

Atlantis does **not** load third-party plugins in the current release. This page describes the **v1 extension model** implemented as an in-process registry scaffold for future work.

## Design principles

Plugins must **not** alter Mermaid syntax or diagram output. All generated content must remain standard Mermaid.

Future plugins may contribute:

- Menu actions and editor tooling (snippets, lint helpers)
- Export handlers (PNG/SVG) via the renderer facade
- Optional editor panels

Plugins are expected to be **local-only**, **filesystem-based**, **sandboxed**, and **globally configured** (not per `.mmd` file).

## Current implementation (v1 scaffold)

| Component | Role |
|-----------|------|
| `PluginManifest` | Declares `id`, `name`, `version`, `api_version`, and `contributions` |
| `ContributionKind` | `menu_action`, `export`, `editor_panel` |
| `PluginRegistry` | In-process registration and contribution queries |

There is **no dynamic loader** yet — manifests are registered by the application or tests only. See `atlantis.plugins` in the API reference.

## Guardrails

- No contribution kind for Mermaid dialect or syntax extensions.
- Export contributions must use the renderer facade when implemented (not raw WebEngine injection).
- Plugin installation UI and marketplace are out of scope.

## Related docs

- [Architecture → Plugin boundaries](../reference/architecture.md)
- [Installation](installation.md) — how to run Atlantis today
