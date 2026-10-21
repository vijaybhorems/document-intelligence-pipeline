# Phase 9: Analytics & hardening

**Goal (SPEC §14):** compactor, DuckDB over GCS, analytics endpoint, load test (Locust, 50 docs).
**Done when:** the §9.3 queries are answered, and the NFR table is filled with real numbers.

## What was built

- [x] **The lake** (`dip.analytics.lake`):
  - **Tables:** `records/*.json` → `lake/records/` and `lake/record_fields/`, Parquet partitioned by day (hive paths).
  - **`dip compact`** rebuilds only the partitions with a newer record.
  - **`dip lake-push-evals`** publishes local eval runs to `lake/eval/`.
  - **Column types** are declared once and shared by the writer and the queries.
- [x] **Named queries** (`src/dip/analytics/sql/*.sql`, `dip.analytics.queries`):

  | Query | Answers |
  |---|---|
  | `clause_prevalence` | which clauses each contract type contains |
  | `governing_law` | governing-law distribution |
  | `production_by_route` | service cost and latency by route and model |
  | `eval_by_route_model` | eval F1, cost and latency by route and model |
  | `field_regressions` | fields whose F1 dropped between two runs |

  `GET /v1/analytics[/{name}]` and `dip query` both run these.
  - **Parameters** are typed and range- or pattern-checked, then bound.
  - **The connection is locked** to the lake, and the lock itself is locked.
- [x] **DuckDB over GCS without keys:** the service account's OAuth token goes into a DuckDB `gcs` secret. `httpfs` is baked into the image, so nothing is downloaded at runtime. DuckDB is imported lazily, guarded by the cold-start test.
- [x] **Contract type from the title** (`dip.analytics.contract_types`): the last strong keyword wins. **95.1%** agreement with CUAD's folder labels (510 contracts).
- [x] **Sweeper** (`dip.service.sweeper`, `dip sweep`): re-sends jobs idle for more than 35 min, at most twice, then fails them. Cloud Tasks' retry window was cut to 30 min so the two never overlap. It uses a composite Firestore index (status, updated_at).
- [x] **Backpressure:** `429` + `Retry-After` once 200 jobs are waiting (a Firestore count aggregation). The problem-details handler now keeps exception headers.
- [x] **Infra** (`jobs.tf`, `alerts.tf`):
  - Cloud Run Jobs `dip-compactor` (hourly) and `dip-sweeper` (every 10 min), on Cloud Scheduler.
  - `sa-compactor` can write **only under `lake/`**, via an IAM condition on object names.
  - `sa-sweeper` and `sa-scheduler`.
  - 3 log-based metrics, each with an email alert policy. The address is in a gitignored tfvars file.
  - CI also rolls out the jobs.
- [x] **Load test** (`loadtest/`, `make loadtest`): a seeded sample of 50 train contracts (10 made into scans), a cost estimate up front, and a hard $1.50 cap.
- [x] Tests: 297 → **322**. Two new CUAD-backed checks: contract-type accuracy, and SQL F1 equal to the scorer's.

## What I measured

**Load test:** 50 train contracts, 10 in flight, dev on Cloud Run; data in `data/loadtest/`. All 50 succeeded, no retries, **$0.44** (estimate $0.42), 13.9 contracts/min.

| | Born-digital (40) | Scanned (10) |
|---|---|---|
| End to end p50 / p95 | 40 s / **64 s** | 32 s / 101 s |
| …of which waiting in the queue (p50) | 26 s | 13 s |
| Extraction (worker) p50 / p95 | 13 s / 22 s | 17 s / 84 s |
| Median cost | $0.0061 | $0.0088 |

