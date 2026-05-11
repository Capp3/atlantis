# TASK ARCHIVE: Atlantis BUILD Phase 5 — Cross-cutting docs / tests / formatting / CI/CD / workspace

## METADATA
- **Task ID**: build-phase5-2026-05-11
- **Complexity**: Level 4 (original Phase 5 of the Atlantis Level 4 plan)
- **Task Type**: Cross-cutting engineering surface (test harness, CI/CD, pre-commit, docs site, workspace)
- **Archive Date**: 2026-05-11
- **Status**: Archived as milestone (project not fully complete)
- **Related Reflection**: `memory-bank/reflection/reflection-build-phase5-2026-05-11.md`
- **Predecessor Archives**:
  - `memory-bank/archive/archive-build-phase4-2026-05-11.md`
  - `memory-bank/archive/archive-build-phase3-2026-05-11.md`
  - `memory-bank/archive/archive-build-phase1-2-2026-05-06.md`

## SUMMARY
This milestone closed the engineering surface around the (already stable) Phase 1-4 app code without changing any user-facing behavior. Five sub-tracks shipped in the planned order (**P5-T → P5-C → P5-F → P5-D → P5-W**): a shared pytest harness with an opt-in `webengine` marker and coverage wiring; a `.github/workflows/ci.yml` running lint + tests + coverage upload + strict docs build (with a `workflow_dispatch`-only macOS smoke); a `.pre-commit-config.yaml` pinned to the same `ruff` tag CI enforces; a real `mkdocs` navigation backed by `mkdocs-material` and `mkdocstrings` (Home / Getting Started / User Guide / Reference / ADRs / Contributing) plus two ADRs; and three new VS Code tasks (Coverage, Pre-commit, Build Docs). Final gate: `ruff format --check` + `ruff check` clean, **21 passed + 1 skipped** (opt-in WebEngine), coverage **69 %**, `mkdocs build --strict` green.

## REQUIREMENTS

**P5-T — Testing harness**
- Shared `tests/conftest.py` with `QT_QPA_PLATFORM=offscreen` + `ATLANTIS_HEADLESS=1` at import time, session-scoped `qapp` fixture, `autosave_tmp` fixture, and a `pytest_collection_modifyitems` hook gating `@pytest.mark.webengine` behind `ATLANTIS_WEBENGINE_TESTS=1`.
- Register the `webengine` marker; enable `--strict-markers`; add coverage `exclude_also` rules.
- Refactor existing `tests/test_phase{1,2,3,4}_*.py` to stop re-declaring Qt env vars and the `_APP` instance.
- One opt-in WebEngine smoke test exercising the real `QWebEngineView` + `WebEngineMermaidBridge`.

**P5-C — CI/CD**
- `.github/workflows/ci.yml` with lint + tests + coverage upload (codecov), non-blocking type-check, and a strict docs build; opt-in `macos-13` smoke gated to `workflow_dispatch`.
- README badges (CI, codecov, docs) + Quickstart using `uv` commands.

**P5-F — Formatting & quality**
- `.pre-commit-config.yaml` with hygiene hooks + ruff/ruff-format pinned to the same tag CI uses.
- New `docs/contributing.md` documenting the loop; mypy hook **deferred** (with rationale).

**P5-D — Documentation site**
- `mkdocs.yml` with a real `nav:` and `mkdocstrings.python` for an auto-generated API reference.
- Split `docs/index.md` into focused pages (Getting Started, User Guide subpages, Reference, Contributing).
- Two ADRs (`0001-mermaid-cdn-mvp.md`, `0002-pyqt6-pin-macos-12.md`).

**P5-W — Workspace**
- `.vscode/tasks.json` gains Coverage, Pre-commit (all files), Build Docs (strict).
- Recommended extensions reviewed.

## IMPLEMENTATION

