"""CI/docs hygiene regression tests (workflow layout + hook pins)."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_ci_workflow_has_no_redundant_docs_build_job() -> None:
    ci = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "docs-build:" not in ci
    assert "mkdocs build" not in ci


def test_docs_workflow_builds_strict_and_publishes_site_directory() -> None:
    docs = (REPO_ROOT / ".github/workflows/docs.yml").read_text(encoding="utf-8")
    assert "pull_request:" in docs
    assert "mkdocs build --strict" in docs
    assert "upload-artifact@v4" in docs
    assert re.search(r"upload-artifact@v4[\s\S]*?path:\s*site/?", docs)
    pages = re.search(
        r"upload-pages-artifact@v\d+[\s\S]*?path:\s*(\S+)",
        docs,
    )
    assert pages is not None
    assert pages.group(1).rstrip("/") == "site"
    assert "path: docs/" not in docs


def test_ci_type_check_job_is_blocking() -> None:
    ci = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    type_check_block = re.search(r"type-check:[\s\S]*?(?=\n  \w|\Z)", ci)
    assert type_check_block is not None
    block = type_check_block.group(0)
    assert "continue-on-error: true" not in block
    assert "make typecheck" in block


def test_ci_lint_job_uses_makefile_targets() -> None:
    ci = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    lint_block = re.search(r"lint-and-test:[\s\S]*?(?=\n  \w|\Z)", ci)
    assert lint_block is not None
    block = lint_block.group(0)
    assert "make format-check" in block
    assert "make lint" in block
    assert "make test-cov" in block


def test_docs_workflow_uses_make_docs() -> None:
    docs = (REPO_ROOT / ".github/workflows/docs.yml").read_text(encoding="utf-8")
    assert "make docs" in docs


def test_pre_commit_includes_mypy_hook() -> None:
    pre_commit = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "id: mypy" in pre_commit
    assert "uv run mypy atlantis" in pre_commit


def test_pre_commit_ruff_rev_matches_pyproject_floor() -> None:
    pre_commit = (REPO_ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    rev_match = re.search(
        r"github\.com/astral-sh/ruff-pre-commit[\s\S]*?rev:\s*v(\d+\.\d+\.\d+)",
        pre_commit,
    )
    floor_match = re.search(r'"ruff>=(\d+\.\d+\.\d+)"', pyproject)
    assert rev_match is not None
    assert floor_match is not None
    assert rev_match.group(1) >= floor_match.group(1)


def test_bundle_workflow_is_dispatch_only() -> None:
    bundle = (REPO_ROOT / ".github/workflows/bundle.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in bundle
    assert "pull_request:" not in bundle
    assert re.search(r"^\s+push:\s*$", bundle, re.MULTILINE) is None


def test_bundle_workflow_uses_make_bundle_smoke() -> None:
    bundle = (REPO_ROOT / ".github/workflows/bundle.yml").read_text(encoding="utf-8")
    assert "make bundle-smoke" in bundle
    assert "--group packaging" in bundle


def test_bundle_workflow_uploads_dist_atlantis() -> None:
    bundle = (REPO_ROOT / ".github/workflows/bundle.yml").read_text(encoding="utf-8")
    assert "upload-artifact@v4" in bundle
    assert re.search(r"path:\s*dist/atlantis/?", bundle) is not None


def test_bundle_workflow_has_sufficient_timeout() -> None:
    bundle = (REPO_ROOT / ".github/workflows/bundle.yml").read_text(encoding="utf-8")
    timeout = re.search(r"timeout-minutes:\s*(\d+)", bundle)
    assert timeout is not None
    assert int(timeout.group(1)) >= 30
