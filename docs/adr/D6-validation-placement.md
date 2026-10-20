# ADR D6: Where validation goes

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-20 |
| **Spec ref** | SPEC §3.1 (D6), §8.4 |

## Context

Validation has four layers (SPEC §8.1): structural (strict schema), semantic (normalizers), grounding, and consistency rules. The question is how far to take it. Do we stop at the schema, check everything after extraction, or also send failures back to the model to fix?

## Options considered

| | Description |
|---|---|
| A | L1 only: strict Structured Outputs, nothing after |
| B | L1–L4 after extraction; flag problems (and optionally drop dependent clauses that rules reject: **B + enforce**) |
| C | B, plus a **re-ask**: one follow-up call per contract with validation *errors*, for just the failing fields, telling the model exactly what failed |

Errors that trigger a re-ask:
- an unsupported value (no grounded quote)
- an extraction or normalization failure
- dates out of order, or an implausible duration
- two **dependency rules**: a competitive-restriction exception with no restriction, or a license property with no license grant

Every rule was first run against **train-split gold** to measure false alarms: 0.3–1.2% of gold contracts, and 3.4% for "fewer than 2 parties", which is therefore only a warning. "Cap and Uncapped Liability both present", proposed in the spec, fires on **21%** of gold and was rejected.

## Evidence

gpt-5.6-luna, single call, dev (80 contracts). Paired bootstrap against A (2,000 resamples). Reports: [`docs/results/d6-d7/`](../results/d6-d7/).

| Option | Overall F1 | Δ vs A (95% CI) | Clause P / R | Valid outputs | Unsupported values | Cost/contract |
|---|---|---|---|---|---|---|
| A: raw | 81.52 | | 67.6 / 85.9 | 79/80 | 1 | $0.0048 |
| B: warn | 81.52 | 0.00 | 67.6 / 85.9 | 79/80 | 1 (flagged) | $0.0048 |
| B + enforce | 81.67 | +0.15 (−0.03 to +0.33) | 68.1 / 85.7 | 79/80 | 1 | $0.0048 |
| **C: warn + re-ask** | **81.70** | **+0.18 (0.00 to +0.37)** | 68.1 / 85.7 | **80/80** | **0** | $0.0054 |

**What the dependency rules found:** on raw predictions, the flagged clause was a false positive 6 times out of 7. Re-asking withdrew all 7. It also repaired the one extraction that had failed and the one unsupported value.

## Decision

**C: post-hoc validation plus re-ask on errors**, with D7 = `warn`. It is the only option with **100% valid outputs and no unsupported values**, and it has the best F1. It costs **+12% per contract** ($0.0006), spent only on the roughly 10% of contracts that have an error. **B + enforce** is the free fallback when the re-ask budget is gone: it makes the same presence changes on dev.

## Consequences

- **The effect on F1 is small**, because the errors validation can *detect* are rare. The dominant error, 274 grounded over-triggers, is invisible to it. Validation's value here is guarantees (every value backed by text, every output parseable) rather than accuracy.
- Re-asking adds latency for contracts with errors: one more call, about 13 s p50.
- The re-ask prompt is versioned (`prompts/v1/reask.txt`) and goes into Phase 5's prompt work.
- **Revisit if:** a route or model produces many more validation errors (OCR, multimodal, a weaker model), where re-ask matters more; or if Phase 5 adds verification-style checks that catch over-triggers, which would make re-ask far more valuable.
