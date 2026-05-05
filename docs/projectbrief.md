# Atlantis Project Brief

## Vision

Atlantis is a desktop application for creating and iterating Mermaid charts in a semi-visual environment.
The goal is to remove constant context switching between writing Mermaid code and opening separate previews.

## Problem Statement

Engineers and architects writing technical documentation need a faster way to build Mermaid diagrams.
Current workflows require repeated back-and-forth between code and external preview tools, which slows iteration and increases friction.

Atlantis solves this by providing a single-window workspace with responsive preview and source-oriented visual navigation.

## Target Users

- Engineers creating technical documents
- Architects creating technical paperwork and design communication artifacts

## Core Product Principles

- Code-first workflow: Mermaid source remains the primary editing surface
- Semi-visual interaction: visual selection helps navigate to source, not replace source editing
- Single-chart focus: one chart is edited at a time
- Offline-first design: the final product should not require network access
- Cross-platform intent: macOS, Windows, Linux
- Standard compatibility: generated content must remain compatible with standard Mermaid

## Technical Baseline

- Language/runtime: Python 3.12
- UI framework: PyQt6
- Preview renderer: Mermaid JS embedded in a Qt WebEngine view
- Execution model:
  - MVP: local Python execution is acceptable
  - Long-term: portable packaged desktop app is preferred
- Connectivity:
  - Final product: Mermaid JS must be bundled locally for offline operation
  - MVP: CDN usage is acceptable if required
- Primary MVP platform target: macOS with Python 3.12
- Long-term platform target: macOS, Windows, Linux

## MVP Scope (Must Have)

### Editor + Preview Layout

- Single main window with:
  - Left pane: Mermaid code editor
  - Right pane: live diagram preview
  - Bottom status/feedback bar
  - Menu bar
- Resizable split between code and preview panes
- Code editor must display line numbers
- Pane sizes and window state persist between sessions
- Theme follows the system theme only
- Menus should be reasonably complete to provide user confidence

### Editor Behavior

- Primary editing target is Mermaid code
- Editor should use a third-party embedded editor component where practical
- Editor must support:
  - Mermaid-specific syntax highlighting
  - Line numbers
  - Inline error highlighting
- Editor configuration:
  - Soft wrap enabled by default and configurable
  - Standardized indentation enforced by the application
- Undo/redo is session-scoped only
- Advanced editing features such as multi-cursor editing are out of scope for MVP

### File Model

- File type: `.mmd` only
- Exactly one Mermaid diagram per file
- Files are standalone; there is no project/workspace abstraction
- One file is open per window
- File operations:
  - Create new chart
  - Open existing chart
  - Save chart
  - Save As
- Recent files are accessible via menu but are not auto-restored
- External file changes should be reflected in-editor where feasible

### Front Matter Handling

- Front matter must support Mermaid-compatible formats where practical, including YAML and TOML
- Front matter must be preserved without formatting changes
- MVP front matter behavior:
  - Display front matter content
  - Front matter changes are performed via menu actions
  - Invalid front matter produces a warning only
  - Prefer schema awareness where practical
- Editing model should align with the underlying format and avoid destructive transformations
- Post-MVP target: support both menu-based and direct editing with dynamic synchronization

### Rendering and Preview

- Rendering uses Mermaid JS in an embedded Qt WebEngine view
- Preview refresh behavior:
  - Trigger render when the editor loses focus
  - Debounce render requests with a user-configurable delay
  - Default debounce delay: 500 ms
- On parse/render error:
  - Keep showing last known good preview
  - Display error feedback
  - Do not retry automatically until further edits occur
- Render timing:
  - Target render latency: 4 seconds, configurable
  - Hard render timeout: 15 seconds, configurable
- No hard diagram size limit in MVP
- Render timeout must be enforced
- Future safeguard: optional setting to disable rendering for large diagrams
- No GPU optimization requirement beyond default WebEngine behavior

### Validation and Feedback

- Show first error line/details in the status bar
- Status bar should support cycling through multiple errors
- Inline editor highlighting should identify errors where possible
- Linting/validation should provide actionable syntax feedback (line/location when possible)
- MVP error messaging may expose raw Mermaid errors
- Future error messaging should provide more user-friendly abstraction
- General warnings are deferred beyond MVP, except invalid front matter warnings

### Source-Oriented Visual Navigation

- Source-oriented visual navigation is desirable but not required for MVP
- Clicking/selecting diagram elements in preview should eventually navigate/highlight corresponding source in the code editor
- This is a navigation shortcut to code, not a full visual editor in MVP
- Menu options should provide clear, guided edit choices where feasible

### Persistence and Recovery

- Autosave included in MVP
- Autosave interval for MVP: every 60 seconds
- Autosave can be disabled via settings
- Autosave model:
  - Single rolling autosave file per document
  - Stored in a globally configurable temp directory
  - Retained until clean exit
- Crash/session recovery should prompt the user to restore recent unsaved work

### Logging and Debugging

- Rendering errors should be logged
- Logs must be user-accessible
- Logging should be configurable via settings
- No telemetry, consistent with offline-first principles
- No GUI debug mode required in MVP
- A hidable stdout/log output panel is desirable for debugging

## Out of Scope for MVP

- Full visual editing of node/edge properties directly on canvas
- Export pipeline (PNG/SVG files)
- Plugin/extensibility system beyond Mermaid capabilities
- Preview element-to-source mapping
- Keyboard-first workflows
- Advanced editor capabilities such as multi-cursor editing
- AI features
- Collaboration features
- GUI debug mode

## Post-MVP / Final Product Goals

- Export support (PNG, SVG)
- Continue supporting copy/paste of Mermaid or markdown-compatible code output
- Improve visual-edit affordances while keeping code-first workflow
- Improve packaging/distribution toward portable app experience across macOS, Windows, Linux
- Bundle Mermaid JS locally for fully offline operation
- Support portable binaries where feasible
- Add optional plugin/extension mechanism
- Consider AI-related functionality as a future plugin domain

## Plugin / Extension Guardrails

Plugins are not part of MVP, but are a planned extension mechanism.

- Plugins must not alter Mermaid syntax or output format
- All generated content must remain fully compatible with standard Mermaid
- Plugins may:
  - Enhance editor behavior such as snippets, linting, and tooling
  - Provide export functionality
  - Integrate external services
  - Add UI components such as panels and menus
- Plugin architecture should be:
  - Local-only and filesystem-based
  - Sandboxed
  - Configured globally

## Future Direction Guardrails

- Visual editing is not intended to become the primary workflow, but is not explicitly prohibited
- AI features are out of scope for MVP and should be treated as a likely future plugin domain
- Collaboration remains undefined and should stay constrained to avoid scope creep

## Success Criteria

- Primary success metric for MVP: complete, reliable end-to-end workflow for creating and iterating a single Mermaid chart
- Performance can be improved iteratively after functionality is stable
- MVP should allow a user to create, open, edit, preview, validate, autosave, recover, and save a standalone `.mmd` Mermaid diagram
