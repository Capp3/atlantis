# Atlantis

A desktop Mermaid editor focused on a code-first workflow with an integrated live preview, built on **PyQt6** and **Qt WebEngine** with **Mermaid.js 10.9.3**.

## Where to start

- New here? See **[Getting Started](getting-started.md)** for install + first run.
- Living in the app? Head to the **User Guide**:
    - [Editor](user-guide/editor.md)
    - [Renderer](user-guide/renderer.md)
    - [Front matter](user-guide/front-matter.md)
    - [Examples](user-guide/examples.md)
    - [Troubleshooting](user-guide/troubleshooting.md)
- Hacking on Atlantis? See **[Contributing](contributing.md)** and the **[Architecture](reference/architecture.md)** + **[API reference](reference/api.md)** pages.
- Curious how we landed on key decisions? Browse the [ADR index](adr/0001-mermaid-cdn-mvp.md).

## Python tooling standard

Atlantis standardises on [`uv`](https://github.com/astral-sh/uv) for environment and dependency management. All commands in this site assume `uv` is installed and on your `PATH`.

```bash
uv sync                  # bootstrap the venv
uv run atlantis          # launch the GUI
uv run pytest -q         # run the default test suite
uv run mkdocs serve      # preview this site locally
```

See `memory-bank/` in the repository for the phased plan, creative decision records, reflections, and archives that backed each release.
