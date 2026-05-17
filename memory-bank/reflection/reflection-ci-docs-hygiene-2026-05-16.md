# Task Reflection: CI/docs hygiene (2026-05-16)

## Summary

Level 2 follow-up from Phase 5 deferrals. Closed three engineering gaps without changing app behavior: (1) removed the redundant `docs-build` job from `ci.yml` and made `docs.yml` the single strict MkDocs gate on PRs and `main`; (2) fixed GitHub Pages to publish the MkDocs `site/` output instead of source `docs/`; (3) documented the opt-in WebEngine pytest environment in troubleshooting and contributing guides. Also ran `pre-commit autoupdate` (hooks v6, ruff v0.15.13) and added `tests/test_ci_docs_hygiene.py` so workflow regressions are caught in the default suite.

Final gate (Linux): `ruff format --check` + `ruff check` clean; **24 passed, 1 skipped** (+3 hygiene tests); `mkdocs build --strict` green.

## What Went Well

- **The Pages path bug was the highest-value fix.** `docs.yml` had `upload-pages-artifact` pointed at `docs/` (Markdown sources) while MkDocs writes to `site/`. Consolidating workflows surfaced this during review; fixing it unblocks a correct publish on the next `main` deploy.
- **Single-workflow docs validation is simpler than split responsibility.** `docs.yml` now runs on `pull_request` + `main`, builds with `--strict`, and only deploys on `main` via artifact handoff — one `uv sync` + build per event, no duplicate job in `ci.yml`.
- **YAML regression tests are cheap insurance.** `tests/test_ci_docs_hygiene.py` asserts no `docs-build` in `ci.yml`, strict build in `docs.yml`, and `site` as the Pages artifact path. Future refactors cannot silently reintroduce duplication or the wrong folder.
- **Pre-commit autoupdate stayed aligned.** Bumping `ruff-pre-commit` to v0.15.13 and `ruff>=0.15.13` in `pyproject.toml` in the same change preserves the Phase 5 “pin hook rev to dev-dep floor” policy.
- **WebEngine docs closed a Phase 5 deferral.** The troubleshooting section (env table, CI pointers, common failures) plus the contributing workflow table give contributors one place to look instead of tribal knowledge in test docstrings.

## Challenges Encountered

- **Latent misconfiguration from Phase 5.** The redundant `docs-build` job was added in Phase 5 without revisiting whether `docs.yml` already built the site — and `docs.yml` never used `--strict` or the correct artifact path. Both issues predated this task; discovery required reading deploy steps, not just CI job names.
- **No standalone PLAN artifact.** Workstream was scoped inline in VAN backlog and executed directly. Acceptable for Level 2, but exit criteria lived only in `tasks.md` until BUILD completed.
- **Autoupdate major bump on pre-commit-hooks (v5 → v6).** Low risk for this repo’s hook set, but worth a full `pre-commit run --all-files` before merge (done during BUILD gates).

## Solutions Applied

- Merged validation + publish into `docs.yml` with `build` / `deploy` jobs and `upload-artifact` / `download-artifact` for `site/`.
- Removed `docs-build` from `ci.yml` entirely; documented the split in `docs/contributing.md`.
- Added pytest guards for workflow structure and ruff rev parity.
- Expanded `docs/user-guide/troubleshooting.md` and cross-linked from `docs/contributing.md`.

## Lessons Learned

- **Always trace artifact paths to MkDocs defaults.** Default `site_dir` is `site/`; assuming `docs/` is a common mistake when wiring GitHub Pages.
- **When adding a CI job, diff against existing workflows first.** Phase 5 added `docs-build` without demoting or extending `docs.yml`; “extend, don’t replace” should include “don’t duplicate.”
- **Config-only work benefits from machine-checked invariants.** Human review caught the Pages bug; tests lock the fix in place.
- **Deferrals belong in reflection archives, not just tasks.md.** This workstream directly addressed two Phase 5 archive bullets; closing them here reduces backlog noise for the next `/van`.

## Process Improvements

- For future CI/docs changes, run `pytest tests/test_ci_docs_hygiene.py` (or full suite) before opening PR — fast signal on workflow edits.
- After any `pre-commit autoupdate`, bump `pyproject.toml` floors in the same commit and note the pairing in the PR description.

## Technical Improvements

- Consider **path filters** on `docs.yml` (`docs/**`, `mkdocs.yml`, `.github/workflows/docs.yml`) to skip builds when only app code changes — deferred; current cost is acceptable.
- Consider **`actionlint`** or a similar workflow linter in pre-commit if CI YAML churn increases — not required yet.
- **Post-merge verification**: confirm GitHub Pages serves HTML from `site/` (navigation works, API reference renders) after the first `main` deploy with the fixed path.

## Plan vs. Actual

| Planned (VAN backlog) | Shipped |
|----------------------|---------|
| Trim redundant docs build | Yes — `docs-build` removed from `ci.yml`; `docs.yml` validates on PRs |
| WebEngine smoke docs | Yes — troubleshooting + contributing |
| `pre-commit autoupdate` | Yes — v6 hooks + ruff v0.15.13 |
| *(implicit)* Pages path fix | Yes — discovered and fixed during BUILD |

## Metrics

- Tests: 21 → **24** passed (default suite), 1 skipped unchanged
- Workflows touched: 2 (`ci.yml`, `docs.yml`)
- New test module: 1 (`test_ci_docs_hygiene.py`)
- App/runtime code changed: **none**

## Next Steps

- Run **`/archive`** to capture the milestone and reset active task.
- After merge to `main`, **smoke-check published docs** (Pages URL, API reference page, strict build in Actions).
- Remaining backlog unchanged: coverage lift, mypy promotion, `nox`/`Makefile`, offline bundle, etc.
