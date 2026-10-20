# Phase 4: Validation & grounding

**Goal (SPEC §14):** normalizers, grounding, consistency rules, re-ask; the D6 and D7 experiments.
**Done when:** hallucination and valid-output rates are reported, and the D6/D7 ADRs are written.

## What was built

- [x] `dip.validate.grounding`: locate every quote as exact, then normalized (whitespace, case, curly quotes), then fuzzy, then **spliced** (quotes that skip an EDGAR page footer or use "..."). Grounded quotes are snapped to source text with offsets.
- [x] `dip.validate.rules`: six consistency rules, each measured against train-split gold before use.
- [x] `dip.validate.validator`: `warn` / `drop` policies (D7) and optional rule enforcement.
- [x] `dip validate <run>`: derived runs that re-process saved predictions **for free**; `--reask` makes one follow-up call per contract with errors, for just the failing fields (D6). Spend goes into the derived run's own ledger, so nothing is counted twice.
- [x] `dip.eval.validation_metrics`: grounding rate, unsupported values, **hallucination vs over-trigger split of false positives**, valid-output rate. Shown in every report, alongside cost and latency.
- [x] Tests: 223 passing (22 new), including a fake re-asker.
- [x] [ADR D6](../adr/D6-validation-placement.md), [ADR D7](../adr/D7-grounding-policy.md); reports in [`docs/results/d6-d7/`](../results/d6-d7/).

## What I measured (dev, 80 contracts, gpt-5.6-luna, single call)

| | |
|---|---|
| Quotes found in the contract | **99.9%** (1457/1459) |
| Hallucinated false positives | **0 of 274** |
| Over-triggering false positives (real text, wrong reading) | **274 of 274** |
| Valid outputs: raw / with re-ask | 79/80 → **80/80** |
| Overall F1: raw / with re-ask | 81.52 → **81.70** (Δ +0.18, CI 0.00 to +0.37) |
| Re-ask cost | +$0.0006/contract (9 of 80 contracts re-asked) |
| Spend so far | $5.73 of $10 |

## Decisions made

- **D7 = warn.** `drop` removed one value, and it was correct (a quote across a redaction). There were no hallucinations to catch.
- **D6 = validate after extraction + re-ask on errors.** It's the only option with 100% valid outputs and 0 unsupported values, at +12% cost. Rule enforcement is the free fallback.
- **Rules come from data.** "Cap and Uncapped Liability both present" was proposed in the spec and rejected: 21% of gold contracts have both. The two "dependency" rules turned out to be excellent false-positive detectors: the flagged prediction was wrong 6 times out of 7.

## The finding that matters for Phase 5

**The model doesn't make things up. It misreads.** Every false positive quotes real text. For example, the model calls something a "competitive restriction exception" when the contract contains no restriction for it to be an exception to. Grounding can't see that kind of error, so validation moved F1 by only +0.18. The precision problem is legal judgment, which is what prompting and context (Phase 5) are for.

## Things that went wrong, and what they taught

1. **Tooling turned `’` escapes into literal curly quotes** in files written through the editor and in heredocs. Ruff flagged them as ambiguous characters. Fix: write code points as `chr(0x2019)`, which nothing rewrites.
2. **The first splice algorithm split on sentence punctuation**, and missed page breaks that fall mid-sentence. The replacement greedily matches the longest run of words (binary search) and allows small gaps in the source.
3. **A test-label leak:** I first measured rule false-alarm rates on all 510 gold contracts, test included. Recomputing on train only gave the same rates (to 0.2 points), so no decision changed. But rule design should only ever look at train.
4. **A derived run could have double-counted spend** (its `run.json` carries the base run's cost). Derived runs always write a ledger, and the ledger takes precedence. A test covers it.

## Concepts to understand before moving on

1. Why compare `warn` and `drop` on the *same* saved predictions rather than two fresh runs? What noise does that remove?
2. A false positive can be a *hallucination* or an *over-trigger*. Why do they need different fixes, and which one does grounding catch?
3. `drop` deleted a correct value. What caused the grounding miss, and how would OCR'd input (Phase 6) change the drop-vs-warn trade-off?
4. Why must a consistency rule be tested against gold before it's used on predictions? What's the cost of one that fires on 21% of gold?
5. The re-ask only touched 11% of contracts. Why does that keep it cheap, and what would make it worth more?

## Try it yourself

```bash
uv run dip validate <run_id> --policy drop                 # free: re-process saved predictions
uv run dip validate <run_id> --policy warn --reask         # small cost: re-asks failing fields only
uv run python -c "from dip.validate.grounding import SourceText; s = SourceText(open('data/raw/CUAD_v1/full_contract_txt/' + __import__('os').listdir('data/raw/CUAD_v1/full_contract_txt')[0]).read()); print(s.locate('This Agreement'))"
```

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
