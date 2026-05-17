# Contributing

Thank you for your interest in Atlantis! This guide describes the local contributor loop. The full architectural rationale lives in `memory-bank/` and the published reference docs.

## Tooling baseline

Atlantis standardises on [`uv`](https://github.com/astral-sh/uv) for Python environment and dependency management. All commands below assume `uv` is installed and on your `PATH`.

| Tool | Purpose |
|------|---------|
| `uv` | Environment + dependency management |
| `ruff` (lint + format) | Code quality gate (also enforced by pre-commit and CI) |
| `mypy` | Static typing (**blocking** in CI and pre-commit on `atlantis/`) |
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
make check-all    # format + lint + mypy + pytest coverage + strict docs
```

PR-sized gate without the docs build:

```bash
make check        # format-check + lint + typecheck + test-cov
```

| Make target | Equivalent `uv run` command |
|-------------|---------------------------|
| `make format-check` | `uv run ruff format --check .` |
| `make lint` | `uv run ruff check .` |
| `make typecheck` | `uv run mypy atlantis` |
| `make test` | `uv run pytest -q` (offscreen env set by Makefile) |
| `make test-cov` | `uv run pytest --cov=atlantis --cov-report=term-missing --cov-report=xml -q` |
| `make docs` | `uv run mkdocs build --strict` |
| `make pre-commit` | `uv run pre-commit run --all-files` |
| `make bundle-smoke` | `uv sync --group packaging` then PyInstaller build + bundled `--smoke-test` (opt-in; not in CI PR gate) |

On systems without GNU Make, run the `uv run` commands from the table directly (export `QT_QPA_PLATFORM=offscreen` and `ATLANTIS_HEADLESS=1` for pytest).

## Release checklist (maintainers)

1. `make check-all` green on the release platform.
2. Update `CHANGELOG.md` and bump `version` in `pyproject.toml`.
3. `uv build` — confirm the wheel lists `atlantis/assets` (e.g. `unzip -l dist/*.whl | grep mermaid`).
4. (Optional, Linux) `uv sync --group packaging` and `make bundle-smoke`, or run **Actions → Bundle Linux (experimental)** for a CI-built artifact (see [Installation → CI-built Linux bundle](user-guide/installation.md#ci-built-linux-bundle)).
5. Tag `vX.Y.Z` and push; publish GitHub Release artifacts when automation exists.

See [Installation → Experimental Linux bundle](user-guide/installation.md#experimental-linux-bundle-pyinstaller) for bundle details.

To exercise the real `QWebEngineView` runtime (skipped by default — requires a desktop Qt session, not a headless CI image):

```bash
make webengine
# or: ATLANTIS_WEBENGINE_TESTS=1 uv run pytest -m webengine -q
```

See [Troubleshooting → Opt-in WebEngine pytest](user-guide/troubleshooting.md#opt-in-webengine-pytest-pytestmarkwebengine) for display-server, CDN, and macOS pin requirements.

### CI workflows

| Workflow | When it runs | What it does |
|----------|----------------|--------------|
| `ci.yml` | PRs + pushes to `main` | Ruff, pytest + coverage, mypy (blocking), opt-in macOS WebEngine smoke (`workflow_dispatch` only) |
| `docs.yml` | PRs + pushes to `main` | `mkdocs build --strict`; publishes `site/` to GitHub Pages on `main` pushes only |
| `bundle.yml` | `workflow_dispatch` only | Linux PyInstaller `make bundle-smoke`; uploads `dist/atlantis/` artifact (not on PR gate) |

Docs are validated once in `docs.yml` (not duplicated in `ci.yml`).

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

`.pre-commit-config.yaml` ships the same `ruff` + `ruff-format` versions that CI's lint job uses, a **mypy** hook (`uv run mypy atlantis`), plus hygiene hooks (trailing whitespace, EOF newline, merge-conflict markers, YAML/TOML validation, line endings). Qt accessor narrowing lives in `atlantis/ui/qt_accessors.py` so UI code stays strict without blanket `# type: ignore`.

## Documentation changes

Documentation pages live under `docs/` and are surfaced through `mkdocs.yml`. Architecture and reference content is generated from docstrings via mkdocstrings; the API reference at `docs/reference/api.md` is a one-liner that pulls the whole `atlantis` package.

When adding a page:

1. Create the Markdown file under the appropriate section.
2. Add it to `nav:` in `mkdocs.yml`.
3. Run `uv run mkdocs build --strict` locally before pushing — the strict build will catch broken links and missing nav entries.

## Memory bank conventions

Atlantis uses a Memory Bank workflow (`/van` → `/plan` → `/creative` → `/build` → `/reflect` → `/archive`) tracked under `memory-bank/`. Contributors do not need to touch these files for routine code changes, but if you're shipping a phase or a feature with cross-cutting impact, follow the existing pattern: update `tasks.md`, log progress in `progress.md`, and archive completed phases under `memory-bank/archive/`.
