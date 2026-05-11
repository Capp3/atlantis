# Memory Bank: Active Context

## Current Focus
**No active task.** BUILD Phase 5 (cross-cutting docs / tests / formatting / CI-CD / workspace) archived 2026-05-11. Use `/van` to initialize the next workstream.

## Status
- **Active task**: none.
- **Last completed milestone**: BUILD Phase 5 (archived 2026-05-11) — see `memory-bank/archive/archive-build-phase5-2026-05-11.md`.
- **Engineering surface (carried forward into all future phases)**:
  - Shared pytest harness in `tests/conftest.py` (offscreen + headless at import time; session `qapp`; `autosave_tmp`; `webengine` marker gated by `ATLANTIS_WEBENGINE_TESTS=1`).
  - Coverage wired with `pytest-cov` + `[tool.coverage.report].exclude_also`; baseline **69 %**.
  - `.github/workflows/ci.yml` (lint + tests + coverage upload + docs strict-build; opt-in `macos-13` smoke on `workflow_dispatch`); existing `docs.yml` publishes on `main`.
  - `.pre-commit-config.yaml` pinned to the same `ruff` tag CI uses (mypy hook deferred).
  - mkdocs nav: Home / Getting Started / User Guide / Reference / ADRs / Contributing; mkdocstrings auto-generates the API reference.
  - VS Code tasks: Ruff Fix, Type Check, Run Tests, Coverage, Pre-commit (all files), Build Docs (strict), Serve Docs, Launch Atlantis (debug / DEBUG log), Tech Validation.
- **Code state**: Phases 1–4 stable; **21 passed + 1 skipped** (opt-in WebEngine) on the default suite.

## Platform & Environment Snapshot
- macOS 12.7.6 (Darwin 21.6.0, x86_64) — `PyQt6<6.10` / `PyQt6-WebEngine<6.10` pins remain in force (ADR `0002-pyqt6-pin-macos-12.md`).
- `.venv/` present; use `uv sync` + `uv run …` per project standard.

## Open Backlog (candidates for the next `/van`)
- **Phase 4 carry-overs**: `FileSession` refactor; structured logging for `atlantis.renderer.bridge`; Stage-2 offline Mermaid bundle (`assets/preview_shell.html`); Qt accessor typing cleanup; menu-driven front matter edit (TOML dict editor; YAML preserved-only).
- **Phase 5 follow-ups**: coverage lift (`atlantis/main.py`, `atlantis/core/logging.py`, opt-in WebEngine path); promote mypy CI job to blocking + add `mirrors-mypy` pre-commit hook; `noxfile.py`/`Makefile` to single-source `uv run …` commands; quarterly `pre-commit autoupdate`; trim redundant docs build between `ci.yml` and `docs.yml`; document WebEngine smoke-test environment requirements.
- **Phase 7 (original plan) — Creative / future-proofing**: revisit plugin architecture, packaging strategy.
- **Phase 8 (original plan) — Rollout**: native bundling, release engineering, distribution.

## References
- Plan + history: `memory-bank/tasks.md`
- Progress timeline: `memory-bank/progress.md`
- Last archive: `memory-bank/archive/archive-build-phase5-2026-05-11.md`
- Last reflection: `memory-bank/reflection/reflection-build-phase5-2026-05-11.md`
- Tech context: `memory-bank/techContext.md`
- Creative decisions (still authoritative):
  - `memory-bank/creative/creative-editor-component.md`
  - `memory-bank/creative/creative-ui-layout-feedback.md`
  - `memory-bank/creative/creative-renderer-offline-bundle.md`
  - `memory-bank/creative/creative-packaging-plugin-boundaries.md`
- ADRs:
  - `docs/adr/0001-mermaid-cdn-mvp.md`
  - `docs/adr/0002-pyqt6-pin-macos-12.md`
