# Contributing

Thank you for your interest in Atlantis! This guide describes the local contributor loop. The full architectural rationale lives in `memory-bank/` and the published reference docs.

## Tooling baseline

Atlantis standardises on [`uv`](https://github.com/astral-sh/uv) for Python environment and dependency management. All commands below assume `uv` is installed and on your `PATH`.

| Tool | Purpose |
|------|---------|
| `uv` | Environment + dependency management |
| `ruff` (lint + format) | Code quality gate (also enforced by pre-commit and CI) |
| `mypy` | Static typing (runs **non-blocking** in CI until UI typing cleanup ships) |
| `pytest` + `pytest-qt` | Test runner (offscreen Qt, opt-in WebEngine marker) |
| `mkdocs` + `mkdocstrings` | Documentation site |
| `pre-commit` | Local commit-time gate (mirrors the CI lint job) |

## First-time setup

```bash
git clone https://github.com/capp3/atlantis.git
cd atlantis
uv sync
uv run pre-commit install
uv run pre-commit run --all-files
```

## The contributor loop

Run these before opening a PR; CI enforces the same gates.

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest -q
uv run mkdocs build --strict
```

To capture coverage locally (the same command CI uses):

```bash
uv run pytest --cov=atlantis --cov-report=term-missing -q
```

To exercise the real `QWebEngineView` runtime (skipped by default — requires a desktop Qt session, not a headless CI image):

```bash
ATLANTIS_WEBENGINE_TESTS=1 uv run pytest -m webengine -q
```

## Test conventions

- All Qt tests rely on the shared harness in `tests/conftest.py`, which sets `QT_QPA_PLATFORM=offscreen` and `ATLANTIS_HEADLESS=1` and provides a session-scoped `qapp` fixture. New test modules should **not** re-declare these env vars or create their own `QApplication`.
- Tests that need an isolated autosave directory can request the `autosave_tmp` fixture instead of poking `ATLANTIS_AUTOSAVE_DIR` directly.
- Long-running or WebEngine-dependent tests should carry the `@pytest.mark.webengine` marker so they only execute under `ATLANTIS_WEBENGINE_TESTS=1`.

## Adding a new test

1. Drop a new `tests/test_<area>.py` module — no boilerplate header needed; the harness is autouse.
2. Use the existing helpers (`_create_window`, `autosave_tmp`, etc.) where possible.
3. If the test exercises the real WebEngine runtime, mark it `@pytest.mark.webengine`.
4. Run `uv run pytest -q` locally to verify it joins the default suite (or is skipped, for WebEngine tests).

## Pre-commit policy

`.pre-commit-config.yaml` ships the same `ruff` + `ruff-format` versions that CI's lint job uses, plus a small set of hygiene hooks (trailing whitespace, EOF newline, merge-conflict markers, YAML/TOML validation, line endings). The mypy hook is intentionally **deferred** until the chronic Qt typing noise is cleaned up; once that lands, the hook is added here and the CI mypy job is flipped to blocking.

## Documentation changes

Documentation pages live under `docs/` and are surfaced through `mkdocs.yml`. Architecture and reference content is generated from docstrings via mkdocstrings; the API reference at `docs/reference/api.md` is a one-liner that pulls the whole `atlantis` package.

When adding a page:

1. Create the Markdown file under the appropriate section.
2. Add it to `nav:` in `mkdocs.yml`.
3. Run `uv run mkdocs build --strict` locally before pushing — the strict build will catch broken links and missing nav entries.

## Memory bank conventions

Atlantis uses a Memory Bank workflow (`/van` → `/plan` → `/creative` → `/build` → `/reflect` → `/archive`) tracked under `memory-bank/`. Contributors do not need to touch these files for routine code changes, but if you're shipping a phase or a feature with cross-cutting impact, follow the existing pattern: update `tasks.md`, log progress in `progress.md`, and archive completed phases under `memory-bank/archive/`.
