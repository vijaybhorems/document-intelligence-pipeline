# ADR D8: MCP tool design

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-21 |
| **Spec ref** | SPEC §12.2.3, §12.2.6; decision D8 |

## Context

The MCP server (Phase 9.5) is used by agents, not people. Two design choices change what an agent can do with it:
- **Granularity:** a few coarse tools (`search_records` takes every filter at once, `get_record` returns any projection), or many fine-grained tools (one finder per filter, an overview, one field at a time).
- **Descriptions:** terse one-liners (v1), or descriptions written for the model (v2) that say when to use a tool, how to combine filters, how often to poll, how to cite, and that quotes are untrusted.

Spec §12.2.6 also asks for an **oracle run**, so that agent errors can be told apart from extraction errors.

## Options considered

The variants are {coarse, fine} × {v1, v2}, run against two stores of the same 80 dev contracts:
- **normal:** what the production pipeline extracted (run `20261020-231956`, prompt v4, validation + re-ask);
- **oracle:** the gold labels as records.

## Evidence

**Setup:**
- **Tasks:** 25, generated from gold: 8 set questions ("which contracts governed by X contain Y?"), 6 expiration dates, 5 renewal yes/no, 6 "quote clause Y".
- **Runs:** each task 3 times, with gpt-5.6-luna at reasoning effort low and only the MCP tools.
- **Scoring:** exact match for sets, dates and booleans. A quote counts if it is found in the contract and overlaps the gold span. Citation accuracy is the share of cited quotes found verbatim (or nearly) in the cited contract.
- **Cost:** 600 agent runs, **$0.43** in total. Full tables are in [`docs/results/d8/`](../results/d8/README.md).

| Variant | Normal accuracy | Oracle accuracy | Citation acc. (normal) | Tool calls / task | $ / task |
|---|---|---|---|---|---|
| **coarse, v2** | 0.640 | **0.933** | **0.903** | 1.28 | 0.00067 |
| fine, v2 | 0.653 | 0.907 | 0.892 | 1.53 | 0.00084 |
| coarse, v1 | 0.653 | 0.893 | 0.763 | 1.04 | 0.00059 |
| fine, v1 | 0.640 | 0.920 | 0.825 | 2.35 | 0.00084 |

Paired differences over the 25 tasks, with 95% bootstrap CIs:

| Comparison | Accuracy | Citation accuracy |
|---|---|---|
| **oracle − normal records** (coarse, v2) | **+29.3 [+13.3, +46.7]** | −2.7 [−13.3, +9.3] |
| v2 − v1 descriptions (normal, coarse) | −1.3 [−4.0, 0.0] | **+8.1 [+2.7, +14.9]** |
| v2 − v1 descriptions (oracle, coarse) | +4.0 [−2.7, +13.3] | +1.3 [−5.3, +9.3] |
| fine − coarse tools (normal, v2) | +1.3 [0.0, +4.0] | −2.7 [−9.3, +2.7] |
| fine − coarse tools (oracle, v2) | −2.7 [−10.7, +4.0] | +1.3 [0.0, +4.0] |

## What we learned

1. **The agent's errors are mostly the records' errors.** With gold records, the same agent answers 93% of tasks; with ours, 64%. Of the 9 tasks that fail with our records, 7 succeed with gold.
   - **Set questions** are hit hardest: 25% exact with our records, 100% with gold. A "which contracts…" answer is exact only if every one of 80 contracts was extracted right for that clause. Field-level F1 around 83 compounds into rare exact sets, though set F1 is still 0.78.
   - **The fix belongs upstream:** better clause precision and recall (prompting, D5), not better tools.
2. **Description quality shows up in citations, not answers.** v2's instructions to "copy quotes verbatim, never paraphrase" raised citation accuracy by 8 points on real records, at +14% cost (≈2,500 more input tokens per task). Answer accuracy didn't move.
3. **Finer tools cost more and buy nothing.** Fine-grained tools needed 20–125% more calls and 25–42% more spend at the same accuracy. On the oracle store they were slightly *worse* on sets (0.83 vs 1.00): intersecting results across calls is work the agent can get wrong, and a combined filter makes impossible.
4. **The eval found two of its own bugs:**
   - **bool-16 had wrong gold:** it asked about *automatic* renewal, but CUAD's Renewal Term includes optional extensions. The agents' "false" was right. The generator is fixed; without that task, oracle accuracy is 0.958 and normal 0.667.
   - **quote-21 is a real agent error:** given up to three quotes for one clause, the agent joined them into one "quote" found nowhere in the contract.
5. **Agents barely needed to recover from errors:** tool errors were ≤ 0.05 per task, and every run ended with an answer. Actionable error messages weren't really tested by this task set.

## Decision

**Coarse tools with v2 descriptions.** That's the spec's tool set (`submit_extraction`, `get_extraction_status`, `get_record`, `search_records`, `run_analytics`), with descriptions written for the model. `dip-mcp` serves `DIP_MCP_DESCRIPTIONS=v2` and coarse tools; the fine variant stays in the code for re-measurement.

## Consequences

- **Agent quality now tracks extraction quality.** Improving clause F1 (Phase 10 error analysis) is the lever for agent answers too. Re-run this eval against new records after any pipeline change: it costs about $0.05 per variant.
- **v2 costs ~2,500 more tokens per task** for better citations. Worth it: a wrong citation is worse than a slightly more expensive right one.
- **Possible tool change:** return one "best" quote per field, or label multiple quotes "separate passages: cite one". That targets the quote-joining error, and is the next description experiment.
- **When I'd choose differently:**
  - **A weaker or smaller agent model** might benefit from fine-grained tools (simpler schemas); re-test before assuming.
  - **Agents that browse rather than answer** (exploratory UIs) might prefer `get_contract_overview`-style tools.
  - **A task set with failing tool calls** (malformed dates, unknown clauses) would test error messages, which this one didn't.
