# Memory Bank: Tech Context

## Technology Stack
- **Language & Runtime**: Python >=3.12,<4.0 (primary target 3.12)
- **UI Framework**: PyQt6 (for native desktop widgets, WebEngine for Mermaid rendering)
- **Build/Packaging**: Hatchling (PEP 517/518), pyproject.toml managed
- **Type Checking**: mypy (strict mode: disallow_untyped_defs, etc.) — scoped to `atlantis/` in pyproject
- **Linting/Formatting**: ruff (comprehensive ruleset, line-length 120, preview format)
- **Testing**: pytest (tests/ dir), coverage via codecov
- **Docs**: mkdocs + mkdocs-material + mkdocstrings[python]
- **CI/Quality**: pre-commit, tox-uv, codecov.yaml
- **Version Control**: Git (main branch, GitHub repo at capp3/atlantis)

## Mermaid Integration
- Embedded via Qt WebEngine (`QWebEngineView`)
- **Default**: Mermaid **10.9.3** vendored at `atlantis/assets/vendor/mermaid/mermaid.min.js` (offline preview; see ADR `docs/adr/0003-mermaid-offline-bundle.md`)
- **CDN fallback**: `ATLANTIS_USE_MERMAID_CDN=1` → `https://cdn.jsdelivr.net/npm/mermaid@10.9.3/dist/mermaid.min.js`
- Rendering: `mermaid.initialize({ startOnLoad: false, securityLevel: "loose" })` then `mermaid.render(id, source)` in page JS; results returned to Python via **QWebChannel** on a small `QObject` bridge (`report_svg` / `report_error` slots)
- **JS diagnostics**: subclass `QWebEnginePage` and override `javaScriptConsoleMessage` (PyQt6 does not expose console output as a connectable signal on the default page)
- **Structured renderer logs**: `atlantis.renderer.bridge` and `atlantis.renderer.assets` emit `event=…` lines (`shell_install`, `render_success`, `render_error`, `render_timeout`, etc.); use `--log-level DEBUG` for diagnosis
- Editor-driven preview in the app remains debounced (500ms default) once the production bridge replaces the placeholder renderer

## Technology Validation PoC (committed)
- **Script**: `scripts/tech_validation_mermaid_webengine.py`
- **Run**: `uv run python scripts/tech_validation_mermaid_webengine.py` (omit `QT_QPA_PLATFORM=offscreen` for best results on macOS)
- **Automation-friendly**: `uv run python scripts/tech_validation_mermaid_webengine.py --no-window` (still needs a working WebEngine stack; may fail in some headless CI images)
- **Measured outcome (2026-05-11, local macOS)**: first successful `mermaid.render` → Python callback **~3.3s** (under the **4s** PoC target; includes CDN fetch + init)
- **VS Code**: task **Tech Validation: Mermaid WebEngine** in `.vscode/tasks.json`

## Project Structure (current)
- `atlantis/` : Main application package (implemented through BUILD Phase 3)
- `scripts/` : Standalone validation utilities (WebEngine + Mermaid PoC)
- `tests/` : Unit and integration tests
- `docs/` : MkDocs source
- `memory-bank/` : Core Memory Bank
- `.cursor/rules/` : Cursor AI rules including isolation_rules
- `.github/` : Dependabot, workflows
- `pyproject.toml` : Single source of truth for deps, tools config

## Development Environment
- Python environment manager: `uv` (required standard)
- Virtualenv location: `.venv` (managed through `uv sync`)
- OS Target: macOS primary for MVP (darwin), cross-platform later
- **macOS 12.x note**: PyQt6 / PyQt6-WebEngine pinned to **>=6.7,<6.10** (newer wheels may require macOS 13+)
- Runtime deps: stdlib + PyQt6 + PyQt6-WebEngine (dev deps in pyproject dependency-groups)
- Strict quality gates: ruff + pytest + **blocking mypy** on `atlantis/` (Qt accessors narrowed via `atlantis/ui/qt_accessors.py`)
- **Canonical local gate**: `make check` (PR) / `make check-all` (+ docs); CI workflows call the same Makefile targets
- **Optional native bundle**: `uv sync --group packaging` then `make bundle` / `make bundle-smoke` (PyInstaller one-folder; ADR `docs/adr/0004-native-bundle-pyinstaller.md`)
- **Plugins (v1 scaffold)**: `atlantis/plugins/` — `PluginRegistry` + manifest types; no dynamic loader

## Headless / CI Policy
- **`ATLANTIS_HEADLESS=1`**: App tests use text preview fallback instead of WebEngine where applicable
- **WebEngine-specific automated tests**: **opt-in only** (e.g. `ATLANTIS_WEBENGINE_TESTS=1` or a dedicated pytest marker) so default `pytest` stays green on hosts without a usable WebEngine display stack

## Constraints
- Offline-first final product (bundle assets)
- No telemetry
- Single-chart, file-based model (no workspace DB in MVP)
- Preserve Mermaid compatibility 100%

## Tooling Notes
- Use `uv` for environment and dependency management (do not use direct `pip` workflows in project docs/scripts)
- Pre-commit hooks for quality
- MkDocs for docs serving: `uv run mkdocs serve`
- Package build verification: `uv build` (produces `dist/` artifacts)
