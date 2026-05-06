# Memory Bank: Tasks

## Current Task
**BUILD Mode (Level 4) - Phase 3**: Implement persistence and recovery features including rolling autosave, startup recovery prompt/restore, external file change handling, and recent-file persistence.

## Status
- [x] VAN
- [x] PLAN
- [x] CREATIVE (if required)
- [x] BUILD (Phase 1)
- [x] BUILD (Phase 2)
- [x] BUILD (Phase 3)
- [ ] REFLECT
- [ ] ARCHIVE

## Last Completed Archive
- `memory-bank/archive/archive-build-phase1-2-2026-05-06.md`

## Next Recommended Task
- Execute technology validation PoC, then continue with BUILD Phase 4.

## Requirements (from VAN + Project Brief)
- Bootstrap full Python package structure (atlantis/ with __init__, main entry, core modules)
- Implement MVP: Single-window PyQt6 app with resizable code editor (Mermaid syntax) + live WebEngine preview
- File model: .mmd only, single-diagram, autosave + recovery
- Front-matter support (YAML/TOML), validation warnings
- Rendering: Mermaid.js via Qt WebEngine, debounce, error handling (last-good preview)
- Validation/feedback: Status bar errors, inline highlights
- Cross-platform foundation (macOS MVP)
- **Explicit inclusions**:
  - **Documentation**: Expand MkDocs (user guide, dev guide, API via mkdocstrings), sync Memory Bank outputs, Mermaid examples
  - **Testing**: pytest + pytest-qt, unit tests (model, renderer), integration (UI flows), fixtures for sample diagrams, coverage >80% target
  - **Formatting & Quality**: Enforce ruff (format + lint), mypy strict in CI/pre-commit; consistent editor settings
  - **CI/CD**: GitHub Actions workflows (lint/type/test/docs/build matrix for macOS/Linux/Windows where feasible); coverage upload, docs deploy
  - **Workspace**: Enhance .vscode/ (code-workspace, settings.json, tasks.json, launch.json for PyQt debugging, recommended extensions)
- Technology stack validation (PyQt6 + WebEngine + Mermaid)
- Phased approach per Level 4 workflow (7 phases: Init/Doc/Arch/Creative/Impl/Reflect/Archive)
- Architectural diagrams and decision records (ADRs)

## Implementation Plan (Level 4 Phased)

### Phase 1: Bootstrap & Project Structure (Foundation) - COMPLETE
- Create `atlantis/` package:
  - `atlantis/__init__.py` (version, __version__ sync with pyproject)
  - `atlantis/main.py` (QApplication entry, main window launch)
  - `atlantis/core/` : `app.py`, `settings.py` (QSettings), `logging.py` (user-accessible logs)
  - `atlantis/ui/` : `main_window.py` (QMainWindow + QSplitter), `editor.py` (code widget), `preview.py` (WebEngine view), `status_bar.py`
  - `atlantis/model/` : `diagram.py` (Mermaid source + frontmatter dataclass), `file_handler.py` (.mmd I/O, autosave)
  - `atlantis/renderer/` : `mermaid_renderer.py` (WebEngine bridge, JS injection, error parsing)
  - `atlantis/utils/` : `frontmatter.py` (YAML/TOML parsers + schema), `debounce.py`
- Update `pyproject.toml`: Add runtime deps (`PyQt6>=6.7,<6.10`, `PyQt6-WebEngine>=6.7,<6.10` for macOS 12 compatibility), scripts entry point (`atlantis = "atlantis.main:main"`), package discovery.
- Add `.gitignore` updates, MANIFEST.in if needed.
- **Workspace**: Update `.vscode/atlantis.code-workspace` with Python interpreter, multi-root if helpful; create `.vscode/settings.json` (ruff, mypy, editor.formatOnSave, python.analysis), `tasks.json` (run: ruff check/fix, mypy, pytest, mkdocs serve), `launch.json` (debug PyQt app with PYTHONPATH).
- Recommended extensions: ms-python.python, ms-python.vscode-pylance, charliermarsh.ruff, njpwerner.autodocstring, etc.
- **Milestone**: `python -m atlantis` launches empty window (no crash).

