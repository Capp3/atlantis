# Memory Bank: Style Guide

## Code Style
- Follow PEP 8 with ruff enforcement (line-length=120, specific ignores documented in pyproject.toml).
- Use type hints everywhere (mypy strict).
- Prefer dataclasses or Pydantic models for structured data.
- Docstrings: Google or NumPy style via mkdocstrings.
- Imports: isort via ruff (I rule).
- Naming: snake_case for functions/vars, PascalCase for classes, UPPER for constants.

## UI/UX Guidelines (PyQt6)
- Native look: respect system theme, no custom dark mode forcing.
- Accessibility: clear labels, keyboard navigation where feasible.
- Layout: use QSplitter, QVBoxLayout/QHBoxLayout, avoid absolute positioning.
- Feedback: status bar for transient messages, non-modal dialogs for confirmations.

## Documentation Style
- Markdown for all docs.
- Memory Bank files use clear headings, checklists, mermaid diagrams where helpful.
- Keep projectbrief.md as single source of truth for scope.
- Update memory-bank/ files incrementally; use partial updates when possible.

## Git & Workflow
- Follow .cursor/rules/gitflow.mdc (Gitflow).
- Commit messages: conventional, descriptive.
- Branch from main for features/fixes.
- Pre-commit hooks mandatory.

## Memory Bank Usage
- Always verify paths start with memory-bank/ before editing core files.
- Use tasks.md for active checklists.
- Update activeContext.md on focus shifts.
- Archive completed tasks to memory-bank/archive/
- Creative phase docs in memory-bank/creative/ for Level 3+ design decisions.

## General
- No comments that narrate obvious code (per clean-code rules).
- Error messages user-friendly.
- All user-facing text in English.
