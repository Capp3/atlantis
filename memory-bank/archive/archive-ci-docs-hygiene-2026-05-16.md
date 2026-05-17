# TASK ARCHIVE: CI/docs hygiene

## METADATA
- **Task ID**: ci-docs-hygiene-2026-05-16
- **Complexity**: Level 2 (Simple Enhancement — config/docs only)
- **Task Type**: CI consolidation, GitHub Pages fix, contributor docs, pre-commit maintenance
- **Archive Date**: 2026-05-16
- **Status**: Complete
- **Related Reflection**: `memory-bank/reflection/reflection-ci-docs-hygiene-2026-05-16.md`
- **Predecessor Archive**: `memory-bank/archive/archive-build-phase5-2026-05-11.md`

## SUMMARY

Phase 5 follow-up that closed engineering hygiene gaps without changing application behavior. Removed the redundant `docs-build` job from `ci.yml`, made `docs.yml` the single strict MkDocs gate on pull requests and `main`, fixed GitHub Pages to publish the MkDocs `site/` output (not source `docs/`), documented the opt-in WebEngine pytest environment, ran `pre-commit autoupdate`, and added regression tests so workflow mistakes cannot silently return.

Final gate (Linux): `ruff format --check` + `ruff check` clean; **24 passed, 1 skipped** (+3 hygiene tests); `mkdocs build --strict` green.

## REQUIREMENTS

1. **Trim redundant docs build** — stop building MkDocs twice (`ci.yml` + `docs.yml`).
2. **PR docs validation** — strict MkDocs build on pull requests, not only on `main` publish.
3. **Correct Pages artifact** — deploy built HTML from `site/`, not Markdown under `docs/`.
4. **WebEngine smoke documentation** — environment requirements for `ATLANTIS_WEBENGINE_TESTS=1` (Phase 5 deferral).
5. **Pre-commit autoupdate** — refresh hook revisions; keep `ruff` pre-commit pin aligned with `pyproject.toml` (Phase 5 deferral).

## IMPLEMENTATION

### CI workflows

**`.github/workflows/ci.yml`**
- Removed the `docs-build` job entirely.
- Retained: `lint-and-test`, `type-check` (non-blocking), `macos-smoke` (opt-in `workflow_dispatch`).

**`.github/workflows/docs.yml`** (workflow name: `Docs`)
- Triggers: `pull_request`, `push` to `main`, `workflow_dispatch`.
- **`build` job**: checkout (`fetch-depth: 0`), Python 3.12, `uv sync --all-extras`, `uv run mkdocs build --strict`; on `main` push only, uploads `site/` as artifact `mkdocs-site`.
- **`deploy` job** (`needs: build`, `main` push only): downloads artifact, `configure-pages`, `upload-pages-artifact` with `path: site`, `deploy-pages`.
- Concurrency: `docs-${{ github.workflow }}-${{ github.ref }}`, `cancel-in-progress: true`.

### Documentation

- **`docs/user-guide/troubleshooting.md`**: new section *Opt-in WebEngine pytest* — when to run, env table (display, WebEngine, CDN, macOS pin), CI pointers, common failures.
- **`docs/contributing.md`**: CI workflow table (`ci.yml` vs `docs.yml`); cross-link to troubleshooting; note that docs are not duplicated in `ci.yml`.

### Tooling

- **`.pre-commit-config.yaml`**: `pre-commit-hooks` v6.0.0; `ruff-pre-commit` v0.15.13.
- **`pyproject.toml`**: `ruff>=0.15.13`.

### Tests

- **`tests/test_ci_docs_hygiene.py`** (new):
  - `test_ci_workflow_has_no_redundant_docs_build_job`
  - `test_docs_workflow_builds_strict_and_publishes_site_directory`
  - `test_pre_commit_ruff_rev_matches_pyproject_floor`

### Files touched

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | Removed `docs-build` job |
| `.github/workflows/docs.yml` | PR strict build + `site/` deploy pipeline |
| `docs/user-guide/troubleshooting.md` | WebEngine pytest section |
| `docs/contributing.md` | CI workflow table + link |
| `.pre-commit-config.yaml` | Autoupdate revisions |
| `pyproject.toml` | `ruff>=0.15.13` |
| `tests/test_ci_docs_hygiene.py` | New regression tests |

**App/runtime code**: none.

## TESTING

| Command | Result |
|---------|--------|
| `uv run ruff format --check .` | PASS (31 files) |
| `uv run ruff check .` | PASS |
| `uv run pytest -q` | **24 passed, 1 skipped** |
| `uv run mkdocs build --strict` | PASS |

Hygiene tests assert workflow invariants without invoking GitHub Actions.

## EXIT CRITERIA — FINAL STATE

- [x] No duplicate mkdocs build between `ci.yml` and `docs.yml`.
- [x] PRs get strict docs validation via `docs.yml`.
- [x] Pages deploy uses `site/` artifact.
- [x] WebEngine smoke environment documented.
- [x] Pre-commit hooks autoupdated; ruff pin aligned.

## LESSONS LEARNED

- Trace CI artifact paths to MkDocs defaults (`site/`, not `docs/`).
- Before adding a CI job, diff against existing workflows to avoid duplication.
- Config-only changes benefit from pytest guards on workflow YAML structure.
- Phase 5’s `docs-build` job masked a latent Pages misconfiguration until this consolidation pass.

## DEFERRALS & FOLLOW-UPS

- **Post-merge**: smoke-check published GitHub Pages after first `main` deploy with fixed `site/` path (navigation, API reference).
- **Optional**: path filters on `docs.yml`; `actionlint` in pre-commit if workflow YAML churn grows.
- **Unchanged backlog**: coverage lift, mypy promotion, `nox`/`Makefile`, offline bundle, Phase 4 carry-overs, Phase 7/8.

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-ci-docs-hygiene-2026-05-16.md`
- Implementation log (ephemeral, now archived): `memory-bank/tasks.md` status section
- Progress: `memory-bank/progress.md`
- Phase 5 archive (source deferrals): `memory-bank/archive/archive-build-phase5-2026-05-11.md`
- Workflows: `.github/workflows/ci.yml`, `.github/workflows/docs.yml`
- Contributor docs: `docs/contributing.md`, `docs/user-guide/troubleshooting.md`
