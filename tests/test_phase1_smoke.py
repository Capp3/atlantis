"""Bootstrap phase smoke tests."""

from __future__ import annotations

import os
import subprocess
import sys

from atlantis.model.diagram import DiagramDocument


def test_diagram_document_defaults() -> None:
    """Phase 1 model scaffolding should be importable and usable."""
    doc = DiagramDocument()
    assert doc.source == ""
    assert doc.front_matter == ""


def test_module_smoke_test_mode_exits_cleanly() -> None:
    """`python -m atlantis --smoke-test` should initialize then exit."""
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    env["ATLANTIS_HEADLESS"] = "1"
    completed = subprocess.run(
        [sys.executable, "-m", "atlantis", "--smoke-test"],
        check=False,
        env=env,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
