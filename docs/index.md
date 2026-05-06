# Atlantis Documentation

Atlantis is a desktop Mermaid editor focused on a code-first workflow with integrated preview.

## Getting Started

### Python Management (Required)

This project standardizes on [`uv`](https://github.com/astral-sh/uv) for Python management.

- Install dependencies and create/update the environment:
  - `uv sync`
- Run tests:
  - `uv run pytest`
- Run linting:
  - `uv run ruff check .`
- Run the app:
  - `uv run python -m atlantis`

### Project Documentation

- Product scope and goals: `docs/projectbrief.md`
- Memory Bank context: `memory-bank/`

## Contributing

Use `uv` commands in local setup and scripts to keep workflows consistent across contributors and CI.
