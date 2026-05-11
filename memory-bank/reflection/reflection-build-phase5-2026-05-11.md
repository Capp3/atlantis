# Task Reflection: Atlantis BUILD Phase 5 — Cross-cutting docs / tests / formatting / CI/CD / workspace

## Summary
Phase 5 closed the engineering surface around the (already stable) Phase 1-4 app code without touching any user-facing behavior. Five sub-tracks were shipped in the planned order (P5-T → P5-C → P5-F → P5-D → P5-W):

- **P5-T**: shared pytest harness (`tests/conftest.py`), opt-in `webengine` marker, coverage wiring (`pytest-cov`, `[tool.coverage.report].exclude_also`), one opt-in WebEngine smoke test.
- **P5-C**: new `.github/workflows/ci.yml` (lint+tests+coverage upload, non-blocking type-check, strict docs build, opt-in `macos-13` smoke) plus README badges and Quickstart.
- **P5-F**: `.pre-commit-config.yaml` (pre-commit-hooks v5 + ruff-pre-commit v0.15.12), mypy hook deferred, new `docs/contributing.md`.
- **P5-D**: `mkdocs.yml` switched to `material` + `mkdocstrings.python`, real nav (Home / Getting Started / User Guide / Reference / ADRs / Contributing), split `docs/index.md`, two ADRs.
- **P5-W**: VS Code tasks **Coverage**, **Pre-commit (all files)**, **Build Docs (strict)**.

Final gate: `ruff format --check` clean, `ruff check` clean, **21 passed + 1 skipped** (opt-in WebEngine), coverage **69%**, `mkdocs build --strict` green.

## What Went Well
- **PLAN refinement set a clean execution order.** P5-T first meant CI had a clear command surface to pin against; P5-C immediately exercised that surface; P5-F kept local + CI parity; P5-D had a stable nav to extend; P5-W consumed the finished commands. Zero rework between tracks.
- **Existing assets reused, not replaced.** `.github/workflows/docs.yml`, `codecov.yaml`, `.editorconfig`, `.vscode/{settings,extensions}.json`, and `pyproject.toml` dev deps were extended rather than rewritten — Phase 5 added one workflow, one hook config, and three VS Code tasks, then everything else slotted into existing files.
- **Shared harness collapsed test boilerplate.** Each Qt-touching test module previously carried a 5-line `QT_QPA_PLATFORM` / `ATLANTIS_HEADLESS` / `_APP = create_application()` header. After `tests/conftest.py` (env vars at import time + autouse session `qapp`), three test modules shed those headers cleanly and the 21-test default suite still runs in ~2 s.
- **`--strict-markers` + `pytest_collection_modifyitems` is the right shape.** Registering the `webengine` marker in `pyproject.toml` (under `[tool.pytest.ini_options]`) caught a typo immediately; the collection hook then skips marked tests unless `ATLANTIS_WEBENGINE_TESTS=1`, so the smoke test ships visible but inert by default.
- **mkdocstrings did the heavy lifting for the API reference.** A one-liner page (`::: atlantis` with `show_submodules: true`) produced a ~3.5k-line `site/reference/api/index.html` covering the entire package. No hand-rolled reference pages required.
- **CI parity discipline.** Pinning `ruff-pre-commit` to **v0.15.12** to match the dev-dep version means pre-commit and the CI lint job enforce identical results — no "works locally, fails in CI" surprise.
- **Material theme + `mkdocs build --strict` was a free quality upgrade.** Already declared as a dev dep, the switch from `readthedocs` produced a noticeably better navigation experience and exercised the `nav:` correctness on every CI run.
- **`uv add --dev pytest-cov` was friction-free.** Single command added the dep, updated the lock, and the gate went green on the next run — no manual `pyproject.toml` patching.

## Challenges
- **Pre-existing format drift in `atlantis/renderer/webengine_bridge.py`**
  - Impact: The first `ruff format --check .` failed because a `0.0 if … else …` expression in `_on_rendered` had been hand-wrapped instead of ruff-formatted (Phase 4 had only run `ruff check`, not `ruff format --check`).
  - Resolution: `uv run ruff format .` reflowed the one expression cleanly.
  - Outcome: Now the CI lint job and the pre-commit hook will both catch drift on every PR. **Net positive** — exactly what Phase 5 was supposed to enable.

- **`pytest-cov` wasn't in dev deps even though `codecov.yaml` was already shipped**
  - Impact: First run of the consolidated gate failed with `unrecognized arguments: --cov=atlantis`.
  - Resolution: `uv add --dev pytest-cov` (pulled in `coverage==7.14.0` + `pytest-cov==7.1.0`).
  - Outcome: Captured as a Lesson — "if a config file exists, the matching plugin should already be a dep". Worth a future check for `.editorconfig`-style orphans.

