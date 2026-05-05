# Memory Bank: Tech Context

## Technology Stack
- **Language & Runtime**: Python >=3.12,<4.0 (primary target 3.12)
- **UI Framework**: PyQt6 (for native desktop widgets, WebEngine for Mermaid rendering)
- **Build/Packaging**: Hatchling (PEP 517/518), pyproject.toml managed
- **Type Checking**: mypy (strict mode: disallow_untyped_defs, etc.)
- **Linting/Formatting**: ruff (comprehensive ruleset, line-length 120, preview format)
- **Testing**: pytest (tests/ dir), coverage via codecov
- **Docs**: mkdocs + mkdocs-material + mkdocstrings[python]
- **CI/Quality**: pre-commit, tox-uv, codecov.yaml
- **Version Control**: Git (main branch, GitHub repo at capp3/atlantis)

## Mermaid Integration
- Embedded via Qt WebEngine (QWebEngineView)
- Mermaid.js loaded locally for offline (post-MVP) or via CDN (MVP acceptable)
- Rendering triggered on editor focus loss + debounce (500ms default)
- Error capture and display without breaking preview

## Project Structure (Planned)
- atlantis/ : Main package (currently absent - setup phase)
- tests/ : Unit and integration tests
- docs/ : MkDocs source (existing projectbrief.md to be synced/expanded)
- memory-bank/ : Core Memory Bank (newly created)
- .cursor/rules/ : Extensive Cursor AI rules including isolation_rules for structured workflow
- .github/ : Dependabot, workflows
- pyproject.toml : Single source of truth for deps, tools config

## Development Environment
- Virtualenv: .venv (Python 3.12)
- OS Target: macOS primary for MVP (darwin), cross-platform later
- No runtime deps beyond stdlib + PyQt6 (dev deps listed in pyproject)
- Strict quality gates: mypy, ruff, pytest required before changes

## Constraints
- Offline-first final product (bundle assets)
- No telemetry
- Single-chart, file-based model (no workspace DB in MVP)
- Preserve Mermaid compatibility 100%

## Tooling Notes
- Use `uv` or pip via pyproject for installs
- Pre-commit hooks for quality
- MkDocs for docs serving: mkdocs serve
