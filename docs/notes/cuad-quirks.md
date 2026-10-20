# CUAD quirks

What we found reconciling CUAD v1's four sources (Phase 1, 2026-10-19), and how the pipeline handles each quirk. Numbers come from [cuad-dataset-profile.md](cuad-dataset-profile.md) and `data/gold/label_issues.parquet`.

## Source files

| Quirk | Handling |
|---|---|
| Filenames disagree across sources in 10 of 510 contracts: `&` vs `_`, `'` vs `_`, trailing spaces, and Unicode normalization (`LECLANCHÉ` as NFC vs NFD) | `match_key()` folds to lowercase ASCII alphanumerics. All 510 resolve uniquely. |
| One PDF has an extra suffix: `…_Development Agreement_Option Agreement.pdf` | Unique-prefix fallback in `_unique_lookup()` |
| PDF extensions mix `.pdf` (199) and `.PDF` (311) | Match on stem, ignore extension |
| 28 PDF folders map to 26 contract types (`Endorsement` vs `Endorsement Agreement`, `Affiliate_Agreements` vs `Affiliate Agreement`) | Explicit `CONTRACT_TYPES` map in `dip.ingest.cuad` |
| JSON context vs `.txt` file | **Identical for all 510.** All 13,823 SQuAD spans index exactly into the text. |

## The answer columns

| Quirk | Example | Handling |
|---|---|---|
| The README lists Warranty Duration's answer format as "number of months or years", but the CSV only has Yes/No | `Warranty Duration-Answer = Yes` | Scored as a **clause** (33 clauses + 8 typed fields, not 32 + 9) |
| Typo in a column header | `Notice Period To Terminate Renewal- Answer` | `FieldSpec.csv_answer_column` special-cases it |
| Span columns store Python list literals | `"['clause one', 'clause two']"` | Spans come from `CUAD_v1.json` instead, which has offsets |
| Missing values are the string `None` | | Treated as absent |
| Two-digit years | `4/8/20`, `1/1/98` | Pivot: under 50 means 20xx, otherwise 19xx |
| Unknown date parts | `[]/[]/2020`, `04/30/[]`, `09/14/200[]` | `PartialDate` with unknown components set to `None` |
| Nothing known | `[]/[]/[]`, `[ ]/[ ]/20[ ]` | No value. Recorded as `unparsed_answer`. |
| Day-first date | `31/01/2025` | Retried as d/m/y when m/d/y is impossible |
| Multi-valued answers | `07/31/2000; 07/[]/2000`, `60 days; 180 days`, `180 days / 6 months` | Domain fields hold lists of values |
| Perpetual terms | `perpetual`, `Perpetual`, `09/05/2019; perpetual` | `perpetual: bool` alongside the values |
| Typos in durations | `succesive`, `succsive`, `sucessive`, `successine` | Regex normalization |
| Number of renewals | `four successive 10 years`, `10 1 years`, `2 5 years` | `Duration.count`. `10 1 years` is read as ten 1-year renewals, which is a guess. |
| Compound durations | `4 years, 6 months` | 54 months |
| Dates in a duration field | `7/22/2019; 7/22/2022` (Renewal Term) | `unparsed_answer` |
| Governing law: about 78 spellings for 57 jurisdictions | `England; Wales`, `England and Wales, UK`, `Province of Ontario, Canada`, `British Columbia,Canada`, `Massachussets` | Alias table with longest match first and word boundaries (`Arkansas` ≠ `Kansas`). Country qualifiers are dropped when a sub-jurisdiction is present. |
| Governing law that isn't a place | `the state in which the breach occurs`, `[* * *]` (redacted), `United Nations Convention on … Sale of Goods` | `unparsed_answer`, plus any place it does name |
| Parties answers mix names, defined terms and boilerplate | `Ingram Micro ("Distributor")`, `ALPS Distributors, Inc. (the “Distributor”)`, `WATER NOW, INC.; ("Water Now")`, `Hydraspin and Distributor ("Party", "Parties")` | `Party(name, aliases)`. Alias-only segments attach to the previous party. Entries whose only aliases are "Party"/"Parties" are dropped. |
| Redacted values labelled as spans | `[*]`, `[●]`, `[•]` as a Parties or Agreement Date span (8 spans); a lone `.` (2 spans) | Kept. Span matching compares word-less spans verbatim, so gold still matches itself (oracle test). |
| Unsigned templates | SPORT-HALEY: party `__________`, date `19__` | Kept as labelled. These are correct labels for a template. |

## Disagreements between the label sources (202 issues across 136 contracts)

| Kind | Count | What it means | Consequence for evaluation |
|---|---|---|---|
| `span_without_answer` | 160 | The text *about* a field is labelled, but no value can be derived. 86 of these are Expiration Date, e.g. "continue until all … benefits are completed". | For typed fields, **"the topic is present" and "the value is correct" are different questions**. Phase 2 must score them separately. |
| `unparsed_answer` | 26 | An answer exists but carries no usable value (`[]/[]/[]`, redactions, non-places) | Exclude from value scoring, but keep for presence |
| `answer_without_span` | 16 | A value with no supporting span. Mostly `perpetual` or dates inferred from elsewhere. Includes 2 clauses (Insurance, Third Party Beneficiary marked Yes with no span). | Presence counts. No evidence to score against. |

Clause presence otherwise agrees between the CSV Yes/No and the JSON spans in 16,828 of 16,830 labels.

## Values that aren't in the text

Expiration and effective dates are often **computed** by the annotator. COOL TECH's expiration `5/26/2022` appears nowhere in the contract: it's "five (5) years from the date hereof" applied to the 5/26/2017 agreement date. The CUAD README describes this explicitly. Extracting these fields is a reasoning task, and it's the main reason to expect lower scores on dates than on clause presence.

## Corpus shape

- **All 510 PDFs are born-digital.** None is image-only. 98 have a few low-text pages, mostly signature or exhibit pages. OCR and multimodal routes can only be compared fairly on synthetic scans (SPEC §6.3).
- **Length varies 100×.** The median is about 33k characters, but Franchise and Agency contracts have a median above 115k, and the longest is 338k characters (roughly 85k tokens). The context budget (SPEC §7.4) matters most for these.
- **Field prevalence ranges from 2.5% (Source Code Escrow, 13 contracts) to 100% (Document Name).** Nine clauses have fewer than 10 positives in the 102-contract test set even with multi-label stratification ([ADR I9](../adr/I9-splits.md)).
