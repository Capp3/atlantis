# Creative Phase: Phase 7/8 Rollout and Release (2026-05-16)

## Status
Complete — supports `/plan` for rollout sub-track.

## Type
Release engineering / distribution strategy

## Problem Statement
Atlantis has a stable Python-package MVP (`uv sync` + `atlantis`) and CI gates (`make check-all`), but no **release narrative** for end users who expect a downloadable app or versioned installers. Rollout must not destabilize PR gates or force premature macOS signing work.

## Requirements
- Clear install paths documented: developer (uv), user (future bundle).
- Semantic versioning story aligned with `pyproject.toml` (`0.0.x` until beta).
- Release checklist reproducible by maintainers.
- CI: keep PR gate fast; optional/manual heavyweight jobs for bundle smoke.
- GitHub Releases / artifacts optional in first slice.

## Options Analysis

### Option 1 — Docs-only rollout (install + roadmap)
- **Pros:** Low risk; immediate value in README/contributing.
- **Cons:** No artifact publishing.

### Option 2 — Docs + VERSIONING.md + release checklist (recommended baseline)
- **Pros:** Defines channels without CI churn; pairs with PyInstaller PoC doc.
- **Cons:** Still no automated release.

### Option 3 — GitHub Actions release workflow on tag
- **Pros:** Automated wheel + Linux bundle upload to Releases.
- **Cons:** Secrets, artifact storage, macOS runner cost; premature before PoC green.

### Option 4 — Full beta channel (signed macOS app + updater)
- **Pros:** Production-grade.
- **Cons:** Far beyond Phase 8 first slice; not recommended now.

## Decision
**Option 2 for Phase 8 rollout BUILD** — document channels, versioning, and maintainer checklist.

**Option 3 deferred** until Linux PyInstaller smoke passes locally and on optional CI job (`workflow_dispatch` or weekly).

## Rollout Channels (target picture)

| Channel | Audience | Command / artifact | Phase 8 status |
|---------|----------|-------------------|----------------|
| **Developer** | Contributors | `uv sync` + `make check` | **Current default** |
| **Python wheel** | Advanced users | `pip install` / `uv tool install` from sdist/wheel | Document; `uv build` already works |
| **Linux bundle** | Desktop testers | PyInstaller one-folder tarball | PoC + smoke |
| **macOS .app** | Primary brief audience | PyInstaller or Briefcase | Manual doc only in 8a |
| **Windows** | Cross-platform brief | PyInstaller one-folder | Manual doc only in 8a |

## Versioning Guidelines
- **0.0.x** — pre-beta; API and bundle layout may change.
- Bump **patch** for fixes; **minor** for user-visible features (front matter editor shipped → would have been `0.1.0` if versioning actively used).
- Git tags `v0.0.x` optional until first GitHub Release.
- Single source: `pyproject.toml` `version` (hatch dynamic version defer — not needed for 0.0.x).

## Release Checklist (maintainer)
1. `make check-all` green on target platform.
2. Update `CHANGELOG.md` (create if missing in PLAN).
3. Bump `version` in `pyproject.toml`.
4. `uv build` — verify wheel contains `atlantis/assets`.
5. (Optional) `make bundle-smoke` on Linux.
6. Tag `vX.Y.Z` and push.
7. (Future) GitHub Release with wheel + Linux tarball attachments.

## CI Integration (deferred)
- **PR CI:** unchanged — `make check` only.
- **Optional job `bundle-smoke`:** `workflow_dispatch`, Linux, `uv sync --group packaging`, PyInstaller build, `dist/atlantis/atlantis --smoke-test`.
- **Do not** add bundle build to every PR (time + cache size).

## Documentation Deliverables (PLAN → BUILD)
- `docs/user-guide/installation.md` — developer vs bundle paths.
- `docs/contributing.md` — release checklist link.
- `README.md` — “Install” section: uv primary; bundle “experimental”.
- ADR 0004 — native bundle (PyInstaller).

## Validation
- [ ] New contributor can install via documented `uv` path.
- [ ] Release checklist exists and matches Makefile targets.
- [ ] No regression to `make check` duration on PRs.

## Next Steps
- Merge rollout sub-tracks into Phase 7/8 PLAN (P8-D docs, P8-E optional CI workflow).
