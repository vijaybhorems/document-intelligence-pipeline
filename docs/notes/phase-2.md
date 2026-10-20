# Phase 2: Eval harness

**Goal (SPEC §14):** matchers, scorer, bootstrap, report, phrasing slice, baselines.
**Done when:** there is a baseline report on dev, and matcher unit tests cover the wrong-value = FP + FN case.

## What was built

- [x] `dip.eval.matchers`: one rule per field type. Every field gets *presence*; typed fields also get *value*, and clauses also get *span* (SPEC §10.3).
- [x] `dip.eval.scorer`: per-field results, rolled up micro and macro by field type, clause family and overall.
- [x] `dip.eval.bootstrap`: 95% CIs from 1,000 resamples of contracts.
- [x] `dip.eval.slices` + `canonical_cues` in the registry: the phrasing slice, with cues tuned on train only.
- [x] `dip.eval.baselines`: `all_absent` and `keyword`, behind a `System` protocol the LLM pipeline will implement in Phase 3.
- [x] `dip.eval.runs` + `dip.eval.report`: each run is a directory recording its git SHA. The report covers type, family, field and slice, with optional comparison against another run.
- [x] CLI: `dip predict | score | report | eval`.
- [x] Committed reports: [baseline-all_absent-dev.md](../results/baseline-all_absent-dev.md), [baseline-keyword-dev.md](../results/baseline-keyword-dev.md).
- [x] Tests: 45 new unit tests, plus an **oracle test** that scores gold against itself over all 510 contracts.

## What I measured (dev, 80 contracts)

| | all_absent | keyword |
|---|---|---|
| Headline micro F1, all fields | 0.0 | **55.8** (CI 52–59) |
| Clause presence P / R / F1 | – / 0 / 0 | 39.6 / 91.1 / **55.2** |
| Clause presence *accuracy* | **78.0%** | |
| Dates (value F1) | 0 | 52.0. Expiration alone is 14.0. |
| Governing law (value F1) | 0 | 75.6 |
| Phrasing slice recall, canonical / non-canonical | | 86.1 / 57.3 (gap **+28.8**) |

## Decisions made

- **Partial dates** (open question 6): match on the components gold knows. A year-only gold date matches any predicted date in that year; a year-only prediction doesn't match a full gold date.
- **Durations** match across units within 2%, so "6 months" = "180 days".
- **Single-answer vs set fields:** dates, durations and the document name are scored as one answer per field (any match counts), because CUAD's multiple values for them are alternatives. Jurisdictions and parties are sets, with each value its own TP/FP/FN.
- **Typed fields without a derivable value** (the 160 `span_without_answer` labels) count for presence and are excluded from value scoring.
- **Bug found by the oracle test:** 10 gold spans have no words (redaction marks like `[●]`, a lone `.`), and token Jaccard scored them 0 against themselves. They're now compared verbatim. The baseline numbers didn't change.

## What the baselines tell Phase 3

- **Accuracy is the wrong metric.** Predicting "absent" for every clause is 78% accurate and completely useless.
- **The keyword baseline over-triggers**: 91% recall at 40% precision. Words like "assign", "license" and "except" appear in almost every contract. An LLM's job on clauses is mostly *precision*: deciding whether the text actually creates the obligation.
- **Span F1 is low even when presence is right** (e.g. Anti-Assignment: presence 93.9, span 21.4). CUAD spans are often multi-sentence, while a keyword hit is one sentence. Evidence quoting needs to capture the whole clause.
- **Expiration dates (14 F1) need reasoning**, as Phase 1 predicted: "five (5) years from the date hereof" has to be computed.
- **Rare clauses have huge CIs.** Source Code Escrow is 0–80 on 2 positives. Don't compare systems on single rare fields; use the type and family rollups.
- **The bar for an LLM to clear**: 55.8 micro F1 overall, and above all closing the 29-point phrasing gap.

## Concepts to understand before moving on

1. Why does a wrong date count as both a false positive *and* a false negative? What would happen to precision if it only counted as an FN?
2. Micro F1 for clauses is 55.2 and macro is 52.2. Which fields pull macro down, and why does macro react to them more than micro?
3. Source Code Escrow F1 is 33.3 with a CI of 0–80. If a new prompt scores 60 on it, have you learned anything?
4. The oracle test found a bug that 45 unit tests missed. What kind of bug does an oracle test catch that hand-written cases don't?
5. Why must the cues be tuned on train and not on dev?
6. The keyword baseline uses the same cues that define the slice. Why does it still get 57% recall on *non-canonical* clauses?

## Try it yourself

```bash
uv run dip eval --system keyword --split experiment
uv run python -c "import duckdb; print(duckdb.sql(\"select field, sum(tp) tp, sum(fp) fp, sum(fn) fn from 'data/runs/*keyword-dev/field_results.parquet' where metric='presence' group by 1 order by fp desc limit 10\"))"
```

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
