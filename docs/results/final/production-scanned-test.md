# Eval report: `20261026-064601-llm-gpt-5.6-luna-single-v4-hybrid-scanned+validate-warn-reask-test`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-hybrid-scanned+validate-warn-reask | test | 102/102 | `789469b` | 2026-10-26 06:46 | $0.0149 (incl. $0.0005 re-ask) | 16.9s / 28.6s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 302 | 89.0 | 91.4 | **90.2** | 85-94 | 90.2 | 85-94 |
| text | 1 | 102 | 91.2 | 91.2 | **91.2** | 85-96 | 91.2 | 85-96 |
| date | 3 | 237 | 89.7 | 84.8 | **87.2** | 84-91 | 86.4 | 82-90 |
| duration | 2 | 61 | 84.8 | 91.8 | **88.2** | 81-94 | 86.5 | 78-93 |
| jurisdiction | 1 | 92 | 77.0 | 94.6 | **84.9** | 81-89 | 84.9 | 81-89 |
| clause | 33 | 777 | 70.2 | 86.2 | **77.4** | 75-80 | 73.6 | 70-76 |
| all fields | 41 | 1571 | 78.1 | 88.0 | **82.8** | 81-84 | 76.3 | 73-78 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 101 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 102 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 263 | 93.1 | 98.1 | **95.6** | 94-97 | 95.4 | 93-97 |
| duration | 2 | 67 | 77.4 | 97.0 | **86.1** | 79-92 | 85.2 | 78-92 |
| jurisdiction | 1 | 89 | 98.9 | 97.8 | **98.3** | 96-100 | 98.3 | 96-100 |
| clause | 33 | 777 | 70.2 | 86.2 | **77.4** | 75-80 | 73.6 | 70-76 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 197 | 72.2 | 79.2 | **75.5** | 71-80 | 66.8 | 59-72 |
| ip_and_licensing | 10 | 180 | 78.6 | 90.0 | **83.9** | 79-88 | 83.0 | 75-88 |
| liability_and_risk | 5 | 115 | 71.4 | 73.9 | **72.6** | 66-79 | 63.6 | 54-71 |
| restrictive_covenants | 6 | 106 | 58.3 | 89.6 | **70.6** | 64-76 | 71.9 | 62-78 |
| term_and_termination | 4 | 179 | 68.5 | 96.1 | **80.0** | 76-84 | 78.8 | 74-83 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `price_restrictions` | clause | presence | 3 | 5.4 | 66.7 | **10.0** | 0-24 | 10.0 | 4.9 |
| `third_party_beneficiary` | clause | presence | 6 | 37.5 | 50.0 | **42.9** | 0-71 | 42.9 | 40.0 |
| `warranty_duration` | clause | presence | 15 | 46.2 | 40.0 | **42.9** | 17-65 | 42.9 | 21.8 |
| `most_favored_nation` | clause | presence | 6 | 66.7 | 33.3 | **44.4** | 0-80 | 44.4 | 44.4 |
| `competitive_restriction_exception` | clause | presence | 15 | 33.3 | 93.3 | **49.1** | 31-65 | 49.1 | 22.9 |
| `uncapped_liability` | clause | presence | 23 | 41.2 | 60.9 | **49.1** | 33-64 | 49.1 | 34.8 |
| `volume_restriction` | clause | presence | 17 | 47.4 | 52.9 | **50.0** | 28-68 | 50.0 | 26.2 |
| `affiliate_license_licensor` | clause | presence | 5 | 40.0 | 80.0 | **53.3** | 15-80 | 53.3 | 23.1 |
| `non_compete` | clause | presence | 23 | 47.1 | 69.6 | **56.1** | 39-71 | 56.1 | 31.3 |
| `post_termination_services` | clause | presence | 36 | 41.4 | 100.0 | **58.5** | 48-68 | 58.5 | 28.6 |
| `covenant_not_to_sue` | clause | presence | 20 | 76.5 | 65.0 | **70.3** | 52-84 | 70.3 | 38.5 |
| `non_disparagement` | clause | presence | 8 | 63.6 | 87.5 | **73.7** | 44-94 | 73.7 | 41.7 |
| `ip_ownership_assignment` | clause | presence | 25 | 61.5 | 96.0 | **75.0** | 62-86 | 75.0 | 38.9 |
| `minimum_commitment` | clause | presence | 39 | 96.0 | 61.5 | **75.0** | 62-86 | 75.0 | 25.6 |
| `no_solicit_of_customers` | clause | presence | 7 | 66.7 | 85.7 | **75.0** | 40-94 | 75.0 | 63.2 |
| `change_of_control` | clause | presence | 24 | 63.9 | 95.8 | **76.7** | 63-87 | 76.7 | 55.4 |
| `notice_period_to_terminate_renewal` | duration | value | 22 | 66.7 | 90.9 | **76.9** | 62-89 | 81.4 |  |
| `expiration_date` | date | value | 71 | 89.3 | 70.4 | **78.7** | 70-87 | 96.6 |  |
| `revenue_profit_sharing` | clause | presence | 33 | 73.7 | 84.8 | **78.9** | 68-89 | 78.9 | 42.9 |
| `affiliate_license_licensee` | clause | presence | 12 | 76.9 | 83.3 | **80.0** | 57-94 | 80.0 | 47.1 |
| `rofr_rofo_rofn` | clause | presence | 17 | 92.9 | 76.5 | **83.9** | 69-95 | 83.9 | 30.6 |
| `termination_for_convenience` | clause | presence | 42 | 79.2 | 90.5 | **84.4** | 75-92 | 84.4 | 75.0 |
| `irrevocable_or_perpetual_license` | clause | presence | 14 | 91.7 | 78.6 | **84.6** | 67-97 | 84.6 | 41.9 |
| `governing_law` | jurisdiction | value | 92 | 77.0 | 94.6 | **84.9** | 81-89 | 98.3 |  |
| `exclusivity` | clause | presence | 41 | 75.5 | 97.6 | **85.1** | 77-92 | 85.1 | 48.3 |
| `non_transferable_license` | clause | presence | 31 | 78.4 | 93.5 | **85.3** | 75-93 | 85.3 | 44.4 |
| `joint_ip_ownership` | clause | presence | 9 | 100.0 | 77.8 | **87.5** | 60-100 | 87.5 | 60.0 |
| `effective_date` | date | value | 73 | 85.7 | 90.4 | **88.0** | 82-93 | 91.6 |  |
| `parties` | entity_list | value | 302 | 89.0 | 91.4 | **90.2** | 85-94 | 100.0 |  |
| `liquidated_damages` | clause | presence | 12 | 100.0 | 83.3 | **90.9** | 74-100 | 90.9 | 59.5 |
| `document_name` | text | value | 102 | 91.2 | 91.2 | **91.2** | 85-96 | 100.0 |  |
| `cap_on_liability` | clause | presence | 59 | 96.3 | 88.1 | **92.0** | 86-97 | 92.0 | 49.5 |
| `no_solicit_of_employees` | clause | presence | 12 | 85.7 | 100.0 | **92.3** | 78-100 | 92.3 | 72.7 |
| `agreement_date` | date | value | 93 | 93.4 | 91.4 | **92.4** | 87-97 | 98.0 |  |
| `license_grant` | clause | presence | 58 | 89.2 | 100.0 | **94.3** | 89-98 | 94.3 | 51.1 |
| `insurance` | clause | presence | 33 | 96.9 | 93.9 | **95.4** | 89-100 | 95.4 | 36.4 |
| `anti_assignment` | clause | presence | 77 | 93.8 | 97.4 | **95.5** | 92-98 | 95.5 | 66.4 |
| `renewal_term` | duration | value | 39 | 100.0 | 92.3 | **96.0** | 91-100 | 89.1 |  |
| `audit_rights` | clause | presence | 49 | 97.9 | 95.9 | **96.9** | 93-100 | 96.9 | 52.2 |
| `source_code_escrow` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 58.8 |
| `unlimited_all_you_can_eat_license` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 75.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 87.5 | 8 | 75.0 | 4 | +12.5 |
| `affiliate_license_licensor` | 75.0 | 4 | 100.0 | 1 | -25.0 |
| `anti_assignment` | 97.3 | 75 | 100.0 | 2 | -2.7 |
| `audit_rights` | 95.8 | 48 | 100.0 | 1 | -4.2 |
| `cap_on_liability` | 94.3 | 35 | 79.2 | 24 | +15.1 |
| `change_of_control` | 100.0 | 9 | 93.3 | 15 | +6.7 |
| `competitive_restriction_exception` | 88.9 | 9 | 100.0 | 6 | -11.1 |
| `covenant_not_to_sue` | 76.9 | 13 | 42.9 | 7 | +34.1 |
| `document_name` | 100.0 | 99 | 100.0 | 3 | +0.0 |
| `exclusivity` | 100.0 | 32 | 88.9 | 9 | +11.1 |
| `expiration_date` | 100.0 | 52 | 88.9 | 36 | +11.1 |
| `governing_law` | 100.0 | 86 | 50.0 | 2 | +50.0 |
| `insurance` | 93.9 | 33 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 15 | 90.0 | 10 | +10.0 |
| `irrevocable_or_perpetual_license` | 91.7 | 12 | 0.0 | 2 | +91.7 |
| `joint_ip_ownership` | 77.8 | 9 | — | 0 | — |
| `license_grant` | 100.0 | 48 | 100.0 | 10 | +0.0 |
| `liquidated_damages` | 100.0 | 8 | 50.0 | 4 | +50.0 |
| `minimum_commitment` | 69.0 | 29 | 40.0 | 10 | +29.0 |
| `most_favored_nation` | 0.0 | 1 | 40.0 | 5 | -40.0 |
| `no_solicit_of_customers` | 100.0 | 3 | 75.0 | 4 | +25.0 |
| `no_solicit_of_employees` | 100.0 | 10 | 100.0 | 2 | +0.0 |
| `non_compete` | 68.2 | 22 | 100.0 | 1 | -31.8 |
| `non_disparagement` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `non_transferable_license` | 95.7 | 23 | 87.5 | 8 | +8.2 |
| `notice_period_to_terminate_renewal` | 92.3 | 13 | 100.0 | 12 | -7.7 |
| `post_termination_services` | 100.0 | 10 | 100.0 | 26 | +0.0 |
| `price_restrictions` | 100.0 | 1 | 50.0 | 2 | +50.0 |
| `renewal_term` | 100.0 | 33 | 88.9 | 9 | +11.1 |
| `revenue_profit_sharing` | 100.0 | 20 | 61.5 | 13 | +38.5 |
| `rofr_rofo_rofn` | 100.0 | 4 | 69.2 | 13 | +30.8 |
| `source_code_escrow` | 100.0 | 3 | — | 0 | — |
| `termination_for_convenience` | 94.1 | 17 | 88.0 | 25 | +6.1 |
| `third_party_beneficiary` | 66.7 | 3 | 33.3 | 3 | +33.3 |
| `uncapped_liability` | 63.2 | 19 | 50.0 | 4 | +13.2 |
| `unlimited_all_you_can_eat_license` | 100.0 | 3 | — | 0 | — |
| `volume_restriction` | 55.6 | 9 | 50.0 | 8 | +5.6 |
| `warranty_duration` | 75.0 | 8 | 0.0 | 7 | +75.0 |
| **all** | 93.9 | 831 | 78.4 | 291 | +15.5 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 102/102 | 100.0 |
| quotes found in the contract | 1822/1825 | 99.8 |
| values with no grounded evidence | 0/1539 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/324 | 0.0 |
| false positives, grounded (over-triggers) | 324/324 |  |
| correct fields whose quote wasn't found | 1 |  |

Validation issues: `ungrounded_quote` 3, `too_few_parties` 2.
