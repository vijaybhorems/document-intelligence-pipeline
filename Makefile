.DEFAULT_GOAL := help
.PHONY: help install fmt lint typecheck test check hooks clean

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

install: ## Create .venv, install locked deps, install git hooks
	uv sync --locked
	uv run pre-commit install

fmt: ## Auto-format and apply safe lint fixes
	uv run ruff format .
	uv run ruff check --fix .

lint: ## Lint and check formatting (no changes)
	uv run ruff check .
	uv run ruff format --check .

typecheck: ## Static type check
	uv run pyright

test: ## Unit tests with coverage
	uv run pytest --cov --cov-report=term-missing

check: lint typecheck test ## Everything CI runs

hooks: ## Run all pre-commit hooks on every file
	uv run pre-commit run --all-files

clean: ## Remove caches
	rm -rf .ruff_cache .pytest_cache .coverage htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
