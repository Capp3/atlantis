# Task Reflection: Offline Mermaid bundle (2026-05-16)

## Summary

Level 3 workstream closing ADR 0001 Stage 2 and the project brief’s offline-first requirement. Vendored **Mermaid 10.9.3** under `atlantis/assets/`, extracted the inline WebEngine HTML shell into `preview_shell.html`, centralized path/script resolution in `mermaid_assets.py`, and refactored `WebEngineMermaidBridge` to load via `setHtml(..., baseUrl=file://…/preview/)` with a relative vendor script. **Default runtime is offline**; `ATLANTIS_USE_MERMAID_CDN=1` restores the jsDelivr URL.

Final gate (Linux): `ruff format --check` + `ruff check` clean; **47 passed, 1 skipped**; coverage **80 %** held (`mermaid_assets` 97 %, `webengine_bridge` 94 %); `mkdocs build --strict` green; wheel contains `mermaid.min.js` (~3.3 MB).

## What Went Well

- **Creative phase paid off without rework.** `creative-renderer-offline-bundle.md` (Option 1: HTML shell + manual render) mapped directly to OB-A–F; no new `/creative` cycle was needed.
- **OB-A→F build order was stable.** Asset tree and hatch `force-include` landed first; resolver module unblocked bridge refactor, tests, and tech validation in one pass.
- **`PreviewAssetSession` + `importlib.resources.as_file` solved the zip-install problem cleanly.** `ExitStack` keeps extracted preview (and implied vendor sibling paths) alive for the bridge lifetime — the right pattern for wheels without mutating install trees.
- **Public bridge API unchanged.** `WebEngineMermaidBridge`, `BridgeRenderResult`, QWebChannel wiring, debounce/timeout behavior, and `MainWindow` flow were preserved; `cdn_url` remains for tests.
- **Deterministic unit tests without network or display.** `test_mermaid_assets.py` asserts vendor size, VERSION pin, placeholders, and env-driven CDN toggle; bridge units assert local `src`, `file://` base URL, and CDN override.
- **ADR 0003 + doc sweep closed the policy loop.** Runtime default, env fallback, upgrade path (`fetch_mermaid_vendor.py`), and supersession note on ADR 0001 are documented for contributors and future upgrades.

## Challenges Encountered

- **Large binary in git (~3.3 MB).** Accepted per plan; wheel size grows accordingly. Fetch script gives maintainers a repeatable upgrade path.
- **`file://` base URL is platform-sensitive.** Plan flagged this early; Linux VAN host validated via unit tests (`base_url` scheme/path). Full cross-platform PoC (macOS pin host) still relies on opt-in WebEngine smoke — not re-run in default CI.
- **Plan named `assets.py`; shipped `mermaid_assets.py`.** Minor naming drift; re-exports from `webengine_bridge` keep import sites stable.
- **Template typo during extraction.** `preview_shell.html` had a malformed closing tag caught during BUILD — caught before gate, not by tests (structural HTML not asserted).
- **Ruff on maintainer scripts.** `urlretrieve` triggered S310; mid-file imports in tech validation triggered E402 — fixed with `urlopen` + top-level imports.

## Solutions Applied

- `PreviewAssetSession` holds `as_file` context for `atlantis.assets.preview` and exposes `QUrl.fromLocalFile(preview_dir/)` as `base_url`.
- Template placeholders `{{MERMAID_SCRIPT_SRC}}` and `{{THEME_JSON}}` with `json.dumps(theme)` on the Python side for safe injection.
- `mermaid_script_src(use_cdn=…)` centralizes local relative path vs CDN; env `ATLANTIS_USE_MERMAID_CDN` with truthy parsing (`1`, `true`, `yes`).
- Hatch `[tool.hatch.build.targets.wheel.force-include]` for the entire `atlantis/assets` tree.
- `scripts/fetch_mermaid_vendor.py` for idempotent vendor refresh; tech validation `--cdn` flag aligned with production.

