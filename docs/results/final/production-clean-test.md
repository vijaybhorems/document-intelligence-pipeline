# Eval report: `20261026-063735-llm-gpt-5.6-luna-single-v4-hybrid-clean+validate-warn-reask-test`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-hybrid-clean+validate-warn-reask | test | 102/102 | `789469b` | 2026-10-26 06:37 | $0.0080 (incl. $0.0006 re-ask) | 14.2s / 20.8s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 302 | 88.2 | 91.4 | **89.8** | 84-94 | 89.8 | 84-94 |
| text | 1 | 102 | 90.2 | 90.2 | **90.2** | 84-96 | 90.2 | 84-96 |
| date | 3 | 237 | 92.4 | 87.3 | **89.8** | 86-93 | 88.7 | 85-92 |
| duration | 2 | 61 | 87.5 | 91.8 | **89.6** | 82-96 | 88.2 | 79-95 |
| jurisdiction | 1 | 92 | 80.6 | 94.6 | **87.0** | 83-91 | 87.0 | 83-91 |
| clause | 33 | 777 | 71.1 | 88.9 | **79.0** | 77-81 | 75.8 | 71-78 |
| all fields | 41 | 1571 | 79.0 | 89.7 | **84.0** | 82-86 | 78.4 | 75-80 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 101 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 102 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 263 | 94.1 | 97.0 | **95.5** | 94-97 | 95.3 | 93-97 |
| duration | 2 | 67 | 78.3 | 97.0 | **86.7** | 80-92 | 86.5 | 79-92 |
| jurisdiction | 1 | 89 | 98.9 | 97.8 | **98.3** | 96-100 | 98.3 | 96-100 |
| clause | 33 | 777 | 71.1 | 88.9 | **79.0** | 77-81 | 75.8 | 71-78 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 197 | 72.9 | 77.7 | **75.2** | 71-79 | 68.3 | 60-74 |
| ip_and_licensing | 10 | 180 | 78.8 | 92.8 | **85.2** | 81-89 | 83.8 | 74-89 |
| liability_and_risk | 5 | 115 | 71.7 | 86.1 | **78.3** | 73-84 | 70.4 | 61-78 |
| restrictive_covenants | 6 | 106 | 62.9 | 94.3 | **75.5** | 70-80 | 76.0 | 67-82 |
| term_and_termination | 4 | 179 | 68.0 | 96.1 | **79.6** | 76-83 | 77.7 | 73-82 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `price_restrictions` | clause | presence | 3 | 5.4 | 66.7 | **10.0** | 0-24 | 10.0 | 9.1 |
| `third_party_beneficiary` | clause | presence | 6 | 40.0 | 66.7 | **50.0** | 15-76 | 50.0 | 44.4 |
| `competitive_restriction_exception` | clause | presence | 15 | 35.7 | 100.0 | **52.6** | 34-67 | 52.6 | 31.6 |
| `post_termination_services` | clause | presence | 36 | 40.4 | 100.0 | **57.6** | 47-67 | 57.6 | 26.3 |
| `volume_restriction` | clause | presence | 17 | 58.8 | 58.8 | **58.8** | 35-77 | 58.8 | 29.5 |
| `uncapped_liability` | clause | presence | 23 | 47.4 | 78.3 | **59.0** | 44-72 | 59.0 | 33.8 |
| `most_favored_nation` | clause | presence | 6 | 75.0 | 50.0 | **60.0** | 0-91 | 60.0 | 40.0 |
| `warranty_duration` | clause | presence | 15 | 57.9 | 73.3 | **64.7** | 43-82 | 64.7 | 22.6 |
| `minimum_commitment` | clause | presence | 39 | 100.0 | 51.3 | **67.8** | 53-81 | 67.8 | 21.9 |
| `change_of_control` | clause | presence | 24 | 55.0 | 91.7 | **68.8** | 55-79 | 68.8 | 47.1 |
| `non_compete` | clause | presence | 23 | 58.8 | 87.0 | **70.2** | 55-83 | 70.2 | 40.0 |
| `affiliate_license_licensor` | clause | presence | 5 | 55.6 | 100.0 | **71.4** | 36-94 | 71.4 | 32.0 |
| `no_solicit_of_customers` | clause | presence | 7 | 66.7 | 85.7 | **75.0** | 40-95 | 75.0 | 60.0 |
| `affiliate_license_licensee` | clause | presence | 12 | 71.4 | 83.3 | **76.9** | 52-93 | 76.9 | 45.7 |
| `non_disparagement` | clause | presence | 8 | 70.0 | 87.5 | **77.8** | 50-97 | 77.8 | 43.5 |
| `covenant_not_to_sue` | clause | presence | 20 | 76.2 | 80.0 | **78.0** | 62-90 | 78.0 | 50.0 |
| `ip_ownership_assignment` | clause | presence | 25 | 66.7 | 96.0 | **78.7** | 65-89 | 78.7 | 45.8 |
| `rofr_rofo_rofn` | clause | presence | 17 | 81.2 | 76.5 | **78.8** | 62-92 | 78.8 | 34.7 |
| `joint_ip_ownership` | clause | presence | 9 | 100.0 | 66.7 | **80.0** | 44-100 | 80.0 | 44.4 |
| `unlimited_all_you_can_eat_license` | clause | presence | 3 | 100.0 | 66.7 | **80.0** | 0-100 | 80.0 | 57.1 |
| `expiration_date` | date | value | 71 | 92.7 | 71.8 | **81.0** | 73-88 | 94.2 |  |
| `revenue_profit_sharing` | clause | presence | 33 | 77.8 | 84.8 | **81.2** | 70-90 | 81.2 | 43.2 |
| `notice_period_to_terminate_renewal` | duration | value | 22 | 74.1 | 90.9 | **81.6** | 68-92 | 85.7 |  |
| `liquidated_damages` | clause | presence | 12 | 83.3 | 83.3 | **83.3** | 63-96 | 83.3 | 45.0 |
| `non_transferable_license` | clause | presence | 31 | 73.2 | 96.8 | **83.3** | 73-91 | 83.3 | 51.0 |
| `termination_for_convenience` | clause | presence | 42 | 82.6 | 90.5 | **86.4** | 79-94 | 86.4 | 74.5 |
| `governing_law` | jurisdiction | value | 92 | 80.6 | 94.6 | **87.0** | 83-91 | 98.3 |  |
| `exclusivity` | clause | presence | 41 | 80.0 | 97.6 | **87.9** | 80-94 | 87.9 | 53.3 |
| `effective_date` | date | value | 73 | 85.7 | 90.4 | **88.0** | 82-93 | 92.2 |  |
| `parties` | entity_list | value | 302 | 88.2 | 91.4 | **89.8** | 84-94 | 100.0 |  |
| `document_name` | text | value | 102 | 90.2 | 90.2 | **90.2** | 84-96 | 100.0 |  |
| `no_solicit_of_employees` | clause | presence | 12 | 85.7 | 100.0 | **92.3** | 78-100 | 92.3 | 70.6 |
| `license_grant` | clause | presence | 58 | 86.6 | 100.0 | **92.8** | 87-97 | 92.8 | 53.6 |
| `renewal_term` | duration | value | 39 | 97.3 | 92.3 | **94.7** | 87-100 | 87.2 |  |
| `cap_on_liability` | clause | presence | 59 | 94.9 | 94.9 | **94.9** | 91-98 | 94.9 | 51.4 |
| `audit_rights` | clause | presence | 49 | 94.0 | 95.9 | **94.9** | 90-99 | 94.9 | 50.5 |
| `insurance` | clause | presence | 33 | 100.0 | 90.9 | **95.2** | 89-100 | 95.2 | 36.6 |
| `irrevocable_or_perpetual_license` | clause | presence | 14 | 100.0 | 92.9 | **96.3** | 87-100 | 96.3 | 59.6 |
| `agreement_date` | date | value | 93 | 97.8 | 96.8 | **97.3** | 94-100 | 99.5 |  |
| `anti_assignment` | clause | presence | 77 | 97.4 | 98.7 | **98.1** | 96-100 | 98.1 | 68.8 |
| `source_code_escrow` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 40.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 87.5 | 8 | 75.0 | 4 | +12.5 |
| `affiliate_license_licensor` | 100.0 | 4 | 100.0 | 1 | +0.0 |
| `anti_assignment` | 98.7 | 75 | 100.0 | 2 | -1.3 |
| `audit_rights` | 95.8 | 48 | 100.0 | 1 | -4.2 |
| `cap_on_liability` | 94.3 | 35 | 95.8 | 24 | -1.5 |
| `change_of_control` | 88.9 | 9 | 93.3 | 15 | -4.4 |
| `competitive_restriction_exception` | 100.0 | 9 | 100.0 | 6 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 13 | 42.9 | 7 | +57.1 |
| `document_name` | 100.0 | 99 | 100.0 | 3 | +0.0 |
| `exclusivity` | 100.0 | 32 | 88.9 | 9 | +11.1 |
| `expiration_date` | 96.2 | 52 | 83.3 | 36 | +12.8 |
| `governing_law` | 100.0 | 86 | 50.0 | 2 | +50.0 |
| `insurance` | 90.9 | 33 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 15 | 90.0 | 10 | +10.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 12 | 50.0 | 2 | +50.0 |
| `joint_ip_ownership` | 66.7 | 9 | — | 0 | — |
| `license_grant` | 100.0 | 48 | 100.0 | 10 | +0.0 |
| `liquidated_damages` | 100.0 | 8 | 50.0 | 4 | +50.0 |
| `minimum_commitment` | 58.6 | 29 | 30.0 | 10 | +28.6 |
| `most_favored_nation` | 0.0 | 1 | 60.0 | 5 | -60.0 |
| `no_solicit_of_customers` | 100.0 | 3 | 75.0 | 4 | +25.0 |
| `no_solicit_of_employees` | 100.0 | 10 | 100.0 | 2 | +0.0 |
| `non_compete` | 86.4 | 22 | 100.0 | 1 | -13.6 |
| `non_disparagement` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `non_transferable_license` | 100.0 | 23 | 87.5 | 8 | +12.5 |
| `notice_period_to_terminate_renewal` | 92.3 | 13 | 100.0 | 12 | -7.7 |
| `post_termination_services` | 100.0 | 10 | 100.0 | 26 | +0.0 |
| `price_restrictions` | 100.0 | 1 | 50.0 | 2 | +50.0 |
| `renewal_term` | 100.0 | 33 | 88.9 | 9 | +11.1 |
| `revenue_profit_sharing` | 100.0 | 20 | 61.5 | 13 | +38.5 |
| `rofr_rofo_rofn` | 100.0 | 4 | 69.2 | 13 | +30.8 |
| `source_code_escrow` | 100.0 | 3 | — | 0 | — |
| `termination_for_convenience` | 94.1 | 17 | 88.0 | 25 | +6.1 |
| `third_party_beneficiary` | 100.0 | 3 | 33.3 | 3 | +66.7 |
| `uncapped_liability` | 78.9 | 19 | 75.0 | 4 | +3.9 |
| `unlimited_all_you_can_eat_license` | 66.7 | 3 | — | 0 | — |
| `volume_restriction` | 77.8 | 9 | 37.5 | 8 | +40.3 |
| `warranty_duration` | 100.0 | 8 | 42.9 | 7 | +57.1 |
| **all** | 95.2 | 831 | 80.4 | 291 | +14.8 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 102/102 | 100.0 |
| quotes found in the contract | 1873/1874 | 99.9 |
| values with no grounded evidence | 0/1554 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/316 | 0.0 |
| false positives, grounded (over-triggers) | 316/316 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: `ungrounded_quote` 1, `too_few_parties` 1.