#### Phase 1 Implementation Results
- Implemented package tree:
  - `atlantis/__init__.py`, `__main__.py`, `main.py`
  - `atlantis/core/{app.py,settings.py,logging.py}`
  - `atlantis/ui/{main_window.py,editor.py,preview.py,status_bar.py}`
  - `atlantis/model/{diagram.py,file_handler.py}`
  - `atlantis/renderer/mermaid_renderer.py`
  - `atlantis/utils/{frontmatter.py,debounce.py}`
- Added workspace support:
  - `.vscode/settings.json`
  - `.vscode/tasks.json`
  - `.vscode/launch.json`
  - `.vscode/extensions.json`
- Added phase test file:
  - `tests/test_phase1_smoke.py`
- Added `--smoke-test` flow to `python -m atlantis` for non-interactive validation.
- Added headless preview fallback (`ATLANTIS_HEADLESS=1`) to avoid WebEngine crash in CI/headless smoke runs.

#### Phase 1 Commands Executed
1. Directory scaffolding (`mkdir -p ...`) and verification (`ls -la`).
2. Dependency install:
   - `python -m ensurepip --upgrade`
   - `python -m pip install -e .`
   - `python -m pip install pytest ruff`
   - `python -m pip install --upgrade "PyQt6>=6.7.0,<6.10.0" "PyQt6-WebEngine>=6.7.0,<6.10.0"`
3. Quality and test gate:
   - `python -m ruff format atlantis tests`
   - `python -m ruff check atlantis tests`
   - `QT_QPA_PLATFORM=offscreen python -m pytest -q`
   - `QT_QPA_PLATFORM=offscreen python -m atlantis --smoke-test`

#### Phase 1 Test Results
- `ruff check`: PASS
- `pytest`: PASS (2 passed)
- `python -m atlantis --smoke-test`: PASS (exit code 0)

#### Phase 1 Exit Criteria
- [x] Basic architectural framework is functional
- [x] Directory/file structure created and verified
- [x] Workspace scaffolding added
- [x] Test gate passed before phase completion
- [x] Milestone command validated in headless mode

### Phase 2: Core Editor + Preview MVP (Primary Feature) - COMPLETE
- Implement resizable QSplitter: left QPlainTextEdit (or advanced editor) with line numbers, Mermaid syntax highlighter (custom QSyntaxHighlighter or Pygments bridge).
- Right: QWebEngineView loading local HTML template embedding Mermaid.js (CDN for MVP, plan local bundle post-MVP).
- Bidirectional? No: code changes → debounced render (500ms default, configurable in settings).
- On render error: retain last successful SVG/preview, display first error in status bar (cycle errors), optional inline red underline via extraSelections.
- Menu bar: File (New, Open, Save, Save As, Recent), Edit (Undo/Redo session-scoped), View (toggle panes, theme follow system), Help.
- **Documentation**: Add initial MkDocs pages: `docs/user-guide.md` (quick start, editor shortcuts), `docs/developer/architecture.md` (high-level from systemPatterns).
- **Testing**: pytest fixtures for sample .mmd content; unit tests for Diagram model and frontmatter parser; basic UI smoke test with pytest-qt (create window, type text, verify no crash).
- **Formatting**: Run ruff format on all new files; add pre-commit hook config if not present (already in dev deps).
- **Milestone**: User can type Mermaid flowchart, see live preview update, save/load .mmd file.

#### Phase 2 Implementation Results
- Implemented `MermaidEditor` upgrades:
  - line-number gutter rendering
  - lightweight Mermaid syntax highlighter
  - current-line + error-line highlights via extra selections