### P5-T — Testing harness
- New `tests/conftest.py`:
  - Module-level `os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")` and `os.environ.setdefault("ATLANTIS_HEADLESS", "1")` so headless mode is on for all Qt-touching tests by default.
  - Session-scoped `qapp` fixture (`create_application()`); autouse glue (`_qapp_autouse`) so each test sees a live `QApplication` without requesting it explicitly.
  - `autosave_tmp(tmp_path, monkeypatch)` fixture that sets `ATLANTIS_AUTOSAVE_DIR` to an isolated dir for the test.
  - `pytest_collection_modifyitems` hook that adds a `pytest.mark.skip` to every item carrying `pytest.mark.webengine` unless `ATLANTIS_WEBENGINE_TESTS=1`.
- `pyproject.toml`:
  - `[tool.pytest.ini_options]`: `addopts = "--strict-markers"`, `markers = ["webengine: …"]`.
  - `[tool.coverage.report].exclude_also = ["if TYPE_CHECKING:", "pragma: no cover", "raise NotImplementedError", "if __name__ == .__main__.:"]`.
  - Dev dep added: `pytest-cov` (pulled `coverage==7.14.0` transitively).
- Refactored `tests/test_phase{2,3,4_window_polish}.py` to drop the 5-line `QT_QPA_PLATFORM` / `ATLANTIS_HEADLESS` / `_APP = create_application()` headers; behaviour identical, central harness owns it.
- New `tests/test_webengine_bridge_smoke.py`:
  - Marked `@pytest.mark.webengine`.
  - Constructs `QWebEngineView` + `WebEngineMermaidBridge`, runs a `QEventLoop` with a 15 s safety timeout, asserts `BridgeRenderResult.ok` and `"<svg" in payload`.
  - Pops `ATLANTIS_HEADLESS` from the env after entering the body, since the marker already gates the test behind `ATLANTIS_WEBENGINE_TESTS=1`.

### P5-C — CI/CD
- New `.github/workflows/ci.yml`:
  - Triggers: `pull_request`, `push` to `main`, `workflow_dispatch`.
  - Concurrency: `${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: true`.
  - Jobs:
    - **lint-and-test** (`ubuntu-latest`, py 3.12): `uv sync --all-extras`, `ruff format --check .`, `ruff check .`, `pytest --cov=atlantis --cov-report=term-missing --cov-report=xml -q`, `codecov/codecov-action@v5` (token-aware via `secrets.CODECOV_TOKEN`).
    - **type-check** (`ubuntu-latest`, py 3.12, `continue-on-error: true`): `uv run mypy atlantis`. Non-blocking until the Phase 4 Qt accessor typing cleanup ships.
    - **docs-build** (`ubuntu-latest`, py 3.12): `uv run mkdocs build --strict`. Existing publishing workflow (`docs.yml`) is untouched.
    - **macos-smoke** (`macos-13`, py 3.12): `pytest -q` only when manually dispatched (`if: github.event_name == 'workflow_dispatch'`) — guards against PyQt6-WebEngine wheel changes that need macOS 13+ without burning CI minutes on every PR.
- `README.md`:
  - Rewritten with CI / docs / codecov badges, a `uv` Quickstart, a "Running the test suite" section, a Contributing pointer, and a docs-site link.
  - Replaces the prior 13-line minimal README.
- Existing `.github/workflows/docs.yml` (Pages deploy) intentionally unchanged — Phase 5 only added a strict build job, not a second publish.

### P5-F — Formatting & quality
- New `.pre-commit-config.yaml`:
  - `pre-commit/pre-commit-hooks` @ v5.0.0: trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-merge-conflict, mixed-line-ending (`--fix=lf`).
  - `astral-sh/ruff-pre-commit` @ **v0.15.12** (matches `ruff>=0.15.12` in `pyproject.toml`): `ruff --fix`, `ruff-format`.
  - mypy hook intentionally deferred — documented in the file header and in `docs/contributing.md`. Will be added the same commit that promotes the CI `type-check` job to blocking.
