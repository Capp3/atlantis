# Memory Bank: Active Context

## Current Focus
Executing BUILD Phase 3 persistence/recovery work for Atlantis and validating autosave, recovery, and file-watch behavior.

## Status
BUILD Phase 3 complete. Autosave and recovery flow are implemented, external file change monitoring is integrated, and recent files persistence is stored in settings. Test gate passed with full suite.

## Latest Changes
- Updated `atlantis/model/file_handler.py` with autosave directory/path/read/write/clear helpers.
- Updated `atlantis/core/settings.py` with autosave/recent-files setting keys.
- Updated `atlantis/ui/main_window.py` with:
  - autosave timer and rolling autosave writes
  - startup recovery restore behavior
  - file watcher reload/warn behavior
  - recent files persistence support
- Added `tests/test_phase3_persistence.py` and passed full suite.

## Open Items
- Execute technology validation PoC for controlled Mermaid rendering in `QWebEngineView`.
- Continue BUILD lifecycle with Phase 4 (validation feedback/polish) after technology validation.