- Implemented `PreviewPane` abstraction:
  - WebEngine backend when available
  - headless/text fallback backend for test environments
  - retained `last_svg` state for last-known-good preview behavior
- Implemented rendering loop in `MainWindow`:
  - debounced render scheduling (`Debouncer`, 500ms)
  - status updates for scheduled/success/error states
  - render failure keeps last-good preview unchanged
- Implemented file/menu workflow:
  - File: New, Open, Save, Save As, Quit
  - View: Toggle Soft Wrap
  - helper methods: `load_from_path`, `save_to_path` for deterministic test coverage
- Improved renderer placeholder behavior:
  - validates basic Mermaid declarations
  - returns explicit errors for unsupported/non-Mermaid input

#### Phase 2 Commands Executed
1. `python -m ruff format atlantis tests`
2. `python -m ruff check atlantis tests`
3. `QT_QPA_PLATFORM=offscreen python -m pytest -q`

#### Phase 2 Test Results
- `ruff check`: PASS
- `pytest`: PASS (5 passed)
- Assertions validated:
  - editor/preview splitter exists
  - render success path updates preview state
  - render error retains last-good preview and shows status error
  - save/load `.mmd` roundtrip works

#### Phase 2 Exit Criteria
- [x] Resizable split editor/preview shell implemented
- [x] Debounced source-to-preview render loop implemented
- [x] Error handling keeps last-known-good preview
- [x] Basic file actions (new/open/save/save-as) implemented
- [x] Milestone behavior validated by tests

### Phase 3: File Model, Persistence & Recovery
- Implement autosave: rolling file in temp dir (QStandardPaths), interval 60s configurable, disable toggle.
- Crash recovery: on startup detect stale autosave, prompt "Restore unsaved work?" with diff preview.
- External file change detection (QFileSystemWatcher) → reload or warn.
- Front matter: Parse YAML/TOML block at top, preserve exactly, menu-driven edit (title, config), warning on invalid (non-blocking).
- Recent files list (QSettings persisted, max 10).
- **Documentation**: Expand `docs/index.md`, add troubleshooting, keyboard reference.
- **Testing**: Integration tests for file roundtrip + autosave simulation; recovery scenario tests.
- **CI/CD contribution**: Add pytest job early.
- **Milestone**: Full create → edit → autosave → crash-sim → recover → save cycle works reliably.

#### Phase 3 Implementation Results
- Implemented rolling autosave model:
  - deterministic autosave file path per document via `autosave_path_for()`
  - untitled document autosave support
  - configurable autosave dir via `ATLANTIS_AUTOSAVE_DIR` (test support)
- Implemented startup recovery behavior:
  - checks autosave for current document context
  - headless mode auto-restore for deterministic tests
  - non-headless prompt-based restore flow
- Implemented external file change handling:
  - `QFileSystemWatcher` integration in `MainWindow`
  - auto-reload when document is clean
  - warning status when local unsaved changes exist
- Implemented recent files persistence:
  - stores/reorders latest 10 file paths in `QSettings`
- Added Phase 3 tests:
  - `tests/test_phase3_persistence.py`

#### Phase 3 Commands Executed
1. `python -m ruff format atlantis tests`
2. `python -m ruff check atlantis tests`
3. `QT_QPA_PLATFORM=offscreen python -m pytest -q`

#### Phase 3 Test Results
- `ruff check`: PASS
- `pytest`: PASS (9 passed total suite)
- Assertions validated:
  - autosave writes rolling file
  - startup recovery restores unsaved content in headless mode
  - external file change reloads when editor is clean
  - recent files list is persisted and ordered

#### Phase 3 Exit Criteria
- [x] Autosave rolling file model implemented
- [x] Startup recovery flow implemented
- [x] External file change detection implemented
- [x] Recent files persisted in settings
- [x] Phase tests pass before completion

