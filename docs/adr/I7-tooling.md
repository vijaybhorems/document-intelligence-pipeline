# ADR I7: Python tooling

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-17 |
| **Spec ref** | SPEC §3.3, I7 |

## Context

The project will grow into an API, a worker, an eval harness and a CLI, with ML-heavy dependencies (Docling, PyTorch) in some images and slim ones in others. It needs reproducible installs locally, in CI and in Docker, plus fast feedback on style and type errors.

## Options considered

1. **uv + ruff + pyright + pytest + pre-commit.**
2. **Poetry + black + isort + flake8 + mypy.**
3. **pip-tools + ruff + mypy.**

## Decision

Option 1:

| Tool | Role | Why |
|---|---|---|
| **uv** | Python version, venv, dependency resolution, `uv.lock` | One tool replaces pyenv + pip + pip-tools + virtualenv. The lockfile gives identical installs in CI and Docker (`uv sync --locked`). Very fast, which matters in CI and image builds. |
| **ruff** | Lint and format | Replaces black, isort, flake8 and its plugins with one fast binary. The rule set includes security (`S`) and timezone (`DTZ`) checks, which matter for date extraction. |
| **pyright** (`standard` mode) | Static types | Fast, with good Pydantic support. Installed via `pyright[nodejs]`, so there's no separate Node setup. `standard` rather than `strict`, because Docling and other ML libraries are only partly typed. Tighten per module later. |
| **pytest** + pytest-cov | Tests | De facto standard. `integration` and `llm` markers keep slow and paid tests out of the default run. |
| **pre-commit** | Local gate | Runs the same checks as CI before each commit, plus secret detection and a large-file guard (CUAD PDFs must never be committed). |

**Python 3.13**, pinned in `.python-version` and `requires-python`.

## Consequences

- One command (`make check`) is the definition of "green", locally and in CI.
- GitHub Actions are pinned to commit SHAs. Dependabot proposes updates weekly.
- **Revisit if:** Docling or PyTorch wheels lag on Python 3.13 (drop to 3.12), or pyright `standard` lets real bugs through (move core modules to `strict`).
