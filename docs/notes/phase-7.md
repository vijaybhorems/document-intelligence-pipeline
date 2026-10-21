# Phase 7: Service

**Goal (SPEC §14):** FastAPI, job model, worker, docker compose with emulators.
**Done when:** a local E2E works: upload PDF → poll → valid record.

## What was built

- [x] `dip.pipeline.Pipeline`: the one orchestration path, with the decided configuration (D1 hybrid route, D2 luna, D4 single call, D5 prompt v4, D6 validate + one re-ask, D7 warn). It returns a `ContractRecord` with provenance: route, model, prompt version, grounding checked/unavailable, tokens, cost and time. `pipeline_version` names every one of those choices, so a cached record is reused only by an identical pipeline.
- [x] **API** (`dip.api.app`), [SPEC §12](../SPEC.md#12-interfaces-rest-api-and-mcp):
  - `POST /v1/extractions` (multipart, `?wait=`, `?force=`, `Idempotency-Key`), `GET /v1/extractions/{id}`, `/record`, `/v1/schema`, `/healthz`, `/readyz`.
  - The upload is sniffed by content, not filename (PDF or UTF-8 text). The size limit is enforced while reading, and the page count is checked before anything is queued.
  - Errors are RFC 9457 `problem+json`. Auth uses `X-API-Key`, compared in constant time.
- [x] **Jobs:** `queued → routing → extracting → validating → succeeded | partially_succeeded | failed`. Dedupe is by SHA-256 + pipeline version. Firestore writes are per-field updates, so a redelivered task can't overwrite newer fields.
- [x] **Worker** (`dip.worker.app`): `POST /internal/process`. A job gets 3 attempts. Before the last, a failure puts it back to `queued` and answers 5xx, so the queue retries. The last failure marks it `failed` and answers 200, so the queue stops.
- [x] **Two backends, one code path:**
  - `local`: a folder, an in-memory job store, and an in-process queue.
  - `gcp`: GCS, Firestore, and Cloud Tasks with OIDC.
  - Compose runs `gcp` against the GCS and Firestore emulators, with an HTTP queue standing in for Cloud Tasks.
- [x] **Docker:**
  - One image for both roles (`DIP_ROLE=api|worker`): multi-stage uv build, 825 MB, non-root (uid 10001), base images pinned by digest.
  - The build fails if the prompt's `field_notes.json` is missing from the wheel.
  - `.dockerignore` is an allowlist, so `.env` can't reach the build context.
- [x] **Compose** (`make up`, `make e2e`, `make down`): api, worker, GCS emulator, Firestore emulator, a one-shot bucket init, and Phoenix. Every port is bound to 127.0.0.1, containers have read-only root filesystems, capabilities are dropped, and only the worker gets the OpenAI key.
- [x] `dip submit`: upload, poll, summarise. It works against any deployment, so Phase 8 reuses it against Cloud Run.
- [x] **Tracing in the worker:** one trace per job (`POST /internal/process` → `extract.contract` → the OpenAI call), with health probes excluded.
- [x] Tests: 293 passing, all offline (fake OpenAI client, in-process app).

## What I measured

The same 5-page CUAD contract (Martin Midstream, Transportation Services), born-digital and as a synthetic scan:

| Run | Route | Grounding | Upload → record | Cost |
|---|---|---|---|---|
| uvicorn, local backend | text | checked | 13.1 s | $0.0054 |
| uvicorn, local backend, scan | multimodal | unavailable | 14.1 s | $0.0073 |
| compose (emulators, HTTP queue, worker container) | text | checked | 13.7 s | $0.0022 |
| compose, scan | multimodal | unavailable | 14.3 s | $0.0023 |

- **Latency is the model call.** The extra hop through the queue and the emulators adds under a second.
- **The compose runs cost less because the prompt cache was warm.** The system prompt and schema are an identical prefix (Phase 3), so a second run of the same contract within minutes pays the cached rate.
- **Same contract, slightly different answers across runs:** document name casing, and 6–8 clauses present. That's LLM nondeterminism inside the A/A noise floor from Phase 2. It is also why dedupe returns the *stored* record instead of re-extracting.
- **Spend:** about $0.02 for the whole phase. Note that service calls are not in the eval ledger (`dip spend`); their cost is on each job and record.

## Things that went wrong, and what they taught

1. **Internal auth was keyed on the wrong thing.** The worker chose OIDC vs shared token by *storage backend*. Compose uses the gcp backend with the HTTP queue, so every delivery would have been rejected. The right key is *how jobs arrive*, so `Settings.queue_kind` now decides both the queue and the auth. Outside the local backend a missing token fails closed (500) rather than open.
2. **The in-process queue never retried.** `process_job` raises to ask for a redelivery, but `InlineQueue` just let the thread die, so a transient error locally left a job `queued` forever. A test that only exercised the happy path couldn't see it.
3. **Stale jobs are a real production gap.** With the worker down, the HTTP queue retried for about 3 s and gave up *silently*, and the job stayed `queued` with no trace in any log. It now logs each failed delivery and `queue.gave_up`. Cloud Tasks gives up eventually too, so the real fix is a sweeper in Phase 9 (SPEC §20).
4. **Tracing was configured but never started.** Only the CLI called `configure_tracing`, so `DIP_OTEL_ENDPOINT` did nothing in the service, and Phase 8's Arize export would have shipped nothing. Then FastAPI's own telemetry traced every health probe, at about 3 spans per probe every 5 s. Lesson: check that the trace store shows what you expect, not just that the setting is set.
5. **Two container gotchas:**
   - Debian already has a group named `dip` (dial-up IP), so `groupadd dip` failed.
   - Phoenix's non-root image couldn't write to a new named volume. Docker seeds a volume with the owner of the directory it's mounted over, and `/mnt/data` didn't exist, so it was root-owned. The Phase 3 compose file had never actually run.
6. **A silent prompt downgrade was one packaging mistake away.** If `field_notes.json` were missing, the prompt loader returns no examples rather than failing. The Docker build now asserts it is present.

## Concepts to understand before moving on

1. Why does `POST /v1/extractions` return 202 and a status URL instead of the record? When is `?wait=true` acceptable, and why is it capped?
2. Two different idempotency mechanisms exist: content-hash dedupe and `Idempotency-Key`. What does each one protect against, and why does reusing a key for a different document return 409?
3. Why must `process_job` be safe to run twice for the same job? Name two ways a queue can deliver a task more than once.
4. Why does the worker answer 200 for a permanently failed job, but 5xx for one that should be retried?
5. Why is `pipeline_version` part of the dedupe key? What would go wrong if it were only the SHA-256?
6. The worker's auth depends on the queue, not the storage backend. Why is "fail closed when the token is missing" the right default?
7. What does the emulator setup *not* test that Phase 8 will (IAM, OIDC, cold starts, Secret Manager)?

## Try it yourself

```bash
DIP_ENV=dev uv run uvicorn dip.api.app:create_app --factory --port 8080   # no Docker
uv run dip submit path/to/contract.pdf

make up && make e2e && open http://localhost:6006    # the Cloud Run code path, traced
docker compose -f docker/compose.yaml stop worker     # then upload: watch queue.gave_up
make down
```

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
