# Atlantis

A Mermaid.js GUI desktop application with a live preview, built on PyQt6 and embedded `QWebEngineView`.

[![CI](https://github.com/capp3/atlantis/actions/workflows/ci.yml/badge.svg)](https://github.com/capp3/atlantis/actions/workflows/ci.yml)
[![Docs](https://github.com/capp3/atlantis/actions/workflows/docs.yml/badge.svg)](https://github.com/capp3/atlantis/actions/workflows/docs.yml)
[![codecov](https://codecov.io/gh/capp3/atlantis/branch/main/graph/badge.svg)](https://codecov.io/gh/capp3/atlantis)

## Python Tooling Standard

Atlantis uses [`uv`](https://github.com/astral-sh/uv) as the standard tool for Python environment and dependency management.

- Create/sync environment: `uv sync`
- Run commands in project env: `uv run <command>`
- Add dependencies: `uv add <package>`
- Add dev dependencies: `uv add --dev <package>`

## Quickstart

```bash
uv sync
uv run atlantis              # launch the GUI
uv run atlantis --smoke-test # headless boot/exit (used by CI)
```

## Running the test suite

```bash
uv run pytest -q                                # default suite (offscreen, headless)
uv run pytest --cov=atlantis --cov-report=term-missing
ATLANTIS_WEBENGINE_TESTS=1 uv run pytest -m webengine -q   # opt-in WebEngine smoke
```

## Contributing

Install hooks once after cloning:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

See `docs/contributing.md` for the full contributor loop (lint → tests → docs → pre-commit). Recommended VS Code tasks are pre-configured under `.vscode/tasks.json` (`Ruff Fix`, `Run Tests`, `Coverage`, `Pre-commit (all files)`, `Build Docs (strict)`, `Serve Docs`).

## Documentation

The full documentation site (built with MkDocs + mkdocstrings) is published at <https://capp3.github.io/atlantis/>. Build it locally with:

```bash
uv run mkdocs serve            # live-reload preview
uv run mkdocs build --strict   # CI-equivalent strict build
```
