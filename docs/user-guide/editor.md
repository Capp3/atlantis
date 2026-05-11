# Editor

The Atlantis editor is built on `QPlainTextEdit` with a custom line-number gutter and a `QSyntaxHighlighter` tuned for Mermaid grammar. The full design rationale lives in `memory-bank/creative/creative-editor-component.md`.

## Keyboard shortcuts

| Action | Shortcut |
|--------|----------|
| New file | `Ctrl+N` (`Cmd+N` on macOS) |
| Open file | `Ctrl+O` (`Cmd+O`) |
| Save | `Ctrl+S` (`Cmd+S`) |
| Save As… | `Ctrl+Shift+S` (`Cmd+Shift+S`) |
| Cycle render errors | `Ctrl+E` (`Cmd+E`) |
| Toggle autosave preferences | via **File → Autosave Preferences…** |

## Recent files

Atlantis maintains a most-recently-used file list under **File → Open Recent**. The list is persisted via `QSettings` and is pruned on startup: entries pointing at files that no longer exist are silently dropped.

## Autosave & recovery

- **Autosave**: enabled by default; configurable via **File → Autosave Preferences…**. The dialog round-trips an enable flag and an interval (in seconds) through `QSettings`.
- **Recovery**: on startup, if an autosave file exists that differs from the on-disk version, Atlantis offers to restore it. The confirmation dialog includes a unified `difflib` diff so you can see exactly what would change.
- **External changes**: Atlantis watches the currently-open file with `QFileSystemWatcher`. If the file changes externally and the editor has no unsaved edits, Atlantis reloads it; if the editor is dirty, you're prompted before any overwrite happens.

## Render errors

The status bar shows the count of active render errors, the elapsed render time, and (when more than one error is active) lets you cycle through them with `Ctrl+E`. The last successfully-rendered SVG is retained while you fix the new errors, so the preview never goes blank mid-edit.

## Themes

The Mermaid preview theme tracks the system theme: a light system palette uses Mermaid's `default` theme; a dark palette uses Mermaid's `dark` theme. The theme is derived from the `QApplication` palette lightness on render.
