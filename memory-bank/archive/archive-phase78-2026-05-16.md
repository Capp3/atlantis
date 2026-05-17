# TASK ARCHIVE: Phase 7/8 — Plugins, packaging, rollout

## METADATA
- **Task ID**: phase78-2026-05-16
- **Complexity**: Level 4 (plugin contracts + native packaging PoC + rollout docs)
- **Task Type**: Extension scaffold + PyInstaller distribution + release narrative
- **Archive Date**: 2026-05-16
- **Status**: Complete
- **Related Reflection**: `memory-bank/reflection/reflection-phase78-2026-05-16.md`
- **Creative**: `memory-bank/creative/creative-packaging-plugin-boundaries.md` (refreshed), `creative-phase78-rollout.md`
- **Predecessor Archive**: `memory-bank/archive/archive-front-matter-edit-2026-05-16.md`
- **Source**: VAN 2026-05-16 — last major roadmap item (plugins/packaging/rollout)

## SUMMARY

Closed the **Phase 7/8** roadmap milestone: **plugin registry scaffold** (no dynamic loader), **PyInstaller one-folder Linux bundle** with `make bundle-smoke`, and **rollout documentation** (ADR 0004, installation guide, plugins guide, `CHANGELOG.md`, release checklist). Tests: **92 → 103 passed, 1 skipped** (+11). Coverage **80%**. `make check-all` and **`make bundle-smoke`** green on Linux. P8-E frozen-path fix skipped; P8-H GitHub bundle workflow deferred.

## REQUIREMENTS

### Phase 7 — Plugins
1. `PluginManifest`, `Contribution`, `ContributionKind` types with validation.
2. `PluginRegistry` — register, list, query contributions; reject duplicates and bad `api_version`.
3. No dynamic `importlib` loading; no plugin settings UI; no `MainWindow` menu wiring.
4. Unit tests ≥8; guardrail: no Mermaid dialect contribution kind.
5. User-facing docs describing planned extension model.

### Phase 8 — Packaging
1. Optional `packaging` uv dependency group with PyInstaller.
2. `packaging/pyinstaller/atlantis.spec` — one-folder bundle with `atlantis/assets` + PyQt6/WebEngine.
3. `make bundle` / `make bundle-smoke` — **not** in `make check`.
4. ADR 0004 documenting PyInstaller-first decision and constraints.
5. Conditional frozen asset fix only if smoke fails.

### Rollout
1. `CHANGELOG.md`, `docs/user-guide/installation.md`.
2. Release checklist in `docs/contributing.md`.
3. README install section; `techContext.md` update.

## IMPLEMENTATION

### Phase 7 — `atlantis/plugins/`

| Module | Role |
|--------|------|
| `manifest.py` | `PluginManifest`, `Contribution`, `ContributionKind`, `SUPPORTED_API_VERSIONS`, `PluginManifestError` |
| `registry.py` | `PluginRegistry.register/list_plugins/contributions/clear` |
| `builtin.py` | `core_plugin_manifest()` for tests |
| `__init__.py` | Public exports |

### Phase 8 — Packaging

| Item | Detail |
|------|--------|
| `pyproject.toml` | `[dependency-groups] packaging = ["pyinstaller>=6.13.0"]` |
| `packaging/pyinstaller/atlantis.spec` | Entry `atlantis/main.py`; `collect_all('PyQt6')`; datas `atlantis/assets` |
| `Makefile` | `bundle`, `bundle-smoke`; `clean` removes `dist/`, `build/pyinstaller/` |
| `packaging/pyinstaller/README.md` | Build steps; macOS/Windows manual notes |

### Rollout docs

| File | Content |
|------|---------|
| `docs/adr/0004-native-bundle-pyinstaller.md` | Accepted decision |
| `docs/user-guide/installation.md` | uv, wheel, experimental bundle |
| `docs/user-guide/plugins.md` | Planned extensions; guardrails |
| `CHANGELOG.md` | Keep a Changelog; Unreleased + 0.0.1 |
| `mkdocs.yml` | Installation nav; plugins; ADR 0004 |

### Files touched (summary)

| Action | Paths |
|--------|-------|
| Add | `atlantis/plugins/*`, `packaging/pyinstaller/*`, ADR 0004, installation.md, plugins.md, CHANGELOG.md, 2 test modules |
| Modify | `pyproject.toml`, `Makefile`, `README.md`, `contributing.md`, `architecture.md`, `techContext.md`, `mkdocs.yml` |
| Skipped | `mermaid_assets.py` frozen-path (P8-E) |

## TESTING

| Command | Result |
|---------|--------|
| `make check-all` | PASS |
| `uv run pytest -q` | **103 passed, 1 skipped** |
| `uv run mypy atlantis` | **0 errors** (35 source files) |
| `make bundle-smoke` | PASS (Linux; ~25s build) |

| Module | Tests |
|--------|-------|
| `test_plugin_registry.py` | 8 |
| `test_packaging_hygiene.py` | 3 |

## EXIT CRITERIA — FINAL STATE

- [x] Plugin registry + manifest; 8 tests; mypy clean
- [x] `make bundle-smoke` on Linux
- [x] ADR 0004 + installation + plugins docs
- [x] 103 tests; 80% cov; PR gate unchanged
- [x] No dynamic loader; no plugin menu
- [ ] P8-H CI bundle workflow — **deferred**

## LESSONS LEARNED

- Defer native bundling until offline assets + core MVP stable; `PreviewAssetSession`/`as_file` avoided P8-E.
- Plugin registry without loader establishes extension contract with minimal security risk.
- PyInstaller via optional uv group; `collect_all('PyQt6')` works but bundle is large/noisy.
- Conditional plan sub-tracks (P8-E) prevent speculative frozen-path code.
- `bundle-smoke` must stay out of `make check` to protect PR CI duration.

## DEFERRALS & FOLLOW-UPS

- **P8-H** — `workflow_dispatch` bundle CI + artifact upload.
- **Dynamic plugin loader** + export contribution (first real plugin).
- **macOS codesign / Windows installer** — manual docs only.
- **Briefcase** — revisit only if PyInstaller blocks macOS 12.
- **Trim PyInstaller collect** — reduce bundle size (exclude unused Qt plugins).
- **FS-F** front-matter cache; **FM** tooltips/nested form UX (Level 2 optional).
- **Removed deferral:** ~~Phase 7/8 plugins/packaging/rollout~~ — **done**.

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-phase78-2026-05-16.md`
- Creative: `memory-bank/creative/creative-packaging-plugin-boundaries.md`, `creative-phase78-rollout.md`
- Predecessor: `memory-bank/archive/archive-front-matter-edit-2026-05-16.md`
- ADR 0002, 0003, 0004
- Install: `docs/user-guide/installation.md`; bundle: `packaging/pyinstaller/README.md`
