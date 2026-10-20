# ADR I9: How the dataset is split

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-19 |
| **Spec ref** | SPEC §2.3 |

## Context

Every result in this project is measured on a split, so a bad split corrupts every decision made from it. Two constraints pull against each other:

- The test set must be **frozen and reproducible**, so results stay comparable for the life of the project.
- 33 of the 41 fields are clauses with very uneven prevalence: Source Code Escrow appears in 13 of 510 contracts, Anti-Assignment in 374. A small split can easily contain zero examples of a rare clause, and then that clause can't be measured at all.

## Options considered

1. **Random split.** Simple, but rare clauses land wherever chance puts them.
2. **Stratify by contract type.** Keeps each contract type proportional. This was the first version.
3. **Multi-label iterative stratification** (Sechidis et al., ECML 2011) over contract type **and** the presence of all 41 fields.

## Evidence

Same seed, same sizes (test 102 / dev 80 / experiment 30). Positives per split:

| Field | Option 2: test | Option 2: experiment | **Option 3: test** | **Option 3: experiment** |
|---|---|---|---|---|
| Most Favored Nation (28 total) | 2 | 3 | **6** | **1** |
| Affiliate License-Licensor (23) | 2 | 0 | **5** | **1** |
| Source Code Escrow (13) | 3 | 0 | **3** | **1** |
| Third Party Beneficiary (32) | 9 | 0 | **6** | **2** |
| Price Restrictions (15) | 4 | 1 | **3** | **1** |
| Contract types in test | 26 | | **26** | |

Option 2 left three fields with **zero** examples in the experiment set, which every parser, model and prompt bake-off uses (decisions D1–D5). Those decisions would have been blind to those fields.

## Decision

Option 3. `make_splits()` runs iterative stratification three times: corpus → test/rest, rest → dev/train, dev → experiment. Smoke is the shortest contract of each type in experiment, for cheap CI runs. The seed and algorithm are recorded in `data/splits.json`. Regenerating with the same seed reproduces the file exactly, and `write_splits()` refuses to overwrite it without `--force`.

The switch happened before any evaluation had run, so no results were invalidated.

## Consequences

- Rare clauses are as proportional as integer counts allow. 30 × 2.5% is still under one, so **per-field metrics for the rarest clauses will be noisy on any split**. Report them with bootstrap CIs and lean on field-type and clause-family rollups (SPEC §10.4).
- Contract-type balance is now approximate (±1 per type) rather than exact. Test still contains all 26 types.
- **Revisit if:** the rarest clauses matter enough to justify cross-validation over train+dev for those fields only, instead of one fixed dev split.
