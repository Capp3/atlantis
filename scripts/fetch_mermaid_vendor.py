#!/usr/bin/env python3
"""Download the pinned Mermaid.js bundle into ``atlantis/assets/vendor/mermaid/``.

Example::

    uv run python scripts/fetch_mermaid_vendor.py
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VENDOR_DIR = REPO_ROOT / "atlantis" / "assets" / "vendor" / "mermaid"

from atlantis.renderer.mermaid_assets import MERMAID_VERSION  # noqa: E402

CDN_URL = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js"


def main() -> int:
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    target = VENDOR_DIR / "mermaid.min.js"
    print(f"Fetching {CDN_URL} -> {target}")
    with urllib.request.urlopen(CDN_URL) as response:  # noqa: S310
        target.write_bytes(response.read())
    (VENDOR_DIR / "VERSION").write_text(f"{MERMAID_VERSION}\n", encoding="utf-8")
    size = target.stat().st_size
    print(f"Wrote {size:,} bytes to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
