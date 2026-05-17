# Memory Bank: System Patterns

## High-Level Architecture
Atlantis follows a classic desktop MVC-inspired pattern adapted for PyQt6:
- **Model**: File I/O layer for .mmd files + in-memory diagram state (front-matter + Mermaid source).
- **View**: PyQt6 main window with QSplitter (editor | preview), status bar, menus. WebEngine view for live Mermaid render.
- **Controller/Presenter**: Event handlers connecting editor changes to preview updates, file ops, validation.

## Key Design Patterns
- **Observer**: Editor document changes notify preview renderer (debounced).
- **Strategy**: Pluggable front-matter parsers (YAML/TOML) with validation.
- **Command**: Menu actions and keyboard shortcuts as executable commands (undo/redo stack scoped to session).
- **Facade**: Simplified API over QWebEngine for Mermaid rendering and error extraction.
- **Singleton-ish**: App-level settings manager for persistence (window geometry, debounce delay, autosave interval).

## Data Flow (MVP)
1. User opens/creates .mmd file → load source + front-matter into editor model.
2. Editor textChanged → schedule debounced render.
3. Render task: inject Mermaid source into WebEngine, capture result or error.
4. On success: update preview; on error: retain last-good + show status.
5. Autosave timer: periodic write to temp rolling file.
6. Exit/crash: on next start, detect recovery file and offer restore.

## Error Handling Strategy
- Syntax/render errors: displayed in status bar (cycle-able), inline highlights in editor where possible.
- File I/O: graceful degradation, user prompts for save conflicts.
- No silent failures; all errors logged to user-accessible log.

## Persistence Strategy
- Per-document autosave in OS temp dir (configurable).
- Window state + recent files in QSettings (or JSON).
- No central project DB; pure file-based.
- **`FileSession`** owns the active document path; **`QTextDocument.isModified()`** owns dirty state (no duplicate flag). **`RecentFilesRegistry`** and **`DocumentFileWatcher`** sit in `atlantis/model/`.

## Security/Offline
- No network in final build (local Mermaid bundle, local-only plugins).
- Sandboxed plugin loading (future).
- No external process execution beyond bundled Qt.

## Quality Patterns
- Type-safe Python (mypy strict).
- Comprehensive linting (ruff).
- Test isolation (pytest).
- Documentation-driven (MkDocs + Memory Bank).

## Evolution Path
MVP: single-window, single-file focus.
Future: multi-tab? export pipeline, visual nav layer (source-oriented), plugin host, full offline bundle, packaging (PyInstaller or similar).
