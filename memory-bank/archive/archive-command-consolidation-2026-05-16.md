# TASK ARCHIVE: Command consolidation

## METADATA
- **Task ID**: command-consolidation-2026-05-16
- **Complexity**: Level 2 (DX; docs/CI alignment; no runtime behavior change)
- **Task Type**: Makefile canonical gates; CI + contributor doc alignment
- **Archive Date**: 2026-05-16
- **Status**: Complete
- **Related Reflection**: `memory-bank/reflection/reflection-command-consolidation-2026-05-16.md`
- **Predecessor Archive**: `memory-bank/archive/archive-filesession-refactor-2026-05-16.md`
- **Source deferral**: Phase 5 archive — `noxfile.py` / `Makefile` to single-source `uv run` commands

## SUMMARY

Closed the Phase 5 command-consolidation deferral by replacing the unrelated Vibe dev-template root **`Makefile`** with Atlantis quality-gate targets (`make check`, `make check-all`, and per-gate recipes), relocating template automation to **`Makefile.vibe`**, and pointing **CI workflows** (`ci.yml`, `docs.yml`) at the same `make` targets contributors use locally. Updated **`docs/contributing.md`**, **`README.md`**, **VS Code tasks**, and **`techContext.md`**. **nox deferred.** Tests: **74 → 80 passed, 1 skipped** (+6 hygiene tests).

## REQUIREMENTS

1. Single local entry point mirroring CI gates (format, lint, mypy, pytest+cov, docs).
2. Remove Atlantis-unrelated targets from root Makefile (Vibe template separated).
3. Export `QT_QPA_PLATFORM=offscreen` and `ATLANTIS_HEADLESS=1` for pytest targets.
4. Document `uv run` equivalents for environments without GNU Make.
5. Align CI with Makefile (no doc-only Make).
6. Regression tests lock Makefile structure and CI YAML.
7. No application code changes; ruff + mypy remain clean.

## IMPLEMENTATION

### CC-A/B — Root `Makefile`

| Target | Command |
|--------|---------|
| `format-check` | `uv run ruff format --check .` |
| `lint` | `uv run ruff check .` |
| `typecheck` | `uv run mypy atlantis` |
| `test` / `test-cov` | `uv run pytest` (+ exported offscreen env) |
| `docs` | `uv run mkdocs build --strict` |
| **`check`** | `format-check` + `lint` + `typecheck` + `test-cov` |
| **`check-all`** | `check` + `docs` |
| Also | `sync`, `format`, `lint-fix`, `docs-serve`, `pre-commit`, `webengine`, `clean` |

### CC-C — `Makefile.vibe`

- Relocated Vibe memory-bank / cursor-rules installer targets
- Invoke: `make -f Makefile.vibe help`

### CC-D / CC-D2 — Docs + CI

- `contributing.md`: `make check-all` primary loop; make ↔ `uv run` table
- `README.md`: `make check` in quickstart
- `ci.yml`: `make format-check`, `lint`, `test-cov`, `typecheck`, `test` (macos smoke)
- `docs.yml`: `make docs`
- `.github/workflows/README.md`: real workflow summary

### CC-E — `.vscode/tasks.json`

- **Check (PR gate)** → `make check`
- Tests/coverage → `make test` / `make test-cov`; consistent `uv run` elsewhere

### CC-F — Tests

- `tests/test_makefile_targets.py` (4): `make help`, `make format-check`, parse `check:` / `check-all:` prerequisites
- `tests/test_ci_docs_hygiene.py` (+2): CI lint job + docs workflow use make targets

### Files touched

| File | Change |
|------|--------|
| `Makefile` | Rewritten (Atlantis gates) |
| `Makefile.vibe` | New (template tooling) |
| `.github/workflows/ci.yml` | make targets |
| `.github/workflows/docs.yml` | `make docs` |
| `docs/contributing.md`, `README.md` | make-first docs |
| `memory-bank/techContext.md` | canonical `make check` |
| `.vscode/tasks.json` | aligned tasks |
| `tests/test_makefile_targets.py` | New |
| `tests/test_ci_docs_hygiene.py` | +2 assertions |

## TESTING

| Command | Result |
|---------|--------|
| `make check-all` | PASS |
| `uv run pytest -q` | **80 passed, 1 skipped** (+6) |
| `uv run mypy atlantis` | **0 errors** |
| `uv run ruff format --check .` + `ruff check .` | PASS |

## EXIT CRITERIA — FINAL STATE

- [x] `make check` / `make check-all` shipped
- [x] CI uses make targets
- [x] `Makefile.vibe` separated
- [x] Docs + VS Code aligned
- [x] 80 tests; ruff/mypy clean
- [x] Hygiene tests lock Makefile + CI

## LESSONS LEARNED

- CI must call the same Make targets as contributors or the Makefile becomes dead documentation.
- Relocate unrelated template Make targets before adding project gates.
- Parse `check:` prerequisites in tests plus subprocess smoke.
- nox optional when uv + Make are project standard.
- Pre-commit stays outside `check` (overlap + slower); document explicitly.

## DEFERRALS & FOLLOW-UPS

- **noxfile.py** — optional thin wrapper over Make.
- **`INCLUDE_PRE_COMMIT=1`** — optional `check-all` variant.
- **Backlog:** menu-driven front matter edit (Level 3); Phase 7/8 (Level 4).
- **Removed deferral:** ~~nox/Makefile consolidation~~ — **done**.

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-command-consolidation-2026-05-16.md`
- Phase 5 source: `memory-bank/archive/archive-build-phase5-2026-05-11.md`
- Predecessor: `memory-bank/archive/archive-filesession-refactor-2026-05-16.md`
- Canonical commands: root `Makefile`, `docs/contributing.md`