- **`mkdocs-material --strict` info noise about MkDocs 2.0**
  - Impact: Every build prints a long red-tinted notice. It's INFO-level (not WARNING), so `--strict` exits 0, but it's distracting.
  - Resolution: Left as-is; not blocking. Recorded as a watch item — if Material starts emitting it at WARNING level, we'd need to either silence it or migrate.
  - Outcome: No code change.

- **Orphan `docs/projectbrief.md` page**
  - Impact: First `mkdocs build --strict` flagged it (INFO, not strict-fail) as a page outside `nav:`.
  - Resolution: Added it under **Reference → Project brief** so it surfaces in nav.
  - Outcome: Strict build now produces zero nav-related info messages.

- **WebEngine smoke test had to opt out of headless mode**
  - Impact: The shared `conftest.py` sets `ATLANTIS_HEADLESS=1` at import time, which would short-circuit the real `QWebEngineView` in `tests/test_webengine_bridge_smoke.py`.
  - Resolution: The test pops `ATLANTIS_HEADLESS` from the env after entering the test body (it's guarded by `ATLANTIS_WEBENGINE_TESTS=1` anyway, so it never executes by accident).
  - Outcome: Documented in the test docstring; CI will not exercise it unless the user explicitly dispatches the `macos-smoke` job.

- **mkdocstrings path config**
  - Impact: First mkdocs build emitted no API content because the default `paths=["src"]` doesn't match this project's layout.
  - Resolution: `paths: ["."]` plus `show_submodules: true` in `mkdocs.yml`. (`atlantis/` lives at repo root.)
  - Outcome: 3.5k-line API page generated cleanly.

## Lessons Learned
- **CI-equivalent gates exposed pre-existing drift on day one.** Adding `ruff format --check` to the gate caught one file that had silently regressed during Phase 4 — strong evidence that Phase 5 was overdue.
- **A registered marker + collection hook beats env-only gating.** `@pytest.mark.webengine` plus `ATLANTIS_WEBENGINE_TESTS=1` is a small amount of glue but it's discoverable (`pytest --markers`), enforced (`--strict-markers`), and self-documenting (the marker description shows up in `pyproject.toml`).
- **Pin pre-commit hook versions to the same tag as the dev dep.** Cheap to do once; eliminates an entire class of "ruff says X locally and Y in CI" issues.
- **mypy stays non-blocking until typing cleanup ships.** The Phase 4 carry-over (Qt accessor noise) would have buried real type errors in the diff. Better to keep the job visible and flip it to blocking later than to break PRs immediately.
- **Material theme is the better default for mkdocstrings-heavy projects.** Navigation features (`navigation.sections`, `navigation.expand`, code annotations) significantly improve the API reference's usability.
- **One ADR per non-obvious decision is the right granularity.** ADRs 0001 (CDN MVP) and 0002 (PyQt6 pin) cost ~30 minutes each to write and immediately replace tribal knowledge with discoverable docs. The contributing guide cross-links them, so new contributors can find rationale without digging through `memory-bank/creative/`.
- **`uv` makes "add a tool, update CI, document it" a 3-command flow.** No friction added a new dep, lock and CI workflow; this is the right tooling baseline.

## Process Improvements
- **Bring `ruff format --check` into every phase's gate from now on.** Phase 4 only enforced `ruff check`; Phase 5 caught the drift. Going forward, the canonical local + CI gate is `ruff format --check` + `ruff check` + `pytest -q` (+ `mkdocs build --strict` for any docs-touching change).
- **When a config file lands, the matching plugin should land in the same commit.** `codecov.yaml` had been in the repo for several phases without `pytest-cov` being a dev dep. A small sanity check: "for every YAML config in the repo, is there a hook actually consuming it?" would have caught this earlier.
- **Continue the "extend, don't replace" rule for engineering assets.** Phase 5 wrote one new workflow and added one new pre-commit config; everything else extended an existing file. This kept the diff readable and made the change reviewable as one PR.
- **Per-track exit criteria from PLAN make BUILD verification mechanical.** Phase 5 closed each track with an explicit checklist in `tasks.md`; the final gate just re-ran the commands. Continue this pattern.
- **Defer ADRs to the moment of the decision, not when a future contributor asks.** Capturing CDN and PyQt6 pin decisions while they were still fresh in memory was easy; reconstructing them later from `memory-bank/creative/` and reflections would have been slower and probably less accurate.

## Technical Improvements
- **Flip mypy CI job to blocking once Qt accessor typing cleanup ships.** Today `continue-on-error: true`; the cleanup is already queued from Phase 4. When it lands, remove the flag and add a `mirrors-mypy` pre-commit hook in `.pre-commit-config.yaml` so local + CI stay in lockstep.
- **Lift coverage from 69%.** Largest deltas: `atlantis/main.py` (0% — entrypoint), `atlantis/core/logging.py` (0% — initialization-only), `atlantis/renderer/webengine_bridge.py` (35% — needs the opt-in WebEngine path to cover). Add a CLI-arg test for `--log-level` and an opt-in WebEngine path test against `BridgeRenderResult`.
- **Auto-update `.pre-commit-config.yaml`** via `pre-commit autoupdate` in a quarterly chore PR; pair with a dev-dep bump of `ruff` in `pyproject.toml`.
- **Document the `webengine` marker in the test invocation pattern table.** Once contributors actually run `ATLANTIS_WEBENGINE_TESTS=1 pytest`, capture environment-specific failures (display-server requirements, codec availability) in `docs/user-guide/troubleshooting.md`.
- **Switch the docs CI job to `mkdocs build --strict` only.** Today both the `docs-build` job in `ci.yml` and the existing `docs.yml` build the site; the latter publishes. Keep `docs.yml` for publishes only and consider extracting its build step into the new `ci.yml` to avoid one redundant install.
- **Consider a `Makefile` or `noxfile.py`** as a thin shim around the canonical commands. Today the README, `docs/contributing.md`, `ci.yml`, and VS Code tasks all repeat the same `uv run …` strings. One source of truth would simplify future tooling bumps.

## Plan vs Actual (Phase 5)
- **P5-T (Testing harness)**: Shipped as planned — `conftest.py`, marker registration, opt-in smoke test, coverage wiring. **Plus**: refactored phase 2/3/4 tests to drop duplicate headers in the same change.
- **P5-C (CI/CD)**: Shipped as planned — `ci.yml` jobs `lint-and-test`, `type-check` (non-blocking), `docs-build`, opt-in `macos-smoke`. Codecov action included; gated on `CODECOV_TOKEN` for private-repo compatibility. README badges added.
- **P5-F (Formatting & quality)**: Shipped as planned — `.pre-commit-config.yaml` with hygiene hooks + ruff/ruff-format; mypy hook **intentionally deferred**, documented in `docs/contributing.md`.
- **P5-D (Documentation site)**: Shipped as planned, plus a theme upgrade (`readthedocs` → `material`) since the dep was already present and the experience win was free. Two ADRs as planned (CDN MVP, PyQt6 pin). API reference is single-page mkdocstrings ingestion, as planned.
- **P5-W (Workspace)**: Shipped exactly as planned. `.vscode/extensions.json` reviewed; no additions needed.

## Metrics Snapshot
- Tests: **21 passing, 1 skipped** (opt-in WebEngine). Same default count as Phase 4, **+1 opt-in**.
- Coverage: **69%** (branch+statement). `[tool.coverage.report].exclude_also` filters `if TYPE_CHECKING:`, `pragma: no cover`, `raise NotImplementedError`, and `if __name__ == "__main__":`.
- Files added: **11** (`tests/conftest.py`, `tests/test_webengine_bridge_smoke.py`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `docs/getting-started.md`, `docs/contributing.md`, `docs/user-guide/{editor,renderer,front-matter,examples,troubleshooting}.md`, `docs/reference/{architecture,api}.md`, `docs/adr/0001-mermaid-cdn-mvp.md`, `docs/adr/0002-pyqt6-pin-macos-12.md`).
- Files modified: **8** (`pyproject.toml`, `mkdocs.yml`, `docs/index.md`, `README.md`, `.vscode/tasks.json`, `tests/test_phase{2,3,4_window_polish}.py`, `atlantis/renderer/webengine_bridge.py` for one-line format pass).
- New runtime deps: **0**.
- New dev deps: **1** (`pytest-cov`; pulled `coverage` as transitive).
- New ADRs: **2**.
- New env hooks: **0** (existing `ATLANTIS_WEBENGINE_TESTS`/`ATLANTIS_HEADLESS`/`ATLANTIS_AUTOSAVE_DIR` reused).
- mkdocs strict build: **green** locally and in the new `ci.yml` `docs-build` job.

## Next Steps
- Run `/archive` to capture the Phase 5 milestone (link this reflection, list new files/configs, document coverage baseline + follow-ups).
- Open follow-ups: lift coverage (entrypoint + logging + WebEngine opt-in); promote mypy CI job to blocking after Qt accessor typing cleanup; consider `noxfile.py` for command consolidation; quarterly `pre-commit autoupdate` chore.
- After archive, the active app-code roadmap is back in focus: Phase 4 carry-overs (`FileSession` refactor, structured renderer logging, Stage-2 offline Mermaid bundle, menu-driven front matter edit) are the natural next workstreams.
