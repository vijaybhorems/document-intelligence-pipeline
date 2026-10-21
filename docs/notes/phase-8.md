# Phase 8: Cloud deploy

**Goal (SPEC §14):** Terraform, Cloud Run, Cloud Tasks, Firestore, Secret Manager, WIF CI/CD, Arize in prod.
**Done when:** a live dev URL processes a CUAD PDF, with no long-lived keys anywhere.

## What was built

- [x] **Terraform** (`infra/terraform`): one root module, one tfvars and state prefix per environment; state in a versioned, private GCS bucket. Provider pinned (`~> 8.6.0`) with a lock file for macOS and Linux. Files by concern:

  | File | What it holds |
  |---|---|
  | `apis.tf` | the 10 Google APIs |
  | `storage.tf` | docs bucket (`raw/` deleted after 30 days, `records/` kept); Firestore `(default)` (delete-protected); Artifact Registry (keeps 10 images) |
  | `secrets.tf` | the 3 secrets, created empty |
  | `iam.tf` | 4 service accounts and their grants |
  | `queue.tf` | Cloud Tasks (rate cap, 5 delivery attempts) |
  | `run.tf` | the two Cloud Run services |
  | `github.tf` | Workload Identity Federation and the deployer account |

- [x] **Least privilege**, one service account per job:

  | Account | Can |
  |---|---|
  | `sa-api` | create and read objects (not delete or overwrite), use Firestore, enqueue to one queue, read `api-keys`, and mint tokens as `sa-tasks-invoker` |
  | `sa-worker` | the same storage and Firestore access, plus read the OpenAI and Arize secrets |
  | `sa-tasks-invoker` | invoke `dip-worker` |
  | `sa-deployer` | push to one image repository, update the two services, and run them as their accounts |

- [x] **Cloud Run:** `dip-api` is public (no IAM check, API key in the app). `dip-worker` has internal ingress, `run.invoker` for `sa-tasks-invoker` only, and the app verifies the OIDC token again. Both scale to zero, `max-instances` 2, request-based CPU billing. Their URLs are deterministic, so the API knows the worker's address and the worker knows its OIDC audience before either exists.
- [x] **Secrets** never touch Terraform state: [`infra/bootstrap/dip-secrets.sh`](../../infra/bootstrap/dip-secrets.sh) pipes values to Secret Manager on stdin.
- [x] **CI/CD without keys:** [`deploy.yml`](../../.github/workflows/deploy.yml) on merge to `main`. GitHub OIDC is exchanged for the deployer through Workload Identity, which accepts only this repository's numeric ID and name, on `refs/heads/main`. The workflow builds and pushes, deploys by **digest** (worker first), and smoke-tests. CI also runs `terraform fmt`/`validate`, and Dependabot watches the Terraform provider.
- [x] **[ADR I10](../adr/I10-deploy-responsibility.md):** a person applies Terraform; CI only ships images.
- [x] **[Runbook](../runbook.md):** first deploy, rollback, failed and stuck jobs, key rotation, budget alerts.
- [x] **Code:** OTLP headers for Arize (`DIP_OTEL_HEADERS`); Cloud Tasks dispatch deadline = worker timeout (15 min); health routes renamed; `dip submit` reads `DIP_API_KEY` from `.env`; LlamaIndex kept out of the service's imports (cold start), with a test that fails if it comes back. 297 tests.

## What I measured

Same 5-page contract as Phase 7, against `https://dip-api-af4t3qyy2a-uc.a.run.app`:

| Run | Route | Upload → record | Cost |
|---|---|---|---|
| First job after `terraform apply` | text | **88.3 s** | $0.0054 |
| Scan, right after | multimodal | 16.9 s | $0.0073 |
| New revision, cold instances, `--force` | text | 18.5 s | $0.0023 |

