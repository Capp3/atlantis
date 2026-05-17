# ADR 0003 — Offline Mermaid bundle (default local assets)

| Status | Date | Owner |
|--------|------|-------|
| Accepted | 2026-05-16 | Atlantis core team |

## Context

ADR [0001](0001-mermaid-cdn-mvp.md) accepted a CDN-loaded Mermaid script for MVP velocity. Stage 2 (see `memory-bank/creative/creative-renderer-offline-bundle.md`) requires a **vendored** Mermaid 10.9.3 so Atlantis works offline and matches the project brief.

## Decision

1. Ship `atlantis/assets/vendor/mermaid/mermaid.min.js` (pinned **10.9.3**) inside the Python package (included in the wheel via hatch `force-include`).
2. Load the preview from `atlantis/assets/preview/preview_shell.html` with `QWebEnginePage.setHtml(html, baseUrl=file://…/preview/)` and a **relative** script `../vendor/mermaid/mermaid.min.js`.
3. **Default runtime is offline** (local bundle). Set `ATLANTIS_USE_MERMAID_CDN=1` to restore the jsDelivr URL for debugging or air-gapped development against a known CDN mirror.
4. Maintain `MERMAID_VERSION` in `atlantis/renderer/mermaid_assets.py` (re-exported from `webengine_bridge.py`).

## Consequences

**Positive**

- Preview works without network access once the package is installed.
- Version pin is explicit (`VERSION` file + constant); upgrades use `scripts/fetch_mermaid_vendor.py`.
- CDN path remains available for comparison testing.

**Negative**

- Wheel/sdist grows by ~3 MB (minified Mermaid).
- `importlib.resources.as_file` keeps extracted asset paths alive for the bridge lifetime (required for zipped installs).

## Supersedes

- ADR 0001 remains historical context; **runtime default** is no longer CDN-first. See ADR 0001 “Follow-ups” and this document for the current policy.

## References

- `atlantis/renderer/mermaid_assets.py`, `atlantis/renderer/webengine_bridge.py`
- `scripts/fetch_mermaid_vendor.py`
- `memory-bank/creative/creative-renderer-offline-bundle.md`
