# ADR 0001 — Ship Mermaid via CDN for MVP

| Status | Date | Owner |
|--------|------|-------|
| Superseded (runtime default) | 2026-05-11 | Atlantis core team |

> **Note:** CDN loading remains available via `ATLANTIS_USE_MERMAID_CDN=1`. The default runtime policy is defined in [ADR 0003 — Offline Mermaid bundle](0003-mermaid-offline-bundle.md).

## Context

The Atlantis preview embeds Mermaid.js inside a `QWebEngineView`. We needed to choose between two delivery models for the MVP:

1. **CDN-loaded JS** — fetch `mermaid.min.js` from `cdn.jsdelivr.net` at first paint.
2. **Bundled JS** — ship a vendored `mermaid.min.js` inside the Python package.

The choice has downstream impact on packaging, offline behaviour, security policy, and the renderer creative record (`memory-bank/creative/creative-renderer-offline-bundle.md`).

## Decision

For MVP, **load Mermaid 10.9.3 from CDN** (`https://cdn.jsdelivr.net/npm/mermaid@10.9.3/dist/mermaid.min.js`). The version is pinned in `atlantis/renderer/webengine_bridge.py` (`MERMAID_VERSION`). Bundling is deferred to a Stage-2 follow-up (see [Renderer guide](../user-guide/renderer.md)).

## Consequences

**Positive**

- MVP ships without an asset pipeline or wheel-bloat.
- Mermaid version bumps are a one-line change; the tech validation PoC under `scripts/tech_validation_mermaid_webengine.py` re-runs in seconds.
- A single, well-cached jsDelivr URL keeps first-paint fast on most networks.

**Negative**

- Offline use is impossible until Stage 2 (`creative-renderer-offline-bundle.md` outlines the planned bundle).
- A firewall/captive-portal that blocks `cdn.jsdelivr.net` will surface as a blank preview; the troubleshooting page documents the failure mode.
- We carry an external trust boundary; mitigated by pinning the exact version and using `securityLevel: "loose"` rather than `securityLevel: "antiscript"` only when the renderer is loaded from this trusted source.

## Follow-ups

- Stage 2: ship `assets/preview_shell.html` with a vendored `mermaid.min.js`, gated by a build-time toggle.
- Confirm with users that the CDN dependency is acceptable for their environments before promoting MVP to GA.
