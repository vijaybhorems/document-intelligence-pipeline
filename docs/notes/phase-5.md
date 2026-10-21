# Phase 5: Prompting & context engineering

**Goal (SPEC §14):** phrasing variants, few-shot examples from train, defined-terms extraction, glossary, retrieval variant; the D3 and D5 ablations.
**Done when:** the non-canonical recall gap has shrunk *or been explained*, and the D3/D5 ADRs are written.

## What was built

- [x] `dip.extract.examples` + `dip build-field-notes`: phrasing variants, a positive and a **hard negative** per field, from **train gold only**, filtered to clause-like text. Committed as `prompts/field_notes.json`.
- [x] `dip.extract.context`: regex extraction of the contract's defined terms, using `"X" means ...` and `ABC Corp. (the "Distributor")`.
- [x] Prompt versions v1–v4. Each adds one feature and inherits earlier prompt files. `--prompt-version`; v4 is now the default.
- [x] `dip.extract.retrieval`: LlamaIndex chunking + `text-embedding-3-small`; one embedded query per field, computed once per run; merged excerpts in document order. `--context retrieved`.
- [x] `Usage.embedding_tokens`, so retrieval never inflates LLM input counts.
- [x] Tests: 238 passing, using `MockEmbedding` and the fake client.
- [x] [ADR D5](../adr/D5-prompt-strategy.md), [ADR D3](../adr/D3-context-budget.md); reports in [`docs/results/d5-d3/`](../results/d5-d3/).

## What I measured

**Progression on dev (80 contracts), overall micro F1:**

| System | F1 (95% CI) | Clause P / R | $/contract |
|---|---|---|---|
| keyword baseline (Phase 2) | 55.8 (52–59) | 39.6 / 91.1 | $0 |
| LLM, prompt v1 (Phase 3) | 81.5 (80–84) | 67.6 / 85.9 | $0.0048 |
| + validation and re-ask (Phase 4) | 81.7 | 68.1 / 85.7 | $0.0054 |
| prompt v4 (Phase 5) | 82.7 | 69.3 / 89.0 | $0.0055 |
| **v4 + validation and re-ask: current best** | **82.8 (81–85)** | **69.7 / 88.7** | **$0.0060** |

For the best system: 100% valid outputs, 0 unsupported values, 0 hallucinated false positives, p50 14.2 s / p95 21.3 s.

**D5 (prompts):** v4 beats v1 by +1.18 on dev (CI +0.07 to +2.38) and by +1.8 on the experiment set (2 runs each). The individual steps are within noise.
**D3 (context):** retrieval saves 17% of LLM input but costs **3–4 F1** (CIs exclude zero). Full context stays.

**Spend so far:** $7.18 of $10.

## The phrasing gap: explained, not closed

The gap between recall on usually-worded and unusually-worded clauses stayed around 11 points (11.7 → 10.7 on dev). Looking at the misses showed why. They aren't odd *wordings* of a recognisable clause; they're clauses where **CUAD's category is broader than its name**:
- a "Success Fee of 0.85%" is Revenue/Profit Sharing;
- "ensure each vessel is seaworthy" is Warranty Duration;
- "won't grant rights to anyone before the Investor exercises its option" is a ROFN.

More phrasing examples can't teach category boundaries; fuller definitions can. That's the next lever, and the slice metric is how you'll know it worked.

## Things that went wrong, and what they taught

1. **"Shortest span" made terrible examples.** CUAD labels clauses as disjoint fragments, so the shortest pieces were meaningless ("and which the Company has not repurchased."). The fix was to filter for complete sentences with obligation language.
2. **A single good run lied a little.** v4's first run was +2.3 and the replicate +1.2. Two runs per arm, plus a confirmation on dev, gave the real number.
3. **Overlapping chunks duplicated text**, and so did whitespace gaps between chunks (a `[...]` marker went into the middle of contiguous text). Caught by checking that a short contract comes back byte-identical.
4. **Embedding tokens were counted as LLM input tokens**, which made retrieval look *more* expensive. Now separate.
5. **Dev and the experiment set overlap** (experiment ⊂ dev), so the dev confirmation isn't fully independent. Prompt content came only from train, so there's no label leak, but the honest final check is the frozen test set in Phase 10.

## Concepts to understand before moving on

1. Why must phrasing variants and examples come from **train** only? What exactly would be inflated if they came from dev?
2. What is a *hard negative*, and why target over-triggering with it rather than with more positive examples?
3. v2, v3 and v4 each moved F1 by less than the noise floor, yet v4 as a whole is a real improvement. How can both be true?
4. Why did retrieval save only 17% of tokens with a single call? When would it save 80%?
5. Why build the defined-terms table from the *full* contract even when sending retrieved excerpts?
6. The phrasing gap didn't close. Why is "explained" an acceptable outcome, and what would you try next?

## Try it yourself

```bash
uv run dip build-field-notes                                          # regenerate from train (deterministic)
uv run dip estimate --split experiment --prompt-version v1            # compare prompt sizes, free
uv run dip estimate --split experiment --prompt-version v4
uv run python -c "from dip.extract.context import extract_defined_terms as x; print(x(open('data/raw/CUAD_v1/full_contract_txt/' + sorted(__import__('os').listdir('data/raw/CUAD_v1/full_contract_txt'))[5]).read())[:10])"
```

## My answers

<!-- Fill in. -->

## What surprised me

<!-- Fill in. -->
