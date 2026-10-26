# Phase 10: Final evaluation and write-up

**Goal (SPEC §14):** **one** test-set run per finalist configuration (≤3), the final report, error analysis, and the portfolio write-up (§15).
**Done when:** `docs/results.md` is complete with charts and screenshots.

## What was built

- [x] **Three finalists, each run once on the 102 test contracts** (untouched until now):
  - production on born-digital PDFs;
  - production on synthetic scans of the same PDFs;
  - the keyword baseline.
- [x] **[`docs/results.md`](../results.md):** the nine sections of SPEC §15.1, plus the resume bullet.
- [x] **Error analysis:** [50 dev errors categorized by hand](../results/error-analysis/README.md), each with a reason and confidence ([`categorized.jsonl`](../results/error-analysis/categorized.jsonl)).
- [x] **Charts** (`dip.eval.final_charts`), checked by rendering and looking:
  - F1 by field type with CIs, plus precision vs recall;
  - a per-field heatmap;
  - the phrasing slice.
- [x] **`paired_delta`:** a tested paired bootstrap in `dip.eval.bootstrap`. Earlier ADRs computed these in one-off scripts.
- [x] **Fixes found on the way** (details below): the hybrid-route estimate, the CLI strategy default, and the valid-output metric.
- [x] Tests: 365 → **368**.

## What I measured

**On the test set** (each finalist run once; [reports](../results/final/)):

| | Overall micro F1 | Clauses | Cost / contract | p50 / p95 |
|---|---|---|---|---|
| production, born-digital | **84.0** [82–86] | 79.0 | $0.0080 | 14.2 / 20.8 s |
| production, scanned | **82.8** [81–84] | 77.4 | $0.0149 | 16.9 / 28.6 s |
| keyword baseline | 54.0 [51–57] | 54.5 | $0 | – |

- **Production − keyword: +30.0 [+26.5, +34.1].**
- **Scanned − born-digital: −1.2 [−2.3, −0.1]**, small but significant. On 30 experiment contracts it was within noise; 102 contracts are enough to see it.
- **Test (84.0) agrees with dev (82.7) and experiment (83.6):** no sign of overfitting to the sets used for decisions.
- **Hallucinated values: 0** among 316 (born-digital) and 324 (scanned) false positives. **Valid outputs: 102/102** after re-ask.
- **Phrasing gap: 14.6 points** (keyword: 43.2).
- **Spend:** Phase 10 cost **$2.35**: $2.33 for the test runs, $0.014 for a trace. Project total ≈ **$19.20 of $20**: the ledger's $18.72, plus ~$0.50 of service calls the ledger doesn't count.

**Error analysis (50 dev errors):**

| Category | Count |
|---|---|
| over-trigger | 21 |
| suspected label noise | 13 (8 high-confidence) |
| missed | 8 |
| wrong value | 6 |
| normalization | 2 |
| hallucinated | 0 |

- **11 of 32 errors that looked like over-triggers read as label noise:** clause precision is a lower bound.
- **One systematic error dominates a whole field type:** the model adds "United States" beside a state. That's 20 of governing law's 21 false positives on test; precision is 80.6, and would be 98.9 without them.

## Things that went wrong, and what they taught

1. **The budget estimate was 2.3× low for scans.** The budget check knew the multimodal route, but priced the hybrid route as text even when it would send page images: $0.66 estimated vs $1.55 real. Caught because two estimates came out identical, which they couldn't be. Fixed with a test: the hybrid route now prices each contract the way it will send it.
2. **A stale default would have run the wrong system.** The CLI still defaulted to the *grouped* strategy that D4 rejected; an estimate showed 612 calls instead of 102. Any `dip eval` without `--strategy single` would have paid for the losing configuration. **Lesson:** after a decision, update the defaults, not just the docs.
3. **A metric said 87% of outputs were invalid.** The valid-output count treated the hybrid route's *notes* ("route: pypdf", "parse: 1/40 pages…") as failures. The report's own issue table listed only two problems, so 13/102 couldn't be right. The fix counts real failures only: 102/102. **Lesson:** a number that contradicts its own table is a bug until proven otherwise.
4. **My shell filters hid an error.** The first test-run attempt failed at once (`--system` missing), and `grep` removed the message. Nothing was spent, but the next attempt sent everything to a log and filtered only the monitor.
5. **Test-set discipline cuts both ways.** The governing-law fix is obvious *now*, but it was found by looking at test results. Fixing it and re-scoring test would be tuning on test. It's recorded as the first next step, to be measured on dev.

## Concepts to understand before moving on

1. Why exactly one test run per finalist? What would a second run after a fix make the number mean?
2. The scan penalty was "within noise" on 30 contracts and "significant" on 102. Did the effect change? What changed?
3. Hallucination was 0% both before and after validation. So what did validation buy?
4. How can a measured error rate overstate the model's real error rate? What would you do before claiming a "noise-adjusted" precision?
5. One fix would move governing-law precision from 80.6 to 98.9. Why is it the first next step, and why isn't it in this report's numbers?
6. Read the per-field heatmap: which low scores would you trust, and which would you discount for small *n*?

## Screenshots

Captured from the repository's own data (charts and a sample record) and from the live systems; see the table at the end of [`results.md`](../results.md).

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
