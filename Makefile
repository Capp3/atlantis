# Atlantis development Makefile — canonical local quality gates (mirrors CI).
# Equivalent uv run commands: docs/contributing.md
# Optional Vibe template tooling: make -f Makefile.vibe help

UV ?= uv

export QT_QPA_PLATFORM ?= offscreen
export ATLANTIS_HEADLESS ?= 1

.DEFAULT_GOAL := help

.PHONY: help sync format format-check lint lint-fix typecheck test test-cov docs docs-serve pre-commit check check-all webengine bundle bundle-smoke clean

help: ## Show available targets
	@grep -hE '^[a-zA-Z0-9_.-]+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*## */ | /' | column -t -s '|' 2>/dev/null || grep -hE '^[a-zA-Z0-9_.-]+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*## */ - /'

sync: ## Install/sync dependencies with uv
	$(UV) sync

format: ## Apply ruff formatter
	$(UV) run ruff format .

format-check: ## Check formatting (CI)
	$(UV) run ruff format --check .

lint: ## Run ruff linter (CI)
	$(UV) run ruff check .

lint-fix: ## Run ruff linter with auto-fix
	$(UV) run ruff check . --fix

typecheck: ## Run mypy on atlantis (CI)
	$(UV) run mypy atlantis

test: ## Run pytest default suite (offscreen)
	$(UV) run pytest -q

test-cov: ## Run pytest with coverage (CI)
	$(UV) run pytest --cov=atlantis --cov-report=term-missing --cov-report=xml -q

docs: ## Build documentation strict (CI docs job)
	$(UV) run mkdocs build --strict

docs-serve: ## Serve documentation with live reload
	$(UV) run mkdocs serve

pre-commit: ## Run all pre-commit hooks
	$(UV) run pre-commit run --all-files

check: format-check lint typecheck test-cov ## PR gate: format + lint + type + test+cov

check-all: check docs ## Full loop: PR gate + strict docs

webengine: ## Opt-in WebEngine tests (desktop Qt; set ATLANTIS_WEBENGINE_TESTS=1)
	ATLANTIS_WEBENGINE_TESTS=1 $(UV) run pytest -m webengine -q

bundle: ## Build PyInstaller one-folder dist (requires: uv sync --group packaging)
	$(UV) run pyinstaller --noconfirm --distpath dist --workpath build/pyinstaller packaging/pyinstaller/atlantis.spec

bundle-smoke: bundle ## Run smoke-test on bundled binary (offscreen)
	dist/atlantis/atlantis --smoke-test

clean: ## Remove build artifacts and test caches
	rm -rf site/ .cache/ .pytest_cache/ htmlcov/ .coverage coverage.xml dist/ build/pyinstaller/
