# Eval report: `20261021-031448-llm-gpt-5.6-luna-single-v4-docling-clean-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-docling-clean | experiment | 30/30 | `58855d2` | 2026-10-21 03:14 | $0.0071 | 16.5s / 23.6s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 86.2 | 82.4 | **84.2** | 75-93 | 84.2 | 75-93 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 95.0 | 86.4 | **90.5** | 85-95 | 89.6 | 82-95 |
| duration | 2 | 21 | 87.5 | 100.0 | **93.3** | 82-100 | 93.5 | 82-100 |
| jurisdiction | 1 | 27 | 83.9 | 96.3 | **89.7** | 83-96 | 89.7 | 83-96 |
| clause | 33 | 215 | 69.8 | 89.3 | **78.4** | 74-82 | 71.6 | 62-78 |
| all fields | 41 | 427 | 77.9 | 88.5 | **82.9** | 80-85 | 75.1 | 68-80 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 92.7 | 96.2 | **94.4** | 90-98 | 94.4 | 90-98 |
| duration | 2 | 22 | 75.9 | 100.0 | **86.3** | 71-95 | 88.0 | 75-95 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 69.8 | 89.3 | **78.4** | 74-82 | 71.6 | 62-78 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 70.2 | 78.4 | **74.1** | 65-82 | 59.0 | 49-68 |
| ip_and_licensing | 10 | 51 | 78.3 | 92.2 | **84.7** | 77-90 | 78.1 | 64-91 |
| liability_and_risk | 5 | 39 | 73.9 | 87.2 | **80.0** | 70-89 | 69.8 | 48-84 |
| restrictive_covenants | 6 | 29 | 62.8 | 93.1 | **75.0** | 62-85 | 74.7 | 51-85 |
| term_and_termination | 4 | 45 | 63.8 | 97.8 | **77.2** | 70-83 | 78.4 | 69-85 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `most_favored_nation` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 10.0 | 100.0 | **18.2** | 0-50 | 18.2 | 16.7 |
| `third_party_beneficiary` | clause | presence | 2 | 25.0 | 50.0 | **33.3** | 0-80 | 33.3 | 22.2 |
| `volume_restriction` | clause | presence | 2 | 25.0 | 50.0 | **33.3** | 0-75 | 33.3 | 0.0 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 17.6 |
| `competitive_restriction_exception` | clause | presence | 4 | 36.4 | 100.0 | **53.3** | 18-80 | 53.3 | 8.3 |
| `uncapped_liability` | clause | presence | 6 | 41.7 | 83.3 | **55.6** | 25-78 | 55.6 | 45.5 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 44.4 |
| `non_compete` | clause | presence | 6 | 57.1 | 66.7 | **61.5** | 20-88 | 61.5 | 37.0 |
| `change_of_control` | clause | presence | 8 | 50.0 | 87.5 | **63.6** | 35-83 | 63.6 | 40.0 |
| `no_solicit_of_customers` | clause | presence | 2 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 42.9 |
| `non_disparagement` | clause | presence | 3 | 60.0 | 100.0 | **75.0** | 0-100 | 75.0 | 18.2 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 60.0 | **75.0** | 0-100 | 75.0 | 30.0 |
| `warranty_duration` | clause | presence | 6 | 71.4 | 83.3 | **76.9** | 40-100 | 76.9 | 54.5 |
| `ip_ownership_assignment` | clause | presence | 9 | 64.3 | 100.0 | **78.3** | 56-94 | 78.3 | 54.1 |
| `expiration_date` | date | value | 19 | 92.9 | 68.4 | **78.8** | 59-91 | 92.3 |  |
| `joint_ip_ownership` | clause | presence | 3 | 100.0 | 66.7 | **80.0** | 0-100 | 80.0 | 40.0 |
| `non_transferable_license` | clause | presence | 8 | 66.7 | 100.0 | **80.0** | 53-95 | 80.0 | 29.6 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 69.2 | **81.8** | 61-96 | 81.8 | 39.0 |
| `revenue_profit_sharing` | clause | presence | 11 | 81.8 | 81.8 | **81.8** | 57-96 | 81.8 | 27.8 |
| `parties` | entity_list | value | 68 | 86.2 | 82.4 | **84.2** | 75-93 | 100.0 |  |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 72.7 |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 17.6 |
| `governing_law` | jurisdiction | value | 27 | 83.9 | 96.3 | **89.7** | 83-96 | 98.1 |  |
| `exclusivity` | clause | presence | 11 | 84.6 | 100.0 | **91.7** | 77-100 | 91.7 | 72.7 |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 98.2 |  |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 66.7 |
| `audit_rights` | clause | presence | 13 | 86.7 | 100.0 | **92.9** | 80-100 | 92.9 | 57.8 |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 80-100 | 81.2 |  |
| `license_grant` | clause | presence | 14 | 87.5 | 100.0 | **93.3** | 81-100 | 93.3 | 55.2 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 94.7 |  |
| `cap_on_liability` | clause | presence | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 97.6 | 47.4 |
| `effective_date` | date | value | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 92.6 |  |
| `affiliate_license_licensor` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 76.9 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `termination_for_convenience` | clause | presence | 7 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 70.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 100.0 | 1 | — | 0 | — |
| `anti_assignment` | 100.0 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 13 | 87.5 | 8 | +12.5 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 94.4 | 18 | 87.5 | 8 | +6.9 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 75.0 | 12 | 0.0 | 1 | +75.0 |
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
| `revenue_profit_sharing` | 100.0 | 7 | 50.0 | 4 | +50.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 33.3 | 3 | +66.7 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 95.2 | 248 | 81.7 | 71 | +13.5 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 29/30 | 96.7 |
| quotes found in the contract | 561/568 | 98.8 |
| values with no grounded evidence | 4/447 | 0.9 |
| false positives, ungrounded (**hallucinated**) | 0/96 | 0.0 |
| false positives, grounded (over-triggers) | 96/96 |  |
| correct fields whose quote wasn't found | 4 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 84.2 | +22.5 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 90.5 | +30.5 |
| duration | 81.1 | 93.3 | +12.3 |
| jurisdiction | 83.3 | 89.7 | +6.3 |
| clause | 53.5 | 78.4 | +24.9 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `most_favored_nation` | 66.7 | 0.0 | -66.7 |
| `third_party_beneficiary` | 50.0 | 33.3 | -16.7 |
| `rofr_rofo_rofn` | 88.9 | 75.0 | -13.9 |
| `non_disparagement` | 85.7 | 75.0 | -10.7 |
| `change_of_control` | 70.6 | 63.6 | -7.0 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `effective_date` | 40.0 | 97.6 | +57.6 |
| `expiration_date` | 10.0 | 78.8 | +68.8 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
| `affiliate_license_licensor` | 8.7 | 100.0 | +91.3 |