### Phase 4: Validation, Feedback & Polish
- Status bar: error count, cycle button, render time indicator.
- Linting: basic Mermaid syntax check via renderer feedback; actionable messages (line numbers).
- Logging: configurable level, log panel toggle (QDockWidget or bottom), export logs.
- Theme: follow system (QPalette or Qt style hints); no forced dark/light.
- Performance: hard timeout 15s on render, cancelable; optional "large diagram" safeguard.
- **Documentation**: User-facing error guide; dev: renderer extension points.
- **Testing**: Error path tests (bad Mermaid syntax, timeout, parse fail); coverage of renderer.
- **Workspace**: Add debug task for "run with --log-level debug".
- **Milestone**: Robust handling of all error cases from projectbrief; user never loses work.

### Phase 5: Documentation, Testing, Formatting, CI/CD & Workspace (Cross-Cutting - Explicit Track)
- **Documentation**:
  - Full MkDocs site: API reference (mkdocstrings for all public modules), tutorials (build first diagram, customize frontmatter), architecture decision records (ADRs in docs/adr/).
  - Sync: Auto-generate sections from memory-bank/ (e.g., via script or manual include).
  - Mermaid examples gallery in docs.
  - README.md expansion with screenshots (once UI exists), install from source, PyPI (future).
  - Post-MVP: Changelog, contributing guide.
- **Testing**:
  - Setup: pytest.ini enhancements, pytest-qt, pytest-mock; fixtures (sample_diagrams.py with valid/invalid Mermaid).
  - Coverage: codecov integration (already yaml present), target 80%+ lines/branches.
  - Strategy: 60% unit (model, utils, renderer logic), 30% integration (UI flows via qtbot), 10% E2E/manual.
  - Run in CI on every PR.
- **Formatting & Quality**:
  - Enforce: ruff check --fix + format in pre-commit and CI (fail on issues).
  - mypy strict on atlantis/ (already configured).
  - Add .editorconfig for consistent indent (4 spaces), trim trailing whitespace.
  - Style-guide.md updates for PyQt6/Qt patterns (signal/slot naming, layout best practices).
- **CI/CD**:
  - New `.github/workflows/ci.yml`: 
    - Job matrix: python-version [3.12, 3.13], os [macos-latest, ubuntu-latest] (windows later for packaging).
    - Steps: checkout, uv/pip install -e ".[dev]", ruff check/format --check, mypy, pytest --cov, codecov upload.
    - Docs job: mkdocs build --strict, deploy to GitHub Pages on main (using peaceiris/actions-gh-pages or mkdocs gh-deploy).
  - Dependabot already present; add for actions.
  - Future: release workflow (build wheel/sdist, PyPI publish on tag), packaging matrix.
  - Status badges in README.
- **Workspace**:
  - `.vscode/`: 
    - `settings.json`: python.defaultInterpreterPath, ruff.organizeImports, editor.formatOnSave=true, python.testing.pytestEnabled, terminal.integrated.env, files.exclude for .venv.
    - `tasks.json`: "Ruff Fix", "Type Check", "Run Tests", "Serve Docs", "Launch Atlantis (debug)".
    - `launch.json`: "Python: Atlantis" with "program": "${workspaceFolder}/atlantis/main.py", "env": {"PYTHONPATH": "${workspaceFolder}"}, "console": "integratedTerminal", PyQt specific args if needed.
    - `extensions.json`: recommendations list.
  - Update `atlantis.code-workspace` with folders, settings overrides.
  - Add Makefile targets or just rely on pyproject scripts + tasks.
- **Milestone**: `make test` or equivalent passes with coverage; `mkdocs serve` works; PRs auto-checked via CI; new dev can clone + open in Cursor/VSCode and run immediately.

