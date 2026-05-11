# Task Reflection: Atlantis Technology Validation Gate + BUILD Phase 4

## Summary
This task closed two adjacent Level 4 milestones in one stretch: the **Technology Validation Gate (Phase 6 of the original plan)** and **BUILD Phase 4 (validation, feedback, polish, plus the Phase 3 deferrals)**. The gate confirmed Mermaid.js 10.9.3 can be rendered inside `QWebEngineView` via `QWebChannel` on macOS 12 within the < 4 s target (~3.3 s observed). Phase 4 then wired that path into the production app behind a small `WebEngineMermaidBridge`, added render-time + error-cycling status, theme awareness, CLI / env log level, real YAML/TOML front matter parsing, a unified-diff recovery dialog, a recent-files submenu (with stale pruning), and an autosave preferences dialog. The test suite expanded from 9 → **21 passing**; `ruff` clean; `uv build` clean.

## What Went Well
- **Tech gate paid off immediately**: validating the JS shell + `QWebChannel` interaction in a standalone script meant the production bridge in `atlantis/renderer/webengine_bridge.py` was almost a transcription of code patterns that were already proven against macOS 12.7.6 / pinned PyQt6.
- **Facade discipline held**: keeping `MermaidRenderer` as the sync validation facade and pushing actual rendering into `PreviewPane.render_source()` let the entire Phase 2/3 headless test path keep working unmodified — Phase 4 added a sibling code path instead of replacing one.
- **Deterministic test surface scaled cleanly**: the existing `ATLANTIS_HEADLESS=1` + `ATLANTIS_AUTOSAVE_DIR` env hooks were enough to make the front-matter, recent-files-prune, autosave-preferences-dialog, and error-cycling tests all deterministic on the offscreen platform.
- **Centralized settings keys paid dividends again**: the prefs dialog and the autosave timer share the same `AUTOSAVE_*` keys defined back in Phase 3, so wiring the dialog was structural, not a refactor.
- **Test gate jumped meaningfully without bloating**: +12 tests (6 front matter, 6 window polish) for the breadth of features touched.
- **Single-pass ruff/pytest gate** after each subsystem completed; only two stylistic ruff hits (one `SIM108`, one `UP042`) which were trivial to resolve.

## Challenges
- **`javaScriptConsoleMessage` is not a connectable signal in PyQt6**
  - Impact: First PoC iteration crashed at startup with `AttributeError: 'builtin_function_or_method' object has no attribute 'connect'`.
  - Resolution: Subclass `QWebEnginePage` (`TechValidationPage` in the script, then transparently inherited intent for the bridge) and **override** the method instead of connecting to it.
  - Outcome: Behavior documented in `techContext.md` so future renderer work doesn't repeat it.
- **Async render vs synchronous validation API**
  - Impact: The existing tests expect `_render_current_source()` to be synchronous and to inspect `preview.last_svg` immediately. A naive switch to the async bridge would have broken the test gate.
  - Resolution: Two-stage flow — sync `MermaidRenderer.render(diagram_source)` still drives line-error UX; the bridge is dispatched only when WebEngine is active. Headless tests never touch the async path; the bridge updates `last_svg` on success via its own callback.
  - Outcome: Phase 2/3 tests remained green with no edits; only one synthetic test (`test_render_with_invalid_toml_front_matter_warns_but_renders`) exercises the combined flow.
- **WebEngine pre-`loadFinished` first render**
  - Impact: A render request can land before the HTML shell's `loadFinished` signal fires.
  - Resolution: `_pending_source` buffer; `_dispatch_render` is only called once `_page_ready` is true, and `_on_load_finished` flushes the pending source.
  - Outcome: No "ghost first render" bugs; the latest request always wins.
- **`QApplication.instance()` typing for theme detection**
  - Impact: `QCoreApplication` lacks `palette()`, so the type checker flags it; the runtime narrows via the surrounding `MainWindow` lifecycle.
  - Resolution: Kept the runtime check; logged as pre-existing UI-module typing noise rather than introducing a `cast`.
  - Outcome: Same ruff/mypy posture as before, with explicit notes in `tasks.md` and the reflection.
- **YAML without a YAML dependency**
  - Impact: The original plan wanted "menu-driven edit (title, config)" which implies dict-level access; adding PyYAML would have been the simplest path but conflicts with "no new deps for MVP".
  - Resolution: Parse YAML structurally as **preserved-only text**, decode TOML via stdlib `tomllib`, return a friendly warning for YAML metadata access.
  - Outcome: Front matter is correctly round-tripped on save without inventing a new runtime dep; menu-driven edit deferred to a future enhancement.

