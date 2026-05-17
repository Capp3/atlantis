# TASK ARCHIVE: P8-H bundle CI

## METADATA
- **Task ID**: p8h-bundle-ci-2026-05-16
- **Complexity**: Level 2 (CI/docs; no runtime behavior change)
- **Task Type**: Opt-in GitHub Actions Linux PyInstaller bundle validation
- **Archive Date**: 2026-05-16
- **Status**: Complete (post-merge manual dispatch optional)
- **Related Reflection**: `memory-bank/reflection/reflection-p8h-bundle-ci-2026-05-16.md`
- **Predecessor Archive**: `memory-bank/archive/archive-phase78-2026-05-16.md`
- **Source deferral**: Phase 7/8 archive — P8-H GitHub bundle workflow deferred

## SUMMARY

Closed the **Phase 8 P8-H deferral** by adding `.github/workflows/bundle.yml` (`workflow_dispatch` only): `uv sync --group packaging`, `make bundle-smoke`, upload `dist/atlantis/` artifact (14-day retention, 45m job timeout). Extended hygiene tests and documented the workflow in contributing, installation, troubleshooting, and workflows README. **No application code changes.** `ci.yml` PR gate unchanged. Tests: **103 → 107 passed, 1 skipped** (+4 hygiene).

## REQUIREMENTS

1. Maintainers can manually run **Actions → Bundle Linux (experimental)** and download a Linux one-folder bundle.
2. CI uses the same **`make bundle-smoke`** target as local builds.
3. **No** bundle build on `pull_request` / `push` (PR duration unchanged).
4. Hygiene regression tests lock workflow structure.
5. Document artifact download (not GitHub Releases yet).

## IMPLEMENTATION

### P8-H-A — `.github/workflows/bundle.yml`

| Property | Value |
|----------|-------|
| Trigger | `workflow_dispatch` only |
| Runner | `ubuntu-latest`, Python 3.12 |
| Sync | `uv sync --python 3.12 --group packaging` |
| Build | `make bundle-smoke` |
| Artifact | `upload-artifact@v4` → `dist/atlantis/`, name `atlantis-linux-bundle-${{ github.run_number }}`, 14-day retention |
| Timeout | 45 minutes |
| Permissions | `contents: read` |

### P8-H-B — Hygiene tests (`tests/test_ci_docs_hygiene.py`)

- `test_bundle_workflow_is_dispatch_only`
- `test_bundle_workflow_uses_make_bundle_smoke`
- `test_bundle_workflow_uploads_dist_atlantis`
- `test_bundle_workflow_has_sufficient_timeout`

### P8-H-C — Documentation

- `.github/workflows/README.md` — Bundle Linux row
- `docs/contributing.md` — CI table + release checklist Actions link
- `docs/user-guide/installation.md` — CI-built Linux bundle section
- `docs/user-guide/troubleshooting.md` — opt-in bundle pointer

### Files touched

| Action | Path |
|--------|------|
| Add | `.github/workflows/bundle.yml` |
| Edit | `tests/test_ci_docs_hygiene.py` |
| Edit | `.github/workflows/README.md` |
| Edit | `docs/contributing.md` |
| Edit | `docs/user-guide/installation.md` |
| Edit | `docs/user-guide/troubleshooting.md` |

## TESTING

| Command | Result |
|---------|--------|
| `make check-all` | PASS |
| `uv run pytest -q` | **107 passed, 1 skipped** (+4) |
| `uv run pytest tests/test_ci_docs_hygiene.py -q` | **11 passed** |
| Remote `workflow_dispatch` | **Pending** (manual post-merge) |

## EXIT CRITERIA — FINAL STATE

- [x] `bundle.yml` dispatch-only
- [x] `make bundle-smoke` in workflow
- [x] Artifact upload configured
- [x] +4 hygiene tests
- [x] Docs updated
- [x] `ci.yml` unchanged
- [x] `make check-all` green
- [ ] Post-merge green dispatch (maintainer optional)

## LESSONS LEARNED

- Build local `make bundle-smoke` before adding CI — P8-H was a thin wrapper, not a packaging debug session.
- Opt-in heavy jobs belong in a **separate workflow** when `ci.yml` dispatch would fan out unrelated jobs.
- Hygiene tests are the right lock for YAML-only CI changes.
- Document Actions artifact download when Releases automation does not exist yet.

## DEFERRALS & FOLLOW-UPS

- Tag-triggered GitHub Release with wheel + tarball (Option 3 full)
- macOS/Windows bundle CI; codesigning
- `uv` cache in `bundle.yml` if cold builds are slow
- ADR 0004 one-line CI validation footnote after first green remote run
- Export plugin, FS-F cache, FM polish (unchanged backlog)

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-p8h-bundle-ci-2026-05-16.md`
- Phase 7/8 archive: `memory-bank/archive/archive-phase78-2026-05-16.md`
- Creative (CI integration): `memory-bank/creative/creative-phase78-rollout.md`
- ADR: `docs/adr/0004-native-bundle-pyinstaller.md`
- Local bundle: `packaging/pyinstaller/README.md`
