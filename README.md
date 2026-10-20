# Document Intelligence Pipeline

Takes messy commercial contracts in on one end and returns clean, validated, evidence-grounded JSON records on the other. Quality is measured against the [CUAD](https://www.atticusprojectai.org/cuad) expert labels, with precision and recall per field, broken down by field type.

- **Spec:** [docs/SPEC.md](docs/SPEC.md)
- **Decisions:** [docs/adr/](docs/adr/)
- **Phase notes:** [docs/notes/](docs/notes/)

## Status

Phase 0 (foundations). See the delivery plan in [SPEC §14](docs/SPEC.md#14-delivery-plan).

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

## Configuration

All settings come from `DIP_*` environment variables or a local `.env` file. Copy `.env.example` to `.env` to start. Never commit `.env`.
