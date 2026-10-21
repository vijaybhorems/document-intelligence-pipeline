.DEFAULT_GOAL := help
.PHONY: help install fmt lint typecheck test check hooks clean up down logs e2e loadtest

help: ## List targets
	@grep -E '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{gsub(/\$$\$$/, "$$", $$2); printf "  %-10s %s\n", $$1, $$2}'

install: ## Create .venv, install locked deps (+ optional Docling), install git hooks
	uv sync --locked --extra docling
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

COMPOSE := docker compose --env-file .env -f docker/compose.yaml
# A 5-page born-digital CUAD contract (experiment split); override with E2E_PDF=path.
E2E_PDF ?= data/raw/CUAD_v1/full_contract_pdf/Part_III/Transportation/MARTINMIDSTREAMPARTNERSLP_01_23_2004-EX-10.3-TRANSPORTATION SERVICES AGREEMENT.PDF

up: ## Build and start the service stack (API, worker, GCS + Firestore emulators, Phoenix)
	$(COMPOSE) up -d --build --wait

down: ## Stop the stack and delete its state
	$(COMPOSE) down --volumes

logs: ## Follow API and worker logs
	$(COMPOSE) logs -f api worker

e2e: ## Upload a contract to the running stack, poll, fetch the record (~$$0.01)
	uv run dip submit "$(E2E_PDF)" --api http://localhost:8080 --api-key "$${DIP_API_KEYS:-local-dev-key}"

loadtest: ## 50 contracts against the deployed dev API, ~$$0.45, capped at $$1.50
	uv run python loadtest/prepare.py
	uv run locust -f loadtest/locustfile.py --headless -u 10 -r 1 --run-time 30m \
		--host "$$(terraform -chdir=infra/terraform output -raw api_url)" --csv data/loadtest/locust --only-summary

clean: ## Remove caches
	rm -rf .ruff_cache .pytest_cache .coverage htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
