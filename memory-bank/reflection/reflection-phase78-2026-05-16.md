# Task Reflection: Phase 7/8 — Plugins, packaging, rollout (2026-05-16)

## Summary

Level 4 workstream advancing Atlantis from Python-package MVP toward **distributable desktop** and **extension-ready** architecture. Shipped **Phase 7** plugin scaffold (`PluginRegistry`, `PluginManifest`, contribution kinds; no dynamic loader) and **Phase 8** PyInstaller one-folder Linux PoC (`make bundle` / `make bundle-smoke`, ADR 0004). Added rollout docs (`CHANGELOG.md`, installation guide, release checklist). Tests: **92 → 103 passed, 1 skipped** (+11). Coverage held at **80%**. `make check-all` and **`make bundle-smoke`** both green on Linux. P8-E frozen-asset fix skipped (smoke passed without `sys._MEIPASS` branches); P8-H release CI deferred.

## What Went Well

- **Creative → PLAN → BUILD alignment** — refreshed `creative-packaging-plugin-boundaries.md` and `creative-phase78-rollout.md mapped 1:1 to P7-A…P8-G sub-tracks.
- **Phase 7 before Phase 8** — pure-Python registry/tests landed first; packaging work did not block PR gate.
- **`PreviewAssetSession` + hatch assets** — PyInstaller bundle smoke passed **without** P8-E code changes; offline bundle investment (ADR 0003) paid off.
- **`collect_all('PyQt6')` in spec** — WebEngine collected; `--smoke-test` on frozen binary exit 0 (~25s build on Linux).
- **Opt-in bundle targets** — `bundle-smoke` excluded from `make check`; PR CI unchanged.
- **`packaging` uv dependency group** — PyInstaller not installed on default `uv sync`; keeps contributor env lean.
- **Guardrail test** — `test_contribution_kinds_exclude_mermaid_dialect` locks enum to planned contribution kinds.
- **Hygiene tests** — spec + Makefile targets locked without subprocess bundle in every PR.

## Challenges Encountered

- **PyInstaller noise** — many warnings for unused Qt modules (3D, QML, SQL drivers); build still succeeded; spec pulls full PyQt6 via `collect_all`.
- **Bundle size/time** — one-folder dist is large; ~25s local build; not suitable for per-PR CI without workflow_dispatch (P8-H deferred).
- **Ruff TRY003** — validation raises in `manifest.py` required `msg = …` before `raise PluginManifestError(msg)` (same pattern as `qt_accessors.py`).
- **MkDocs nav growth** — installation page at top level + plugins under User Guide; strict build caught no broken links.
- **Scope discipline** — resisted wiring registry to `MainWindow` menus and implementing export plugin in same milestone.

## Solutions Applied

- **Frozen dataclasses** for `PluginManifest` / `Contribution` — immutable manifests, explicit `validate()` before register.
- **`api_version` gate** — `SUPPORTED_API_VERSIONS = frozenset({"1"})` for forward-compatible loader later.
- **Spec uses repo-root paths** — `SPECPATH` + `repo_root` for `atlantis/main.py` entry and `atlantis/assets` datas.
- **Makefile `clean`** — extended to remove `dist/` and `build/pyinstaller/`.
- **Release narrative** — `CHANGELOG.md` + contributing checklist without automating GitHub Releases yet.

## Lessons Learned

- **Defer bundling until core + assets stable** — 2026-05-05 creative decision was correct; executing PoC only after offline bundle + front matter kept risk low.
- **`importlib.resources` + `as_file` beats early `sys._MEIPASS` hacks** — test frozen layout before adding MEIPASS branches.
- **Plugin registry without loader is still valuable** — tests + docs establish contract for export/menu contributions without security surface of dynamic import.
- **Optional uv groups for heavy tools** — packaging deps belong in `[dependency-groups.packaging]`, not default dev or runtime.
- **Conditional sub-tracks (P8-E) save churn** — plan explicit skip when smoke passes; avoids speculative frozen-path code.

## Process Improvements

- Run **`make bundle-smoke` once** before claiming installation docs are accurate — already done; keep as release checklist step 4.
- Add **P8-H** only after two green local/CI bundle runs — avoid artifact storage costs on flaky spec.
- For Level 4 milestones, keep **plugin + packaging + docs** as separate BUILD log rows — simplifies partial archive if one track slips.

## Technical Improvements

- **Optional:** trim PyInstaller spec excludes to reduce bundle size (drop QML/3D plugins from collect).
- **Optional:** `ATLANTIS_BUNDLE_TESTS=1` subprocess test mirroring webengine marker.
- **Next plugin work:** dynamic loader + export contribution behind renderer facade.
- **Next packaging:** macOS `.app` manual doc validation; Briefcase comparison doc only if PyInstaller blocks macOS 12.
- **Backlog:** P8-H workflow_dispatch; FS-F cache; FM polish; codecov 90% long-term.

## Plan vs. Actual

| Plan item | Actual |
|-----------|--------|
| Plugin registry + manifest (P7) | **Shipped** — 4 modules, 8 tests |
| No dynamic loader / no plugin menu | **Shipped** |
| PyInstaller spec + README (P8-B) | **Shipped** |
| `make bundle-smoke` (P8-C) | **Shipped** — Linux green |
| ADR 0004 (P8-D) | **Shipped** |
| P8-E frozen asset fix | **Skipped** — smoke passed |
| Hygiene tests ≥3 (P8-F) | **3** tests |
| Rollout docs + CHANGELOG (P8-G) | **Shipped** |
| P8-H GitHub workflow | **Deferred** |
| ≥95 tests | **103 passed** |
| 80% coverage | **80%** held |

## Metrics

- New production modules: **4** (`atlantis/plugins/`)
- New packaging: `packaging/pyinstaller/atlantis.spec`, README
- Tests added: **11** (8 plugin + 3 packaging hygiene)
- Mypy source files: **31 → 35**
- Bundle build time (Linux): ~25s
- New docs: ADR 0004, installation.md, plugins.md, CHANGELOG.md

## Next Steps

- Run **`/archive`** to capture milestone and reset active task.
- Future: export plugin (first real contribution), P8-H CI bundle job, macOS bundle validation, FS-F / FM optional polish.