- New `docs/contributing.md`:
  - Tooling baseline table.
  - First-time setup (`uv sync` + `uv run pre-commit install` + `uv run pre-commit run --all-files`).
  - Contributor loop (ruff + pytest + mkdocs strict + coverage + opt-in WebEngine).
  - Test conventions (rely on `conftest.py`; use `autosave_tmp`; mark long-running tests `webengine`).
  - Documentation conventions (build with `mkdocs serve` / `mkdocs build --strict` before pushing).
  - Memory-bank workflow pointer.

### P5-D — Documentation site
- `mkdocs.yml`:
  - Theme switched from `readthedocs` to `material` (already a dev dep). Features enabled: `navigation.instant`, `navigation.sections`, `navigation.expand`, `toc.integrate`, `content.code.copy`, `content.code.annotate`. Light/dark palette via `prefers-color-scheme`.
  - Plugins: `search`, `mkdocstrings` (handler `python`, `paths: ["."]`, Google docstring style, `show_submodules: true`, `merge_init_into_class: true`).
  - `nav:` reworked into Home / Getting Started / User Guide (Editor, Renderer, Front matter, Examples, Troubleshooting) / Reference (Architecture, API, Project brief) / ADRs (0001, 0002) / Contributing.
- New pages:
  - `docs/getting-started.md` — install + first run + smoke test + tests + logging.
  - `docs/user-guide/editor.md` — keyboard shortcuts, recent files, autosave/recovery, errors, theme.
  - `docs/user-guide/renderer.md` — WebEngine + Mermaid integration, render-flow diagram, validation PoC, tuning.
  - `docs/user-guide/front-matter.md` — YAML/TOML behaviour table, examples (valid + invalid).
  - `docs/user-guide/examples.md` — flowchart, sequenceDiagram, classDiagram snippets.
  - `docs/user-guide/troubleshooting.md` — blank preview, `mermaid is not defined`, macOS 12, timeouts, test lifecycle, pre-commit/CI drift, logging.
  - `docs/reference/architecture.md` — distilled view of `systemPatterns.md` + creative records.
  - `docs/reference/api.md` — one-liner `::: atlantis` mkdocstrings entry that produces a ~3.5 k-line `site/reference/api/index.html`.
  - `docs/adr/0001-mermaid-cdn-mvp.md` — formal record of the CDN-MVP decision (Stage-2 bundle still deferred).
  - `docs/adr/0002-pyqt6-pin-macos-12.md` — formal record of the `PyQt6<6.10` pin rationale.
- `docs/index.md` — rewritten as a landing page that cross-links the new structure.

### P5-W — Workspace
- `.vscode/tasks.json` gains three new tasks alongside the existing seven:
  - **Coverage**: `uv run pytest --cov=atlantis --cov-report=term-missing -q`
  - **Pre-commit (all files)**: `uv run pre-commit run --all-files`
  - **Build Docs (strict)**: `uv run mkdocs build --strict`
- `.vscode/extensions.json` reviewed; `charliermarsh.ruff`, `anysphere.cursorpyright`, `yzhang.markdown-all-in-one` already present — no additions required.

### Key Files Added / Changed
- **New (11)**:
  - `tests/conftest.py`
  - `tests/test_webengine_bridge_smoke.py`
  - `.github/workflows/ci.yml`
  - `.pre-commit-config.yaml`
  - `docs/getting-started.md`
  - `docs/contributing.md`
  - `docs/user-guide/editor.md`
  - `docs/user-guide/renderer.md`
  - `docs/user-guide/front-matter.md`
  - `docs/user-guide/examples.md`
  - `docs/user-guide/troubleshooting.md`
  - `docs/reference/architecture.md`
  - `docs/reference/api.md`
  - `docs/adr/0001-mermaid-cdn-mvp.md`
  - `docs/adr/0002-pyqt6-pin-macos-12.md`
  - `memory-bank/reflection/reflection-build-phase5-2026-05-11.md`
