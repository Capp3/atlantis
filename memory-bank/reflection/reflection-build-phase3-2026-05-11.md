# Task Reflection: Atlantis BUILD Phase 3

## Summary
Phase 3 delivered the persistence and recovery layer for Atlantis: rolling per-document autosave, startup recovery flow (with headless and interactive modes), `QFileSystemWatcher`-based external change handling, and a persisted recent files list. All work landed behind small, testable helpers in `atlantis/model/file_handler.py` and `atlantis/ui/main_window.py`, keeping the UI layer thin and the model layer test-friendly. The full test suite expanded from 5 to 9 passing tests with no regressions.

## What Went Well
- **Layered design held up**: file_handler stayed pure (path + bytes), MainWindow owned UI side effects (status, prompt, watcher). This made testing autosave and recovery straightforward.
- **Deterministic test surface**: introducing `ATLANTIS_AUTOSAVE_DIR` and `ATLANTIS_HEADLESS` env hooks let us assert real autosave/recovery behavior without GUI prompts or temp-dir pollution.
- **Settings keys centralized**: adding `AUTOSAVE_*` and `RECENT_FILES_KEY` in `atlantis/core/settings.py` kept persistence concerns in one place and aligned with the systemPatterns guidance.
- **Watcher integration was non-invasive**: a single `QFileSystemWatcher` and one slot covered both auto-reload and "dirty buffer" warning behaviors.
- **Test gate worked on first run**: ruff + pytest passed cleanly with 9 tests, with only minor format auto-fixes applied.

## Challenges
- **Headless prompt avoidance**
  - Impact: recovery prompt cannot run in test mode.
  - Resolution: split recovery into headless auto-restore and interactive prompt-restore paths via `_headless_mode()`.
  - Outcome: deterministic Phase 3 tests without skipping recovery logic.
- **Untitled document autosave naming**
  - Impact: autosave keyed off `Path` only; an unnamed document had no obvious file.
  - Resolution: introduced a stable `untitled.mmd.autosave` filename in the autosave dir.
  - Outcome: untitled-document recovery works deterministically; same path is reused across restarts.
- **File watcher list churn**
  - Impact: switching documents could leave stale watched paths.
  - Resolution: `_set_watched_file()` clears existing watched paths before adding the new one.
  - Outcome: predictable single-watch behavior consistent with single-window scope.
- **Recent files type handling in QSettings**
  - Impact: `QSettings.value` can return native list/None forms across platforms.
  - Resolution: defensive normalization with `type=list` and empty fallback.
  - Outcome: stable cross-environment recent files persistence.

## Lessons Learned
- Always pair a UI-driven flow with an environment-toggle headless equivalent to keep tests honest.
- Autosave should treat "untitled" as a real, stable bucket; failing to do so would make recovery look broken to users.
- Single-window apps benefit from explicit watcher reset semantics; never just `addPath()` without considering churn.
- `QSettings` round-trip semantics differ slightly across platforms; type-hinted reads with safe defaults prevent surprise failures.

## Process Improvements
- Reuse the per-phase test module pattern (`tests/test_phaseX_*.py`) for every BUILD phase.
- Continue documenting commands and test results inside `memory-bank/tasks.md` while a phase is open; this makes reflection and archiving quick.
- Add a short "env hooks introduced this phase" log section in future phase implementation summaries (e.g. `ATLANTIS_AUTOSAVE_DIR`).
- Keep settings keys defined centrally before touching UI consumers, not after.

## Technical Improvements
- Add a recovery-restore decision result type so `MainWindow` does not embed UX choices in conditionals.
- Wire autosave interval/enabled into a settings UI surface (View → Preferences) in Phase 4.
- Add a "diff preview" affordance for recovery as originally specified in projectbrief once Phase 4 polish lands.
- Persist recent files only for files that actually exist on disk at startup to avoid stale menu entries.
- Add a structured `FileSession` model to fold `_current_path`, dirty state, and watcher membership into one object for easier reasoning.

## Plan vs Actual (Phase 3)
- **Autosave**: implemented with rolling per-document file; timer interval defaults to 60s (configurable via settings keys). Matches plan.
- **Recovery**: implemented with both headless and interactive paths; diff preview deferred to a Phase 4 polish task.
- **External change handling**: implemented; reload-when-clean / warn-when-dirty behavior matches plan.
- **Front matter parsing**: not implemented in this phase. Kept in scope for a follow-up (depends on `atlantis/utils/frontmatter.py`).
- **Recent files**: implemented and persisted in `QSettings` (`RECENT_FILES_KEY`); UI menu entries deferred to Phase 4.

## Metrics Snapshot
- Tests passing: 9 (5 prior + 4 new Phase 3)
- New env hooks introduced: 2 (`ATLANTIS_AUTOSAVE_DIR`, existing `ATLANTIS_HEADLESS` reused)
- New settings keys introduced: 3 (`AUTOSAVE_ENABLED_KEY`, `AUTOSAVE_INTERVAL_KEY`, `RECENT_FILES_KEY`)
- New helpers in `file_handler.py`: 5

## Next Steps
- Execute the technology validation PoC for `QWebEngineView` + Mermaid bridge.
- Begin BUILD Phase 4 (validation, feedback, polish):
  - render time indicator and cycle-through error UI in status bar
  - settings UI for autosave toggle/interval
  - recent files menu wiring
  - diff preview for recovery prompt
  - front matter parsing surface (deferred from Phase 3)
- Update `memory-bank/tasks.md` continuously during Phase 4 build work.
