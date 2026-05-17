# Troubleshooting

Common issues and how to resolve them.

## Preview is blank

1. Confirm the vendored bundle exists: `atlantis/assets/vendor/mermaid/mermaid.min.js` (run `uv run python scripts/fetch_mermaid_vendor.py` after clone if missing).
2. Run with verbose logging: `uv run atlantis --log-level DEBUG`.
3. In the log file or stderr, search for renderer events: `event=shell_load_failed` (WebEngine shell did not load), `event=render_error` (Mermaid rejected the source), or missing `event=shell_install` (bridge never initialized).
4. Run the standalone PoC: `uv run python scripts/tech_validation_mermaid_webengine.py`.
5. If you set `ATLANTIS_USE_MERMAID_CDN=1`, confirm internet access to `cdn.jsdelivr.net`.

## `mermaid is not defined`

Usually means Mermaid JS did not load. For the **default offline** path, check that the vendored file is present and readable. If using `ATLANTIS_USE_MERMAID_CDN=1`, a firewall or captive portal blocking jsDelivr produces the same symptom. Increase log verbosity (`--log-level DEBUG`) and check JS console output from the page's `javaScriptConsoleMessage` override.

## App refuses to render on macOS 12

Keep `PyQt6` and `PyQt6-WebEngine` pinned `< 6.10` in `pyproject.toml`. Newer wheels require macOS 13+. ADR [0002 — PyQt6 pin for macOS 12](../adr/0002-pyqt6-pin-macos-12.md) captures the full reasoning.

## Render takes longer than expected

A 15 s hard timeout is enforced. The status bar surfaces an explicit `Render timed out` message when it trips. At DEBUG or WARNING you should see `event=render_timeout` from logger `atlantis.renderer.bridge`. Common causes:

- Very large diagrams (try splitting into multiple files).
- Missing or corrupt vendored `mermaid.min.js` (re-run `scripts/fetch_mermaid_vendor.py`).
- CDN fallback enabled but network blocked (`ATLANTIS_USE_MERMAID_CDN=1`).
- A heavy front-matter parsing path — switch to TOML and verify in the [Front matter guide](front-matter.md).

## Opt-in WebEngine pytest (`@pytest.mark.webengine`)

The default suite runs headless (`QT_QPA_PLATFORM=offscreen`, `ATLANTIS_HEADLESS=1` via `tests/conftest.py`). The WebEngine smoke test boots a real `QWebEngineView` and is **skipped** unless you opt in:

```bash
ATLANTIS_WEBENGINE_TESTS=1 uv run pytest -m webengine -q
```

### When to run it

- After changing `atlantis/renderer/webengine_bridge.py` or the preview HTML shell.
- On a **desktop session** with a working Qt WebEngine stack (local macOS or Linux with a display server).

### Environment requirements

| Requirement | Notes |
|-------------|--------|
| Display / compositor | Needs a real GUI session. Pure SSH without X11/Wayland forwarding usually fails. |
| `PyQt6-WebEngine` | Installed via `uv sync` (declared in `pyproject.toml`). |
| Mermaid assets | Default: vendored `mermaid.min.js` (offline). CDN only when `ATLANTIS_USE_MERMAID_CDN=1`. |
| macOS 12 | Keep `PyQt6` / `PyQt6-WebEngine` `< 6.10` (see ADR 0002). |

### CI

- **Pull requests**: docs are built in `.github/workflows/docs.yml` (`mkdocs build --strict`). Lint/tests run in `ci.yml`; there is no redundant docs job in CI.
- **macOS WebEngine smoke**: opt-in only — run **Actions → CI → macOS WebEngine smoke (opt-in)** (`workflow_dispatch` on `ci.yml`). Requires a macOS runner with WebEngine; not part of the default PR gate.
- **Linux bundle build**: opt-in only — run **Actions → Bundle Linux (experimental)** (`workflow_dispatch` on `bundle.yml`). Builds `dist/atlantis/` via PyInstaller and uploads a large artifact; not part of the PR gate. See [Installation → CI-built Linux bundle](installation.md#ci-built-linux-bundle).

### Common failures

- **Skipped immediately**: `ATLANTIS_WEBENGINE_TESTS` is unset (expected on CI and local default runs).
- **Timeout / empty result**: CDN blocked, no display server, or WebEngine failed to initialize — try `uv run python scripts/tech_validation_mermaid_webengine.py` first.
- **Conflicts with headless env**: the smoke test clears `ATLANTIS_HEADLESS` for its duration; do not set headless flags in the same shell before opting in.

## Tests fail with `QApplication` lifecycle errors

The shared `tests/conftest.py` provides a session-scoped `qapp` fixture and autouses it; individual test modules should **not** create their own `QApplication`. If you see lifecycle errors after adding a new test, the most likely cause is re-creating Qt singletons inside the test body — switch to the fixture instead.

## Pre-commit hook versions drift from CI

`.pre-commit-config.yaml` pins the same `ruff` version range that the project uses in `pyproject.toml`. If you see a difference, bump both files in the same commit. The contributing guide records the policy in detail.

## Logging

Atlantis honors `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}` (default `WARNING`) and the `ATLANTIS_LOG_LEVEL` env var. Logs are written to the platform-standard app-data path and also streamed to stderr.
