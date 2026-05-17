# TASK ARCHIVE: Offline Mermaid bundle (Stage 2)

## METADATA
- **Task ID**: offline-mermaid-bundle-2026-05-16
- **Complexity**: Level 3 (Intermediate feature — asset pipeline + renderer refactor + packaging + docs)
- **Task Type**: Vendored Mermaid assets, WebEngine shell refactor, wheel packaging, ADR/docs
- **Archive Date**: 2026-05-16
- **Status**: Complete
- **Related Reflection**: `memory-bank/reflection/reflection-offline-mermaid-bundle-2026-05-16.md`
- **Related Creative**: `memory-bank/creative/creative-renderer-offline-bundle.md`
- **Predecessor Archive**: `memory-bank/archive/archive-coverage-lift-2026-05-16.md`
- **Source deferral**: Phase 4 archive + ADR 0001 Stage 2 follow-up — CDN-first MVP → offline-first default

## SUMMARY

Closed ADR 0001 Stage 2 and the project brief’s offline-first requirement by vendoring **Mermaid 10.9.3** under `atlantis/assets/`, extracting the inline WebEngine HTML shell into `preview_shell.html`, and centralizing asset resolution in `mermaid_assets.py`. `WebEngineMermaidBridge` now loads via `setHtml(html, baseUrl=file://…/preview/)` with a relative vendor script. **Default runtime is offline**; `ATLANTIS_USE_MERMAID_CDN=1` restores the jsDelivr URL for debugging.

Public bridge API unchanged. Final gate (Linux): **47 passed, 1 skipped**; **80 %** coverage held; wheel includes `mermaid.min.js` (~3.3 MB).

## REQUIREMENTS

1. Commit vendored `mermaid.min.js` pinned to **10.9.3** matching `MERMAID_VERSION`.
2. Preview works without network when `ATLANTIS_USE_MERMAID_CDN` is unset.
3. CDN fallback via env for emergency/debug use.
4. Package assets in wheel (`hatch` `force-include`).
5. Asset + bridge unit tests; no default-suite regressions.
6. ADR 0003 + user docs; mkdocs strict build green.
7. Do not change `WebEngineMermaidBridge` public API or main-window render flow.

## IMPLEMENTATION

### OB-A — Asset layout + vendoring
- `atlantis/assets/__init__.py`, `preview/preview_shell.html`, `vendor/mermaid/mermaid.min.js`, `vendor/mermaid/VERSION`
- `pyproject.toml`: `[tool.hatch.build.targets.wheel.force-include]` for `atlantis/assets`
- `scripts/fetch_mermaid_vendor.py` — idempotent download from jsDelivr

### OB-B — Asset resolution (`atlantis/renderer/mermaid_assets.py`)
- `MERMAID_VERSION`, `MERMAID_CDN`, `MERMAID_VENDOR_RELATIVE`
- `use_mermaid_cdn()`, `mermaid_script_src()`, `preview_shell_template()`, `mermaid_version_file()`
- `PreviewAssetSession` — `ExitStack` + `importlib.resources.as_file` for `file://` base URL

### OB-C — Bridge + shell refactor
- Template placeholders `{{MERMAID_SCRIPT_SRC}}`, `{{THEME_JSON}}`
- `webengine_bridge.py` uses `PreviewAssetSession`, loads template, re-exports version constants
- `cdn_url` constructor param retained for tests

### OB-D — Tooling
- `scripts/tech_validation_mermaid_webengine.py` — `--cdn` flag; shared `mermaid_assets` imports
- Upgrade path documented in `docs/user-guide/renderer.md`

### OB-E — Tests
- **New**: `tests/test_mermaid_assets.py` (5 tests — vendor size, VERSION, local/CDN src, placeholders)
- **Updated**: `tests/test_webengine_bridge_unit.py` (local script, `file://` base, CDN override)

### OB-F — Docs + ADR
- **New**: `docs/adr/0003-mermaid-offline-bundle.md`
- **Updated**: ADR 0001 supersession note, `renderer.md`, `troubleshooting.md`, `mkdocs.yml` nav, `memory-bank/techContext.md`

### Files touched

| Action | Path |
|--------|------|
| Add | `atlantis/assets/**`, `atlantis/renderer/mermaid_assets.py`, `scripts/fetch_mermaid_vendor.py`, `tests/test_mermaid_assets.py`, `docs/adr/0003-mermaid-offline-bundle.md` |
| Modify | `webengine_bridge.py`, `pyproject.toml`, `tests/test_webengine_bridge_unit.py`, `docs/user-guide/{renderer,troubleshooting}.md`, `docs/adr/0001-mermaid-cdn-mvp.md`, `mkdocs.yml`, `scripts/tech_validation_mermaid_webengine.py`, `memory-bank/techContext.md` |

## TESTING

| Command | Result |
|---------|--------|
| `uv run ruff format --check .` | PASS (38 files) |
| `uv run ruff check .` | PASS |
| `uv run pytest -q` | **47 passed, 1 skipped** |
| `uv run pytest --cov=atlantis -q` | **80 %** total (`mermaid_assets` 97 %, `webengine_bridge` 94 %) |
| `uv run mkdocs build --strict` | PASS |
| `uv build` + `unzip -l dist/*.whl \| grep mermaid` | Vendored JS in wheel |

## EXIT CRITERIA — FINAL STATE

- [x] Vendored Mermaid 10.9.3 committed; VERSION matches constant
- [x] Offline default; `ATLANTIS_USE_MERMAID_CDN=1` restores CDN
- [x] Wheel packages assets
- [x] `test_mermaid_assets.py` + updated bridge tests pass
- [x] 47 passed, 1 skipped (up from 39 baseline)
- [x] mkdocs strict + ADR 0003 in nav
- [x] Troubleshooting no longer CDN-only

## LESSONS LEARNED

- Creative doc (Option 1 HTML shell) mapped 1:1 to implementation — no rework.
- `importlib.resources.as_file` is required when WebEngine needs real filesystem paths from packaged wheels.
- Env-gated CDN fallback is simpler and clearer than runtime auto-detect.
- Sequencing after coverage lift (bridge unit tests) made offline migration low-risk.
- `file://` base validated on Linux via units; macOS pin host still benefits from opt-in WebEngine smoke.

## DEFERRALS & FOLLOW-UPS

- **Optional**: interactive offline PoC on macOS 12 with network disabled (`ATLANTIS_WEBENGINE_TESTS=1`).
- **Optional**: subprocess wheel-inspect test in CI; HTML template sanity check in tests.
- **Structured logging** for `atlantis.renderer` (bridge + asset resolution).
- **Qt typing cleanup** + promote mypy CI/pre-commit to blocking.
- **`FileSession` refactor**, menu-driven front matter, nox/Makefile, Phase 7/8.
- **Git LFS** only if repo policy objects to ~3 MB vendored blob.

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-offline-mermaid-bundle-2026-05-16.md`
- Creative: `memory-bank/creative/creative-renderer-offline-bundle.md`
- ADR: `docs/adr/0003-mermaid-offline-bundle.md` (supersedes CDN-default in ADR 0001)
- Resolver: `atlantis/renderer/mermaid_assets.py`
- Bridge: `atlantis/renderer/webengine_bridge.py`
- Fetch script: `scripts/fetch_mermaid_vendor.py`
- Tests: `tests/test_mermaid_assets.py`, `tests/test_webengine_bridge_unit.py`
