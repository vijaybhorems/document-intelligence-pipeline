# Phase 0: Foundations

**Goal (SPEC §14):** repo, tooling, CI skeleton, GCP project + budget alert.
**Done when:** CI is green and the budget alert is set.

## What was built

- [x] git repo, `uv` project (`pyproject.toml`, `uv.lock`, Python 3.13)
- [x] `src/dip` package: `config.py` (pydantic-settings, `DIP_*` env vars, secrets masked) and `cli.py` (`dip version`, `dip info`)
- [x] Unit tests (6) with coverage
- [x] ruff (lint + format), pyright, pytest wired into `make check`
- [x] pre-commit hooks: whitespace, YAML/TOML, private-key detection, large-file guard, uv-lock sync, ruff, pyright
- [x] GitHub Actions CI (`.github/workflows/ci.yml`), actions pinned to SHAs, Dependabot
- [x] ADR template + [ADR I7](../adr/I7-tooling.md)
- [ ] GitHub repo created and first CI run green
- [x] GCP bootstrap wizard: [`infra/bootstrap/gcp-bootstrap.sh`](../../infra/bootstrap/gcp-bootstrap.sh)
- [x] GCP projects (`dev`, `prod`) created and linked to billing (verified 2026-10-19: billing enabled on both)
- [x] Budget alerts set on the billing account: dev 20 USD, prod 10 USD, each scoped to its project, alerting at 50/90/100% actual and 100% forecast
- [ ] Budget screenshot in `docs/img/`

> Why a wizard script and not Terraform? Creating projects and linking billing is a one-time step done with your personal credentials, before any automation identity exists. From Phase 8, Terraform manages everything *inside* these projects.

## Concepts to understand before moving on

Answer these in your own words below. If you can't, re-read the linked file.

1. What does `uv.lock` guarantee that `pyproject.toml` alone doesn't? Why does CI run `uv sync --locked`?
2. Why does `config.py` type the API key as `SecretStr`? What does `dip info` print for it, and which test proves it?
3. Why are GitHub Actions pinned to a commit SHA instead of `@v7`?
4. What's the difference between a GCP **budget alert** and a hard spending cap? (Hint: a budget alert does not stop spending.)
5. Why separate `dev` and `prod` GCP projects instead of one project with two sets of resources?

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
