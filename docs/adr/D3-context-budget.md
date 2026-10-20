# ADR D3: How much of the contract to send

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-20 |
| **Spec ref** | SPEC §3.1 (D3), §7.4 |

## Context

Sending the whole contract costs input tokens on every call. Retrieval sends only the parts relevant to the fields, which saves tokens but risks missing clauses that sit somewhere unexpected.

## Options considered

1. **full**: the whole contract.
2. **retrieved**: LlamaIndex `SentenceSplitter` chunks (~384 tokens), embedded with `text-embedding-3-small`. One query per field (definition + phrasing variants); top 3 chunks per field, unioned and sent in document order as excerpts.
3. **retrieved + definitions**: as 2, plus the defined-terms table built from the *full* contract, so definitions survive even when retrieval drops the definitions section.

## Evidence

gpt-5.6-luna, single call, experiment set (30 contracts). Paired bootstrap against full v4 (mean of 2 runs). Reports: [`docs/results/d5-d3/`](../results/d5-d3/).

| Arm | Overall F1 | Δ vs full (95% CI) | Clause P / R | LLM input / contract | Cost / contract |
|---|---|---|---|---|---|
| **full (v4)** | 83.6 (mean) | | 70.0 / 89.1 | 23,506 | $0.0060 |
| retrieved (v3 prompts) | 79.0 | −4.59 (−7.02 to −2.37) | 68.5 / 85.1 | 19,052 | $0.0053 |
| retrieved + definitions (v4) | 80.2 | −3.42 (−6.17 to −0.79) | 70.3 / 83.7 | 19,474 | $0.0053 |

Embeddings add 11,309 tokens per contract at $0.02/M, which is negligible ($0.0002).

## What we learned

1. **Retrieval saved little.** A single call needs chunks for all 41 fields, so the union of their top-3 chunks covers much of a typical CUAD contract (median about 7k tokens). The 6.3k-token field instructions are fixed regardless. Net: −17% LLM input, −11% cost.
2. **Recall paid for it:** clause recall fell 89 → 84–85, and the CIs exclude zero. Clauses sit in unexpected places (definitions, schedules, termination sections), which is the risk the spec predicted.
3. **Definitions help under retrieval** (+1.2 over retrieved without them), but not enough to close the gap.
4. **An accounting bug:** embedding tokens were first counted as LLM input tokens, which made retrieved runs look *more* expensive in input. `Usage.embedding_tokens` now keeps them apart.

## Decision

**full context.** Losing 3–4 F1 points to save 11% is a bad trade at $0.006 per contract.

## Consequences

- Retrieval stays implemented (`--context retrieved`) and tested, for the cases where it would win:
  - **Contracts over the context budget.** The longest CUAD contract is about 85k tokens and fits, but a 500-page agreement won't.
  - **Per-field or per-group calls.** Each call then needs only its own fields' chunks, so savings grow with the number of calls (D4 chose a single call).
  - **Expensive models** (D2), where input tokens cost 20× more.
- **Revisit if:** inputs get longer, the model gets pricier, or the strategy moves away from a single call. Test with a larger `top_k` first; recall is what fails.