- **~20-page contracts (15–25 pages): p95 63 s**, against the 90 s target.
- **Status polls:** p95 160 ms over 977 requests. Record fetch: 260 ms. Upload: 1.3 s, because it carries the file.
- **Queue wait dominates the end-to-end time.** With 10 jobs in flight and 4 dispatched, the median contract waited twice as long as it took to extract. That's backpressure doing its job: the OpenAI rate limit is protected, and latency is the price. Throughput ≈ 4 / 17 s ≈ 14/min, which matches the observed 13.9.
- **Worker time grows ~0.25 s per page** (born-digital, r = 0.73). Scans grow much faster: one 49-page scan took 110 s of model time.
- **The lake agrees with Locust,** independently:
  - `production_by_route`: text $0.0059 median, p95 22 s.
  - `eval_by_route_model` reproduces the D1–D5 ADR tables, e.g. luna/pypdf 83.6, terra 82.7, sol 82.6, per-field calls at $0.112/contract.
  - `field_regressions` (luna → sol) finds the same two clause drops ADR D2 reports.
- **Analytics queries take about 2 s** each: a fresh DuckDB connection, the token, and Parquet over the network.

## Things that went wrong, and what they taught

1. **The cold-start guard paid for itself on day one.** The new analytics code imported DuckDB at module level, so the API and worker paid for it on every cold start. `test_service_import_path_stays_lean` (Phase 8) failed at once, and the imports became lazy.
2. **The jobs' logs were plain text.** The CLI never configured structlog, so `dip compact` and `dip sweep` printed console lines. The log-based alerts match `jsonPayload.message`, so **two of the three alerts could never have fired**. Found by reading the jobs' first logs, not by a test. Now every CLI run logs JSON outside `local` (with a test), and the alert path was verified end to end: a planted stranded job → swept → failed 3× → both metrics counted it.
3. **Monitoring rejects alert filters without a resource type.** `job.failed` comes from a Cloud Run *revision* and the sweeper's events from a Cloud Run *job*, so each policy names its own.
4. **"Present" needed one definition.** My first test fixture cleared a clause's flag but kept its quote, and the lake counted it as present. The lake uses the scorer's `is_present`, so analytics prevalence and eval F1 mean the same thing. The fixture was wrong, not the code.
5. **Averaging across configs lies.** The first `eval_by_route_model` showed "luna txt v1: $0.030/contract", an average of single, grouped and per-field runs. Grouping by strategy and context gave the real, very different numbers.
6. **A heuristic needs a measurement, then a stop.** The title rule went 94.5% → 95.1% with one change ("supply" is weak). The remaining misses are titles with no type ("First Amendment"); more rules would only overfit CUAD.
7. **The sweeper's threshold is a correctness constraint, not a tuning knob.** Below the queue's retry window it double-bills. Above the longest legitimate queue wait it's safe, which is why the 429 cap matters: it bounds that wait.

## Concepts to understand before moving on

1. Why are JSON records the source of truth and Parquet a derived copy? What do you get back if the lake is deleted?
2. Why partition by day, and rebuild a whole partition instead of appending? What would appending cost the reader?
3. The analytics endpoint takes parameters but never SQL. List three things the parameter checks *and* the DuckDB lock each prevent.
4. Why does backpressure belong at admission (429) and not only at dispatch (the Tasks rate cap)? What does each protect?
5. The sweeper's 35 minutes sits between two other numbers. Which ones, and what breaks on each side?
6. The load test says 100% success. Why can't 50 samples show "≥ 99%"? How many would you need?
7. End-to-end p95 was 64 s, but extraction p95 was 22 s. Where did the rest go, and which setting trades it against what?

## Try it yourself

```bash
uv run dip query list
uv run dip query eval_by_route_model split=experiment
gcloud run jobs execute dip-compactor --region=us-central1 --project=dip-dev-c7a284e91f63 --wait
curl -H "X-API-Key: $DIP_API_KEY" "https://dip-api-af4t3qyy2a-uc.a.run.app/v1/analytics/governing_law"
make loadtest   # ~$0.45
```

## Still open

- **Arize:** the service key from Phase 8 is still rejected (`invalid api-key`), so production traces are dropped. Rotate it with `./infra/bootstrap/dip-secrets.sh`.
- **Image size:** about 825 MB. LlamaIndex, DuckDB and NumPy are runtime dependencies, though the service imports none of them at startup. Moving the eval-only ones into an extra would cut cold start further.

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
