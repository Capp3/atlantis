# GitHub Actions Workflows

| Workflow | File | Triggers | Purpose |
|----------|------|----------|---------|
| CI | `ci.yml` | PR, push to `main`, `workflow_dispatch` | `make format-check`, `make lint`, `make test-cov`, `make typecheck`; optional macOS WebEngine smoke |
| Docs | `docs.yml` | PR, push to `main`, `workflow_dispatch` | `make docs` (strict MkDocs); publishes `site/` to GitHub Pages on `main` |
| Bundle Linux (experimental) | `bundle.yml` | `workflow_dispatch` only | `uv sync --group packaging`, `make bundle-smoke`; uploads `dist/atlantis/` artifact (14-day retention) |

Local equivalents: `make check` (CI gates) and `make check-all` (+ docs). See `docs/contributing.md`.

Optional Vibe template Makefile (memory-bank installer): `make -f Makefile.vibe help`.
