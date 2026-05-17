# TASK ARCHIVE: Structured logging

## METADATA
- **Task ID**: structured-logging-2026-05-16
- **Complexity**: Level 2 (observability — renderer package only)
- **Task Type**: Structured stdlib logging for WebEngine Mermaid bridge and assets
- **Archive Date**: 2026-05-16
- **Status**: Complete
- **Related Reflection**: `memory-bank/reflection/reflection-structured-logging-2026-05-16.md`
- **Predecessor Archive**: `memory-bank/archive/archive-offline-mermaid-bundle-2026-05-16.md`
- **Source deferral**: Phase 4 reflection — logger name `atlantis.renderer.bridge`; log dock deferred

## SUMMARY

Closed the Phase 4 structured-logging deferral by adding **`atlantis/renderer/logging_events.py`** with grep-friendly `event=…` log lines, instrumenting **`webengine_bridge.py`** and **`mermaid_assets.py`**, and shipping **9 caplog tests**. Uses existing `--log-level` / `ATLANTIS_LOG_LEVEL`; no structlog, no log dock UI, no bridge API changes. Default level remains WARNING; DEBUG exposes full render lifecycle.

## REQUIREMENTS

1. Logger **`atlantis.renderer.bridge`** for all bridge events (not module `__name__`).
2. Logger **`atlantis.renderer.assets`** for asset session / CDN selection.
3. Events: shell install/load, dispatch, success, JS error, timeout — with `event=` prefix.
4. Never log full diagram source at INFO+; use `source_chars` only.
5. Stdlib `logging` only; no global formatter change.
6. `tests/test_renderer_logging.py` + default suite green.

## IMPLEMENTATION

### SL-A — `atlantis/renderer/logging_events.py`
- `BRIDGE_LOGGER`, `ASSETS_LOGGER`
- `log_event(logger, level, event, **fields)` — sorted `key=value` message + `extra` dict
- `truncate_error()`, `mermaid_src_label()` (`local` / `cdn`)

### SL-B — `webengine_bridge.py`
| Event | Level |
|-------|-------|
| `shell_install` | DEBUG |
| `shell_load_failed` | WARNING |
| `render_dispatch` | DEBUG |
| `render_success` | INFO |
| `render_error` | WARNING |
| `render_timeout` | WARNING |

### SL-C — `mermaid_assets.py`
- `assets_session_open` (DEBUG, `preview_dir` basename)
- `mermaid_src_cdn` (DEBUG when CDN env/path selected)

### SL-D — `tests/test_renderer_logging.py` (9 tests)
- `log_event` formatting, truncate/mermaid_src helpers, logger name
- caplog: shell load failed, render success/error/timeout, shell_install

### SL-E — Docs
- `docs/user-guide/renderer.md` — *Diagnostic logging* subsection
- `docs/user-guide/troubleshooting.md` — `event=` hints for blank preview / timeout
- `memory-bank/techContext.md` — renderer logger line

### Files touched

| File | Change |
|------|--------|
| `atlantis/renderer/logging_events.py` | New |
| `tests/test_renderer_logging.py` | New |
| `atlantis/renderer/webengine_bridge.py` | Instrumented |
| `atlantis/renderer/mermaid_assets.py` | Instrumented |
| `docs/user-guide/renderer.md` | Diagnostic logging |
| `docs/user-guide/troubleshooting.md` | Event grep hints |
| `memory-bank/techContext.md` | Logger note |

## TESTING

| Command | Result |
|---------|--------|
| `uv run ruff format --check .` | PASS (40 files) |
| `uv run ruff check .` | PASS |
| `uv run pytest -q` | **56 passed, 1 skipped** (+9) |

## EXIT CRITERIA — FINAL STATE

- [x] `atlantis.renderer.bridge` used for bridge events
- [x] shell_load_failed, render_success, render_error, render_timeout logged
- [x] No full source at INFO+
- [x] 56 passed, 1 skipped; ruff clean
- [x] Docs updated

## LESSONS LEARNED

- Message-encoded `event=…` fields suffice without structlog for desktop support workflows.
- Caplog must target explicit logger names when aliases differ from `__name__`.
- Instrument state transitions, not raw Mermaid source.
- Pairs naturally after offline bundle + bridge unit test harness.

## DEFERRALS & FOLLOW-UPS

- **Log dock / QDockWidget** — consume `extra=` or bridge logger when UI resumes.
- **`ATLANTIS_LOG_JSON`** — optional future formatter.
- **`preview.py` headless** — optional `event=preview_headless` at DEBUG.
- **Optional:** single choke-point for `render_dispatch` to avoid duplicate DEBUG lines.
- **Backlog:** Qt typing + mypy blocking, `FileSession` refactor, front matter editor, nox/Makefile, Phase 7/8.

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-structured-logging-2026-05-16.md`
- Phase 4 source: `memory-bank/reflection/reflection-build-phase4-2026-05-11.md`
- Helper: `atlantis/renderer/logging_events.py`
- Bridge: `atlantis/renderer/webengine_bridge.py`
- Tests: `tests/test_renderer_logging.py`
