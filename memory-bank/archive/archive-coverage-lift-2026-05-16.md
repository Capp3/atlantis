# TASK ARCHIVE: Coverage lift

## METADATA
- **Task ID**: coverage-lift-2026-05-16
- **Complexity**: Level 2 (tests only; no user-visible behavior change)
- **Task Type**: Test coverage for CLI entrypoint, logging config, WebEngine bridge
- **Archive Date**: 2026-05-16
- **Status**: Complete
- **Related Reflection**: `memory-bank/reflection/reflection-coverage-lift-2026-05-16.md`
- **Predecessor Archive**: `memory-bank/archive/archive-ci-docs-hygiene-2026-05-16.md`
- **Source deferral**: Phase 5 archive — lift coverage from 69 % (`main.py`, `logging.py`, WebEngine opt-in path)

## SUMMARY

Closed the Phase 5 coverage deferral by adding **15 tests** in three sub-tracks (CL-T → LG-T → WB-T). Project coverage rose **69 % → 80 %**. Target modules: `main.py` **100 %**, `logging.py` **100 %**, `webengine_bridge.py` **92 %** (default suite with mocked page; opt-in smoke unchanged). One production change: `force=True` on `logging.basicConfig` for reliable re-configuration in tests and on re-entry.

## REQUIREMENTS

1. Add tests for `atlantis/main.py` (CLI, `--log-level`, smoke path) — was 0 %.
2. Add tests for `atlantis/core/logging.py` — was 0 %.
3. Improve `atlantis/renderer/webengine_bridge.py` coverage without requiring opt-in WebEngine in default CI — was 35 %.
4. Project total ≥ **75 %** interim target; no new dependencies.
5. Default suite remains **1 skipped** (webengine smoke).

## IMPLEMENTATION

### CL-T — `tests/test_main_cli.py` (7 tests)
- `build_parser()` — `--smoke-test`, `--log-level` choices.
- `_resolve_log_level()` — CLI overrides env; env default; invalid env → `WARNING`.
- `main(["--smoke-test"])` in-process (headless).
- `main([])` with stubbed `create_application` / `MainWindow` and `app.exec` return code.

### LG-T — `tests/test_logging_config.py` (2 tests)
- `default_log_path()` with `monkeypatch` on `atlantis.core.logging.QStandardPaths.writableLocation`.
- `configure_logging(DEBUG)` writes to file and sets root level (handler flush before assert).

### WB-T — `tests/test_webengine_bridge_unit.py` (6 tests)
- `_FakePage(QObject)` with `loadFinished = pyqtSignal(bool)`.
- `BridgeRenderResult`, shell HTML / theme, pending render + dispatch, load failure, rendered success, timeout (`qtbot.wait`).

### Shared / production
- **`tests/conftest.py`**: `reset_root_logging` fixture (save/restore root handlers).
- **`atlantis/core/logging.py`**: `logging.basicConfig(..., force=True)`.

### Files touched

| File | Change |
|------|--------|
| `tests/test_main_cli.py` | New |
| `tests/test_logging_config.py` | New |
| `tests/test_webengine_bridge_unit.py` | New |
| `tests/conftest.py` | `reset_root_logging` fixture |
| `atlantis/core/logging.py` | `force=True` on `basicConfig` |

## TESTING

| Command | Result |
|---------|--------|
| `uv run ruff format --check .` | PASS (34 files) |
| `uv run ruff check .` | PASS |
| `uv run pytest -q` | **39 passed, 1 skipped** |
| `uv run pytest --cov=atlantis --cov-report=term-missing -q` | **80 %** total |

| Module | Before | After |
|--------|--------|-------|
| `main.py` | 0 % | **100 %** |
| `logging.py` | 0 % | **100 %** |
| `webengine_bridge.py` | 35 % | **92 %** |
| **Total** | 69 % | **80 %** |

## EXIT CRITERIA — FINAL STATE

- [x] Three new test modules exist.
- [x] Module coverage targets met or exceeded.
- [x] Project ≥ 75 % (achieved 80 %).
- [x] 39 passed, 1 skipped; ruff gates clean.

## LESSONS LEARNED

- In-process `main(argv)` attributes coverage to `main.py`; subprocess smoke stays as integration guard.
- Patch `QStandardPaths` on `atlantis.core.logging`, not only in the test module.
- `basicConfig` + pytest needs `force=True` and handler-reset fixture.
- QObject fake with real `pyqtSignal` exercises bridge logic without `QWebEngineView`.
- Remaining bridge gaps (`report_svg` / `report_error` slots, immediate dispatch when page ready) need opt-in WebEngine smoke or direct slot tests.

## DEFERRALS & FOLLOW-UPS

- **Codecov 90 % project target** — still aspirational; next deltas likely UI modules (`main_window`, editors); pair with Qt typing + mypy promotion.
- **Optional**: direct `_BridgeChannel` slot tests for 100 % bridge coverage without WebEngine.
- **Optional**: update `docs/contributing.md` coverage baseline note (69 % → 80 %).
- **Unchanged backlog**: structured logging, offline bundle, `FileSession`, front matter editor, nox/Makefile, Phase 7/8.

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-coverage-lift-2026-05-16.md`
- Plan (ephemeral, archived here): `memory-bank/tasks.md` status section
- Phase 5 archive (source deferral): `memory-bank/archive/archive-build-phase5-2026-05-11.md`
- Opt-in smoke: `tests/test_webengine_bridge_smoke.py`
- Harness: `tests/conftest.py`
