# D8 agent task eval: results

Generated from `data/runs/*-agent-*-dev` by `dip.agent_eval.compare` (2026-10-21).
25 tasks over the 80 dev contracts, 3 runs each; agent gpt-5.6-luna (reasoning low), only the MCP tools.

| Store | Descriptions | Tools | Accuracy | Set | Date | Boolean | Quote | Set F1 | Citation acc. | Tool calls / task | Input tokens / task | $ / task |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| normal | v2 | coarse | 0.640 | 0.25 | 1.00 | 0.73 | 0.72 | 0.778 | 0.903 | 1.28 | 5,896 | 0.00067 |
| normal | v2 | fine | 0.653 | 0.25 | 1.00 | 0.80 | 0.72 | 0.773 | 0.892 | 1.53 | 5,715 | 0.00084 |
| normal | v1 | coarse | 0.653 | 0.25 | 1.00 | 0.80 | 0.72 | 0.778 | 0.763 | 1.04 | 3,432 | 0.00059 |
| normal | v1 | fine | 0.640 | 0.25 | 1.00 | 0.80 | 0.67 | 0.776 | 0.825 | 2.35 | 5,152 | 0.00084 |
| oracle | v2 | coarse | 0.933 | 1.00 | 1.00 | 0.87 | 0.83 | 1.000 | 0.888 | 1.2 | 5,669 | 0.00067 |
| oracle | v2 | fine | 0.907 | 0.83 | 1.00 | 0.93 | 0.89 | 0.981 | 0.881 | 1.56 | 5,649 | 0.00080 |
| oracle | v1 | coarse | 0.893 | 1.00 | 1.00 | 0.80 | 0.72 | 1.000 | 0.868 | 1.01 | 3,354 | 0.00054 |
| oracle | v1 | fine | 0.920 | 0.96 | 1.00 | 0.80 | 0.89 | 0.996 | 0.883 | 2.56 | 5,151 | 0.00083 |

## Paired differences (95% bootstrap CI over the 25 tasks)

| Comparison | Accuracy | Citation accuracy |
|---|---|---|
| v2 vs v1 descriptions (normal, coarse) | -1.3 [-4.0, +0.0] | +8.1 [+2.7, +14.9] |
| v2 vs v1 descriptions (oracle, coarse) | +4.0 [-2.7, +13.3] | +1.3 [-5.3, +9.3] |
| fine vs coarse tools (normal, v2) | +1.3 [+0.0, +4.0] | -2.7 [-9.3, +2.7] |
| fine vs coarse tools (oracle, v2) | -2.7 [-10.7, +4.0] | +1.3 [+0.0, +4.0] |
| oracle vs normal records (v2, coarse) | +29.3 [+13.3, +46.7] | -2.7 [-13.3, +9.3] |

## Where the errors come from (normal vs oracle, v2 coarse)

- **Extraction** (right with gold records, wrong with ours): quote-20, set-00, set-01, set-02, set-04, set-05, set-06
- **Agent / task** (wrong even with gold records): bool-16, quote-21
- Right in both: 16 tasks

`bool-16` turned out to be a task defect: it asked whether a contract renews *automatically*, but its gold
renewal term is an optional extension by mutual consent, so the agents' "false" was right. The generator
now asks about renewal or extension. Accuracy without it: normal/v2/coarse 0.667, oracle/v2/coarse 0.958.
`quote-21` is a real agent error: given several quotes for one clause, the agent joined them into one
"quote" that appears nowhere in the contract.
