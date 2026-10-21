# Eval report: `20261020-210832-llm-gpt-5.6-luna-single-experiment`

| system | split | contracts | git | created (UTC) |
|---|---|---|---|---|
| llm-gpt-5.6-luna-single | experiment | 30 | `e3ac30c` | 2026-10-20 21:08 |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 92.5 | 87-98 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 90.3 | 84.8 | **87.5** | 80-93 | 85.5 | 76-92 |
| duration | 2 | 21 | 87.5 | 100.0 | **93.3** | 83-100 | 93.5 | 82-100 |
| jurisdiction | 1 | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 91.2 | 85-98 |
| clause | 33 | 215 | 67.8 | 87.0 | **76.2** | 71-81 | 68.4 | 59-75 |
| all fields | 41 | 427 | 77.5 | 88.5 | **82.6** | 80-85 | 72.4 | 65-78 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 90.7 | 98.7 | **94.5** | 91-98 | 94.5 | 91-98 |
| duration | 2 | 22 | 73.3 | 100.0 | **84.6** | 68-94 | 86.8 | 74-94 |
| jurisdiction | 1 | 27 | 96.3 | 96.3 | **96.3** | 90-100 | 96.3 | 90-100 |
| clause | 33 | 215 | 67.8 | 87.0 | **76.2** | 71-81 | 68.4 | 59-75 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 69.5 | 80.4 | **74.5** | 64-82 | 66.9 | 52-74 |
| ip_and_licensing | 10 | 51 | 77.2 | 86.3 | **81.5** | 73-87 | 62.1 | 51-79 |
| liability_and_risk | 5 | 39 | 66.7 | 82.1 | **73.6** | 60-84 | 67.6 | 45-82 |
| restrictive_covenants | 6 | 29 | 62.8 | 93.1 | **75.0** | 63-84 | 76.7 | 56-86 |
| term_and_termination | 4 | 45 | 62.3 | 95.6 | **75.4** | 67-82 | 75.4 | 64-83 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 11.1 | 100.0 | **20.0** | 0-55 | 20.0 | 18.2 |
| `volume_restriction` | clause | presence | 2 | 16.7 | 50.0 | **25.0** | 0-67 | 25.0 | 15.4 |
| `third_party_beneficiary` | clause | presence | 2 | 33.3 | 50.0 | **40.0** | 0-100 | 40.0 | 0.0 |
| `uncapped_liability` | clause | presence | 6 | 31.2 | 83.3 | **45.5** | 18-69 | 45.5 | 35.7 |
| `competitive_restriction_exception` | clause | presence | 4 | 30.8 | 100.0 | **47.1** | 14-74 | 47.1 | 14.3 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 22.5 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 36.4 |
| `affiliate_license_licensor` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 0.0 |
| `change_of_control` | clause | presence | 8 | 53.8 | 87.5 | **66.7** | 37-87 | 66.7 | 45.2 |
| `expiration_date` | date | value | 19 | 78.6 | 57.9 | **66.7** | 44-83 | 94.5 |  |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `no_solicit_of_customers` | clause | presence | 2 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 46.2 |
| `non_compete` | clause | presence | 6 | 80.0 | 66.7 | **72.7** | 25-100 | 72.7 | 41.7 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 61.5 | **76.2** | 50-94 | 76.2 | 39.0 |
| `non_transferable_license` | clause | presence | 8 | 61.5 | 100.0 | **76.2** | 46-93 | 76.2 | 50.0 |
| `warranty_duration` | clause | presence | 6 | 71.4 | 83.3 | **76.9** | 40-100 | 76.9 | 57.1 |
| `revenue_profit_sharing` | clause | presence | 11 | 75.0 | 81.8 | **78.3** | 55-94 | 78.3 | 25.6 |
| `insurance` | clause | presence | 5 | 80.0 | 80.0 | **80.0** | 40-100 | 80.0 | 22.2 |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 71.4 | **83.3** | 50-100 | 83.3 | 58.8 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 66.7 |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 66.7 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 0.0 |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `termination_for_convenience` | clause | presence | 7 | 77.8 | 100.0 | **87.5** | 60-100 | 87.5 | 60.9 |
| `exclusivity` | clause | presence | 11 | 78.6 | 100.0 | **88.0** | 71-100 | 88.0 | 66.7 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 36.4 |
| `cap_on_liability` | clause | presence | 21 | 94.7 | 85.7 | **90.0** | 78-98 | 90.0 | 45.3 |
| `license_grant` | clause | presence | 14 | 82.4 | 100.0 | **90.3** | 76-100 | 90.3 | 50.0 |
| `governing_law` | jurisdiction | value | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 96.3 |  |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 94.5 |  |
| `parties` | entity_list | value | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 100.0 |  |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 78-100 | 78.8 |  |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 94.7 |  |
| `ip_ownership_assignment` | clause | presence | 9 | 90.0 | 100.0 | **94.7** | 80-100 | 94.7 | 51.6 |
| `anti_assignment` | clause | presence | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 97.6 | 64.6 |
| `effective_date` | date | value | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 94.5 |  |
| `audit_rights` | clause | presence | 13 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 57.1 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 100.0 | 1 | — | 0 | — |
| `anti_assignment` | 95.2 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 13 | 62.5 | 8 | +37.5 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 83.3 | 6 | 0.0 | 1 | +83.3 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 100.0 | 8 | +0.0 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 75.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 66.7 | 12 | 0.0 | 1 | +66.7 |
| `most_favored_nation` | 100.0 | 1 | — | 0 | — |
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
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 0.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 94.0 | 248 | 81.7 | 71 | +12.3 |

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 92.5 | +30.9 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 87.5 | +27.5 |
| duration | 81.1 | 93.3 | +12.3 |
| jurisdiction | 83.3 | 91.2 | +7.9 |
| clause | 53.5 | 76.2 | +22.7 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `unlimited_all_you_can_eat_license` | 28.6 | 0.0 | -28.6 |
| `third_party_beneficiary` | 50.0 | 40.0 | -10.0 |
| `non_transferable_license` | 85.7 | 76.2 | -9.5 |
| `change_of_control` | 70.6 | 66.7 | -3.9 |
| `cap_on_liability` | 93.0 | 90.0 | -3.0 |
| `no_solicit_of_employees` | 54.5 | 100.0 | +45.5 |
| `no_solicit_of_customers` | 20.0 | 66.7 | +46.7 |
| `expiration_date` | 10.0 | 66.7 | +56.7 |
| `effective_date` | 40.0 | 97.7 | +57.7 |
| `affiliate_license_licensor` | 8.7 | 66.7 | +58.0 |