## Lessons Learned

- **Deferring offline bundle until after bridge unit tests (coverage lift) was the right sequence.** `_FakePage` tests could be updated for local `src` and `file://` base without first building a fragile CDN-dependent suite.
- **`as_file` is required whenever WebEngine needs real filesystem paths from packaged resources** — `Traversable.read_bytes()` alone is insufficient for `QUrl.fromLocalFile` and relative script resolution.
- **Keep version pin in one module (`mermaid_assets`) and mirror in `VERSION` + tests** — avoids drift between constant, vendored file, and ADR.
- **Env-gated CDN fallback is cheaper than runtime auto-detect** and matches ADR 0003 (“explicit opt-in for debugging”).
- **Asset layout (`preview/` sibling to `vendor/`) makes relative `../vendor/mermaid/…` predictable** regardless of install layout once base URL points at `preview/`.

## Process Improvements

- Run `uv build && unzip -l dist/*.whl | grep mermaid` once per asset pipeline change — catches hatch misconfiguration faster than runtime-only tests.
- Add a lightweight HTML sanity check (e.g. balanced tags or `grep` for `</div>`) on `preview_shell.html` if template edits become frequent.
- For Level 3 asset work, schedule **one interactive offline PoC** (tech validation or app with network disabled) on macOS pin host before `/archive`, even when Linux unit gates pass.

## Technical Improvements

- **Optional:** subprocess wheel-inspect test in CI (plan listed as optional; file-exists + size tests used instead).
- **Optional:** extend opt-in WebEngine smoke to assert offline render without CDN on macOS CI (`macos-smoke` workflow_dispatch).
- **Follow-up:** structured logging for `atlantis.renderer` (bridge + asset resolution failures).
- **Follow-up:** consider Git LFS only if repo policy objects to ~3 MB blobs in history.
- **Docs:** `getting-started.md` already describes WebEngine preview generically; renderer/troubleshooting carry offline-default detail — no gap found at reflect time.

## Plan vs. Actual

| Plan item | Actual |
|-----------|--------|
| Module `atlantis/renderer/assets.py` | **`mermaid_assets.py`** (same responsibilities) |
| `MERMAID_VERSION` in `webengine_bridge.py` | **Canonical in `mermaid_assets.py`**, re-exported from bridge |
| Synthetic `https://atlantis.local` base if `file://` breaks | **`file://` works on Linux**; no synthetic fallback needed |
| `getting-started.md` CDN/offline note | **Renderer + troubleshooting + ADR** updated; getting-started unchanged (acceptable) |
| 39+ tests, 1 skipped | **47 passed**, 1 skipped (+8) |
| Coverage no regression | **80 %** maintained |
| Wheel includes vendor JS | **Verified** via `uv build` + `unzip -l` |
| Offline PoC with network disabled | **Unit-level validation**; full interactive PoC deferred to opt-in smoke / manual |

## Metrics

- New production modules/files: `atlantis/assets/**`, `mermaid_assets.py`, `preview_shell.html`, `fetch_mermaid_vendor.py`, ADR 0003
- Vendored asset size: **~3.3 MB** (`mermaid.min.js`)
- Tests added/updated: **`test_mermaid_assets.py`** (5 tests) + bridge unit updates
- Production API surface: **unchanged** (bridge constructor + signals)
- Default test suite: **47 passed, 1 skipped**; coverage **80 %**

## Next Steps

- Run **`/archive`** to capture the milestone and reset active task.
- Backlog (unchanged priority hints): Qt typing + mypy blocking, structured renderer logging, `FileSession` refactor, menu-driven front matter, nox/Makefile, Phase 7/8.
- Optional: manual or `ATLANTIS_WEBENGINE_TESTS=1` smoke on macOS 12 with `ATLANTIS_USE_MERMAID_CDN` unset to confirm `file://` on primary release target.
