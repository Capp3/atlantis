# TASK ARCHIVE: Qt typing cleanup + mypy blocking

## METADATA
- **Task ID**: qt-typing-mypy-2026-05-16
- **Complexity**: Level 2–3 (UI typing + CI/pre-commit promotion; no intended runtime behavior change)
- **Task Type**: PyQt6 stub accessor narrowing; promote mypy to blocking gate
- **Archive Date**: 2026-05-16
- **Status**: Complete
- **Related Reflection**: `memory-bank/reflection/reflection-qt-typing-mypy-2026-05-16.md`
- **Predecessor Archive**: `memory-bank/archive/archive-structured-logging-2026-05-16.md`
- **Source deferral**: Phase 4/5 — chronic Qt stub `Optional` accessors; CI `type-check` job `continue-on-error: true`; pre-commit had no mypy hook

## SUMMARY

Closed the Phase 4/5 mypy deferral by fixing **53 mypy errors in 5 files** (no blanket `# type: ignore`), adding **`atlantis/ui/qt_accessors.py`** to narrow PyQt6 stub optional returns, and promoting **`uv run mypy atlantis`** to a **blocking** CI job and **pre-commit** hook. Renderer/core paths were already clean. Final gate: **0 mypy errors**, **59 passed / 1 skipped** tests (+3 hygiene locks).

## REQUIREMENTS

1. `uv run mypy atlantis` → **0 errors** (baseline: 53 in 5 files).
2. Remove `continue-on-error: true` from CI `type-check` job.
3. Add pre-commit mypy hook matching CI command (`uv run mypy atlantis`).
4. Fix real Qt typing issues — accessors, overrides, QAction stubs — not mass ignores.
5. Update `docs/contributing.md` and `memory-bank/techContext.md` — mypy blocking.
6. Regression tests lock CI/pre-commit invariants.
7. Default suite green; ruff clean; no new dependencies.

## IMPLEMENTATION

### QT-A — `atlantis/ui/qt_accessors.py` (new)

| Function | Purpose |
|----------|---------|
| `require_status_bar(window)` | Narrow `QMainWindow.statusBar()` |
| `require_menu_bar(window)` | Narrow `menuBar()` |
| `require_menu(menu_bar, title)` | Narrow `QMenuBar.addMenu()` (discovered mid-build) |
| `require_text_document(editor)` | Narrow `QPlainTextEdit.document()` |
| `require_qapplication()` | `isinstance` guard on `QApplication.instance()` |

### QT-B — `core/app.py` + `preview.py`

- **`app.py`**: Return existing instance only when `isinstance(app, QApplication)`.
- **`preview.py`**: `TYPE_CHECKING` import for WebEngine; runtime `except ImportError` with `# type: ignore[misc, assignment]`; explicit `RuntimeError` if view class missing (ruff S101).

### QT-C — `editor.py`

- Proper Qt parent/event types (`QWidget`, `QPaintEvent`, `QResizeEvent`, `QTextDocument`).
- `highlightBlock(self, text: str | None)` matches stub.
- `MermaidEditor.text_document()` helper for call sites.

### QT-D/E — `status_bar.py` + `main_window.py`

- Cached `self._status_bar` after `initialize_status_bar`.
- `require_menu_bar` / `require_menu` for menu construction.
- `QAction` + `setCheckable(True)` (not `checkable=` ctor kwarg).
- `require_qapplication()` for palette in preview theme.
- `closeEvent(self, event: QCloseEvent | None)` with None guard.

### QT-F — CI, pre-commit, docs

- **`.github/workflows/ci.yml`**: Removed `continue-on-error` from `type-check`; job renamed **Type check** (blocking).
- **`.pre-commit-config.yaml`**: Local hook `uv run mypy atlantis`, `pass_filenames: false`.
- **`docs/contributing.md`**, **`memory-bank/techContext.md`**: mypy blocking documented.

### QT-G — Tests

- **`tests/test_mypy_gate.py`**: Subprocess `uv run mypy atlantis` expects exit 0.
- **`tests/test_ci_docs_hygiene.py`**: Asserts type-check job blocking + pre-commit mypy hook present.

### Files touched

| File | Change |
|------|--------|
| `atlantis/ui/qt_accessors.py` | New (~51 lines) |
| `atlantis/ui/main_window.py` | Accessors, menus, QAction, closeEvent |
| `atlantis/ui/editor.py` | Event/parent types, text_document |
| `atlantis/ui/status_bar.py` | require_status_bar |
| `atlantis/core/app.py` | isinstance QApplication |
| `atlantis/ui/preview.py` | TYPE_CHECKING WebEngine import |
| `.github/workflows/ci.yml` | Blocking type-check |
| `.pre-commit-config.yaml` | mypy hook |
| `docs/contributing.md` | Blocking mypy |
| `memory-bank/techContext.md` | Blocking mypy |
| `tests/test_mypy_gate.py` | New |
| `tests/test_ci_docs_hygiene.py` | +2 assertions |

## TESTING

| Command | Result |
|---------|--------|
| `uv run mypy atlantis` | **0 errors** (26 source files) |
| `uv run ruff format --check .` | PASS (42 files) |
| `uv run ruff check .` | PASS |
| `uv run pytest -q` | **59 passed, 1 skipped** (+3) |
| `uv run pre-commit run mypy --all-files` | PASS (after hook added) |

## EXIT CRITERIA — FINAL STATE

- [x] Mypy 53 → 0 errors across 5 UI/core files
- [x] CI `type-check` blocking
- [x] Pre-commit mypy hook aligned with CI
- [x] 59 passed, 1 skipped; ruff clean
- [x] Contributing + techContext updated
- [x] Hygiene tests prevent silent regression

## LESSONS LEARNED

- PyQt stub optional returns (`statusBar`, `menuBar`, `addMenu`, `document`) dominate UI mypy noise — plan all accessors at PLAN time.
- Centralized `require_*` module beats scattered `cast()`; add helpers when a second optional pattern appears.
- Promote CI gates only after subprocess mypy passes; lock with `test_mypy_gate.py` + YAML hygiene tests.
- Strict mypy on Qt UI is achievable without `pyqt6-stubs` when signatures and narrowing are correct.
- `QAction(checkable=True)` invalid in stubs — use `setCheckable(True)`.
- Ruff S101/TRY004 affect typing guards — prefer explicit `RuntimeError` / `TypeError` over `assert`.

## DEFERRALS & FOLLOW-UPS

- **Optional:** unit tests for `qt_accessors` raise paths (low priority; mypy gate covers integration).
- **Optional:** `pyqt6-stubs` only if PyQt upgrades reintroduce mass errors.
- **Backlog:** `FileSession` refactor (may shrink `main_window.py` typing surface).
- **Backlog:** command consolidation (nox/Makefile) — include `mypy` session.
- **Backlog:** menu-driven front matter edit; Phase 7/8.
- **Removed deferral:** ~~Promote mypy CI to blocking~~ — **done**.

## REFERENCES

- Reflection: `memory-bank/reflection/reflection-qt-typing-mypy-2026-05-16.md`
- Plan + BUILD detail (historical): captured in this archive; was in `memory-bank/tasks.md` before reset
- Helpers: `atlantis/ui/qt_accessors.py`
- Tests: `tests/test_mypy_gate.py`, `tests/test_ci_docs_hygiene.py`
- Phase 4 source: `memory-bank/archive/archive-build-phase4-2026-05-11.md` (Qt typing flagged as deferral)
