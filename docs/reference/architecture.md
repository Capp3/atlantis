# Architecture overview

A distilled view of the architecture decisions captured in `memory-bank/systemPatterns.md` and the creative records. For the full design history, browse `memory-bank/creative/`.

## High-level layout

```
atlantis/
├── core/         # app factory, settings, logging
├── model/        # DiagramDocument and persistence primitives
├── renderer/     # MermaidRenderer facade + WebEngineMermaidBridge
├── ui/           # MainWindow, MermaidEditor, PreviewPane, dialogs
├── plugins/      # PluginManifest + PluginRegistry (v1 scaffold)
└── utils/        # frontmatter parsing
```

## Key components

- **`MainWindow`** owns the splitter, menus, status bar, and the lifecycle of all subcomponents. It debounces edits, drives autosave + recovery, watches the on-disk file via `QFileSystemWatcher`, and persists window state through `QSettings`.
- **`MermaidEditor`** is a `QPlainTextEdit` subclass with a custom line-number gutter and a `QSyntaxHighlighter` tuned to Mermaid keywords. See `memory-bank/creative/creative-editor-component.md`.
- **`PreviewPane`** owns the embedded `QWebEngineView` (or a `QTextEdit` fallback in headless mode). It owns the `WebEngineMermaidBridge` and exposes a `render_source(source, on_done)` async API plus a `sourceRendered` signal.
- **`WebEngineMermaidBridge`** installs a Mermaid HTML shell into the `QWebEnginePage`, sets up a `QWebChannel` so JS can call back into Python with `report_svg` / `report_error`, and serialises render requests with a pending-source buffer + 15 s timeout.
- **`MermaidRenderer`** is a small synchronous facade that returns a placeholder SVG or an explicit error. Its role inside `MainWindow` is to detect syntax errors for editor markers; the production preview goes through the WebEngine bridge.

## Design records (creative phase outputs)

| Record | Decision |
|--------|----------|
| `creative-editor-component.md` | `QPlainTextEdit` + custom gutter + `QSyntaxHighlighter` |
| `creative-ui-layout-feedback.md` | Two-pane `QSplitter` with a status bar |
| `creative-renderer-offline-bundle.md` | `QWebEngineView` HTML shell with manual Mermaid rendering; staged CDN→local-bundle path |
| `creative-packaging-plugin-boundaries.md` | Plugin registry scaffold; PyInstaller bundle PoC (ADR 0004) |

## Cross-cutting policies

- **Headless mode**: `ATLANTIS_HEADLESS=1` swaps `QWebEngineView` for a `QTextEdit` fallback so the test suite stays fast and dependency-light.
- **Settings**: `atlantis/core/settings.py` centralises `QSettings` keys (window geometry, splitter state, autosave config, recent files).
- **Logging**: `atlantis/core/logging.py` configures the app-data log path and stderr stream; severity controlled by `--log-level` / `ATLANTIS_LOG_LEVEL`.
- **Front matter**: `atlantis/utils/frontmatter.py` splits and (for TOML) parses fenced front matter without ever blocking the render path.
- **Plugins**: `atlantis/plugins/` exposes `PluginRegistry` and `PluginManifest` for future extensions; no dynamic loader in v1. See [Plugins](../user-guide/plugins.md).

The auto-generated API reference is on the [API page](api.md).