- **Modified (8)**:
  - `pyproject.toml` (pytest markers + addopts, coverage `exclude_also`, `pytest-cov` dev dep)
  - `mkdocs.yml` (theme switch, mkdocstrings, full nav)
  - `docs/index.md` (rewritten as landing page)
  - `README.md` (rewritten with badges + Quickstart)
  - `.vscode/tasks.json` (3 new tasks)
  - `tests/test_phase2_window.py` / `tests/test_phase3_persistence.py` / `tests/test_phase4_window_polish.py` (dropped duplicate env/`_APP` header)
  - `atlantis/renderer/webengine_bridge.py` (one-line `ruff format` pass on a hand-wrapped ternary)
  - `memory-bank/tasks.md`, `memory-bank/activeContext.md`, `memory-bank/progress.md`
- `uv.lock` regenerated as a side-effect of `uv add --dev pytest-cov`.

## TESTING
- **Final gate commands**:
  - `uv run ruff format --check .`
  - `uv run ruff check .`
  - `uv run pytest -q`
  - `uv run pytest --cov=atlantis --cov-report=term-missing -q`
  - `uv run mkdocs build --strict`
  - `uv run pre-commit validate-config .pre-commit-config.yaml`
- **Results**:
  - `ruff format --check`: PASS (30 files, no drift).
  - `ruff check`: PASS (zero findings).
  - `pytest`: PASS — **21 passed, 1 skipped** (the new `webengine` smoke is opt-in; runs only under `ATLANTIS_WEBENGINE_TESTS=1`).
  - `pytest --cov`: PASS, **69 %** total (statement + branch). Largest gaps: `atlantis/main.py` (0 %), `atlantis/core/logging.py` (0 %), `atlantis/renderer/webengine_bridge.py` (35 % — needs the opt-in WebEngine path to cover).
  - `mkdocs build --strict`: PASS (Site generated; mkdocstrings produced `site/reference/api/index.html` with 3525 lines).
  - `pre-commit validate-config`: PASS.
- **Behavior validated**:
  - Existing test modules execute without their previous Qt-env headers; the central `conftest.py` provides the lifecycle.
  - `@pytest.mark.webengine` is registered (`pytest --markers` lists it) and skipped by default; toggling `ATLANTIS_WEBENGINE_TESTS=1` flips the gate.
  - CI workflow file passes GitHub Actions schema (loaded without errors locally; will run on first PR/push to verify end-to-end).
  - Material theme renders all new pages; nav matches the file tree; no orphan pages flagged by strict mode.
  - mkdocstrings API page resolves `atlantis` + all submodules.

## PHASE 5 EXIT CRITERIA — FINAL STATE
- [x] `tests/conftest.py` exists; existing tests stop re-declaring env/`_APP`; default `pytest` still ≥ 21 passing.
- [x] `webengine` pytest marker registered and the opt-in smoke test is skipped by default.
- [x] `.github/workflows/ci.yml` runs lint + tests + coverage upload + docs strict-build on PRs and `main`.
- [x] `.pre-commit-config.yaml` exists and `uv run pre-commit validate-config` is clean.
- [x] `mkdocs.yml` carries the new nav; `uv run mkdocs build --strict` is green locally; mkdocstrings produces an API page.
- [x] `README.md` has CI / codecov / docs badges and a Quickstart using `uv` commands; `docs/contributing.md` describes the contributor loop.
- [x] `.vscode/tasks.json` has Coverage, Pre-commit (all files), and Build Docs tasks.
- [x] `ruff format --check` + `ruff check` + default `pytest` pass.

