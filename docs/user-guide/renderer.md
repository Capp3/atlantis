# Renderer (WebEngine + Mermaid)

The preview embeds **Mermaid.js 10.9.3** inside **Qt WebEngine** via a `QWebChannel` bridge (`atlantis/renderer/webengine_bridge.py`). The bridge is owned by `PreviewPane` and is active whenever `ATLANTIS_HEADLESS` is unset and `PyQt6-WebEngine` is installed. Tests run in headless mode and use a text fallback.

The full rationale, including why we ship as CDN-loaded JS for MVP rather than bundling, lives in:

- `memory-bank/creative/creative-renderer-offline-bundle.md`
- ADR [0001 — Mermaid via CDN for MVP](../adr/0001-mermaid-cdn-mvp.md)

## How a render flows

```
editor text change
      │
      ▼
debounced (500 ms) ────► WebEngineMermaidBridge.render(source)
                                    │
                                    ▼
                 JS shell installed once (Mermaid 10.9.3 + QWebChannel)
                                    │
                                    ▼
                 mermaid.render(id, source)  ── on success ──► report_svg ──► PreviewPane
                                    │           on failure ──► report_error ──► status bar
                                    ▼
                 15s timeout guard ─────────► report timeout ───► status bar
```

## Validating the stack independently

Run the standalone PoC bundled at `scripts/tech_validation_mermaid_webengine.py`:

```bash
uv run python scripts/tech_validation_mermaid_webengine.py
```

For a non-interactive smoke pass (still requires a working Qt WebEngine stack — not headless CI images):

```bash
uv run python scripts/tech_validation_mermaid_webengine.py --no-window
```

On macOS, avoid `QT_QPA_PLATFORM=offscreen` for this script if you want the most reliable first run.

## Tuning

- **Pinned version**: `MERMAID_VERSION = "10.9.3"` in `atlantis/renderer/webengine_bridge.py`. Bumping requires a re-run of the tech validation PoC.
- **Theme**: `WebEngineMermaidBridge.set_theme("default" | "dark")`. Atlantis derives this from the `QApplication` palette automatically.
- **Timeout**: defaults to 15 s. The bridge emits a `BridgeRenderResult(ok=False, payload="Render timed out", …)` and the status bar surfaces it.

## Headless / test behaviour

Setting `ATLANTIS_HEADLESS=1` swaps the `QWebEngineView` preview for a `QTextEdit` fallback so the test suite can exercise the surrounding logic without a real WebEngine. The opt-in `webengine` pytest marker exercises the real path (see [Contributing](../contributing.md#the-contributor-loop)).