- **The 88 s was IAM propagation, not the app.** Cloud Run returned 403 to Cloud Tasks' first three deliveries, because the `run.invoker` grant was about 90 seconds old. Tasks retried at 10, 20 and 40 s, and the fourth delivery succeeded. The job's `attempts` stayed at 1: those deliveries never reached the app, which is why the queue allows more attempts (5) than the app (3).
- **Steady state is the same as on a laptop:** about 15 s of model time, plus 1–3 s for the queue hop.
- **Cold start**, measured from Cloud Run's "Starting new instance" to uvicorn's "Started server process":

  | Image | Worker | API |
  |---|---|---|
  | first deploy | 10–21 s | — |
  | LlamaIndex no longer imported at startup | **8.7–9.5 s** | 11.3–11.5 s |

  The startup probe allows 30 s (15 × 2 s), so the first image ran with almost no margin. Locally the import takes 1.2 s → 0.8 s; Cloud Run's sandbox makes every imported file far more expensive. What remains is mostly fetching the 825 MB image. Next lever (Phase 9): move eval-only dependencies (LlamaIndex, DuckDB, matplotlib) to an optional extra so the image shrinks too.
- **Idle cost** is about $0.50/month: Secret Manager versions and image storage. Everything else scales to zero or sits in a free tier.
- **Spend this phase:** about $0.02 of OpenAI.

## Things that went wrong, and what they taught

1. **IAM is eventually consistent.** A grant that `terraform apply` reports as created can take minutes to be enforced. Retries absorbed it here. A deploy script that tested immediately and failed hard would have reported a broken deployment that wasn't.
2. **`/healthz` is not yours on Cloud Run.** Google's front end answers some paths ending in `z` with its own 404, so the public liveness check failed while internal probes passed. Renaming the route needed the image and the probe to change in one revision, or the new revision would fail its startup probe. `gcloud run deploy --startup-probe` did both, and `terraform plan` then showed no drift.
3. **Arize rejected the first service key** (`403 invalid api-key`). The Space ID was valid: the EU and Canada endpoints rejected *it*, which means the account lives in the US region. The traces were dropped, but jobs were unaffected: exporting is asynchronous and best-effort. That's the right failure mode for telemetry, but it would have stayed silent without reading the logs. A new key is needed (see below).
4. **Secrets need values before services exist.** A Cloud Run revision that references a secret with no versions can't start. So the first apply is staged: secrets and registry first, then values, then everything else.
5. **Cold start was 2× what it needed to be, and invisible in local timing.** `python -X importtime` showed `dip.extract.retrieval` (LlamaIndex) at 43% of startup imports, used only by the D3 experiment. The import now happens only where a retriever is built, and `test_cold_start.py` fails if the API or worker imports LlamaIndex, DuckDB, matplotlib, Docling or tiktoken again.
6. **An Apple Silicon build is arm64 by default;** Cloud Run needs `--platform linux/amd64`. CI builds on x86 runners, so only the first, hand-built image needed it.
7. **The application-default credentials carried another project as their quota project.** `billing_project` + `user_project_override` in the provider keeps API quota and billing on the dev project, whoever runs Terraform.

## Status: Arize

- [ ] Production traces. The worker exports to `otlp.arize.com`, but the stored service key is rejected. Fix: create a new service key in Arize (Settings → Account Settings → Service Keys, with your space assigned), run `./infra/bootstrap/dip-secrets.sh` and rotate only `arize-otlp-headers`, then redeploy the worker.

## Concepts to understand before moving on

1. Why does the worker check the OIDC token itself when Cloud Run already enforces `run.invoker`? What would each check alone miss?
2. Why does the Workload Identity condition pin the repository's numeric ID and not just its name?
3. Why deploy by digest instead of by tag? What could go wrong between `docker push` and `gcloud run deploy` if you used `:latest`?
4. The API creates Cloud Tasks with an OIDC token *as* `sa-tasks-invoker`. Why does that need `serviceAccountUser` on the invoker account, and what would it mean if every enqueuer had it?
5. Why does Terraform ignore the container image? What happens on the next `terraform apply` if it didn't?
6. What's the blast radius if `sa-deployer`'s token leaks, versus a JSON key for a project Editor?
7. Why is `max_attempts` on the queue (5) larger than `MAX_ATTEMPTS` in the app (3)?

## Try it yourself

```bash
cd infra/terraform && terraform init -backend-config=envs/dev.gcs.tfbackend && terraform plan -var-file=envs/dev.tfvars
uv run dip submit contract.pdf --api "$(terraform -chdir=infra/terraform output -raw api_url)"
gcloud run revisions list --service=dip-worker --region=us-central1 --project=dip-dev-c7a284e91f63
gcloud logging read 'resource.type="cloud_tasks_queue"' --project=dip-dev-c7a284e91f63 --limit=10
```

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
