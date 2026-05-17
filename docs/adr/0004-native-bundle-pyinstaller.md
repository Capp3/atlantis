# ADR 0004 — Native bundle via PyInstaller (one-folder PoC)

| Status | Date | Owner |
|--------|------|-------|
| Accepted | 2026-05-16 | Atlantis core team |

## Context

Atlantis ships as a Python package (`uv sync` + `atlantis` console script). The project brief targets a **portable desktop app** on macOS, Windows, and Linux. Core MVP features (editor, WebEngine preview, offline Mermaid, persistence, front matter) are stable; packaging risk can be explored without blocking the PR gate.

ADR [0002](0002-pyqt6-pin-macos-12.md) pins `PyQt6<6.10` for macOS 12. ADR [0003](0003-mermaid-offline-bundle.md) vendored Mermaid into `atlantis/assets/`.

## Decision

1. Add an **experimental PyInstaller one-folder** build under `packaging/pyinstaller/atlantis.spec`.
2. Expose **`make bundle`** and **`make bundle-smoke`** (opt-in; **not** part of `make check`).
3. Keep **hatch wheel/sdist** as the canonical Python distribution; PyInstaller consumes the same entry point (`atlantis.main:main`) and asset tree.
4. **Defer** BeeWare Briefcase, macOS codesign/notarization, and Windows installers until the Linux PoC smoke test passes reliably.
5. **Defer** dynamic plugin loading; Phase 7 only adds `PluginRegistry` + manifest types.

## Consequences

**Positive**

- Contributors can validate bundle size and WebEngine collection on Linux.
- `importlib.resources` + hatch `force-include` remain the source of truth for assets; frozen layout validated via `--smoke-test`.

**Negative**

- Large `dist/` artifacts; not committed to git.
- PyInstaller layout may require a small frozen-path helper in `mermaid_assets.py` if `as_file` behaves differently (address only if smoke fails).

## Fallback

If PyInstaller cannot collect Qt WebEngine reliably, document cx_Freeze or Nuitka as alternatives before committing to Briefcase.

## References

- `packaging/pyinstaller/README.md`
- `memory-bank/creative/creative-packaging-plugin-boundaries.md`
- `docs/user-guide/installation.md`
