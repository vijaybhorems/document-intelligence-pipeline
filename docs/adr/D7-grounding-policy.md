# ADR D7: What to do with values whose evidence isn't in the contract

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-20 |
| **Spec ref** | SPEC §3.1 (D7), §8.3 |

## Context

Every extracted value comes with quotes. Grounding (`dip.validate.grounding`) locates each quote in the contract: exact, then normalized, then fuzzy, then spliced across EDGAR page footers. A value with no grounded quote might be a hallucination. Should it be removed (`drop`) or kept and flagged (`warn`)?

## Options considered

1. **warn**: keep the value; mark each quote `grounded: true/false` and add an `unsupported_value` issue.
2. **drop**: remove ungrounded quotes; remove any value left with no grounded evidence.

## Evidence

gpt-5.6-luna, single call, dev (80 contracts). Both policies were applied to the *same* saved predictions, so the difference is exact, with no LLM noise. Reports: [`docs/results/d6-d7/`](../results/d6-d7/).

| | raw | warn | drop |
|---|---|---|---|
| Quotes found in the contract | 1457 / 1459 (99.9%) | same | 100% (2 removed) |
| False positives that are ungrounded (**hallucinated**) | **0 / 274** | 0 / 274 | 0 / 274 |
| Values removed | | 0 | **1, and it was correct** |
| Overall micro F1 | 81.52 | 81.52 | 81.48 (Δ −0.05, CI −0.15 to 0) |

What the two ungrounded quotes were:
- a **ROFR clause** quoted across a redaction (`[***]`) with an ellipsis. The value was **correct**, and `drop` deleted it.
- an **agreement date** quoted from a signature block that EDGAR laid out in columns (`Date: 7/1/98 By: /s/ ...`). Another quote supported the value, so nothing was dropped.

## Decision

**warn.** On this model there are no hallucinated values to catch, and every value `drop` removed was correct. A grounding miss caused by layout or redaction costs more than the hallucinations `drop` would prevent. Clients still see `grounded` per quote and an `unsupported_value` issue per field, so a downstream consumer can apply `drop` itself.

## Consequences

- **The real error is over-triggering, not hallucination.** All 274 false positives quote real contract text and read it wrong. Precision work belongs in prompting (Phase 5), not validation.
- `unsupported_value` is an *error*, so it triggers a re-ask under D6. The model gets a chance to fix the quote instead of the pipeline deleting the value.
- **Revisit if:** the extraction route changes (D1, Phase 6). OCR'd or multimodal input can make both hallucinations *and* grounding misses more common, so re-run this comparison per route. Also revisit if a model's hallucination rate on dev rises above about 1%.
