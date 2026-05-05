# Memory Bank: Product Context

## Product Overview
Atlantis is a desktop GUI application for authoring Mermaid.js diagrams with integrated live preview. It targets technical documentation workflows for engineers and architects, emphasizing a code-first approach with semi-visual aids to reduce friction in diagram iteration.

## Target Audience
- Primary: Software engineers, system architects, and technical writers producing Mermaid-based documentation (e.g., architecture diagrams, flowcharts, sequence diagrams).
- Secondary: Any users of Mermaid.js seeking a dedicated, efficient editing environment beyond plain text editors or browser-based tools.

## Key Product Goals
- Eliminate context switching between code editing and preview rendering.
- Provide reliable, fast feedback on Mermaid syntax and rendering.
- Maintain full compatibility with standard Mermaid syntax and output.
- Deliver a polished, native-feeling desktop experience (PyQt6 on macOS MVP, cross-platform long-term).
- Support offline operation in final product.

## Core Features (MVP)
- Split-pane editor + live Mermaid preview (WebEngine).
- .mmd file handling (single-diagram files).
- Syntax highlighting, error feedback, line numbers.
- Autosave + session recovery.
- System-theme following UI.
- Menu-driven front-matter management.

## Non-Functional Requirements
- Performance: Render updates within ~4s target, with debounce and timeout controls.
- Reliability: Graceful error handling, last-good preview retention.
- Usability: Intuitive for Mermaid-familiar users, minimal learning curve.
- Maintainability: Clean Python codebase with strict typing (mypy), linting (ruff), testing (pytest).

## Success Metrics (MVP)
- User can complete full create-edit-preview-save cycle for a single diagram without leaving the app.
- No data loss on crash via autosave.
- Diagrams render identically to standard Mermaid.js.

## Roadmap Alignment
MVP focuses on core editor+preview loop. Post-MVP expands to export, packaging, plugins, and advanced navigation. Memory Bank system (this setup) enables rigorous tracking of implementation phases.
