# Task Reflection: P8-H bundle CI (2026-05-16)

## Summary

Level 2 workstream closing the **Phase 8 deferral (P8-H)**: opt-in GitHub Actions workflow for Linux PyInstaller bundle validation. Added `.github/workflows/bundle.yml` (`workflow_dispatch` only) that runs `uv sync --group packaging`, `make bundle-smoke`, and uploads `dist/atlantis/` as a 14-day artifact. Extended CI/docs hygiene tests and documented the workflow in contributing, installation, and troubleshooting guides. **No application code changes.** PR gate unchanged (`ci.yml` untouched). Tests: **103 → 107 passed, 1 skipped** (+4 hygiene).

## What Went Well

- **Plan-to-build was mechanical** — creative decisions were already captured in `creative-phase78-rollout.md`; no `/creative` cycle needed.
- **Separate `bundle.yml` workflow** — dispatching bundle work does not also run lint/test/macos jobs from `ci.yml`; maintainers get a single-purpose Actions entry.
- **`make bundle-smoke` as CI step** — command-consolidation invariant held; Makefile offscreen env applies in CI without duplicating `QT_QPA_PLATFORM` in YAML.
- **`uv sync --group packaging` only** — faster than `--all-extras`; sufficient for PyInstaller build (validated in Phase 7/8 locally).
- **Hygiene tests extended existing module** — four assertions lock dispatch-only trigger, Make target, artifact path, and timeout ≥ 30m; pattern matches command-consolidation and ci-docs-hygiene archives.
- **Docs triad** — workflows README, release checklist, installation “CI-built bundle” section, troubleshooting pointer — mirrors macOS smoke documentation style.

## Challenges Encountered

- **Cannot verify remote workflow locally** — `make bundle-smoke` passes on dev machine; first real `ubuntu-latest` PyInstaller run is post-merge manual dispatch (accepted risk; same as initial macos-smoke pattern).
- **Artifact size / retention** — hundreds of MB per run; 14-day retention and “not on PR gate” documented to avoid surprise storage use.
- **Push trigger guard in test** — used regex for `^\s+push:\s*$` so `push:` in comments or unrelated strings do not false-positive; `pull_request:` absent is sufficient for dispatch-only contract.

## Solutions Applied

- Standalone workflow with `permissions: contents: read` only.
- `timeout-minutes: 45` on job (plan specified; hygiene test enforces ≥ 30).
- Artifact name `atlantis-linux-bundle-${{ github.run_number }}` for unique downloads per run.
- Skipped ADR 0004 edit (optional footnote deferred until post-merge green run).

## Lessons Learned

- **Defer heavy CI until local smoke is green** — Phase 7/8 built `make bundle-smoke` first; P8-H was a thin workflow wrapper, not a packaging debug session.
- **Opt-in workflows belong in their own file** when dispatch would otherwise fan out unrelated jobs.
- **Hygiene tests are the right lock for workflow-only changes** — no need to run PyInstaller in default pytest suite.
- **Document artifact download path at ship time** — installation guide section prevents “where is the Release binary?” confusion when only Actions artifacts exist.

## Process Improvements

- Add “dispatch Bundle Linux once” to maintainer post-merge checklist for packaging-related PRs.
- If bundle CI fails on runner, capture logs before adding `apt` packages — avoid speculative system deps in YAML.
- Consider `actionlint` only if workflow YAML churn increases (still optional).

## Technical Improvements

- **Post-merge:** one green `workflow_dispatch` run; optionally add one-line ADR 0004 footnote after confirmation.
- **Future:** tag-triggered Release with wheel + tarball (Option 3 full — still deferred).
- **Future:** `uv` cache in `bundle.yml` if cold-runner build time becomes painful.
- **Unchanged backlog:** export plugin, FS-F cache, FM polish, macOS bundle/codesign.

## Plan vs. Actual

| Plan item | Actual |
|-----------|--------|
| New `bundle.yml` dispatch-only | **Shipped** |
| `make bundle-smoke` in CI | **Shipped** |
| `upload-artifact` `dist/atlantis/` | **Shipped** |
| +2–3 hygiene tests | **4** (+ timeout guard) |
| Docs (4 files) | **Shipped** (ADR footnote skipped as optional) |
| `ci.yml` unchanged | **Confirmed** |
| 103 → ~106 tests | **107 passed** |
| Post-merge dispatch | **Pending** (manual) |

## Metrics

- New files: `.github/workflows/bundle.yml`
- Edited: `tests/test_ci_docs_hygiene.py`, `.github/workflows/README.md`, `docs/contributing.md`, `docs/user-guide/installation.md`, `docs/user-guide/troubleshooting.md`
- Workflow steps: 5 (checkout, python, uv sync, bundle-smoke, upload)
- App code changed: **none**

## Next Steps

- Run **`/archive`** to capture milestone and reset active task.
- **Post-merge:** dispatch **Bundle Linux (experimental)** once; download artifact and smoke locally if desired.
- **Backlog:** export plugin (Level 3–4), FS-F / FM polish (Level 2), macOS bundle (Level 4).
