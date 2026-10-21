# Document Intelligence Pipeline

Takes messy commercial contracts in on one end and returns clean, validated, evidence-grounded JSON records on the other. Quality is measured against the [CUAD](https://www.atticusprojectai.org/cuad) expert labels, with precision and recall per field, broken down by field type.

- **Spec:** [docs/SPEC.md](docs/SPEC.md)
- **Decisions:** [docs/adr/](docs/adr/)
- **Phase notes:** [docs/notes/](docs/notes/)

## Status

Phase 7 (service) complete: upload a contract to a FastAPI service, poll the job, and fetch a validated record, locally or in docker compose with GCP emulators. The pipeline uses the hybrid route (pypdf text for born-digital PDFs, multimodal for scans) on gpt-5.6-luna. Current best on dev: **82.8 micro F1** at about $0.0075/contract. [Cost vs quality chart](docs/img/d1-d2-pareto.png).

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

## Configuration

All settings come from `DIP_*` environment variables or a local `.env` file. Copy `.env.example` to `.env` to start. Never commit `.env`.
