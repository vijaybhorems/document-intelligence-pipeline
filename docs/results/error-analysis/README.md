# Error analysis: 50 dev errors, categorized by hand

SPEC §10.8. Source: the production configuration on dev, run `20261020-231956-llm-gpt-5.6-luna-single+validate-warn-reask-dev` (prompt v4, one call, validation + re-ask), 80 contracts.

## Method

1. **List every error:** a (contract, field) pair with a false positive or false negative on the headline metric. There are **382**:

   | | Errors |
   |---|---|
   | By field type | 290 clause, 40 date, 22 parties, 12 governing law, 9 duration, 9 document name |
   | By rule-based first guess | 244 "over-trigger" (a prediction where gold is absent), 71 "missed", 67 "wrong value" |

2. **Sample 50**, stratified by that guess, with at most two per field for variety (seed 20261026).
3. **Read each one:** the gold span, the predicted quote and value, and, where a quote was cut off, the contract text itself. Then assign one category from the SPEC taxonomy, a confidence, and a one-line reason.

All 50 verdicts, with reasons, are in [`categorized.jsonl`](categorized.jsonl).

## Results

| Category | Count | Meaning |
|---|---|---|
| `over_trigger` | **21** | a real quote, but the clause doesn't legally qualify |
| `label_noise` | **13** (8 high-confidence) | the text qualifies; gold says it doesn't (or gold has a typo) |
| `missed` | **8** | the clause was there and wasn't extracted |
| `wrong_value` | **6** | the right place, the wrong value |
| `normalization` | **2** | our matcher, not the model |
| `hallucinated` | **0** | (Phase 4: 0 of 274 false positives were ungrounded) |
| `parse_error` | **0** | dev runs on CUAD text; parsing is measured separately (D1) |

**The finding that changes how to read the scores:** of the 32 sampled errors the rule-based guess called over-triggers, **11 look like label noise** once read. Eight are clear-cut:
- E11: "in no event shall any indemnity… exceed the net proceeds" is a cap on liability.
- E28: "IBM grants MSL a royalty-free license…" is a licence grant.
- E31: "All right, title and interest… shall vest in… the Licensor" is an IP ownership assignment.
- E17: "the Patent License shall terminate immediately upon ETI ceasing to be a Subsidiary of NTL" is a change-of-control trigger.
- E30: "will not use User Data to… solicit any Excite users… for twelve months" is a no-solicit of customers.
- E12: "shall not… transfer in any manner any right… to the License Technology" is a non-transferable licence.
- E22: optional three-year extensions are a renewal term, the same pattern gold counts as one elsewhere (D8, task bool-16).
- E46: gold says "Northern *America* Chapter"; the contract says "Northern *California* Chapter".

So measured **clause precision understates true precision**. These verdicts are one reader's legal judgment, not a re-annotation of CUAD, so the reported scores stay against gold, unchanged.

## Why these categories are hard

**1. Clauses that need legal judgment, not keyword matching (the over-triggers).** The model finds text that *talks about* the topic and reads it as the clause:
- **An indemnity is not uncapped liability** (E21, E27). Uncapped liability needs an explicit statement that liability isn't capped, or exceptions to a cap.
- **A survival clause is not post-termination services** (E13).
- **Price tiers are not a volume restriction** (E09); "prices are in US dollars, FOB Frisco" is not a price restriction (E10).
- **An anti-assignment clause with a merger exception is not change of control** in CUAD's convention (E19), even though "merger" appears.
- **Background recitals ("WHEREAS…") describe licences granted elsewhere** (E08, E15).

These are the fields at the bottom of the per-field table: price restrictions, volume restriction, third-party beneficiary, uncapped liability, competitive restriction exception, post-termination services.

**2. CUAD's categories are broader, or narrower, than their names.**
- **Broader, so it misses:**
  - A yearly promotional obligation is a *minimum commitment* (E36).
  - An employee's named beneficiary is a *third-party beneficiary* (E37).
  - Exceptions to a damages limitation ("except for breach of Article VIII…") count as *uncapped liability* (E40).
- **Narrower, so it over-triggers:**
  - An option to order more product is not a *price restriction* (E18).
  - A restaurant development schedule is not a *minimum commitment* (E32).

  Phase 5 found the same thing: definitions and examples moved precision, but a few phrasing variants can't teach where a category ends.

**3. Dates that must be computed or looked up** (E45, E48, E49):
- "twelve months after the Launch";
- "continue for a period of three (3) years" from an effective date given elsewhere;
- an effective date defined only by reference.

The model returns no value rather than guessing, which is the safe failure: it shows up as lower recall on expiration dates (69 on dev), not as wrong dates.

**4. Two plausible answers in one document** (E44, E50): a preamble date and a signature date; a title and a different name in the preamble. CUAD's convention picks one (preamble date, title), and the model sometimes picks the other.

**5. Our own matching** (E42, E43, E47).
- **E42 is systematic:** the model adds "United States" next to a state's law (also visible in the Phase 9.5 MCP test, "Delaware, United States").
- **The fix:** a normalizer rule that drops a country when one of its states is present. On the test set it accounts for 20 of governing law's 21 false positives (precision 80.6, or 98.9 without them): the cheapest win on this list.
- **E43 and E47:** party names with descriptors ("…, a Nevada corporation"), and full title lines, need looser matching.

**6. Plain misses still exist** (E33, E41): "Either party may terminate… by providing [*] month's written notice" was missed outright. They're a minority (2 of 50).

## What I'd do next, in order of value per effort

1. **Normalizer:** drop "United States" when a US state is present; strip entity descriptors from party names. Free, and it fixes a systematic error.
2. **Hard negatives for the over-triggers above:**
   - indemnity vs uncapped liability;
   - survival vs post-termination;
   - assignment-with-merger-exception vs change of control;
   - WHEREAS recitals.

   Re-measure on dev (≈$0.50 per run, 2 runs for the noise floor).
3. **Date computation:** ask for the expression ("three years from the Effective Date") as well as the value, and compute it in code when an anchor date exists.
4. **Report noise-adjusted precision as a secondary number:** have a second reader re-annotate the suspected label-noise cases, then report both.
