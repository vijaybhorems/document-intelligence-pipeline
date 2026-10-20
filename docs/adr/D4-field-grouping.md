# ADR D4: How many LLM calls per contract

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-20 |
| **Spec ref** | SPEC §3.1 (D4), §6.1 |

## Context

The extractor must fill 41 fields from one contract. Splitting the fields across more calls gives each field more of the model's attention, but costs more: every call re-sends the whole contract. OpenAI's prompt caching could make the repeated contract cheap, which is why the spec's default was 6 grouped calls.

## Options considered

1. **single**: one call for all 41 fields.
2. **grouped**: one call per field group (6 calls), with one shared schema so the prefix is cacheable.
3. **grouped, own schema**: 6 calls, each with a schema containing only its fields.
4. **per_field**: one call per field (41 calls), shared schema.

## Evidence

gpt-5.6-luna, reasoning effort low, prompt v1, experiment set (30 contracts). Reports: [`docs/results/d4/`](../results/d4/).

| Strategy | Overall micro F1 (95% CI) | Clause F1 | Macro F1 | Cost/contract | p50 latency | Cached input |
|---|---|---|---|---|---|---|
| keyword baseline | 57.7 (53–62) | 53.5 | 53.5 | $0 | <0.1 s | |
| **single** | **81.1 (79–83)** | 73.3 | 69.8 | **$0.0061** | **13.5 s** | 0% |
| single, re-run | 82.6 | | | $0.0028 | 12.7 s | 100%* |
| grouped | 81.5 (79–83) | 74.1 | 72.7 | $0.0197 | 20.2 s | 20% |
| grouped, own schema | 79.0 (76–81) | 70.6 | 70.7 | $0.0100 | 14.3 s | 66%* |
| per_field | 80.9 (79–83) | 73.1 | 72.0 | $0.1119 | 82.5 s | 24% |

\* Cache warmed by an earlier run with identical prompts, so it isn't representative.

**Paired bootstrap of the difference** (2,000 resamples of the same 30 contracts):

| Comparison | Δ F1 | 95% CI |
|---|---|---|
| grouped − single | +0.4 | −1.3 to +2.0 |
| per_field − single | −0.1 | −1.8 to +1.6 |
| grouped own schema − grouped | −2.5 | −4.5 to −0.6 |
| **single re-run − single** (noise floor) | **+1.6** | −0.2 to +3.0 |
| single − keyword | +23.4 | +19.0 to +28.1 |

## What we learned

1. **More calls didn't improve quality.** The differences between strategies are no bigger than the difference between two runs of the *same* strategy. With a noise floor of about ±1.5 points, a strategy that's 0.4 points better hasn't been shown to be better at all.
2. **OpenAI caches the Structured Outputs schema as part of the prompt prefix.** A different schema per call got 0 cached tokens, while the same schema got 99.9% (verified directly). Hence the shared nullable schema.
3. **Caching within a run is unreliable under concurrency.** Even with identical prefixes, calls fired together landed on different cache servers, so grouped got 20% cache hits and per_field 24%, against a best case of about 83% and 98%. Caching *across* runs worked almost perfectly: the re-run hit 100% and cost 54% less. Budget with the no-cache estimate.
4. **The shared schema scored better than per-call schemas** (−2.5 points without it, just beyond noise). A plausible reason is that seeing all 41 definitions helps the model separate neighbouring fields. It's weak evidence from one run each.
5. **Rare fields swing wildly between identical runs**, by up to 67 points for Affiliate License-Licensor. Never compare systems on a single rare field from a single run.

## Decision

**single**: one call per contract. It matches the alternatives on quality, is 3.2× cheaper than grouped and 18× cheaper than per_field, and has the lowest latency. On dev (80 contracts) it scores 35/41 fields above the keyword baseline at **$0.0048 per contract** and **12.8 s p50** ([report](../results/llm-single-dev.md)).

## Consequences

- One call means one point of failure per contract. A truncated or refused response loses all 41 fields, so watch the `issues` count. So far there has been 1 issue in 80 contracts.
- The longest CUAD contract (about 85k tokens) fits comfortably in one call. Contracts beyond the context budget will need chunking (SPEC §6.1).
- Prompt work (Phase 5) now changes one prompt, not six.
- **Revisit if:** a stronger model or a longer, richer prompt (Phase 5 adds phrasing variants and defined terms) makes the single call's output long enough to degrade, or if per-group prompts become specialized enough to justify the extra calls. Re-test with ≥2 runs per arm so the noise floor is measured, not assumed.