## Lessons Learned
- For any Qt/JS bridge, validate the smallest plausible PoC with the **exact** target OS pin before integrating into the app — it shaved hours of debugging in production code.
- "Async overlaid on sync" is workable in Qt apps if you treat them as two channels with overlapping side effects (status + `last_svg`), not as a swap-in replacement.
- A pending-source buffer plus a `_page_ready` flag is a reusable pattern for any `runJavaScript`-based bridge.
- When adding a non-blocking warning surface (front matter), unify it with whatever already drives the status bar/error model (here: `_set_render_errors`) — fewer code paths to test.
- Centralizing settings keys before the first consumer made adding the prefs dialog mechanical rather than a refactor.

## Process Improvements
- Continue per-phase test modules (`tests/test_phase4_*.py`). Naming by phase makes regressions easy to localize during reflection and archive.
- Keep recording exact commands + outcomes in `tasks.md` while the phase is open; reflection writes itself.
- Treat ruff/pytest as the gate, but **note** persistent type-checker noise explicitly in the archive so it doesn't slowly accumulate or get treated as "new" later.
- Use opt-in env flags (`ATLANTIS_WEBENGINE_TESTS=…`) for live WebEngine tests rather than carving CI variants prematurely — keep CI uniform until we actually have a usable WebEngine job image.
- When a task naturally chains a gate and the next phase, document them in a single PLAN refinement (as done 2026-05-11) and keep both phases visible in the Status checklist.

## Technical Improvements
- Add a real PyQt-typed `cast` (or pyright/mypy `# type: ignore[union-attr]`) at the few Qt accessor sites (`statusBar()`, `document()`, `palette()`) to start retiring the chronic noise without changing runtime behavior.
- Introduce a small `FileSession` model (carry-over from Phase 3 reflection) that bundles `_current_path`, dirty state, watcher membership, and the front-matter cache; `MainWindow` would shrink and become easier to test.
- Replace ad-hoc render-time logging with structured logs (logger name `atlantis.renderer.bridge`) once the logging dock arrives.
- Move the WebEngine shell HTML into a templated resource (`assets/preview_shell.html`) once the offline bundle lands, to align with `creative-renderer-offline-bundle.md` Stage 2.
- Add a minimal opt-in WebEngine pytest behind `ATLANTIS_WEBENGINE_TESTS=1` to exercise `BridgeRenderResult` end-to-end; today the bridge is only proven by the PoC script.
- Provide a "menu-driven edit" path for front matter (open in a small dict editor for TOML; preserve YAML text untouched until a YAML dep is approved).

## Plan vs Actual (Phase 4)
- **Track A (renderer integration)**: Implemented exactly as planned: `WebEngineMermaidBridge` behind `PreviewPane`; production `MainWindow._render_current_source` keeps the existing facade.
- **Track B (status bar)**: Implemented — render-time + error cycling action `Ctrl+E`. Cancel-on-long-render not implemented as a separate UI action; timeout still enforced (15 s) at the bridge level.
- **Track C (logging)**: Implemented — `--log-level` + `ATLANTIS_LOG_LEVEL`; full log panel (QDockWidget) deferred (was already flagged as "start minimal").
- **Track D (theme)**: Implemented via QPalette lightness; CSS `prefers-color-scheme` not used (single explicit theme value sent to Mermaid is sufficient).
- **Track E (Phase 3 deferrals)**: All five implemented (front matter, recovery diff, recent menu, autosave prefs, stale prune).
- **Track F (docs/tests/workspace)**: Implemented — 12 new tests, docs sections, VS Code debug-log task. No opt-in WebEngine pytest yet (listed as a Technical Improvement).

## Metrics Snapshot
- Tests passing: **21** (9 prior + 12 new Phase 4)
- New modules: 2 (`atlantis/renderer/webengine_bridge.py`, `atlantis/ui/preferences.py`)
- New utility: 1 (`build_recovery_diff` in `atlantis/ui/main_window.py`)
- New env hooks introduced: **0** (reused `ATLANTIS_HEADLESS`, `ATLANTIS_AUTOSAVE_DIR`); new optional `ATLANTIS_LOG_LEVEL`
- New settings keys: 0 (existing autosave/recent-files keys sufficient)
- Tech gate timing: **~3285 ms** first Mermaid → Python callback on validation host (under 4 s target)
- `uv build`: PASS (sdist + wheel)

## Next Steps
- Run `/archive` to capture the Phase 4 milestone (link reflection, tests, bridge module, PoC, doc changes).
- Open follow-up issues for: opt-in WebEngine pytest, `FileSession` refactor, structured renderer logging, Qt accessor type cleanup, offline Mermaid bundle (Stage 2 per creative renderer doc), menu-driven front matter edit.
- Begin Phase 5 (cross-cutting docs/CI/coverage track) when product priorities allow.
