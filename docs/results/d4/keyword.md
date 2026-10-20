# Eval report: `20261020-204758-keyword-experiment`

| system | split | contracts | git | created (UTC) |
|---|---|---|---|---|
| keyword | experiment | 30 | `4132e5e` | 2026-10-20 20:47 |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 71.2 | 54.4 | **61.7** | 48-75 | 61.7 | 48-75 |
| text | 1 | 30 | 70.8 | 56.7 | **63.0** | 44-79 | 63.0 | 44-79 |
| date | 3 | 66 | 88.2 | 45.5 | **60.0** | 50-70 | 47.3 | 37-57 |
| duration | 2 | 21 | 93.8 | 71.4 | **81.1** | 67-94 | 80.1 | 61-95 |
| jurisdiction | 1 | 27 | 95.2 | 74.1 | **83.3** | 68-94 | 83.3 | 68-94 |
| clause | 33 | 215 | 37.6 | 92.6 | **53.5** | 48-59 | 51.0 | 43-56 |
| all fields | 41 | 427 | 47.0 | 74.5 | **57.7** | 53-62 | 53.5 | 47-58 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 86.7 | **92.9** | 85-98 | 92.9 | 85-98 |
| text | 1 | 30 | 100.0 | 80.0 | **88.9** | 78-97 | 88.9 | 78-97 |
| date | 3 | 79 | 97.1 | 41.8 | **58.4** | 48-68 | 49.7 | 39-58 |
| duration | 2 | 22 | 100.0 | 77.3 | **87.2** | 73-97 | 85.8 | 67-98 |
| jurisdiction | 1 | 27 | 100.0 | 77.8 | **87.5** | 76-96 | 87.5 | 76-96 |
| clause | 33 | 215 | 37.6 | 92.6 | **53.5** | 48-59 | 51.0 | 43-56 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 39.3 | 90.2 | **54.8** | 44-64 | 55.4 | 39-65 |
| ip_and_licensing | 10 | 51 | 32.9 | 92.2 | **48.5** | 38-57 | 43.6 | 35-51 |
| liability_and_risk | 5 | 39 | 40.2 | 94.9 | **56.5** | 47-66 | 52.7 | 37-66 |
| restrictive_covenants | 6 | 29 | 28.6 | 96.6 | **44.1** | 30-56 | 47.4 | 29-60 |
| term_and_termination | 4 | 45 | 51.9 | 91.1 | **66.1** | 56-75 | 63.6 | 50-73 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `price_restrictions` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `affiliate_license_licensor` | clause | presence | 1 | 4.5 | 100.0 | **8.7** | 0-26 | 8.7 | 0.0 |
| `expiration_date` | date | value | 19 | 100.0 | 5.3 | **10.0** | 0-30 | 7.4 |  |
| `volume_restriction` | clause | presence | 2 | 9.5 | 100.0 | **17.4** | 0-38 | 17.4 | 4.5 |
| `no_solicit_of_customers` | clause | presence | 2 | 12.5 | 50.0 | **20.0** | 0-53 | 20.0 | 0.0 |
| `affiliate_license_licensee` | clause | presence | 3 | 13.6 | 100.0 | **24.0** | 0-47 | 24.0 | 0.0 |
| `competitive_restriction_exception` | clause | presence | 4 | 14.3 | 100.0 | **25.0** | 7-44 | 25.0 | 2.3 |
| `joint_ip_ownership` | clause | presence | 3 | 16.7 | 100.0 | **28.6** | 0-52 | 28.6 | 3.5 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 16.7 | 100.0 | **28.6** | 0-67 | 28.6 | 16.7 |
| `warranty_duration` | clause | presence | 6 | 20.7 | 100.0 | **34.3** | 13-54 | 34.3 | 2.3 |
| `uncapped_liability` | clause | presence | 6 | 22.2 | 100.0 | **36.4** | 14-57 | 36.4 | 0.0 |
| `effective_date` | date | value | 21 | 66.7 | 28.6 | **40.0** | 14-62 | 51.4 |  |
| `post_termination_services` | clause | presence | 9 | 29.2 | 77.8 | **42.4** | 19-63 | 42.4 | 2.8 |
| `non_compete` | clause | presence | 6 | 27.3 | 100.0 | **42.9** | 18-65 | 42.9 | 10.5 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 30.8 | 100.0 | **47.1** | 13-75 | 47.1 | 38.7 |
| `liquidated_damages` | clause | presence | 4 | 37.5 | 75.0 | **50.0** | 0-83 | 50.0 | 43.5 |
| `third_party_beneficiary` | clause | presence | 2 | 33.3 | 100.0 | **50.0** | 0-100 | 50.0 | 33.3 |
| `termination_for_convenience` | clause | presence | 7 | 35.0 | 100.0 | **51.9** | 25-73 | 51.9 | 11.1 |
| `no_solicit_of_employees` | clause | presence | 3 | 37.5 | 100.0 | **54.5** | 0-86 | 54.5 | 17.4 |
| `insurance` | clause | presence | 5 | 38.5 | 100.0 | **55.6** | 18-80 | 55.6 | 13.8 |
| `ip_ownership_assignment` | clause | presence | 9 | 39.1 | 100.0 | **56.2** | 32-74 | 56.2 | 5.6 |
| `revenue_profit_sharing` | clause | presence | 11 | 42.9 | 81.8 | **56.2** | 32-74 | 56.2 | 5.4 |
| `exclusivity` | clause | presence | 11 | 39.3 | 100.0 | **56.4** | 35-73 | 56.4 | 29.9 |
| `parties` | entity_list | value | 68 | 71.2 | 54.4 | **61.7** | 48-75 | 92.9 |  |
| `document_name` | text | value | 30 | 70.8 | 56.7 | **63.0** | 44-79 | 88.9 |  |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 50.0 |
| `change_of_control` | clause | presence | 8 | 66.7 | 75.0 | **70.6** | 36-92 | 70.6 | 33.3 |
| `license_grant` | clause | presence | 14 | 56.0 | 100.0 | **71.8** | 53-86 | 71.8 | 9.6 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 100.0 | 62.5 | **76.9** | 44-100 | 80.0 |  |
| `minimum_commitment` | clause | presence | 13 | 65.0 | 100.0 | **78.8** | 61-92 | 78.8 | 34.3 |
| `audit_rights` | clause | presence | 13 | 70.6 | 92.3 | **80.0** | 62-93 | 80.0 | 22.5 |
| `governing_law` | jurisdiction | value | 27 | 95.2 | 74.1 | **83.3** | 68-94 | 87.5 |  |
| `renewal_term` | duration | value | 13 | 90.9 | 76.9 | **83.3** | 62-100 | 91.7 |  |
| `covenant_not_to_sue` | clause | presence | 7 | 85.7 | 85.7 | **85.7** | 57-100 | 85.7 | 56.0 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 18.2 |
| `non_transferable_license` | clause | presence | 8 | 100.0 | 75.0 | **85.7** | 57-100 | 85.7 | 57.1 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 29.6 |
| `anti_assignment` | clause | presence | 21 | 80.8 | 100.0 | **89.4** | 78-96 | 89.4 | 22.8 |
| `agreement_date` | date | value | 26 | 95.8 | 88.5 | **92.0** | 82-98 | 90.2 |  |
| `cap_on_liability` | clause | presence | 21 | 90.9 | 95.2 | **93.0** | 82-100 | 93.0 | 18.2 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 100.0 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 100.0 | 1 | — | 0 | — |
| `anti_assignment` | 100.0 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 0.0 | 1 | +100.0 |
| `cap_on_liability` | 100.0 | 13 | 87.5 | 8 | +12.5 |
| `change_of_control` | 100.0 | 5 | 33.3 | 3 | +66.7 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 80.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 5.6 | 18 | 0.0 | 8 | +5.6 |
| `governing_law` | 80.8 | 26 | — | 0 | — |
| `insurance` | 100.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 100.0 | 1 | +0.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `most_favored_nation` | 100.0 | 1 | — | 0 | — |
| `no_solicit_of_customers` | 100.0 | 1 | 0.0 | 1 | +100.0 |
| `no_solicit_of_employees` | 100.0 | 2 | 100.0 | 1 | +0.0 |
| `non_compete` | 100.0 | 4 | 100.0 | 2 | +0.0 |
| `non_disparagement` | 100.0 | 1 | 100.0 | 2 | +0.0 |
| `non_transferable_license` | 100.0 | 6 | 0.0 | 2 | +100.0 |
| `notice_period_to_terminate_renewal` | 60.0 | 5 | 75.0 | 4 | -15.0 |
| `post_termination_services` | 100.0 | 2 | 71.4 | 7 | +28.6 |
| `price_restrictions` | — | 0 | 0.0 | 1 | — |
| `renewal_term` | 100.0 | 11 | 0.0 | 2 | +100.0 |
| `revenue_profit_sharing` | 100.0 | 7 | 50.0 | 4 | +50.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 100.0 | 2 | — | 0 | — |
| `uncapped_liability` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `warranty_duration` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| **all** | 87.9 | 248 | 62.0 | 71 | +25.9 |
