# Eval report: `20261020-205741-llm-gpt-5.6-luna-per_field-experiment`

| system | split | contracts | git | created (UTC) |
|---|---|---|---|---|
| llm-gpt-5.6-luna-per_field | experiment | 30 | `e3ac30c` | 2026-10-20 20:57 |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 92.5 | 87-98 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 89.2 | 87.9 | **88.5** | 83-94 | 86.7 | 79-93 |
| duration | 2 | 21 | 87.5 | 100.0 | **93.3** | 83-100 | 93.5 | 82-100 |
| jurisdiction | 1 | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 92.9 | 87-98 |
| clause | 33 | 215 | 61.7 | 89.8 | **73.1** | 68-77 | 67.7 | 60-73 |
| all fields | 41 | 427 | 73.2 | 90.4 | **80.9** | 79-83 | 72.0 | 66-76 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 90.6 | 97.5 | **93.9** | 91-97 | 93.9 | 90-97 |
| duration | 2 | 22 | 75.9 | 100.0 | **86.3** | 72-95 | 88.0 | 76-95 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 61.7 | 89.8 | **73.1** | 68-77 | 67.7 | 60-73 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 63.3 | 74.5 | **68.5** | 61-75 | 63.7 | 50-69 |
| ip_and_licensing | 10 | 51 | 77.6 | 88.2 | **82.6** | 75-88 | 68.3 | 56-80 |
| liability_and_risk | 5 | 39 | 51.4 | 94.9 | **66.7** | 57-75 | 59.4 | 44-70 |
| restrictive_covenants | 6 | 29 | 56.0 | 96.6 | **70.9** | 59-80 | 73.4 | 56-82 |
| term_and_termination | 4 | 45 | 61.6 | 100.0 | **76.3** | 67-83 | 75.9 | 64-83 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 8.3 | 100.0 | **15.4** | 0-44 | 15.4 | 10.0 |
| `volume_restriction` | clause | presence | 2 | 14.3 | 50.0 | **22.2** | 0-59 | 22.2 | 0.0 |
| `third_party_beneficiary` | clause | presence | 2 | 15.4 | 100.0 | **26.7** | 0-57 | 26.7 | 26.1 |
| `uncapped_liability` | clause | presence | 6 | 26.1 | 100.0 | **41.4** | 17-63 | 41.4 | 28.6 |
| `competitive_restriction_exception` | clause | presence | 4 | 28.6 | 100.0 | **44.4** | 13-70 | 44.4 | 14.6 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 30.8 | **47.1** | 15-74 | 47.1 | 26.3 |
| `post_termination_services` | clause | presence | 9 | 32.1 | 100.0 | **48.6** | 27-68 | 48.6 | 17.6 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 40.0 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 40.0 |
| `liquidated_damages` | clause | presence | 4 | 50.0 | 75.0 | **60.0** | 0-91 | 60.0 | 40.0 |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `expiration_date` | date | value | 19 | 80.0 | 63.2 | **70.6** | 48-86 | 90.6 |  |
| `non_compete` | clause | presence | 6 | 62.5 | 83.3 | **71.4** | 33-93 | 71.4 | 28.6 |
| `warranty_duration` | clause | presence | 6 | 62.5 | 83.3 | **71.4** | 36-94 | 71.4 | 63.6 |
| `change_of_control` | clause | presence | 8 | 57.1 | 100.0 | **72.7** | 44-90 | 72.7 | 24.4 |
| `non_transferable_license` | clause | presence | 8 | 61.5 | 100.0 | **76.2** | 47-93 | 76.2 | 57.1 |
| `joint_ip_ownership` | clause | presence | 3 | 100.0 | 66.7 | **80.0** | 0-100 | 80.0 | 40.0 |
| `exclusivity` | clause | presence | 11 | 68.8 | 100.0 | **81.5** | 62-95 | 81.5 | 60.0 |
| `revenue_profit_sharing` | clause | presence | 11 | 81.8 | 81.8 | **81.8** | 57-96 | 81.8 | 33.3 |
| `termination_for_convenience` | clause | presence | 7 | 70.0 | 100.0 | **82.4** | 55-100 | 82.4 | 56.0 |
| `ip_ownership_assignment` | clause | presence | 9 | 80.0 | 88.9 | **84.2** | 60-100 | 84.2 | 52.9 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 20.0 |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 43.5 |
| `insurance` | clause | presence | 5 | 83.3 | 100.0 | **90.9** | 61-100 | 90.9 | 39.1 |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 55.6 |
| `parties` | entity_list | value | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 100.0 |  |
| `governing_law` | jurisdiction | value | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 98.1 |  |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 80-100 | 81.2 |  |
| `effective_date` | date | value | 21 | 87.5 | 100.0 | **93.3** | 84-100 | 92.9 |  |
| `license_grant` | clause | presence | 14 | 87.5 | 100.0 | **93.3** | 82-100 | 93.3 | 63.3 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 94.7 |  |
| `agreement_date` | date | value | 26 | 96.2 | 96.2 | **96.2** | 88-100 | 98.2 |  |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 51.7 |
| `cap_on_liability` | clause | presence | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 97.7 | 61.9 |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 70.3 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 85.7 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 0.0 | 1 | — | 0 | — |
| `anti_assignment` | 100.0 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 13 | 100.0 | 8 | +0.0 |
| `change_of_control` | 100.0 | 5 | 100.0 | 3 | +0.0 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 75.0 | 8 | +25.0 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 100.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 83.3 | 6 | +16.7 |
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
| `notice_period_to_terminate_renewal` | 100.0 | 5 | 100.0 | 4 | +0.0 |
| `post_termination_services` | 100.0 | 2 | 100.0 | 7 | +0.0 |
| `price_restrictions` | — | 0 | 100.0 | 1 | — |
| `renewal_term` | 100.0 | 11 | 100.0 | 2 | +0.0 |
| `revenue_profit_sharing` | 100.0 | 7 | 50.0 | 4 | +50.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 100.0 | 2 | — | 0 | — |
| `uncapped_liability` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 95.2 | 248 | 83.1 | 71 | +12.1 |

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 92.5 | +30.9 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 88.5 | +28.5 |
| duration | 81.1 | 93.3 | +12.3 |
| jurisdiction | 83.3 | 92.9 | +9.5 |
| clause | 53.5 | 73.1 | +19.6 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `minimum_commitment` | 78.8 | 47.1 | -31.7 |
| `third_party_beneficiary` | 50.0 | 26.7 | -23.3 |
| `non_transferable_license` | 85.7 | 76.2 | -9.5 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `most_favored_nation` | 66.7 | 66.7 | +0.0 |
| `joint_ip_ownership` | 28.6 | 80.0 | +51.4 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `effective_date` | 40.0 | 93.3 | +53.3 |
| `expiration_date` | 10.0 | 70.6 | +60.6 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
