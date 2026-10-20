# Eval report: `20261020-203205-keyword-dev`

| system | split | contracts | git | created (UTC) |
|---|---|---|---|---|
| keyword | dev | 80 | `4b3c312` (dirty) | 2026-10-20 20:32 |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 217 | 68.9 | 41.9 | **52.1** | 38-67 | 52.1 | 38-67 |
| text | 1 | 80 | 67.9 | 47.5 | **55.9** | 44-67 | 55.9 | 44-67 |
| date | 3 | 180 | 78.7 | 38.9 | **52.0** | 45-59 | 44.0 | 36-51 |
| duration | 2 | 44 | 77.8 | 63.6 | **70.0** | 56-83 | 68.0 | 54-82 |
| jurisdiction | 1 | 71 | 93.8 | 63.4 | **75.6** | 66-84 | 75.6 | 66-84 |
| clause | 33 | 582 | 39.6 | 91.1 | **55.2** | 51-59 | 52.2 | 47-56 |
| all fields | 41 | 1174 | 47.2 | 68.3 | **55.8** | 52-59 | 53.0 | 49-56 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 80 | 100.0 | 82.5 | **90.4** | 85-95 | 90.4 | 85-95 |
| text | 1 | 80 | 100.0 | 70.0 | **82.4** | 75-89 | 82.4 | 75-89 |
| date | 3 | 206 | 94.4 | 41.3 | **57.4** | 50-64 | 50.9 | 44-57 |
| duration | 2 | 46 | 81.1 | 65.2 | **72.3** | 58-84 | 70.5 | 55-83 |
| jurisdiction | 1 | 70 | 100.0 | 65.7 | **79.3** | 70-87 | 79.3 | 70-87 |
| clause | 33 | 582 | 39.6 | 91.1 | **55.2** | 51-59 | 52.2 | 47-56 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 133 | 39.7 | 90.2 | **55.2** | 49-61 | 52.7 | 44-59 |
| ip_and_licensing | 10 | 132 | 32.5 | 88.6 | **47.6** | 41-54 | 45.9 | 37-52 |
| liability_and_risk | 5 | 96 | 38.3 | 93.8 | **54.4** | 47-61 | 50.9 | 40-60 |
| restrictive_covenants | 6 | 81 | 33.1 | 96.3 | **49.2** | 41-58 | 51.1 | 42-59 |
| term_and_termination | 4 | 140 | 61.3 | 89.3 | **72.7** | 67-78 | 69.9 | 62-76 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `price_restrictions` | clause | presence | 2 | 2.0 | 50.0 | **3.9** | 0-12 | 3.9 | 1.6 |
| `affiliate_license_licensor` | clause | presence | 4 | 7.4 | 100.0 | **13.8** | 3-27 | 13.8 | 2.6 |
| `expiration_date` | date | value | 52 | 80.0 | 7.7 | **14.0** | 4-26 | 11.0 |  |
| `joint_ip_ownership` | clause | presence | 7 | 13.0 | 100.0 | **23.0** | 10-37 | 23.0 | 2.8 |
| `affiliate_license_licensee` | clause | presence | 9 | 16.7 | 100.0 | **28.6** | 15-43 | 28.6 | 1.3 |
| `competitive_restriction_exception` | clause | presence | 12 | 16.9 | 100.0 | **28.9** | 16-42 | 28.9 | 1.8 |
| `warranty_duration` | clause | presence | 12 | 16.9 | 100.0 | **28.9** | 16-41 | 28.9 | 4.9 |
| `source_code_escrow` | clause | presence | 2 | 25.0 | 50.0 | **33.3** | 0-80 | 33.3 | 0.0 |
| `volume_restriction` | clause | presence | 11 | 21.6 | 100.0 | **35.5** | 20-51 | 35.5 | 9.6 |
| `most_favored_nation` | clause | presence | 4 | 28.6 | 50.0 | **36.4** | 0-67 | 36.4 | 25.0 |
| `no_solicit_of_customers` | clause | presence | 5 | 23.5 | 80.0 | **36.4** | 10-59 | 36.4 | 4.7 |
| `unlimited_all_you_can_eat_license` | clause | presence | 3 | 23.1 | 100.0 | **37.5** | 0-64 | 37.5 | 22.2 |
| `effective_date` | date | value | 58 | 66.7 | 31.0 | **42.4** | 27-56 | 58.9 |  |
| `uncapped_liability` | clause | presence | 19 | 27.5 | 100.0 | **43.2** | 31-55 | 43.2 | 0.0 |
| `third_party_beneficiary` | clause | presence | 5 | 29.4 | 100.0 | **45.5** | 14-72 | 45.5 | 30.3 |
| `ip_ownership_assignment` | clause | presence | 19 | 31.6 | 94.7 | **47.4** | 33-61 | 47.4 | 7.2 |
| `liquidated_damages` | clause | presence | 10 | 36.4 | 80.0 | **50.0** | 26-69 | 50.0 | 31.7 |
| `non_compete` | clause | presence | 19 | 35.2 | 100.0 | **52.1** | 39-65 | 52.1 | 15.9 |
| `parties` | entity_list | value | 217 | 68.9 | 41.9 | **52.1** | 38-67 | 90.4 |  |
| `revenue_profit_sharing` | clause | presence | 26 | 37.7 | 88.5 | **52.9** | 41-64 | 52.9 | 8.3 |
| `post_termination_services` | clause | presence | 29 | 40.3 | 86.2 | **54.9** | 42-67 | 54.9 | 4.6 |
| `irrevocable_or_perpetual_license` | clause | presence | 11 | 37.9 | 100.0 | **55.0** | 34-70 | 55.0 | 34.6 |
| `document_name` | text | value | 80 | 67.9 | 47.5 | **55.9** | 44-67 | 82.4 |  |
| `termination_for_convenience` | clause | presence | 26 | 42.3 | 84.6 | **56.4** | 43-68 | 56.4 | 15.9 |
| `notice_period_to_terminate_renewal` | duration | value | 18 | 75.0 | 50.0 | **60.0** | 36-79 | 62.5 |  |
| `exclusivity` | clause | presence | 30 | 44.1 | 100.0 | **61.2** | 49-72 | 61.2 | 24.4 |
| `no_solicit_of_employees` | clause | presence | 9 | 47.1 | 88.9 | **61.5** | 37-80 | 61.5 | 26.1 |
| `non_disparagement` | clause | presence | 6 | 55.6 | 83.3 | **66.7** | 33-90 | 66.7 | 24.0 |
| `covenant_not_to_sue` | clause | presence | 16 | 68.8 | 68.8 | **68.8** | 48-84 | 68.8 | 41.4 |
| `rofr_rofo_rofn` | clause | presence | 13 | 80.0 | 61.5 | **69.6** | 42-87 | 69.6 | 7.1 |
| `minimum_commitment` | clause | presence | 25 | 55.8 | 96.0 | **70.6** | 57-81 | 70.6 | 33.3 |
| `insurance` | clause | presence | 23 | 54.8 | 100.0 | **70.8** | 57-83 | 70.8 | 21.8 |
| `change_of_control` | clause | presence | 23 | 80.0 | 69.6 | **74.4** | 57-87 | 74.4 | 18.2 |
| `agreement_date` | date | value | 70 | 84.2 | 68.6 | **75.6** | 67-84 | 82.8 |  |
| `governing_law` | jurisdiction | value | 71 | 93.8 | 63.4 | **75.6** | 66-84 | 79.3 |  |
| `non_transferable_license` | clause | presence | 22 | 93.3 | 63.6 | **75.7** | 57-89 | 75.7 | 51.4 |
| `license_grant` | clause | presence | 39 | 60.9 | 100.0 | **75.7** | 66-84 | 75.7 | 12.5 |
| `renewal_term` | duration | value | 26 | 79.2 | 73.1 | **76.0** | 62-88 | 78.4 |  |
| `audit_rights` | clause | presence | 29 | 71.8 | 96.6 | **82.4** | 71-91 | 82.4 | 22.5 |
| `cap_on_liability` | clause | presence | 50 | 82.1 | 92.0 | **86.8** | 79-93 | 86.8 | 18.3 |
| `anti_assignment` | clause | presence | 62 | 88.6 | 100.0 | **93.9** | 89-98 | 93.9 | 21.4 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 100.0 | 8 | 100.0 | 1 | +0.0 |
| `affiliate_license_licensor` | 100.0 | 3 | 100.0 | 1 | +0.0 |
| `anti_assignment` | 100.0 | 60 | 100.0 | 2 | +0.0 |
| `audit_rights` | 100.0 | 28 | 0.0 | 1 | +100.0 |
| `cap_on_liability` | 100.0 | 25 | 84.0 | 25 | +16.0 |
| `change_of_control` | 100.0 | 13 | 30.0 | 10 | +70.0 |
| `competitive_restriction_exception` | 100.0 | 5 | 100.0 | 7 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 11 | 0.0 | 5 | +100.0 |
| `document_name` | 70.9 | 79 | 0.0 | 1 | +70.9 |
| `exclusivity` | 100.0 | 27 | 100.0 | 3 | +0.0 |
| `expiration_date` | 9.1 | 44 | 0.0 | 24 | +9.1 |
| `governing_law` | 69.7 | 66 | 0.0 | 3 | +69.7 |
| `insurance` | 100.0 | 23 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 8 | 90.9 | 11 | +9.1 |
| `irrevocable_or_perpetual_license` | 100.0 | 11 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 6 | 100.0 | 1 | +0.0 |
| `license_grant` | 100.0 | 33 | 100.0 | 6 | +0.0 |
| `liquidated_damages` | 100.0 | 7 | 33.3 | 3 | +66.7 |
| `minimum_commitment` | 100.0 | 19 | 83.3 | 6 | +16.7 |
| `most_favored_nation` | 100.0 | 2 | 0.0 | 2 | +100.0 |
| `no_solicit_of_customers` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `no_solicit_of_employees` | 100.0 | 7 | 50.0 | 2 | +50.0 |
| `non_compete` | 100.0 | 16 | 100.0 | 3 | +0.0 |
| `non_disparagement` | 100.0 | 3 | 66.7 | 3 | +33.3 |
| `non_transferable_license` | 100.0 | 14 | 0.0 | 8 | +100.0 |
| `notice_period_to_terminate_renewal` | 50.0 | 10 | 55.6 | 9 | -5.6 |
| `post_termination_services` | 100.0 | 9 | 80.0 | 20 | +20.0 |
| `price_restrictions` | 100.0 | 1 | 0.0 | 1 | +100.0 |
| `renewal_term` | 100.0 | 20 | 0.0 | 7 | +100.0 |
| `revenue_profit_sharing` | 100.0 | 20 | 50.0 | 6 | +50.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 54.5 | 11 | +45.5 |
| `source_code_escrow` | 100.0 | 1 | 0.0 | 1 | +100.0 |
| `termination_for_convenience` | 100.0 | 11 | 73.3 | 15 | +26.7 |
| `third_party_beneficiary` | 100.0 | 5 | — | 0 | — |
| `uncapped_liability` | 100.0 | 14 | 100.0 | 5 | +0.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 3 | — | 0 | — |
| `volume_restriction` | 100.0 | 7 | 100.0 | 4 | +0.0 |
| `warranty_duration` | 100.0 | 9 | 100.0 | 3 | +0.0 |
| **all** | 86.1 | 632 | 57.3 | 213 | +28.8 |

## Compared with `20261020-203153-all_absent-dev` (all_absent)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 0.0 | 52.1 | +52.1 |
| text | 0.0 | 55.9 | +55.9 |
| date | 0.0 | 52.0 | +52.0 |
| duration | 0.0 | 70.0 | +70.0 |
| jurisdiction | 0.0 | 75.6 | +75.6 |
| clause | 0.0 | 55.2 | +55.2 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `price_restrictions` | 0.0 | 3.9 | +3.9 |
| `affiliate_license_licensor` | 0.0 | 13.8 | +13.8 |
| `expiration_date` | 0.0 | 14.0 | +14.0 |
| `joint_ip_ownership` | 0.0 | 23.0 | +23.0 |
| `affiliate_license_licensee` | 0.0 | 28.6 | +28.6 |
| `license_grant` | 0.0 | 75.7 | +75.7 |
| `renewal_term` | 0.0 | 76.0 | +76.0 |
| `audit_rights` | 0.0 | 82.4 | +82.4 |
| `cap_on_liability` | 0.0 | 86.8 | +86.8 |
| `anti_assignment` | 0.0 | 93.9 | +93.9 |
