# ADR D5: Prompt strategy

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-20 |
| **Spec ref** | SPEC §3.1 (D5), §7.2–7.3 |

## Context

Phase 4 showed the model doesn't hallucinate: **all 274 false positives on dev quote real text and misread it**. The remaining errors are legal judgment (over-triggering) and clauses phrased unusually. Prompt v1 gave the model only CUAD's one-line category definitions.

## Options considered (cumulative, one feature at a time)

| Version | Adds | Field-instruction tokens |
|---|---|---|
| v1 | CUAD definitions | 1,323 |
| v2 | + **phrasing variants**: up to 3 real wordings per field that avoid the obvious keywords | 4,215 |
| v3 | + **examples**: one positive and one **hard negative** per field (a sentence with the field's keywords, from a contract the experts say lacks the clause) | 6,269 |
| v4 | + **defined-terms table**: the contract's own definitions, extracted by regex | + 0–1.5k per contract |

All variants and examples come from **train-split gold only** ([`field_notes.json`](../../src/dip/extract/prompts/field_notes.json), `dip build-field-notes`), so dev and test labels never reach the prompt. Only clause-like text is used: complete sentences, obligation language, no redactions. The first version picked the *shortest* spans, which turned out to be meaningless fragments.

## Evidence

gpt-5.6-luna, single call, full context. Reports: [`docs/results/d5-d3/`](../results/d5-d3/).

**Experiment set (30 contracts).** Paired bootstrap against the mean of two v1 runs:

| Arm | Overall F1 | Δ vs v1 (95% CI) | Clause P / R / F1 | Phrasing gap |
|---|---|---|---|---|
| v1 (2 runs) | 81.1, 82.6 | | 65.5 / 87.2 / 74.8 | +11.6 |
| v2 | 82.9 | +1.00 (−0.29 to +2.30) | 66.1 / 88.8 / 75.8 | +11.3 |
| v3 | 82.9 | +1.07 (−0.29 to +2.52) | 68.2 / 88.8 / 77.2 | +10.3 |
| **v4 (2 runs)** | 84.2, 83.0 | +2.33 and +1.18 | **70.0 / 89.1 / 78.4** | +14.6 |

**Dev (80 contracts)**, the confirmation:

| | Overall F1 | Δ (95% CI) | Clause P / R / F1 | Phrasing gap |
|---|---|---|---|---|
| v1 | 81.52 | | 67.6 / 85.9 / 75.6 | +11.7 |
| **v4** | **82.70** | **+1.18 (+0.07 to +2.38)** | **69.3 / 89.0 / 78.0** | **+10.7** |

The biggest per-field gains on dev are on the judgment-heavy fields Phase 4 flagged: Volume Restriction 15→33, Covenant Not to Sue 64→80, Uncapped Liability 49→62, Warranty Duration 65→77, Cap on Liability 86→96. The biggest losses are on rare fields within noise, such as Non-Disparagement with 6 positives.

## What we learned

1. **The full v4 bundle helps, and each increment is within noise.** v1→v2→v3→v4 moved +1.0, +0.1, +0.7 (v4 as the mean of its two runs). With a noise floor of ±0.8 per run, 30 contracts can't attribute the gain to a single feature. Isolating them would take ≥2 runs per arm on dev, about $2.
2. **Precision and recall both rose.** Hard negatives were expected to trade recall for precision. Instead, clause precision went 65.5 → 70.0 *and* recall 87.2 → 89.1.
3. **The phrasing gap barely moved, and the reason is the definitions, not the wording.** The unusually worded clauses that get missed are cases where **CUAD's category is broader than its name**. A "Success Fee of 0.85% of the purchase price" counts as Revenue/Profit Sharing. "Owner shall ensure each vessel is seaworthy" counts as Warranty Duration. "Company will not grant rights to any third party before the Investor exercises its option" counts as a ROFN. Three phrasing variants per field can't teach category boundaries. 22 of the 27 misses were single-span clauses with a median length of 581 characters.
4. **Example selection is a real design problem.** "Shortest gold span" produced fragments like "and which the Company has not repurchased.", because CUAD labels many clauses as disjoint pieces.

## Decision

**v4** (definitions + phrasing variants + examples with hard negatives + defined-terms table). It's the only arm whose gain over v1 holds on both sets, and on dev its CI excludes zero. It costs about **+25%** per contract on dev ($0.0060 vs $0.0048; input tokens +29%, from the longer field instructions).

## Consequences

- `CURRENT_VERSION = "v4"`. Every prompt file is versioned; v2–v4 inherit v1's text and add features, so the ablation stays reproducible.
- The field instructions (6.3k tokens) are identical for every contract but sit *after* the contract, so they're never cached across contracts. Moving them into the system prompt would make them cacheable, saving about $0.001 per contract at luna prices. That's worth doing at scale; re-measure quality when you do, since instruction position can change behaviour.
- **Next lever:** fuller category definitions in the style of CUAD's annotation guidelines, especially for broad categories (Revenue/Profit Sharing, Warranty Duration, ROFR/ROFO/ROFN, Minimum Commitment). The phrasing slice is the metric that should move.
- **Revisit if:** the model changes (D2), since a stronger model may need fewer examples; or once fuller definitions exist, to re-run the ablation with ≥2 runs per arm.
