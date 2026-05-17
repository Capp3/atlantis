# Installation

Atlantis supports several install paths. **Contributors and most users** should use the Python package workflow; native bundles are experimental.

## Developer install (recommended)

Requires Python **3.12+** and [`uv`](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/capp3/atlantis.git
cd atlantis
uv sync
uv run atlantis
```

Run the headless smoke check:

```bash
uv run atlantis --smoke-test
```

See [Getting Started](../getting-started.md) and [Contributing](../contributing.md) for the full contributor loop (`make check-all`).

## Python wheel / sdist

Build artifacts from the repository root:

```bash
uv build
```

Install the wheel in another environment with a compatible Python and PyQt6 stack. The wheel includes `atlantis/assets` (offline Mermaid bundle). PyQt6 is **not** bundled inside the wheel — it remains a runtime dependency.

## Experimental Linux bundle (PyInstaller)

For desktop testers evaluating a standalone folder layout:

```bash
uv sync --group packaging
make bundle-smoke
```

This produces `dist/atlantis/` and runs `atlantis --smoke-test` on the bundled binary. Expect a large download (PyQt6 + WebEngine).

Details: `packaging/pyinstaller/README.md` and [ADR 0004](../adr/0004-native-bundle-pyinstaller.md).

**macOS and Windows** builds use the same spec file but are maintained manually; codesigning and installers are not part of the PoC.

## CI-built Linux bundle

Maintainers can produce a Linux one-folder bundle on GitHub without a local PyInstaller run:

1. Open **Actions → Bundle Linux (experimental)**.
2. Click **Run workflow** (requires `workflow_dispatch` permission on the repo).
3. When the job completes, download the **atlantis-linux-bundle-*** artifact from the run summary.
4. Extract and run `./atlantis --smoke-test` from the folder (same layout as local `dist/atlantis/`).

The artifact is large (PyQt6 + WebEngine) and retained for **14 days**. It is not attached to GitHub Releases yet.

## macOS 12 note

PyQt6 and PyQt6-WebEngine are pinned to **&lt; 6.10** (see [ADR 0002](../adr/0002-pyqt6-pin-macos-12.md)). Newer wheels may require macOS 13+.

## What is not available yet

- App Store or signed macOS `.app` distribution
- Windows installer (MSI/MSIX)
- Plugin packages or an extension marketplace
