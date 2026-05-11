# Troubleshooting

Common issues and how to resolve them.

## Preview is blank

1. Confirm internet access to `cdn.jsdelivr.net`. The MVP loads Mermaid 10.9.3 from CDN; the offline bundle is post-MVP.
2. Run with verbose logging: `uv run atlantis --log-level DEBUG`.
3. Run the standalone PoC to isolate the renderer from the app: `uv run python scripts/tech_validation_mermaid_webengine.py`.

## `mermaid is not defined`

Indicates the CDN load failed (firewall, captive portal, offline). Increase log verbosity (`--log-level DEBUG`) and check the JS console output captured by the page's `javaScriptConsoleMessage` override. Usually resolved by restoring network access.

## App refuses to render on macOS 12

Keep `PyQt6` and `PyQt6-WebEngine` pinned `< 6.10` in `pyproject.toml`. Newer wheels require macOS 13+. ADR [0002 — PyQt6 pin for macOS 12](../adr/0002-pyqt6-pin-macos-12.md) captures the full reasoning.

## Render takes longer than expected

A 15 s hard timeout is enforced. The status bar surfaces an explicit `Render timed out` message when it trips. Common causes:

- Very large diagrams (try splitting into multiple files).
- A slow or blocked CDN response (offline mode is a deferred follow-up).
- A heavy front-matter parsing path — switch to TOML and verify in the [Front matter guide](front-matter.md).

## Tests fail with `QApplication` lifecycle errors

The shared `tests/conftest.py` provides a session-scoped `qapp` fixture and autouses it; individual test modules should **not** create their own `QApplication`. If you see lifecycle errors after adding a new test, the most likely cause is re-creating Qt singletons inside the test body — switch to the fixture instead.

## Pre-commit hook versions drift from CI

`.pre-commit-config.yaml` pins the same `ruff` version range that the project uses in `pyproject.toml`. If you see a difference, bump both files in the same commit. The contributing guide records the policy in detail.

## Logging

Atlantis honors `--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}` (default `WARNING`) and the `ATLANTIS_LOG_LEVEL` env var. Logs are written to the platform-standard app-data path and also streamed to stderr.
