# Eval report: `20261020-204959-llm-gpt-5.6-luna-grouped-experiment`

| system | split | contracts | git | created (UTC) |
|---|---|---|---|---|
| llm-gpt-5.6-luna-grouped | experiment | 30 | `4132e5e` | 2026-10-20 20:49 |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 92.5 | 87-98 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 90.3 | 84.8 | **87.5** | 79-94 | 85.5 | 75-93 |
| duration | 2 | 21 | 91.3 | 100.0 | **95.5** | 87-100 | 95.2 | 85-100 |
| jurisdiction | 1 | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 92.9 | 87-98 |
| clause | 33 | 215 | 63.8 | 88.4 | **74.1** | 70-78 | 68.5 | 61-74 |
| all fields | 41 | 427 | 75.0 | 89.2 | **81.5** | 79-83 | 72.7 | 66-77 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 95.1 | 98.7 | **96.9** | 94-99 | 96.9 | 94-99 |
| duration | 2 | 22 | 80.8 | 95.5 | **87.5** | 74-96 | 87.8 | 74-96 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 63.8 | 88.4 | **74.1** | 70-78 | 68.5 | 61-74 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 64.9 | 72.5 | **68.5** | 60-76 | 63.8 | 50-71 |
| ip_and_licensing | 10 | 51 | 83.6 | 90.2 | **86.8** | 80-93 | 71.1 | 58-83 |
| liability_and_risk | 5 | 39 | 50.7 | 89.7 | **64.8** | 54-74 | 57.3 | 41-68 |
| restrictive_covenants | 6 | 29 | 62.2 | 96.6 | **75.7** | 65-84 | 76.2 | 60-84 |
| term_and_termination | 4 | 45 | 61.1 | 97.8 | **75.2** | 67-82 | 74.0 | 63-82 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 8.3 | 100.0 | **15.4** | 0-44 | 15.4 | 11.1 |
| `third_party_beneficiary` | clause | presence | 2 | 10.0 | 50.0 | **16.7** | 0-46 | 16.7 | 31.6 |
| `volume_restriction` | clause | presence | 2 | 16.7 | 50.0 | **25.0** | 0-67 | 25.0 | 0.0 |
| `uncapped_liability` | clause | presence | 6 | 26.1 | 100.0 | **41.4** | 17-63 | 41.4 | 31.1 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 30.8 | **47.1** | 15-74 | 47.1 | 27.0 |
| `competitive_restriction_exception` | clause | presence | 4 | 33.3 | 100.0 | **50.0** | 17-77 | 50.0 | 31.2 |
| `no_solicit_of_customers` | clause | presence | 2 | 33.3 | 100.0 | **50.0** | 0-86 | 50.0 | 37.5 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 17.0 |
| `change_of_control` | clause | presence | 8 | 50.0 | 87.5 | **63.6** | 33-83 | 63.6 | 30.3 |
| `affiliate_license_licensee` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 40.0 |
| `expiration_date` | date | value | 19 | 78.6 | 57.9 | **66.7** | 42-83 | 94.3 |  |
| `liquidated_damages` | clause | presence | 4 | 60.0 | 75.0 | **66.7** | 0-100 | 66.7 | 46.2 |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `warranty_duration` | clause | presence | 6 | 50.0 | 100.0 | **66.7** | 36-88 | 66.7 | 40.0 |
| `joint_ip_ownership` | clause | presence | 3 | 100.0 | 66.7 | **80.0** | 0-100 | 80.0 | 40.0 |
| `revenue_profit_sharing` | clause | presence | 11 | 81.8 | 81.8 | **81.8** | 57-96 | 81.8 | 35.6 |
| `termination_for_convenience` | clause | presence | 7 | 70.0 | 100.0 | **82.4** | 55-100 | 82.4 | 60.9 |
| `non_compete` | clause | presence | 6 | 83.3 | 83.3 | **83.3** | 44-100 | 83.3 | 41.4 |
| `non_transferable_license` | clause | presence | 8 | 72.7 | 100.0 | **84.2** | 57-100 | 84.2 | 71.4 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 18.2 |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `exclusivity` | clause | presence | 11 | 78.6 | 100.0 | **88.0** | 71-100 | 88.0 | 68.3 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 21.6 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 33.3 |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 100.0 |  |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 73.7 |
| `parties` | entity_list | value | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 100.0 |  |
| `governing_law` | jurisdiction | value | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 98.1 |  |
| `license_grant` | clause | presence | 14 | 87.5 | 100.0 | **93.3** | 81-100 | 93.3 | 64.5 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 88.9 |  |
| `ip_ownership_assignment` | clause | presence | 9 | 90.0 | 100.0 | **94.7** | 80-100 | 94.7 | 61.5 |
| `cap_on_liability` | clause | presence | 21 | 100.0 | 90.5 | **95.0** | 86-100 | 95.0 | 51.9 |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 61.5 |
| `renewal_term` | duration | value | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 86.7 |  |
| `effective_date` | date | value | 21 | 95.5 | 100.0 | **97.7** | 91-100 | 96.3 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 65.7 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 85.7 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 44.4 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 0.0 | 1 | — | 0 | — |
| `anti_assignment` | 100.0 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 13 | 75.0 | 8 | +25.0 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 87.5 | 8 | +12.5 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 33.3 | 12 | 0.0 | 1 | +33.3 |
| `most_favored_nation` | 100.0 | 1 | — | 0 | — |
| `no_solicit_of_customers` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `no_solicit_of_employees` | 100.0 | 2 | 100.0 | 1 | +0.0 |
| `non_compete` | 75.0 | 4 | 100.0 | 2 | -25.0 |
| `non_disparagement` | 100.0 | 1 | 100.0 | 2 | +0.0 |
| `non_transferable_license` | 100.0 | 6 | 100.0 | 2 | +0.0 |
| `notice_period_to_terminate_renewal` | 80.0 | 5 | 100.0 | 4 | -20.0 |
| `post_termination_services` | 100.0 | 2 | 100.0 | 7 | +0.0 |
| `price_restrictions` | — | 0 | 100.0 | 1 | — |
| `renewal_term` | 100.0 | 11 | 100.0 | 2 | +0.0 |
| `revenue_profit_sharing` | 100.0 | 7 | 50.0 | 4 | +50.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| **all** | 94.0 | 248 | 83.1 | 71 | +10.9 |

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 92.5 | +30.9 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 87.5 | +27.5 |
| duration | 81.1 | 95.5 | +14.4 |
| jurisdiction | 83.3 | 92.9 | +9.5 |
| clause | 53.5 | 74.1 | +20.6 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `third_party_beneficiary` | 50.0 | 16.7 | -33.3 |
| `minimum_commitment` | 78.8 | 47.1 | -31.7 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `change_of_control` | 70.6 | 63.6 | -7.0 |
| `non_transferable_license` | 85.7 | 84.2 | -1.5 |
| `joint_ip_ownership` | 28.6 | 80.0 | +51.4 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `expiration_date` | 10.0 | 66.7 | +56.7 |
| `effective_date` | 40.0 | 97.7 | +57.7 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
