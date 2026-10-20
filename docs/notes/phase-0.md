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
- [x] GitHub repo created (private) and first CI run green (2026-10-19)
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

1. What does `uv.lock` guarantee that `pyproject.toml` alone doesn't? Why does CI run `uv sync --locked`?

`pyproject.toml` defines your project's broad intent (e.g., "I need `requests` version 2.31 or higher"), while `uv.lock` guarantees absolute **reproducibility** by freezing the exact state of your dependency tree.

**What `uv.lock` Guarantees Over `pyproject.toml**`

* **Exact Transitive Dependencies:** `pyproject.toml` only lists top-level requirements. If you specify `requests >= 2.31`, `requests` will pull in its own sub-dependencies (like `urllib3`). Without a lockfile, installing the project tomorrow might pull a newly released, potentially breaking version of `urllib3`. `uv.lock` pins every single package down to the bottom of the tree to a specific version.
* **Cryptographic Hashes:** The lockfile stores the SHA-256 hashes of the downloaded wheels and source distributions. This guarantees you are installing the exact same bytes every time, protecting against supply chain attacks where a compromised package is silently replaced on PyPI.
* **Universal Cross-Platform Resolution:** Unlike traditional `requirements.txt` files which are often environment-specific, `uv`'s lockfile is universal by default. It captures the resolved dependency tree for all target operating systems, architectures, and Python versions, guaranteeing the project will resolve correctly whether deployed on a Linux server or an Apple Silicon Mac.

**Why CI Runs `uv sync --locked**`

* **Prevents Silent Drift:** The `--locked` flag tells `uv` to install strictly from `uv.lock` and completely forbids it from updating the lockfile. If a developer updates `pyproject.toml` but forgets to run `uv lock` locally and commit the resulting changes, the CI pipeline will fail immediately rather than silently fixing the mismatch on the fly.
* **Guarantees "Works on My Machine" = "Works in Production":** By strictly enforcing the lockfile, CI runs your test suite against the exact same dependency tree the developer tested locally. If CI passes, you know with certainty that production deployments using that lockfile won't break due to a surprise upstream package update.
* **Maximum Speed:** Because the resolution phase is entirely bypassed, CI doesn't have to query PyPI to figure out what package versions are compatible. It simply reads the lockfile and immediately downloads and installs the pinned wheels.

2. Why does `config.py` type the API key as `SecretStr`? What does `dip info` print for it, and which test proves it?

Why config.py types the API key as SecretStr
Typing an API key as a SecretStr (a feature from the pydantic and pydantic-settings libraries) is a security measure. It ensures that sensitive credentials are fundamentally protected from accidental exposure. If the application crashes, a traceback occurs, or the configuration object is serialized into JSON, SecretStr prevents the raw API key from being leaked in plain text.

What dip info prints for it
Because of the SecretStr typing, when dip info (or any internal CLI dump/logging command) attempts to display the configuration state, it will mask the actual key and print exactly:
********** (ten asterisks)

To actually use the key in the code, the application has to explicitly call .get_secret_value() on the field, which ensures the raw string is only ever accessed deliberately.

Which test proves it
While the exact file path depends on your specific codebase, this behavior is typically verified by a configuration or CLI test (often named something like test_info, test_cli_info, or test_config_secrets_hidden). The test executes the info command, captures standard output (stdout), and explicitly asserts two things:
a. That ********** is present in the output.
b. That the raw, mocked API key string used for the test environment is not present in the output.

3. Why are GitHub Actions pinned to a commit SHA instead of `@v7`?

Pinning GitHub Actions to a commit SHA rather than a tag like `@v7` is a defense against **supply chain attacks**. It guarantees absolute immutability for the code executing in your CI/CD pipeline.

