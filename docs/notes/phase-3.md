# Phase 3: Extraction v0

**Goal (SPEC §14):** LLM schema, prompt v1, Structured Outputs on CUAD txt, Phoenix tracing locally, the D4 experiment.
**Done when:** the LLM beats the regex baseline on most fields, cost per contract is measured, and the D4 ADR is written.

## What was built

- [x] `dip.schema.llm`: strict-compatible output schema generated from the registry. Quotes come before answers; one nullable variant is shared across calls.
- [x] `dip.extract.convert`: LLM output to domain fields, through the Phase 1 normalizers.
- [x] `dip.extract.extractor.OpenAIExtractor`: single / grouped / per_field strategies; retries on truncation (only when there's room); refusals, nulls and exceptions recorded per call; prompt-cache key; `store=False`.
- [x] Versioned prompts (`extract/prompts/v1/`).
- [x] Cost control: pricing table with source and date, `dip estimate` (tiktoken, calibrated), a **crash-safe per-call spend ledger** (`usage.jsonl`), `dip spend`, and a pre-run budget check plus a hard in-run cap.
- [x] Tracing: OpenTelemetry + OpenInference, off by default. Verified with an in-memory exporter; Phoenix compose file ready.
- [x] One `System` interface for baselines and LLMs; runs record usage, latency p50/p95, issues and completeness.
- [x] Tests: fake OpenAI client (CI never calls the API). 201 passing.
- [x] [ADR D4](../adr/D4-field-grouping.md), reports in [`docs/results/`](../results/).

## What I measured

**Models:** listed what the API key can access, then checked prices on OpenAI's pricing page (2026-10-20). Chose `gpt-5.6-luna` as the cheap model ($0.20 / $0.02 cached / $1.20 per 1M tokens) and `gpt-5.6-sol` as the large one ($4 / $0.40 / $20), kept for D2 in Phase 6.

**Dev (80 contracts), single call, gpt-5.6-luna:**

| | keyword | LLM |
|---|---|---|
| Overall micro F1 (95% CI) | 55.8 (52–59) | **81.5 (80–84)** |
| Clauses (presence F1) | 55.2 | **75.6** |
| Dates (value F1) | 52.0 | **85.2** |
| Durations | 70.0 | **91.7** |
| Parties | 52.1 | **88.3** |
| Governing law | 75.6 | **94.6** |
| Document name | 55.9 | **85.0** |
| Fields better than keyword | | **35 / 41** |
| Phrasing gap (canonical − non-canonical recall) | +28.8 | **+11.7** |
| Cost per contract | $0 | **$0.0048** |
| Latency p50 / p95 | | **12.8 s / 16.8 s** |

**Weakest LLM fields on dev:** Price Restrictions (P 8%), Volume Restriction (F1 15), Third Party Beneficiary, Most Favored Nation, Competitive Restriction Exception (P 32%), Uncapped Liability (P 36%), Minimum Commitment (R 40%), Post-Termination Services (P 41%). Mostly **over-triggering on clauses that need legal judgment**, plus under-recall on two commercial clauses. That's the input for Phase 5.

**Spend so far:** $5.68 of $10, including a $0.73 conservative entry for one crashed run (see below). `dip spend` lists every run.

## Things that went wrong, and what they taught

1. **Prompt caching silently failed.** The first grouped run cached 0 tokens. A three-call probe showed OpenAI caches the *schema* as part of the prefix, so a different schema per call means no cache. Fix: one shared nullable schema.
2. **Caching was still only about 20% within a run**, because concurrent calls land on different cache servers. Across runs it was 100%. Lesson: budget with the no-cache estimate.
3. **A run crashed and its spend wasn't recorded**: usage was only written at the end. Fix: append every paid call to `usage.jsonl` as it happens, and contain any exception to its own call. The crashed run's spend is recorded at its full estimate.
4. **A pointless retry:** a 41-field call already at the 32k token cap was "retried with more room", which was the same limit and double the cost. Caught by a unit test before it ever ran for real.
5. **The noise floor:** re-running the identical system moved the score 1.6 points, about the same as the differences between strategies. Without that A/A run, D4 would have "found" a winner that is really noise.

## Concepts to understand before moving on

1. Why does the schema need to be identical across calls for prompt caching to work? What else is part of the cached prefix?
2. Why are `quotes` placed *before* `present`/`value` in the schema? What does the order of JSON fields have to do with how a model generates?
3. Grouped scored 0.4 points higher than single. Why isn't that evidence that grouped is better? What would you need to claim it is?
4. Why does the spend ledger write after *every* call rather than at the end of a run?
5. On dev the LLM's clause *recall* (85.9%) is lower than keyword's (91.1%), yet its F1 is 20 points higher. Explain using precision (67.6% vs 39.6%).
6. Expiration date value F1 went from 14 (keyword) to the 80s. What does the model do that regexes can't?

## Try it yourself

```bash
uv run dip estimate --split dev --strategy single          # free
uv run dip spend
docker compose -f docker/compose.yaml up -d phoenix        # needs Docker running
DIP_OTEL_ENDPOINT=http://localhost:6006/v1/traces uv run dip predict --system llm --strategy single --split smoke
open http://localhost:6006
```

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
