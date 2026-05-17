# PyInstaller bundle (experimental)

One-folder desktop bundle for Atlantis. This is a **proof of concept** for Linux; macOS `.app` and Windows installers are documented manually until a later phase.

## Prerequisites

```bash
uv sync --group packaging
```

Respect the PyQt6 pin in `pyproject.toml` (ADR 0002: `PyQt6<6.10` on macOS 12).

## Build (from repository root)

```bash
make bundle
```

Output: `dist/atlantis/atlantis` (executable) plus collected PyQt6/WebEngine libraries and `atlantis/assets`.

## Smoke test

```bash
make bundle-smoke
```

Runs `dist/atlantis/atlantis --smoke-test` with offscreen Qt env vars (same as pytest harness).

## Expected size

Hundreds of MB — PyQt6 + Qt WebEngine dominate the bundle.

## macOS / Windows (manual)

1. Install the `packaging` dependency group on the target OS.
2. From repo root: `uv run pyinstaller --noconfirm --distpath dist --workpath build/pyinstaller packaging/pyinstaller/atlantis.spec`
3. Run `dist/atlantis/atlantis --smoke-test` on a machine with a display or offscreen platform plugin.
4. Codesigning (macOS) and installers are **out of scope** for this PoC.

## Troubleshooting

- **Missing WebEngine**: ensure `collect_all('PyQt6')` ran; add hidden imports in `atlantis.spec` if needed.
- **Missing Mermaid assets**: verify `atlantis/assets` appears under `dist/atlantis/_internal/atlantis/assets` (layout may vary by PyInstaller version).
- **CDN preview in bundle**: default is offline vendor JS; do not set `ATLANTIS_USE_MERMAID_CDN` unless debugging.

## References

- ADR `docs/adr/0004-native-bundle-pyinstaller.md`
- `docs/user-guide/installation.md`