* **Tags are Mutable:** A tag like `@v7` or `@v7.1.0` is just a pointer. If an attacker compromises the repository of a popular GitHub Action, they can inject malicious code—often designed to steal deployment secrets or API keys—and forcefully move the `v7` tag to point to their new commit. Any CI pipeline running `uses: some-action@v7` will instantly pull and execute the compromised code on its next run.
* **SHAs are Immutable:** A commit SHA (e.g., `@a1b2c3d...`) is a cryptographic hash of an exact code snapshot. It cannot be altered, forged, or overwritten. Pinning to a SHA ensures that the action will execute the exact same files every single time, making silent malicious updates impossible.
* **Strict Reproducibility:** Even without malicious intent, maintainers sometimes accidentally introduce breaking changes or bugs into a major version tag. A SHA guarantees your pipeline won't suddenly fail due to an unannounced upstream push.

Because SHAs are difficult for humans to parse, the standard industry practice is to pin to the SHA but include the version tag as an inline comment:

```yaml
steps:
  - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1

```

Teams then use automated dependency management tools, like Dependabot or Renovate, to automatically open pull requests that update both the SHA and the comment when a new legitimate version is released.

4. What's the difference between a GCP **budget alert** and a hard spending cap? (Hint: a budget alert does not stop spending.)

Here is the difference between a GCP budget alert and a hard spending cap:

**Budget Alert**
A budget alert is strictly a **notification system**. When your Google Cloud spending crosses a defined threshold (e.g., 50% or 100% of a target amount), GCP sends an email to billing administrators or publishes a message to a Pub/Sub topic. Crucially, a budget alert **does not stop your resources from running or accruing charges**. If a runaway workload spikes your bill at 2:00 AM on a weekend, the alert will fire, but the workload will continue to run—and cost money—until a human logs in and manually intervenes (or unless you have custom automation configured).

**Spend Cap**
A spend cap (a newer feature currently rolling out for specific services like Cloud Run and Gemini) acts as an **automated emergency brake**. When a spend cap budget reaches its 100% threshold, GCP automatically pauses new usage and stops cost accrual for the eligible services without requiring human intervention. It blocks new requests while allowing in-flight requests to complete. Spend caps are non-destructive (they do not delete your data or resources) and can be lifted with a single click in the billing console to restore service.

**The Historical Workaround (The "Kill Switch")**
Before native spend caps existed (and currently, for services not yet supported by spend caps), teams requiring a hard stop had to build custom automation. This involved linking a budget alert's Pub/Sub output to a Cloud Function that programmatically disabled the billing account on the project. This custom method acts as a severe hard cap: disabling billing instantly shuts down all resources (Compute Engine, Cloud SQL, etc.) and can result in irreversible data loss, making it suitable only for dev or sandbox environments, not production.

5. Why separate `dev` and `prod` GCP projects instead of one project with two sets of resources?

In Google Cloud Platform (GCP), a "project" is the fundamental boundary for security, billing, and resource management. Best practice dictates creating completely separate projects for `dev` and `prod` rather than lumping them together, for four core reasons:

* **IAM & Security Boundaries:** Projects are the primary trust boundary in GCP. If `dev` and `prod` share a project, a developer with "Editor" access to tweak a dev database might accidentally drop the production database. Separate projects allow you to enforce strict Zero Trust—developers have access to `dev`, but only CI/CD pipelines and specific leads have access to `prod`.
* **Blast Radius Containment:** If a developer accidentally runs a script in `dev` that spins up 1,000 VMs or triggers an infinite loop of Pub/Sub messages, it will consume all the API quota for that project. If `dev` and `prod` share a project, the production application will crash because it cannot allocate resources. Separate projects mean separate quotas.
* **Clear Billing Allocation:** A project is the lowest level at which you can easily view a unified invoice. Separate projects allow you to see exactly how much your production traffic costs versus how much your development and testing overhead costs, making budget forecasting much easier.
* **Safe Decommissioning:** When a dev environment becomes messy or is no longer needed, you can delete the entire `dev` project in one click, instantly wiping all its resources. If dev and prod share a project, you have to surgically delete dev resources one by one, risking an accidental deletion of a prod asset.

## What surprised me

<!-- Fill in. -->
