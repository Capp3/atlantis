# Creative Phase: Packaging and Plugin Boundaries (refreshed 2026-05-16)

## Status
**Refreshed** for Phase 7/8 — core MVP stable; ready for `/plan`.

## Type
Architecture design (packaging + plugin host boundaries)

## Context Since Original Decision (2026-05-05)

| Area | Then (MVP BUILD) | Now (post–front matter, 2026-05-16) |
|------|------------------|-------------------------------------|
| Assets | Planned `atlantis/assets/` | **Shipped** — hatch `force-include`, `PreviewAssetSession` + `as_file` |
| Offline Mermaid | Deferred | **Shipped** — ADR 0003, vendored bundle |
| Wheel/sdist | Phase 5 target | **`uv build`** in CI/contributor flow |
| Packaging | Defer all bundling | **Core stable** — PoC warranted |
| Plugins | Boundaries only | Still **no runtime**; registry scaffold is Phase 7 scope |
| Front matter | Parse only | Menu editor shipped (`tomli-w` write path) |
| Quality gates | Partial | `make check-all`, blocking mypy, 92 tests, 80 % cov |

Original **Option 1 (defer bundling)** was correct for Phases 1–6. Phase 7/8 **does not** repeat full MVP BUILD; it adds distribution and extension **scaffolding**.

---

## 🎨🎨🎨 CREATIVE PHASE: Packaging Strategy

### Requirements
- Portable desktop app path for macOS, Windows, Linux (project brief).
- Respect **PyQt6 &lt; 6.10** on macOS 12 (ADR 0002).
- Offline Mermaid must work in bundled layout (`file://` + vendored JS).
- CI must remain green on Linux; packaging smoke must not block PR `make check`.
- Avoid tool-specific paths leaking into production code (keep `importlib.resources` + `PreviewAssetSession`).

### Options Analysis

#### Option A — Stay on hatch wheel only (no native bundle yet)
- **Pros:** Zero packaging risk; current contributor flow unchanged.
- **Cons:** Does not advance Phase 8 rollout goal; user install still `uv sync` + `atlantis`.
- **Fit:** Only if Phase 7/8 is split across multiple milestones.

#### Option B — PyInstaller one-folder PoC (recommended)
- **Description:** Add `packaging/pyinstaller/` spec + `make bundle-smoke` (Linux). One-folder dist with PyQt6/WebEngine collected; entry `atlantis.main:main`.
- **Pros:** Industry standard for PyQt; early bundle-size/WebEngine signal; Linux CI can smoke-run binary with `QT_QPA_PLATFORM=offscreen` + `--smoke-test`.
- **Cons:** Large artifacts; macOS codesign/notarization out of band; spec maintenance when deps change.
- **Fit:** **High** — matches “evaluate PyInstaller first for macOS `.app`” from 2026-05-05 guidelines.

#### Option C — Briefcase first
- **Pros:** Native `.app` / installer story long-term.
- **Cons:** WebEngine + PyQt6 pin + macOS 12 uncertainty; higher setup than PoC needs.
- **Fit:** **Low** for first BUILD slice — revisit after PyInstaller PoC passes.

#### Option D — cx_Freeze / Nuitka
- **Pros:** Alternatives if PyInstaller fails WebEngine collect.
- **Cons:** Less team familiarity; no advantage for first PoC.
- **Fit:** **Fallback** only — document in ADR, do not implement in parallel.

### Decision (Packaging)
**Option B — PyInstaller one-folder PoC**, scoped as:

1. **Phase 8a (BUILD):** Linux PoC + `--smoke-test` on built binary; document macOS/Windows manual steps.
2. **Phase 8b (defer):** macOS `.app` + codesign; Windows installer; CI matrix upload artifacts.
3. **Keep hatch wheel** as the canonical Python distribution; PyInstaller consumes the same entry point and assets.

### Packaging Implementation Guidelines
- New directory: `packaging/pyinstaller/` (spec, README, optional hook helpers).
- **No** `sys._MEIPASS` branches in `mermaid_assets.py` until PoC proves need — prefer `PreviewAssetSession` / resource paths that work in both editable and frozen layouts.
- Makefile target: `bundle-smoke` (opt-in, not in `make check`) — builds if `pyinstaller` installed, runs binary smoke.
- Dev dependency group: `packaging = ["pyinstaller>=6.0"]` (optional group, not default `uv sync`).
- ADR **0004-native-bundle-pyinstaller.md** records decision and macOS 12 constraints.

### Packaging Validation
- [ ] `uv build` wheel still passes; assets in wheel unchanged.
- [ ] Frozen binary: `atlantis --smoke-test` exit 0 (Linux).
- [ ] Offline render: default env (no CDN) loads vendored Mermaid from bundle.
- [ ] Bundle size documented in archive (expect hundreds of MB with WebEngine).