### Phase 6: Technology Validation Gate (Mandatory for Level 4)
- **Stack Selection Documented** (in techContext.md update if needed): PyQt6 + WebEngine chosen for native + web render; Mermaid.js for compatibility; Hatch for build.
- **Hello World PoC** (create in `scripts/` or temp, not committed):
  - Minimal PyQt6 app: QWebEngineView, set HTML with `<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js">`, then `mermaid.run()` or render a simple flowchart.
  - Verify: diagram renders, errors captured via JS bridge (QWebChannel or console messages).
- **Dependencies Verified**: PyQt6-WebEngine installs cleanly on macOS; no conflicts with dev tools.
- **Build Config**: `python -m build` or hatch build succeeds; wheel contains package.
- **Test Build**: Run PoC, confirm render latency <4s target on sample diagram.
- **Checkpoint**:
  ```
  ✓ TECHNOLOGY VALIDATION
  - Stack selected and justified? YES
  - Minimal Mermaid-in-WebEngine PoC successful? YES
  - Deps installable and compatible? YES
  - Build config valid? YES
  - Test render passes? YES
  ```
- **Outcome**: Clear to proceed; any issues (e.g., WebEngine sandbox on macOS) mitigated in plan (e.g., set env vars).

### Phase 7: Creative Phase Identification & Future-Proofing
Flag for CREATIVE mode (or inline decisions):
- **Editor Widget Choice**: QPlainTextEdit + custom highlighter (simple, lightweight) vs. QWebEngine + embedded Monaco/CodeMirror (richer Mermaid language support, but heavier). **Decision needed**: Recommend lightweight for MVP, extensible later.
- **Layout & UX Details**: Exact pane proportions, keyboard shortcuts, context menu on preview (copy SVG?), status bar iconography.
- **Error Visualization**: Inline vs. dedicated error panel vs. tooltip on hover.
- **Packaging Strategy**: For post-MVP portable app (briefcase? PyInstaller? macOS .app bundle first).
- **Mermaid Version Pinning & Offline Bundle**: How/when to vendor mermaid.js + fonts.
- **Plugin Architecture Sketch** (future): Filesystem hooks without altering core Mermaid.
- Create `memory-bank/creative/creative-ui-layout.md` and `creative-editor-component.md` if proceeding to CREATIVE.
- Risk mitigation: Scope guardrails from projectbrief (no full visual editing, no AI in MVP).

### Phase 8: Phased Implementation & Rollout (High-Level)
- **MVP Release** (Phases 1-4 core): End-to-end single-chart workflow.
- **Beta Polish** (Phase 5 enhancements + recovery UX).
- **Post-MVP** (Export PNG/SVG via WebEngine capture, visual source mapping, full offline bundle, cross-platform packaging, plugin system).
- Dependencies between phases documented; parallelizable where possible (e.g., docs/CI can start early).
- Integration points: All subsystems communicate via Qt signals or simple callbacks; renderer facade hides WebEngine details.

### Risk Assessment & Mitigation
- **Risk**: WebEngine + Mermaid compatibility/version drift → Pin Mermaid version, test matrix.
- **Risk**: PyQt6 packaging bloat / platform quirks (esp. macOS notarization) → Early PoC + research packaging options in Phase 5.
- **Risk**: Scope creep (visual editing, multi-file) → Strict adherence to projectbrief MVP boundaries; creative phase to document "why not".
- **Risk**: Low test coverage on UI → Mandate pytest-qt + manual test checklist.
- **Mitigation**: Continuous Memory Bank updates, frequent REFLECT checkpoints.

