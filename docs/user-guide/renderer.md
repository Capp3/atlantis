# Renderer (WebEngine + Mermaid)

The preview embeds **Mermaid.js 10.9.3** inside **Qt WebEngine** via a `QWebChannel` bridge (`atlantis/renderer/webengine_bridge.py`). The bridge is owned by `PreviewPane` and is active whenever `ATLANTIS_HEADLESS` is unset and `PyQt6-WebEngine` is installed. Tests run in headless mode and use a text fallback.

Design background:

- `memory-bank/creative/creative-renderer-offline-bundle.md`
- ADR [0001 — Mermaid via CDN for MVP](../adr/0001-mermaid-cdn-mvp.md) (historical)
- ADR [0003 — Offline Mermaid bundle](../adr/0003-mermaid-offline-bundle.md) (current default)

## Asset layout

Mermaid and the preview HTML shell ship under `atlantis/assets/`:

| Path | Role |
|------|------|
| `preview/preview_shell.html` | WebChannel + `atlantisRender` JS |
| `vendor/mermaid/mermaid.min.js` | Vendored Mermaid 10.9.3 |
| `vendor/mermaid/VERSION` | Plain-text version pin |

By default the bridge loads the **local** script via a `file://` base URL. Set `ATLANTIS_USE_MERMAID_CDN=1` to load from jsDelivr instead (debugging only).

## How a render flows

```
editor text change
      │
      ▼
debounced (500 ms) ────► WebEngineMermaidBridge.render(source)
                                    │
                                    ▼
                 JS shell installed once (local Mermaid + QWebChannel)
                                    │
                                    ▼
                 mermaid.render(id, source)  ── on success ──► report_svg ──► PreviewPane
                                    │           on failure ──► report_error ──► status bar
                                    ▼
                 15s timeout guard ─────────► report timeout ───► status bar
```

## Validating the stack independently

Run the standalone PoC at `scripts/tech_validation_mermaid_webengine.py` (uses the same vendored bundle by default):

```bash
uv run python scripts/tech_validation_mermaid_webengine.py
```

For a non-interactive smoke pass (still requires a working Qt WebEngine stack — not headless CI images):

```bash
uv run python scripts/tech_validation_mermaid_webengine.py --no-window
```

To compare against the CDN path:

```bash
ATLANTIS_USE_MERMAID_CDN=1 uv run python scripts/tech_validation_mermaid_webengine.py
# or
uv run python scripts/tech_validation_mermaid_webengine.py --cdn
```

On macOS, avoid `QT_QPA_PLATFORM=offscreen` for this script if you want the most reliable first run.

## Upgrading Mermaid

1. Bump `MERMAID_VERSION` in `atlantis/renderer/mermaid_assets.py`.
2. Run `uv run python scripts/fetch_mermaid_vendor.py`.
3. Re-run `uv run python scripts/tech_validation_mermaid_webengine.py` and the test suite.

## Tuning

- **Pinned version**: `MERMAID_VERSION` in `atlantis/renderer/mermaid_assets.py` (re-exported from `webengine_bridge.py`).
- **Theme**: `WebEngineMermaidBridge.set_theme("default" | "dark")`. Atlantis derives this from the `QApplication` palette automatically.
- **Timeout**: defaults to 15 s. The bridge emits a `BridgeRenderResult(ok=False, payload="Render timed out", …)` and the status bar surfaces it.

## Diagnostic logging

Renderer events use dedicated loggers (stdlib `logging`, no extra dependencies):

| Logger | Purpose |
|--------|---------|
| `atlantis.renderer.bridge` | Shell install/load, render dispatch, success, JS errors, timeouts |
| `atlantis.renderer.assets` | Asset session open, CDN script selection |

Enable verbose output:

```bash
uv run atlantis --log-level DEBUG
# or
ATLANTIS_LOG_LEVEL=DEBUG uv run atlantis
```

Example lines (grep-friendly `event=` prefix):

```text
event=shell_install mermaid_src=local theme=default
event=render_success elapsed_ms=42.1 source_chars=28
event=render_error elapsed_ms=12.0 source_chars=28 error=Parse error on line 1
event=shell_load_failed page_ready=false
event=render_timeout elapsed_ms=15000.0
```

Diagram source text is **not** logged at INFO or above — only `source_chars` for privacy and size.

## Headless / test behaviour

Setting `ATLANTIS_HEADLESS=1` swaps the `QWebEngineView` preview for a `QTextEdit` fallback so the test suite can exercise the surrounding logic without a real WebEngine. The opt-in `webengine` pytest marker exercises the real path (see [Contributing](../contributing.md#the-contributor-loop)).
