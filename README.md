# Document Intelligence Pipeline

Takes messy commercial contracts in on one end and returns clean, validated, evidence-grounded JSON records on the other. Quality is measured against the [CUAD](https://www.atticusprojectai.org/cuad) expert labels, with precision and recall per field, broken down by field type.

- **Spec:** [docs/SPEC.md](docs/SPEC.md)
- **Decisions:** [docs/adr/](docs/adr/)
- **Phase notes:** [docs/notes/](docs/notes/)
- **Design guide** (every decision, and how to defend it): [docs/design-guide.md](docs/design-guide.md)

## Status

Phase 9.5 (MCP interface) complete: agents can search and cite the contracts through an MCP server, locally (Claude Desktop, stdio) or on Cloud Run with Google OAuth. With gold records, the same agent answers 93% of the task set; with ours, 64%. The gap is extraction, not tool design ([ADR D8](docs/adr/D8-mcp-tool-design.md)). The service runs on Google Cloud Run (dev), built with Terraform and deployed from GitHub Actions without stored keys. Records are compacted hourly into a Parquet lake that DuckDB queries straight from GCS, behind whitelisted `/v1/analytics` queries. Load-tested with 50 contracts: p95 63 s end to end for a ~20-page contract, 160 ms for status calls, $0.0061 median per contract, 50/50 succeeded ([numbers](docs/SPEC.md#121-non-functional-targets-measured)). The pipeline uses the hybrid route (pypdf text for born-digital PDFs, multimodal for scans) on gpt-5.6-luna. Current best on dev: **82.8 micro F1** at about $0.0075/contract. [Cost vs quality chart](docs/img/d1-d2-pareto.png).

## Quickstart

Requires [uv](https://docs.astral.sh/uv/). uv installs the right Python (3.13) for you.

```bash
make install     # create .venv, install deps, install git hooks
make check       # lint + format check + typecheck + tests (same as CI)
uv run dip --help
```

## Common tasks

| Command | What it does |
|---|---|
| `make fmt` | Auto-format and auto-fix lint issues |
| `make lint` | Ruff lint + format check |
| `make typecheck` | Pyright |
| `make test` | Unit tests with coverage |
| `make check` | Everything CI runs |
| `make up` / `make down` | Start / stop the service stack (docker compose) |
| `make e2e` | One contract through the running stack |
| `make loadtest` | 50 contracts against the deployed API, with Locust |

## Google Cloud setup (one-time)

Creates the `dev` and `prod` projects, links billing, and sets monthly budget alerts. It's interactive and safe to re-run.

```bash
./infra/bootstrap/gcp-bootstrap.sh
```

## Data (Phase 1)

```bash
uv run dip download-cuad   # 106 MB from Zenodo, MD5-verified, into data/raw/
uv run dip build-gold      # data/gold/*.json + Parquet tables
uv run dip profile-pdfs    # text-layer coverage of every PDF
uv run dip cuad-report     # regenerates docs/notes/cuad-dataset-profile.md
```

`data/splits.json` is committed and frozen. `dip make-splits` won't overwrite it without `--force`. Findings: [CUAD quirks](docs/notes/cuad-quirks.md), [dataset profile](docs/notes/cuad-dataset-profile.md).

## Evaluation (Phase 2)

```bash
uv run dip eval --system keyword --split dev              # predict + score + report
uv run dip report <run_id> --compare <other_run_id>       # re-render, with a comparison
```

```bash
uv run dip estimate --system llm --split dev                          # tokens + cost, no API calls
uv run dip eval --system llm --strategy single --split dev           # needs DIP_OPENAI_API_KEY
uv run dip spend                                                       # spend so far vs DIP_BUDGET_USD
uv run dip validate <run_id> --policy warn --reask                    # ground + check + re-ask failing fields
uv run dip eval --system llm --split dev --prompt-version v1          # earlier prompt (default: v4)
uv run dip eval --system llm --split dev --context retrieved          # LlamaIndex retrieval instead of the full contract
uv run dip build-field-notes                                          # rebuild prompt examples from train
uv run dip eval --system llm --split experiment --route hybrid        # production route (D1)
uv run dip make-scans --split experiment                              # synthetic image-only scans
uv run dip pareto --split experiment                                  # cost vs F1 chart (needs dev deps)
```

Runs live in `data/runs/<run_id>/` (predictions, per-field results as Parquet, per-call `usage.jsonl`, report). Committed reports: [docs/results/](docs/results/).

Tracing (optional): `docker compose -f docker/compose.yaml up -d phoenix`, set `DIP_OTEL_ENDPOINT=http://localhost:6006/v1/traces`, then open http://localhost:6006.

## Service (Phase 7)

The API takes a PDF or text contract and returns a job; a worker extracts, validates and stores a `ContractRecord`. Endpoints, auth and retry rules are in [SPEC §12](docs/SPEC.md#12-interfaces-rest-api-and-mcp).

**Without Docker** (local backend: files on disk, jobs in memory, worker in-process):

```bash
DIP_ENV=dev uv run uvicorn dip.api.app:create_app --factory --port 8080
uv run dip submit path/to/contract.pdf          # upload, poll, print a summary
```

**With docker compose** (the Cloud Run code path, with GCS and Firestore emulators, and the worker as its own container):

```bash
make up      # build and start; needs DIP_OPENAI_API_KEY in .env
make e2e     # one CUAD contract end to end, about $0.01
make logs
make down
```

By hand:

```bash
curl -H 'X-API-Key: local-dev-key' -F file=@contract.pdf localhost:8080/v1/extractions
curl -H 'X-API-Key: local-dev-key' localhost:8080/v1/extractions/<job_id>
curl -H 'X-API-Key: local-dev-key' localhost:8080/v1/extractions/<job_id>/record
```

Interactive docs are at <http://localhost:8080/docs>, and traces at <http://localhost:6006> (Phoenix).

## Deployment (Phase 8)

```text
client ──X-API-Key──▶ dip-api (Cloud Run, public) ──▶ GCS raw/ · Firestore job · Cloud Tasks
                                                                         │ OIDC
                          dip-worker (Cloud Run, internal) ◀─────────────┘
                            ──▶ OpenAI · GCS records/ · Firestore · Arize traces
```

- **Infrastructure:** [`infra/terraform`](infra/terraform), applied by a person ([ADR I10](docs/adr/I10-deploy-responsibility.md)).
- **Deploys:** every merge to `main` builds the image and rolls it out ([`deploy.yml`](.github/workflows/deploy.yml)). GitHub authenticates through Workload Identity Federation, so there are no service-account keys.
- **Operations:** first deploy, rollback, key rotation and incidents are in the [runbook](docs/runbook.md).

```bash
uv run dip submit contract.pdf --api "$(terraform -chdir=infra/terraform output -raw api_url)"   # key: DIP_API_KEY in .env
```

## Analytics (Phase 9)

`dip-compactor` turns `records/*.json` into Parquet tables (`records`, `record_fields`) every hour. `GET /v1/analytics/{name}` runs one of a fixed set of queries over them. The API never accepts SQL.

```bash
curl -H "X-API-Key: $DIP_API_KEY" "$API/v1/analytics"                                 # the queries and their parameters
curl -H "X-API-Key: $DIP_API_KEY" "$API/v1/analytics/clause_prevalence?min_contracts=3"
uv run dip lake-push-evals --bucket dip-dev-c7a284e91f63-docs                          # eval runs -> lake/eval/
uv run dip query eval_by_route_model split=experiment                                   # same queries, from the CLI
```

| Query | Answers |
|---|---|
| `clause_prevalence` | which clauses each contract type contains |
| `governing_law` | governing-law distribution |
| `production_by_route` | service cost and latency by route and model |
| `eval_by_route_model` | eval F1, cost and latency by route, model, prompt and strategy (D1–D5 tables) |
| `field_regressions` | fields whose F1 dropped between two eval runs |

**Load test:** `make loadtest`, which runs 50 train contracts, costs ~$0.45 and is capped at $1.50.

## Agent access: MCP (Phase 9.5)

The same contracts, as tools an AI agent can call (SPEC §12.2):

| Tool | For |
|---|---|
| `search_records` | "which contracts…": every filter in one call, with a quote per matched clause |
| `get_record` | one contract, projected to the fields you ask for, each with evidence |
| `run_analytics` | the analytics queries above |
| `submit_extraction` / `get_extraction_status` | add a document (https URL or the bucket's `inbox/`) and poll it |

**Locally (Claude Desktop):** add this under `mcpServers` in `claude_desktop_config.json` (needs `uv run dip agent-eval prepare` once, to build the store):

```json
"dip": {
  "command": "/path/to/uv",
  "args": ["--directory", "/path/to/document_intelligence_pipeline",
           "run", "dip", "mcp-stdio", "--store", "data/mcp-store/normal"]
}
```

**Deployed:** `https://dip-mcp-<project-number>.us-central1.run.app/mcp`, with Google OAuth ([ADR I8](docs/adr/I8-mcp-authorization.md)). Setup is `./infra/bootstrap/dip-mcp-oauth.sh`, then `dip principals add <email>`. Connecting MCP Inspector is described in the [runbook](docs/runbook.md#mcp-dip-mcp).

**Measuring tool design:** `uv run dip agent-eval run --store normal|oracle --descriptions v1|v2 --granularity coarse|fine` runs 25 gold-derived tasks through an agent (about $0.05 per variant).

## Configuration

All settings come from `DIP_*` environment variables or a local `.env` file. Copy `.env.example` to `.env` to start. Never commit `.env`.