## Checklist (Updated for PLAN + Inclusions)
- [x] Read all context (tasks, activeContext, projectbrief, rules)
- [x] Codebase structure analysis (empty src, config-heavy)
- [x] Comprehensive requirements documented
- [x] Architectural diagrams planned (Mermaid flows for data, render pipeline)
- [x] Subsystems identified (ui, model, renderer, core)
- [x] Dependencies & integration mapped
- [x] Phased implementation strategy created (8 phases above)
- [x] Technology validation gate defined + PoC plan
- [x] Creative phases flagged (editor choice, UX details, packaging)
- [x] Documentation track detailed (MkDocs + user/dev guides)
- [x] Testing track detailed (pytest-qt strategy + coverage)
- [x] Formatting track detailed (ruff enforcement + pre-commit)
- [x] CI/CD track detailed (workflows for lint/test/docs)
- [x] Workspace track detailed (.vscode full setup)
- [x] Creative decisions documented in memory-bank/creative/
- [ ] Execute technology PoC (manual or in BUILD)
- [x] Update progress.md and activeContext.md post-creative
- [x] Final creative verification checkpoint

## Creative Phase Decisions
- `memory-bank/creative/creative-editor-component.md`
  - Decision: Use `QPlainTextEdit` with a custom line number gutter and `QSyntaxHighlighter` for the MVP.
  - Rationale: Best balance of native behavior, testability, low packaging risk, and MVP scope.
- `memory-bank/creative/creative-ui-layout-feedback.md`
  - Decision: Use a classic two-pane `QSplitter` layout with source left, preview right, and concise status-bar feedback.
  - Rationale: Directly matches the code-first product brief and keeps the first UI understandable.
- `memory-bank/creative/creative-renderer-offline-bundle.md`
  - Decision: Use a `QWebEngineView` HTML shell with manual Mermaid rendering and a staged CDN-to-local-bundle path.
  - Rationale: Supports controlled render timing, last-good preview behavior, and eventual offline operation.
- `memory-bank/creative/creative-packaging-plugin-boundaries.md`
  - Decision: Run MVP from a clean Python package and defer native app bundling/plugin runtime until the core app stabilizes.
  - Rationale: Protects MVP scope while preserving asset and extension boundaries for future packaging/plugins.

## Next Steps
1. Execute technology validation PoC (`QWebEngineView` + Mermaid JS bridge).
2. Proceed to `/build` Phase 3 (autosave, recovery, external file change handling).
3. Continuous: Update this tasks.md during BUILD with progress; use partial diffs.

## Verification Checkpoint (PLAN Complete)
```
✓ PLAN MODE CHECKPOINT
- All Level 4 planning elements covered? YES
- Technology validation defined? YES
- Creative flags documented? YES
- Docs/Tests/Formatting/CI/CD/Workspace explicitly planned? YES
- Memory Bank path verified (memory-bank/tasks.md)? YES
- Ready for mode transition? YES
```
→ If all YES: PLAN complete. Update Memory Bank and transition.

## Verification Checkpoint (CREATIVE Complete)
```
✓ CREATIVE MODE CHECKPOINT
- Plan complete and creative phases identified? YES
- Editor component decision documented? YES
- UI layout and feedback decision documented? YES
- Renderer/offline bundle decision documented? YES
- Packaging/plugin boundary decision documented? YES
- Options, tradeoffs, rationale, implementation guidelines included? YES
- Ready for technology validation and BUILD? YES
```
→ If all YES: CREATIVE complete. Proceed to technology validation, then BUILD Phase 1.

## Verification Checkpoint (REFLECT Phase 1-2 Complete)
```
✓ REFLECT CHECKPOINT (PHASES 1-2)
- Phase 1 implementation reviewed against plan? YES
- Phase 2 implementation reviewed against plan? YES
- Successes and challenges documented? YES
- Lessons, process, and technical improvements documented? YES
- Reflection file created in memory-bank/reflection/? YES
```
→ Reflection complete for phases 1-2. Continue BUILD lifecycle.

## Reflection Artifacts
- `memory-bank/reflection/reflection-build-phase1-2-2026-05-06.md`

**Memory Bank path verified**: All edits to `memory-bank/tasks.md`. No core files created outside `memory-bank/`.

## Archive Note
Upon completion of this task (full MVP), merge detailed checklists and this plan into `memory-bank/archive/archive-[task_id].md`, then clear for next task.