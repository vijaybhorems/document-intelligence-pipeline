# Document Intelligence Pipeline

Takes messy commercial contracts in on one end and returns clean, validated, evidence-grounded JSON records on the other. Quality is measured against the [CUAD](https://www.atticusprojectai.org/cuad) expert labels, with precision and recall per field, broken down by field type.

- **Spec:** [docs/SPEC.md](docs/SPEC.md)
- **Decisions:** [docs/adr/](docs/adr/)
- **Phase notes:** [docs/notes/](docs/notes/)

## Status

Phase 3 (LLM extraction v0) complete. See the delivery plan in [SPEC §14](docs/SPEC.md#14-delivery-plan).

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
```

Runs live in `data/runs/<run_id>/` (predictions, per-field results as Parquet, per-call `usage.jsonl`, report). Committed reports: [docs/results/](docs/results/).

Tracing (optional): `docker compose -f docker/compose.yaml up -d phoenix`, set `DIP_OTEL_ENDPOINT=http://localhost:6006/v1/traces`, then open http://localhost:6006.

## Configuration

All settings come from `DIP_*` environment variables or a local `.env` file. Copy `.env.example` to `.env` to start. Never commit `.env`.
