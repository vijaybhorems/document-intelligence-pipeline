# Eval report: `20261020-204803-llm-gpt-5.6-luna-single-experiment`

| system | split | contracts | git | created (UTC) |
|---|---|---|---|---|
| llm-gpt-5.6-luna-single | experiment | 30 | `4132e5e` | 2026-10-20 20:48 |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 92.5 | 87-98 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 90.6 | 87.9 | **89.2** | 82-95 | 88.1 | 80-94 |
| duration | 2 | 21 | 84.0 | 100.0 | **91.3** | 80-98 | 90.9 | 77-98 |
| jurisdiction | 1 | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 91.2 | 85-98 |
| clause | 33 | 215 | 63.1 | 87.4 | **73.3** | 69-77 | 65.0 | 58-69 |
| all fields | 41 | 427 | 74.3 | 89.2 | **81.1** | 79-83 | 69.8 | 64-73 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 91.9 | 100.0 | **95.8** | 93-98 | 95.8 | 93-98 |
| duration | 2 | 22 | 71.0 | 100.0 | **83.0** | 67-93 | 84.4 | 70-93 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 63.1 | 87.4 | **73.3** | 69-77 | 65.0 | 58-69 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 63.5 | 78.4 | **70.2** | 62-77 | 65.1 | 51-71 |
| ip_and_licensing | 10 | 51 | 68.8 | 86.3 | **76.5** | 70-82 | 55.0 | 44-67 |
| liability_and_risk | 5 | 39 | 58.9 | 84.6 | **69.5** | 56-80 | 64.3 | 49-76 |
| restrictive_covenants | 6 | 29 | 64.3 | 93.1 | **76.1** | 65-85 | 76.2 | 56-86 |
| term_and_termination | 4 | 45 | 60.3 | 97.8 | **74.6** | 67-81 | 73.3 | 62-81 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 9.1 | 100.0 | **16.7** | 0-46 | 16.7 | 15.4 |
| `volume_restriction` | clause | presence | 2 | 12.5 | 50.0 | **20.0** | 0-57 | 20.0 | 0.0 |
| `third_party_beneficiary` | clause | presence | 2 | 16.7 | 50.0 | **25.0** | 0-67 | 25.0 | 36.4 |
| `uncapped_liability` | clause | presence | 6 | 25.0 | 83.3 | **38.5** | 12-60 | 38.5 | 37.5 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 24.0 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 40.0 |
| `competitive_restriction_exception` | clause | presence | 4 | 40.0 | 100.0 | **57.1** | 20-82 | 57.1 | 18.2 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 30.8 |
| `change_of_control` | clause | presence | 8 | 46.7 | 87.5 | **60.9** | 33-82 | 60.9 | 42.4 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 46.2 | **63.2** | 30-86 | 63.2 | 35.0 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `non_compete` | clause | presence | 6 | 80.0 | 66.7 | **72.7** | 25-100 | 72.7 | 33.3 |
| `expiration_date` | date | value | 19 | 81.2 | 68.4 | **74.3** | 53-89 | 94.5 |  |
| `warranty_duration` | clause | presence | 6 | 71.4 | 83.3 | **76.9** | 40-100 | 76.9 | 52.6 |
| `ip_ownership_assignment` | clause | presence | 9 | 64.3 | 100.0 | **78.3** | 56-95 | 78.3 | 42.1 |
| `revenue_profit_sharing` | clause | presence | 11 | 75.0 | 81.8 | **78.3** | 55-94 | 78.3 | 29.4 |
| `non_transferable_license` | clause | presence | 8 | 66.7 | 100.0 | **80.0** | 50-96 | 80.0 | 44.4 |
| `termination_for_convenience` | clause | presence | 7 | 70.0 | 100.0 | **82.4** | 56-100 | 82.4 | 60.9 |
| `exclusivity` | clause | presence | 11 | 73.3 | 100.0 | **84.6** | 67-97 | 84.6 | 70.3 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 66.7 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 20.0 |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `liquidated_damages` | clause | presence | 4 | 80.0 | 100.0 | **88.9** | 57-100 | 88.9 | 66.7 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 80.0 | 100.0 | **88.9** | 67-100 | 90.0 |  |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 28.6 |
| `license_grant` | clause | presence | 14 | 82.4 | 100.0 | **90.3** | 77-100 | 90.3 | 50.8 |
| `insurance` | clause | presence | 5 | 83.3 | 100.0 | **90.9** | 67-100 | 90.9 | 22.2 |
| `governing_law` | jurisdiction | value | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 98.1 |  |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 98.2 |  |
| `cap_on_liability` | clause | presence | 21 | 100.0 | 85.7 | **92.3** | 81-100 | 92.3 | 45.9 |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 66.7 |
| `parties` | entity_list | value | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 100.0 |  |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 78-100 | 78.8 |  |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 59.1 |
| `effective_date` | date | value | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 94.5 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 0.0 | 1 | — | 0 | — |
| `anti_assignment` | 100.0 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 13 | 62.5 | 8 | +37.5 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 100.0 | 8 | +0.0 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 100.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 75.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 100.0 | 1 | +0.0 |
| `minimum_commitment` | 50.0 | 12 | 0.0 | 1 | +50.0 |
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
| **all** | 94.0 | 248 | 83.1 | 71 | +10.9 |

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 92.5 | +30.9 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 89.2 | +29.2 |
| duration | 81.1 | 91.3 | +10.2 |
| jurisdiction | 83.3 | 91.2 | +7.9 |
| clause | 53.5 | 73.3 | +19.8 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `unlimited_all_you_can_eat_license` | 28.6 | 0.0 | -28.6 |
| `third_party_beneficiary` | 50.0 | 25.0 | -25.0 |
| `minimum_commitment` | 78.8 | 63.2 | -15.6 |
| `change_of_control` | 70.6 | 60.9 | -9.7 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `liquidated_damages` | 50.0 | 88.9 | +38.9 |
| `warranty_duration` | 34.3 | 76.9 | +42.6 |
| `no_solicit_of_employees` | 54.5 | 100.0 | +45.5 |
| `effective_date` | 40.0 | 97.7 | +57.7 |
| `expiration_date` | 10.0 | 74.3 | +64.3 |
