# Getting Started

This page covers installation, the smoke-test flow, and the first interactive launch.

## Prerequisites

- macOS, Linux, or Windows with a working Qt-capable desktop session.
- Python **3.12+** managed by [`uv`](https://github.com/astral-sh/uv).
- On **macOS 12**, the `PyQt6 < 6.10` / `PyQt6-WebEngine < 6.10` pin is mandatory (newer wheels require macOS 13+). This is already declared in `pyproject.toml`.

## Install

```bash
git clone https://github.com/capp3/atlantis.git
cd atlantis
uv sync
```

## First run

```bash
uv run atlantis
```

The app opens with a two-pane window: source editor on the left, Mermaid live preview on the right. Typing in the editor triggers a debounced render through the WebEngine bridge (see [Renderer](user-guide/renderer.md)).

## Headless smoke test

CI and contributors can confirm the package boots without a display:

```bash
uv run atlantis --smoke-test
```

This sets `ATLANTIS_HEADLESS=1`, initialises the application, and exits cleanly.

## Running the tests

```bash
uv run pytest -q
```

To enable the opt-in WebEngine smoke test (requires a real desktop Qt session — not a headless CI image):

```bash
ATLANTIS_WEBENGINE_TESTS=1 uv run pytest -m webengine -q
```

## Logging

```bash
uv run atlantis --log-level DEBUG
# or:
ATLANTIS_LOG_LEVEL=DEBUG uv run atlantis
```

Atlantis writes logs to the platform-standard app-data path and streams the same records to stderr. See the [Troubleshooting page](user-guide/troubleshooting.md) for details on what gets logged when.

## Next steps

- Read the [Editor guide](user-guide/editor.md) to learn the shortcuts, autosave behaviour, and recent-files workflow.
- See [Front matter](user-guide/front-matter.md) for YAML/TOML support and **View → Edit Front Matter…** for TOML metadata.
- See the [Examples gallery](user-guide/examples.md) for working diagrams you can paste into the editor.