## LESSONS LEARNED
- **CI-equivalent gates expose pre-existing drift on day one.** Adding `ruff format --check` caught hand-formatted drift in `atlantis/renderer/webengine_bridge.py` that Phase 4's `ruff check`-only gate had let through. Every phase gate going forward should run both `ruff format --check` and `ruff check`.
- **For every config file in the repo, the matching consumer should already be a dep.** `codecov.yaml` had been shipped for several phases without `pytest-cov`; an audit step ("does anything actually consume this YAML?") would have caught it sooner.
- **Registered marker + collection hook > env-only gating.** `@pytest.mark.webengine` is discoverable (`pytest --markers`), enforced by `--strict-markers`, and self-documenting in `pyproject.toml`.
- **Pin pre-commit hook versions to the same tag the dev-dep uses.** Eliminates "works locally, fails in CI" drift before it can occur.
- **mypy stays non-blocking until typing cleanup ships.** Better to keep the job visible than to bury real type errors under the chronic Qt accessor noise inherited from Phase 4.
- **Material is the right default for mkdocstrings-heavy projects.** Already a dev dep; navigation features (`navigation.sections`, `navigation.expand`, code annotations) significantly improve the auto-generated API reference's usability.
- **One ADR per non-obvious decision is the right granularity.** Capturing CDN-MVP and PyQt6-pin ADRs while still fresh cost ~30 minutes each and replaces tribal knowledge with discoverable docs.
- **"Extend, don't replace" keeps the diff reviewable.** Phase 5 wrote one new workflow + one new pre-commit config + three new VS Code tasks; everything else extended existing files.

## DEFERRALS & FOLLOW-UPS
- **Promote mypy CI job to blocking** once the Qt accessor typing cleanup (Phase 4 carry-over) ships; add a `mirrors-mypy` pre-commit hook in lockstep.
- **Lift coverage from 69 %**: add tests for `atlantis/main.py` (CLI entrypoint + `--log-level`), `atlantis/core/logging.py`, and the opt-in WebEngine path (`atlantis/renderer/webengine_bridge.py` at 35 %).
- **`pre-commit autoupdate`** quarterly chore paired with a `ruff` dev-dep bump to keep CI and pre-commit in lockstep.
- **Trim redundant docs build**: today both the new `ci.yml docs-build` job and the existing `docs.yml` build the site; consider extracting `docs.yml` to publish-only or sharing the build artifact.
- **`noxfile.py` (or `Makefile`)** to single-source the `uv run …` commands repeated across README, `docs/contributing.md`, `ci.yml`, and VS Code tasks.
- **Document WebEngine smoke-test environment requirements** in `docs/user-guide/troubleshooting.md` once contributors start running it (display-server, codec availability).
- **Watch `mkdocs-material --strict` notice** — INFO-level today; if it escalates to WARNING with the 2.0 transition, evaluate either silencing or theme migration.

## REFERENCES
- Plan and implementation log: `memory-bank/tasks.md` (see **PLAN Refinement: BUILD Phase 5 (2026-05-11)** and **BUILD Phase 5 Implementation Results (2026-05-11)**)
- Progress timeline: `memory-bank/progress.md`
- Reflection: `memory-bank/reflection/reflection-build-phase5-2026-05-11.md`
- Tech context: `memory-bank/techContext.md`
- Predecessor archives:
  - `memory-bank/archive/archive-build-phase4-2026-05-11.md`
  - `memory-bank/archive/archive-build-phase3-2026-05-11.md`
  - `memory-bank/archive/archive-build-phase1-2-2026-05-06.md`
- Creative decisions (still authoritative):
  - `memory-bank/creative/creative-editor-component.md`
  - `memory-bank/creative/creative-ui-layout-feedback.md`
  - `memory-bank/creative/creative-renderer-offline-bundle.md`
  - `memory-bank/creative/creative-packaging-plugin-boundaries.md`
- New ADRs (this milestone):
  - `docs/adr/0001-mermaid-cdn-mvp.md`
  - `docs/adr/0002-pyqt6-pin-macos-12.md`
- CI surface: `.github/workflows/ci.yml`, `.github/workflows/docs.yml`, `.pre-commit-config.yaml`, `codecov.yaml`