---

## 🎨🎨🎨 CREATIVE PHASE: Plugin Host v1 (scaffold only)

### Requirements (from project brief)
- Plugins **must not** alter Mermaid syntax or output format.
- Local-only, filesystem-based, sandboxed, globally configured.
- MVP has **no** plugin runtime — Phase 7 adds **contracts + registry stub**, not marketplace/dynamic load.

### Options Analysis

#### Option 1 — Docs-only guardrails (status quo)
- **Pros:** Zero code risk.
- **Cons:** Phase 7 “plugins” track has nothing to BUILD; boundaries stay informal.

#### Option 2 — Registry + manifest schema, no loader (recommended)
- **Description:** `atlantis/plugins/` package with `PluginManifest` (dataclass/TypedDict), `PluginRegistry` (register builtins + scan paths later), `atlantis.plugins` entry point **reserved** but only built-in no-ops in v1.
- **Pros:** Establishes API surface for export/snippets/lint contributions; testable without dynamic import risk.
- **Cons:** Slight code volume; must resist loading arbitrary code in same PR.

#### Option 3 — Full dynamic loader (importlib + entry points)
- **Pros:** Real plugins immediately.
- **Cons:** Security, crash isolation, settings UI, and test matrix explode; violates incremental Phase 7 scope.

### Decision (Plugins)
**Option 2 — Registry + manifest schema, no dynamic loader** in first Phase 7 BUILD slice.

### Plugin v1 shape

```text
atlantis/plugins/
  __init__.py      # public exports
  manifest.py      # PluginManifest, ContributionKind enum
  registry.py      # PluginRegistry (register, list, get_contributions)
  builtin.py       # empty or single "core" pseudo-plugin for tests
```

**Manifest fields (minimum):**
- `id`, `name`, `version`, `description`
- `contributions: list[Contribution]` where `Contribution.kind` ∈ `menu_action`, `export`, `editor_panel` (future)
- `api_version: str` (e.g. `"1"`)

**Guardrails (enforced in registry docs + unit tests):**
- No contribution may register Mermaid dialect hooks.
- Export contributions receive SVG/PNG bytes from renderer facade only — not raw JS injection.
- Future loader must check manifest `api_version` before activation.

**Integration boundaries (unchanged from 2026-05-05):**
| Boundary | Extension use |
|----------|----------------|
| `renderer` facade | Export, render hooks |
| `utils.frontmatter` | Schema helpers (read-only warnings) |
| `ui` menu registry | Menu actions (Phase 7: wire registry to `MainWindow` menu bar **stub** — one disabled “Plugins…” placeholder or skip UI until export plugin) |

**UI for Phase 7:** Prefer **no new user-visible plugin menu** until first real contribution (export). Registry is internal + tested; docs describe future layout.

### Plugin Validation
- [ ] Unit tests: register manifest, list contributions, reject invalid `api_version`.
- [ ] No `importlib` dynamic load of user paths in Phase 7a.
- [ ] MkDocs page: “Plugins (planned)” under user guide or ADR.

---

## 🎨🎨🎨 EXITING CREATIVE PHASE

## Consolidated Decisions (Phase 7/8)

| Track | Decision | BUILD slice |
|-------|----------|-------------|
| **Phase 7 — Plugins** | Registry + manifest; no dynamic loader | P7-A manifest, P7-B registry, P7-C tests + docs |
| **Phase 8 — Packaging** | PyInstaller one-folder PoC (Linux smoke) | P8-A spec + ADR, P8-B `make bundle-smoke`, P8-C docs |
| **Phase 8 — Rollout** | See `creative-phase78-rollout.md` | Versioning, release checklist, CI artifact defer |

## What stays deferred
- Briefcase / Windows installer / macOS notarization
- Dynamic plugin loading + settings UI
- Export PNG/SVG (first **plugin contribution** candidate, not core)
- Plugin marketplace or network install

## References
- ADR 0002 (PyQt6 pin), ADR 0003 (offline bundle)
- `atlantis/renderer/mermaid_assets.py`, `PreviewAssetSession`
- Original 2026-05-05 decision rationale preserved above (Option 1 was correct for MVP)

## Next Steps
- Run **`/plan`** — decompose P7-A…P8-C sub-tracks with acceptance criteria and gates.
- ADR 0004 (packaging) and plugin doc page listed in PLAN.

## Quality Score (refreshed)
- Requirement coverage: 48/50
- Testability: registry + bundle smoke well-defined
- Scope discipline: explicit deferrals for loader and notarization
