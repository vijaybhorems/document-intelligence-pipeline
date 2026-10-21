# Runbook

How to operate the deployed service (SPEC §13). Commands assume the dev project; swap
the project and tfvars file for prod.

```bash
export P=dip-dev-c7a284e91f63 R=us-central1
```

## First deploy (once per environment)

1. **Terraform state bucket** (Terraform can't create its own backend):
   ```bash
   gcloud storage buckets create gs://$P-tfstate --project=$P --location=$R \
     --uniform-bucket-level-access --public-access-prevention
   gcloud storage buckets update gs://$P-tfstate --versioning
   ```
2. **APIs, empty secrets, image registry:**
   ```bash
   cd infra/terraform
   terraform init -backend-config=envs/dev.gcs.tfbackend
   terraform apply -var-file=envs/dev.tfvars \
     -target=google_secret_manager_secret.this -target=google_artifact_registry_repository.images
   ```
3. **Secret values:** `./infra/bootstrap/dip-secrets.sh`. Services can't start until all three secrets have a version.
4. **First image.** Cloud Run runs linux/amd64; on an Apple Silicon Mac, say so explicitly:
   ```bash
   gcloud auth configure-docker $R-docker.pkg.dev
   IMG=$R-docker.pkg.dev/$P/dip/dip:$(git rev-parse --short HEAD)
   docker build --platform linux/amd64 -f docker/Dockerfile -t $IMG . && docker push $IMG
   DIGEST=$(docker inspect --format '{{index .RepoDigests 0}}' $IMG)
   ```
5. **Everything else:** `terraform apply -var-file=envs/dev.tfvars -var image=$DIGEST`
6. **CI variables:** set each output of `terraform output github_actions_variables` with `gh variable set NAME --body VALUE`. From then on, every merge to `main` deploys.
7. **Check:** `uv run dip submit <contract.pdf> --api "$(terraform output -raw api_url)"` (the key comes from `DIP_API_KEY` in `.env`).

## Deploy

Merge to `main`. `.github/workflows/deploy.yml` builds, pushes, rolls out the worker and then the API by digest, and smoke-tests. To re-deploy without a change: Actions → Deploy (dev) → Run workflow.

Infrastructure changes are **not** deployed by CI (ADR I10). After merging a change under `infra/terraform`, run `terraform plan -var-file=envs/dev.tfvars` and apply it.

## Roll back a bad revision

```bash
gcloud run revisions list --service=dip-api --region=$R --project=$P --limit=5
gcloud run services update-traffic dip-api --to-revisions=<good-revision>=100 --region=$R --project=$P
```

Do the same for `dip-worker`. The next deploy from `main` moves traffic to the new revision again, so fix forward or revert the commit.

## A job failed or is stuck

- **Failed** (`status: failed`, `error` says why): fix the cause, then re-submit the same document with `?force=true` (`dip submit --force`). The upload is content-addressed, so nothing is stored twice.
- **Stuck in `queued`** (SPEC §20, open question 9): its deliveries ran out.
  - Look for `queue.gave_up` in the API logs.
  - Look for failed attempts in the Cloud Tasks logs:
    ```bash
    gcloud logging read 'resource.type="cloud_tasks_queue"' --project=$P --limit=20
    ```
  - Re-submit with `?force=true`. Phase 9 adds a sweeper that does this automatically.
- **Logs for one job:**
  ```bash
  gcloud logging read "jsonPayload.job_id=\"<job id>\"" --project=$P --limit=50 --format='value(jsonPayload)'
  ```

## Re-extract everything with a new pipeline version

Records are keyed by document hash **and** `pipeline_version` (schema, prompt, model, route, re-ask). Deploying a new prompt or model changes the version, so the next upload of any document extracts fresh, and old records stay readable. There is no bulk re-extraction yet; that's a Phase 9 Cloud Run Job.

## Rotate a key

| Secret | How |
|---|---|
| `openai-api-key` | Create a new key in the OpenAI dashboard. Re-run `./infra/bootstrap/dip-secrets.sh` and choose rotate. Redeploy the worker so instances pick it up (`gcloud run services update dip-worker --region=$R --project=$P` with any no-op flag, or run the deploy workflow). Then revoke the old key. |
| `api-keys` | The wizard generates a new key. To keep old clients working during the switch, add a version holding `new,old` (comma-separated), redeploy, migrate clients, then add a version with only `new`. |
| `arize-otlp-headers` | Create a new service key in Arize, re-run the wizard, redeploy the worker, then delete the old key. |

Old versions stay in Secret Manager until disabled: `gcloud secrets versions disable <n> --secret=<name> --project=$P`.

There are no Google credentials to rotate: CI uses Workload Identity Federation and the services use their attached service accounts.

## A budget alert fired

1. **Where's the money going?** Billing → Reports, grouped by service. OpenAI spend shows in the OpenAI dashboard, not in GCP.
2. **Stop the bleeding:**
   - Pause the queue: `gcloud tasks queues pause dip-jobs --location=$R --project=$P`. Uploads still succeed; jobs wait.
   - Then lower `worker_max_instances` or `tasks_max_concurrent` in tfvars and apply.
3. **Resume:** `gcloud tasks queues resume dip-jobs --location=$R --project=$P`.
