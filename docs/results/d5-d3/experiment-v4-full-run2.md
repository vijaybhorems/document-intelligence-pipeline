# Eval report: `20261020-230247-llm-gpt-5.6-luna-single-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single | experiment | 30/30 | `96b1a5f` | 2026-10-20 23:02 | $0.0030 | 15.5s / 23.7s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 88.1 | 86.8 | **87.4** | 81-94 | 87.4 | 81-94 |
| text | 1 | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 90.0 | 80-100 |
| date | 3 | 66 | 94.9 | 84.8 | **89.6** | 84-94 | 88.3 | 81-94 |
| duration | 2 | 21 | 91.3 | 100.0 | **95.5** | 85-100 | 96.4 | 89-100 |
| jurisdiction | 1 | 27 | 78.8 | 96.3 | **86.7** | 80-94 | 86.7 | 80-94 |
| clause | 33 | 215 | 69.3 | 88.4 | **77.7** | 73-82 | 68.8 | 61-75 |
| all fields | 41 | 427 | 78.0 | 88.8 | **83.0** | 80-85 | 73.0 | 67-79 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 92.8 | 97.5 | **95.1** | 91-98 | 95.0 | 91-98 |
| duration | 2 | 22 | 78.6 | 100.0 | **88.0** | 73-96 | 90.6 | 81-97 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 69.3 | 88.4 | **77.7** | 73-82 | 68.8 | 61-75 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 68.4 | 76.5 | **72.2** | 64-80 | 61.0 | 50-71 |
| ip_and_licensing | 10 | 51 | 73.0 | 90.2 | **80.7** | 74-86 | 65.8 | 54-79 |
| liability_and_risk | 5 | 39 | 81.0 | 87.2 | **84.0** | 73-92 | 74.6 | 51-91 |
| restrictive_covenants | 6 | 29 | 64.3 | 93.1 | **76.1** | 64-88 | 74.5 | 52-86 |
| term_and_termination | 4 | 45 | 62.9 | 97.8 | **76.5** | 68-83 | 76.0 | 65-84 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `most_favored_nation` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 9.1 | 100.0 | **16.7** | 0-46 | 16.7 | 15.4 |
| `third_party_beneficiary` | clause | presence | 2 | 33.3 | 50.0 | **40.0** | 0-100 | 40.0 | 50.0 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 23.5 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 40.0 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 46.2 |
| `volume_restriction` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 22.2 |
| `uncapped_liability` | clause | presence | 6 | 45.5 | 83.3 | **58.8** | 27-82 | 58.8 | 47.6 |
| `competitive_restriction_exception` | clause | presence | 4 | 44.4 | 100.0 | **61.5** | 22-89 | 61.5 | 19.0 |
| `non_compete` | clause | presence | 6 | 57.1 | 66.7 | **61.5** | 20-88 | 61.5 | 32.0 |
| `change_of_control` | clause | presence | 8 | 53.8 | 87.5 | **66.7** | 36-87 | 66.7 | 45.2 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `non_transferable_license` | clause | presence | 8 | 53.3 | 100.0 | **69.6** | 40-87 | 69.6 | 48.3 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 53.8 | **70.0** | 40-90 | 70.0 | 35.9 |
| `revenue_profit_sharing` | clause | presence | 11 | 72.7 | 72.7 | **72.7** | 46-90 | 72.7 | 26.3 |
| `expiration_date` | date | value | 19 | 92.3 | 63.2 | **75.0** | 54-89 | 94.3 |  |
| `non_disparagement` | clause | presence | 3 | 60.0 | 100.0 | **75.0** | 0-100 | 75.0 | 33.3 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 60.0 | **75.0** | 0-100 | 75.0 | 30.0 |
| `covenant_not_to_sue` | clause | presence | 7 | 85.7 | 85.7 | **85.7** | 57-100 | 85.7 | 52.6 |
| `ip_ownership_assignment` | clause | presence | 9 | 75.0 | 100.0 | **85.7** | 62-100 | 85.7 | 47.1 |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 72.7 |
| `governing_law` | jurisdiction | value | 27 | 78.8 | 96.3 | **86.7** | 80-94 | 98.1 |  |
| `parties` | entity_list | value | 68 | 88.1 | 86.8 | **87.4** | 81-94 | 100.0 |  |
| `termination_for_convenience` | clause | presence | 7 | 77.8 | 100.0 | **87.5** | 60-100 | 87.5 | 60.9 |
| `document_name` | text | value | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 100.0 |  |
| `warranty_duration` | clause | presence | 6 | 100.0 | 83.3 | **90.9** | 60-100 | 90.9 | 58.8 |
| `exclusivity` | clause | presence | 11 | 84.6 | 100.0 | **91.7** | 77-100 | 91.7 | 70.6 |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 98.2 |  |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 78-100 | 81.2 |  |
| `license_grant` | clause | presence | 14 | 87.5 | 100.0 | **93.3** | 81-100 | 93.3 | 51.9 |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 60.5 |
| `cap_on_liability` | clause | presence | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 97.6 | 48.0 |
| `effective_date` | date | value | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 92.6 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 63.6 |
| `insurance` | clause | presence | 5 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 22.9 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 76.9 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 |  |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 0.0 | 1 | — | 0 | — |
| `anti_assignment` | 100.0 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 13 | 87.5 | 8 | +12.5 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 87.5 | 8 | +12.5 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 100.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 58.3 | 12 | 0.0 | 1 | +58.3 |
| `most_favored_nation` | 0.0 | 1 | — | 0 | — |
| `no_solicit_of_customers` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `no_solicit_of_employees` | 100.0 | 2 | 100.0 | 1 | +0.0 |
| `non_compete` | 50.0 | 4 | 100.0 | 2 | -50.0 |
| `non_disparagement` | 100.0 | 1 | 100.0 | 2 | +0.0 |
| `non_transferable_license` | 100.0 | 6 | 100.0 | 2 | +0.0 |
| `notice_period_to_terminate_renewal` | 100.0 | 5 | 100.0 | 4 | +0.0 |
| `post_termination_services` | 100.0 | 2 | 100.0 | 7 | +0.0 |
| `price_restrictions` | — | 0 | 100.0 | 1 | — |
| `renewal_term` | 100.0 | 11 | 100.0 | 2 | +0.0 |
| `revenue_profit_sharing` | 100.0 | 7 | 25.0 | 4 | +75.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 33.3 | 3 | +66.7 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 95.2 | 248 | 80.3 | 71 | +14.9 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 29/30 | 96.7 |
| quotes found in the contract | 544/544 | 100.0 |
| values with no grounded evidence | 0/444 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/96 | 0.0 |
| false positives, grounded (over-triggers) | 96/96 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 87.4 | +25.7 |
| text | 63.0 | 90.0 | +27.0 |
| date | 60.0 | 89.6 | +29.6 |
| duration | 81.1 | 95.5 | +14.4 |
| jurisdiction | 83.3 | 86.7 | +3.3 |
| clause | 53.5 | 77.7 | +24.2 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `most_favored_nation` | 66.7 | 0.0 | -66.7 |
| `non_transferable_license` | 85.7 | 69.6 | -16.1 |
| `rofr_rofo_rofn` | 88.9 | 75.0 | -13.9 |
| `non_disparagement` | 85.7 | 75.0 | -10.7 |
| `third_party_beneficiary` | 50.0 | 40.0 | -10.0 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `warranty_duration` | 34.3 | 90.9 | +56.6 |
| `effective_date` | 40.0 | 97.6 | +57.6 |
| `expiration_date` | 10.0 | 75.0 | +65.0 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
