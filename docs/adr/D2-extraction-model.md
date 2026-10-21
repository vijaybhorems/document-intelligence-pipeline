# ADR D2: Which model extracts

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-21 |
| **Spec ref** | SPEC §3.1 (D2), §7.5 |

## Context

Phases 3–5 ran on the cheapest current OpenAI model available to this account, gpt-5.6-luna. The question is whether a larger model buys enough quality to justify its price. Prices come from OpenAI's pricing page (2026-10-20), per 1M tokens (input / cached / output):

| Model | Price |
|---|---|
| gpt-5.6-luna | $0.20 / $0.02 / $1.20 |
| gpt-5.6-terra | $2.00 / $0.20 / $12.00 |
| gpt-5.6-sol | $4.00 / $0.40 / $20.00 |

## Options considered

luna, terra and sol, all with the **same pipeline**: the D1 production route for born-digital PDFs (pypdf text layer), prompt v4, one call per contract, reasoning effort `low`, on the experiment set (30 contracts).

## Evidence

Reports: [`docs/results/d2/`](../results/d2/). The chart is [`docs/img/d1-d2-pareto.png`](../img/d1-d2-pareto.png) (clean panel).

| Model | Overall F1 [95% CI] | Clause P / R / F1 | Date F1 | Parties F1 | $/contract | Output tokens / contract | p50 / p95 |
|---|---|---|---|---|---|---|---|
| **luna** | **83.6** [81–86] | 68.2 / 88.8 / **77.2** | 89.8 | 91.0 | **$0.0074** | 1,950 | 17 / 24 s |
| terra | 82.7 [80–85] | 67.5 / 88.8 / 76.7 | 91.1 | 89.6 | $0.0819 (11×) | 2,568 | 16 / 24 s |
| sol | 82.6 [80–85] | **63.9** / 89.8 / 74.7 | 91.5 | 94.0 | $0.1597 (22×) | 2,878 | 25 / 38 s |

Paired bootstrap against luna (2,000 resamples of the same 30 contracts):

| | Overall | Clauses | Dates |
|---|---|---|---|
| terra − luna | −0.91 [−2.6, +0.7] | −0.46 [−3.1, +2.2] | +1.29 [−2.8, +6.0] |
| sol − luna | −1.07 [−2.8, +0.5] | **−2.51 [−4.9, −0.3]** | +1.71 [−1.4, +5.9] |

Where sol moves, compared with luna:
- **Up:** Change of Control 61→78, ROFR/ROFO/ROFN 75→89, Non-Compete 62→73.
- **Down:** Non-Disparagement 75→57, Covenant Not to Sue 92→77, Uncapped Liability 56→46 (precision 30%), No-Solicit of Customers 67→57 (precision 40%).

No model produced a hallucinated false positive: grounding found every quote.

## What we learned

1. **Bigger wasn't better on this task.** Overall F1 is within noise for all three, and sol is *significantly worse on clauses*, driven by precision (68 → 64). It reads clauses more broadly than CUAD's annotators do. That's the over-triggering pattern from Phase 4, made worse.
2. **The larger models gain on the careful-reading fields** (parties, dates, Change of Control, ROFR), but not significantly at n = 30.
3. **The prompt was tuned with luna.** v4's examples and hard negatives were measured on luna in Phase 5. A prompt tuned to one model can underperform on another, so this is a comparison of *the pipeline as built*, not of the models in the abstract.
4. **Cost scales faster than price lists suggest.** Larger models wrote 30–50% more output (longer quotes, more reasoning), so terra came in 22% over its estimate.

## Decision

**gpt-5.6-luna.** It's on the Pareto frontier with the best overall F1 and clause F1, at one-eleventh of terra's cost and one-twenty-second of sol's. `DIP_EXTRACTION_MODEL` stays `gpt-5.6-luna`.

## Consequences

- Production cost stays at about $0.0075 per born-digital contract and about $0.015 per scanned one (D1).
- The finding is specific to this pipeline. A future prompt change must be re-measured on whatever model it ships with, and model upgrades need a re-run of this comparison, which costs about $7 on the experiment set.
- Not tested, for budget reasons: a larger model on the multimodal route (about $9 for one scanned pass), and higher reasoning effort.

**When I'd choose differently:**
- **If parties and dates matter most** (for example a contract-metadata product rather than clause review): sol's gains there are consistent in direction. Run sol on dev to see whether they're real before paying 22×.
- **After re-tuning the prompt per model:** sol's over-triggering might respond to stronger negative guidance or CUAD-style annotation definitions (the next lever from ADR D5).
- **At a higher reasoning effort**, which wasn't tested here. Check whether careful reading fixes the precision drop at acceptable cost.
- **For a second-pass reviewer:** run luna on everything, and sol only on fields where luna's answer fails validation or sits in a judgment-heavy clause family. That's a targeted spend, not 22× across the board.
