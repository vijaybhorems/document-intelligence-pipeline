# Eval report: `20261020-205540-llm-gpt-5.6-luna-grouped-own_schema-experiment`

| system | split | contracts | git | created (UTC) |
|---|---|---|---|---|
| llm-gpt-5.6-luna-grouped-own_schema | experiment | 30 | `e3ac30c` | 2026-10-20 20:55 |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 90.9 | 88.2 | **89.6** | 82-96 | 89.6 | 82-96 |
| text | 1 | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 90.0 | 80-100 |
| date | 3 | 66 | 91.7 | 83.3 | **87.3** | 80-94 | 84.8 | 76-92 |
| duration | 2 | 21 | 91.3 | 100.0 | **95.5** | 87-100 | 95.2 | 85-100 |
| jurisdiction | 1 | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 91.2 | 85-98 |
| clause | 33 | 215 | 58.4 | 89.3 | **70.6** | 65-76 | 66.1 | 58-72 |
| all fields | 41 | 427 | 70.8 | 89.2 | **79.0** | 76-81 | 70.7 | 65-75 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 90.8 | 100.0 | **95.2** | 92-98 | 95.2 | 92-98 |
| duration | 2 | 22 | 78.6 | 100.0 | **88.0** | 74-96 | 89.3 | 78-97 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 58.4 | 89.3 | **70.6** | 65-76 | 66.1 | 58-72 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 61.5 | 78.4 | **69.0** | 60-76 | 57.8 | 49-67 |
| ip_and_licensing | 10 | 51 | 70.1 | 92.2 | **79.7** | 71-86 | 71.4 | 56-85 |
| liability_and_risk | 5 | 39 | 45.9 | 87.2 | **60.2** | 47-70 | 55.3 | 42-66 |
| restrictive_covenants | 6 | 29 | 51.9 | 93.1 | **66.7** | 53-77 | 71.5 | 51-82 |
| term_and_termination | 4 | 45 | 62.0 | 97.8 | **75.9** | 68-83 | 74.8 | 63-83 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `most_favored_nation` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 6.7 | 100.0 | **12.5** | 0-38 | 12.5 | 5.7 |
| `third_party_beneficiary` | clause | presence | 2 | 7.7 | 50.0 | **13.3** | 0-36 | 13.3 | 24.0 |
| `volume_restriction` | clause | presence | 2 | 14.3 | 50.0 | **22.2** | 0-60 | 22.2 | 0.0 |
| `competitive_restriction_exception` | clause | presence | 4 | 21.1 | 100.0 | **34.8** | 10-58 | 34.8 | 18.5 |
| `uncapped_liability` | clause | presence | 6 | 23.1 | 100.0 | **37.5** | 14-58 | 37.5 | 29.0 |
| `affiliate_license_licensor` | clause | presence | 1 | 25.0 | 100.0 | **40.0** | 0-100 | 40.0 | 28.6 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 19.3 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 40.0 |
| `expiration_date` | date | value | 19 | 83.3 | 52.6 | **64.5** | 42-82 | 96.3 |  |
| `affiliate_license_licensee` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 40.0 |
| `change_of_control` | clause | presence | 8 | 53.8 | 87.5 | **66.7** | 38-87 | 66.7 | 41.2 |
| `liquidated_damages` | clause | presence | 4 | 50.0 | 100.0 | **66.7** | 29-91 | 66.7 | 37.5 |
| `non_compete` | clause | presence | 6 | 66.7 | 66.7 | **66.7** | 22-92 | 66.7 | 37.5 |
| `warranty_duration` | clause | presence | 6 | 55.6 | 83.3 | **66.7** | 33-89 | 66.7 | 59.3 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 53.8 | **70.0** | 42-90 | 70.0 | 39.0 |
| `non_transferable_license` | clause | presence | 8 | 57.1 | 100.0 | **72.7** | 43-90 | 72.7 | 60.0 |
| `ip_ownership_assignment` | clause | presence | 9 | 60.0 | 100.0 | **75.0** | 50-91 | 75.0 | 53.1 |
| `joint_ip_ownership` | clause | presence | 3 | 100.0 | 66.7 | **80.0** | 0-100 | 80.0 | 40.0 |
| `revenue_profit_sharing` | clause | presence | 11 | 81.8 | 81.8 | **81.8** | 57-96 | 81.8 | 29.2 |
| `termination_for_convenience` | clause | presence | 7 | 70.0 | 100.0 | **82.4** | 55-100 | 82.4 | 60.9 |
| `exclusivity` | clause | presence | 11 | 73.3 | 100.0 | **84.6** | 67-97 | 84.6 | 65.2 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 20.0 |
| `license_grant` | clause | presence | 14 | 77.8 | 100.0 | **87.5** | 73-97 | 87.5 | 58.5 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 37.0 |
| `parties` | entity_list | value | 68 | 90.9 | 88.2 | **89.6** | 82-96 | 100.0 |  |
| `document_name` | text | value | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 100.0 |  |
| `insurance` | clause | presence | 5 | 83.3 | 100.0 | **90.9** | 61-100 | 90.9 | 30.8 |
| `governing_law` | jurisdiction | value | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 98.1 |  |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 96.4 |  |
| `cap_on_liability` | clause | presence | 21 | 100.0 | 85.7 | **92.3** | 81-100 | 92.3 | 62.7 |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 60.0 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 94.7 |  |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 57.7 |
| `renewal_term` | duration | value | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 83.9 |  |
| `effective_date` | date | value | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 92.9 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 65.7 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 85.7 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 100.0 | 1 | — | 0 | — |
| `anti_assignment` | 100.0 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 92.3 | 13 | 75.0 | 8 | +17.3 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 100.0 | 8 | +0.0 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 100.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 100.0 | 1 | +0.0 |
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
| `revenue_profit_sharing` | 100.0 | 7 | 50.0 | 4 | +50.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 95.2 | 248 | 84.5 | 71 | +10.7 |

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 89.6 | +27.9 |
| text | 63.0 | 90.0 | +27.0 |
| date | 60.0 | 87.3 | +27.3 |
| duration | 81.1 | 95.5 | +14.4 |
| jurisdiction | 83.3 | 91.2 | +7.9 |
| clause | 53.5 | 70.6 | +17.1 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `most_favored_nation` | 66.7 | 0.0 | -66.7 |
| `third_party_beneficiary` | 50.0 | 13.3 | -36.7 |
| `non_transferable_license` | 85.7 | 72.7 | -13.0 |
| `minimum_commitment` | 78.8 | 70.0 | -8.8 |
| `change_of_control` | 70.6 | 66.7 | -3.9 |
| `joint_ip_ownership` | 28.6 | 80.0 | +51.4 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `expiration_date` | 10.0 | 64.5 | +54.5 |
| `effective_date` | 40.0 | 97.7 | +57.7 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
