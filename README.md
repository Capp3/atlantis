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

## Install

**Recommended:** clone the repo and use `uv` (Python 3.12+). See [Installation](docs/user-guide/installation.md) for wheels and the experimental PyInstaller bundle.

```bash
uv sync
uv run atlantis              # launch the GUI
uv run atlantis --smoke-test # headless boot/exit (used by CI)
```

## Running the test suite

```bash
make check              # PR gate: format + lint + mypy + coverage (matches CI)
make check-all          # above + strict docs build
make test               # pytest only (offscreen)
make webengine          # opt-in WebEngine smoke (desktop Qt)
```

Equivalent `uv run` commands are listed in `docs/contributing.md`.

## Contributing

Install hooks once after cloning:

```bash
uv sync
uv run pre-commit install
make pre-commit         # or: uv run pre-commit run --all-files
```

See `docs/contributing.md` for the full contributor loop. VS Code tasks under `.vscode/tasks.json` include **Check (PR gate)** (`make check`) and individual gate tasks using `uv run`.

## Documentation

The full documentation site (built with MkDocs + mkdocstrings) is published at <https://capp3.github.io/atlantis/>. Build it locally with:

```bash
make docs-serve                # live-reload preview
make docs                      # CI-equivalent strict build
```
