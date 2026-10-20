# Phase 1: Data & gold

**Goal (SPEC §14):** CUAD download, DuckDB exploration, field registry, gold builder, splits, text-layer check.
**Done when:** gold validates against the domain schema, the prevalence table is written up, and `splits.json` is committed.

## What was built

- [x] `dip download-cuad`: MD5-verified download from Zenodo, zip-slip-safe extraction, idempotent
- [x] CUAD index (`dip.ingest.cuad`): joins JSON + CSV + txt + PDF for all 510 contracts despite inconsistent filenames
- [x] Field registry (`dip.schema.registry`): 41 fields, each with type, extraction group and CUAD definition
- [x] Domain schema (`dip.schema.domain`): partial dates, multi-valued answers, party aliases, `GoldRecord`
- [x] Normalizers (`dip.validate.normalize`): dates, durations, jurisdictions, parties. Built from the real answer strings, and reused for predictions in Phase 4.
- [x] `dip build-gold`: 510 `GoldRecord` JSON files that validate against the schema, plus `gold_fields`, `documents` and `label_issues` Parquet tables
- [x] `dip profile-pdfs`: text-layer coverage of every PDF
- [x] `dip make-splits`: frozen, multi-label stratified splits in `data/splits.json` ([ADR I9](../adr/I9-splits.md))
- [x] `dip cuad-report`: [cuad-dataset-profile.md](cuad-dataset-profile.md), generated from the SQL in `analytics/queries/`
- [x] [cuad-quirks.md](cuad-quirks.md): every inconsistency found, and how it's handled
- [x] Tests: 119 unit tests run in CI. 8 tests against the real data, including 5 hand-checked contracts, run locally and skip in CI.

## What I measured

| | |
|---|---|
| Contracts / pages | 510 / 9,348 |
| Gold spans | 13,823, all with exact offsets |
| Image-only PDFs | **0**. Every PDF is born-digital. |
| Answers the normalizers couldn't parse | 26 of 2,870 typed answers (under 1%), each either valueless or ambiguous (`[]/[]/[]`, redactions, "the state in which the breach occurs") |
| Rarest / commonest field | Source Code Escrow 2.5% / Document Name 100% |
| Clause prevalence (mean) | 21.9%. Most clauses are absent from most contracts. |
| Fields with < 10 positives in test | 9, after multi-label stratification |

## Decisions made

- **Warranty Duration is a clause**, not a duration. The gold data only says Yes/No ([cuad-quirks.md](cuad-quirks.md)).
- **Gold spans come from the JSON, typed values from the CSV.** The JSON has offsets. The CSV has normalized answers.
- **Same normalizers for gold and predictions**, so formatting differences can't show up as extraction errors.
- **Multi-label stratified splits** ([ADR I9](../adr/I9-splits.md)). Stratifying on contract type alone left 3 fields with zero examples in the experiment set. Switched before any evaluation ran.

## Implications for later phases

- **Phase 2:** for typed fields, score *presence* ("did it find the expiration clause?") separately from *value* ("is the date right?"). 160 labels have a span but no derivable value.
- **Phase 2:** partial gold dates (`[]/[]/2020`) need a rule. Probably: match on the components gold knows.
- **Phase 2:** with 2.5–7% prevalence on many clauses, an "all absent" baseline will have high accuracy and zero recall. That's why the spec uses precision/recall, not accuracy.
- **Phase 3:** expiration dates are often *computed* ("five years from the date hereof"), so extraction needs reasoning, not just lookup.
- **Phase 3:** contracts range from 1k to 338k characters. Franchise and Agency contracts average more than 115k, so the context budget is a real constraint.
- **Phase 6:** OCR vs multimodal can only be compared fairly on synthetic scans.

## Concepts to understand before moving on

1. Why do the gold builder and (later) the predictions go through the *same* normalizers? What would go wrong if gold used `parse_cuad_dates` and predictions used a different parser?
2. Open `data/splits.json`. Why is the test set frozen, and what exactly would `--force` invalidate?
3. Run `cuad_test_support.sql`. Three clauses have 3 positives in test. If the model finds 2 of 3, recall is 67%. If it finds 3 of 3, recall is 100%. What does that tell you about comparing two models on those fields?
4. Iterative stratification picks the *rarest* label first. Why does the order matter?
5. Look at an Expiration Date `span_without_answer` example in `label_issues.parquet`. Should the model be rewarded for finding that clause even though there's no date?

## Try it yourself

```bash
uv run python -c "import duckdb; con = duckdb.connect(); con.execute(open('analytics/views.sql').read()); print(con.sql(open('analytics/queries/cuad_field_prevalence.sql').read()))"
```

Or install the DuckDB CLI (`brew install duckdb`) and run `duckdb -init analytics/views.sql` from the repo root to query interactively.

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
