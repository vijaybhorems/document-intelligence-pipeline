# Eval report: `20261021-032202-llm-gpt-5.6-luna-single-v4-docling-scanned-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-docling-scanned | experiment | 30/30 | `58855d2` | 2026-10-21 03:22 | $0.0070 | 15.6s / 21.2s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 89.2 | 85.3 | **87.2** | 81-94 | 87.2 | 81-94 |
| text | 1 | 30 | 89.7 | 86.7 | **88.1** | 76-98 | 88.1 | 76-98 |
| date | 3 | 66 | 87.3 | 72.7 | **79.3** | 67-88 | 75.4 | 61-86 |
| duration | 2 | 21 | 87.0 | 95.2 | **90.9** | 80-98 | 90.2 | 76-98 |
| jurisdiction | 1 | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 92.9 | 87-98 |
| clause | 33 | 215 | 70.2 | 86.5 | **77.5** | 73-82 | 66.3 | 60-72 |
| all fields | 41 | 427 | 78.1 | 85.2 | **81.5** | 79-84 | 69.8 | 65-75 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 96.7 | **98.3** | 95-100 | 98.3 | 95-100 |
| date | 3 | 79 | 93.7 | 93.7 | **93.7** | 89-98 | 93.6 | 89-98 |
| duration | 2 | 22 | 75.0 | 95.5 | **84.0** | 68-94 | 85.1 | 71-94 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 70.2 | 86.5 | **77.5** | 73-82 | 66.3 | 60-72 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 67.3 | 72.5 | **69.8** | 59-79 | 52.7 | 44-64 |
| ip_and_licensing | 10 | 51 | 80.4 | 88.2 | **84.1** | 77-90 | 66.5 | 54-85 |
| liability_and_risk | 5 | 39 | 76.1 | 89.7 | **82.4** | 73-90 | 71.0 | 51-84 |
| restrictive_covenants | 6 | 29 | 72.2 | 89.7 | **80.0** | 68-89 | 76.0 | 53-89 |
| term_and_termination | 4 | 45 | 59.7 | 95.6 | **73.5** | 66-81 | 72.2 | 61-80 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `most_favored_nation` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `volume_restriction` | clause | presence | 2 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 10.0 | 100.0 | **18.2** | 0-50 | 18.2 | 16.7 |
| `third_party_beneficiary` | clause | presence | 2 | 25.0 | 50.0 | **33.3** | 0-80 | 33.3 | 60.0 |
| `expiration_date` | date | value | 19 | 63.6 | 36.8 | **46.7** | 20-69 | 92.3 |  |
| `no_solicit_of_customers` | clause | presence | 2 | 50.0 | 50.0 | **50.0** | 0-100 | 50.0 | 22.2 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 15.2 |
| `uncapped_liability` | clause | presence | 6 | 41.7 | 83.3 | **55.6** | 24-80 | 55.6 | 36.4 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 44.4 |
| `change_of_control` | clause | presence | 8 | 50.0 | 87.5 | **63.6** | 35-83 | 63.6 | 36.4 |
| `competitive_restriction_exception` | clause | presence | 4 | 50.0 | 100.0 | **66.7** | 25-91 | 66.7 | 22.2 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `non_compete` | clause | presence | 6 | 80.0 | 66.7 | **72.7** | 25-100 | 72.7 | 33.3 |
| `liquidated_damages` | clause | presence | 4 | 75.0 | 75.0 | **75.0** | 0-100 | 75.0 | 40.0 |
| `non_disparagement` | clause | presence | 3 | 60.0 | 100.0 | **75.0** | 0-100 | 75.0 | 36.4 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 60.0 | **75.0** | 0-100 | 75.0 | 20.0 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 61.5 | **76.2** | 50-94 | 76.2 | 35.0 |
| `revenue_profit_sharing` | clause | presence | 11 | 80.0 | 72.7 | **76.2** | 50-92 | 76.2 | 28.6 |
| `termination_for_convenience` | clause | presence | 7 | 63.6 | 100.0 | **77.8** | 50-95 | 77.8 | 56.0 |
| `insurance` | clause | presence | 5 | 80.0 | 80.0 | **80.0** | 40-100 | 80.0 | 17.1 |
| `non_transferable_license` | clause | presence | 8 | 66.7 | 100.0 | **80.0** | 50-96 | 80.0 | 37.0 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 66.7 |
| `effective_date` | date | value | 21 | 94.4 | 81.0 | **87.2** | 71-97 | 88.5 |  |
| `parties` | entity_list | value | 68 | 89.2 | 85.3 | **87.2** | 81-94 | 100.0 |  |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 87.5 | 87.5 | **87.5** | 62-100 | 88.9 |  |
| `document_name` | text | value | 30 | 89.7 | 86.7 | **88.1** | 76-98 | 98.3 |  |
| `ip_ownership_assignment` | clause | presence | 9 | 81.8 | 100.0 | **90.0** | 71-100 | 90.0 | 38.7 |
| `warranty_duration` | clause | presence | 6 | 100.0 | 83.3 | **90.9** | 60-100 | 90.9 | 55.6 |
| `exclusivity` | clause | presence | 11 | 84.6 | 100.0 | **91.7** | 77-100 | 91.7 | 66.7 |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 100.0 |  |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 66.7 |
| `governing_law` | jurisdiction | value | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 98.1 |  |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 80-100 | 81.2 |  |
| `license_grant` | clause | presence | 14 | 87.5 | 100.0 | **93.3** | 81-100 | 93.3 | 49.1 |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 55.8 |
| `anti_assignment` | clause | presence | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 97.6 | 64.6 |
| `cap_on_liability` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 41.6 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 0.0 | 1 | — | 0 | — |
| `anti_assignment` | 95.2 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 13 | 100.0 | 8 | +0.0 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 96.7 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 75.0 | 8 | +25.0 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 75.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 66.7 | 12 | 0.0 | 1 | +66.7 |
| `most_favored_nation` | 0.0 | 1 | — | 0 | — |
| `no_solicit_of_customers` | 100.0 | 1 | 0.0 | 1 | +100.0 |
| `no_solicit_of_employees` | 100.0 | 2 | 100.0 | 1 | +0.0 |
| `non_compete` | 50.0 | 4 | 100.0 | 2 | -50.0 |
| `non_disparagement` | 100.0 | 1 | 100.0 | 2 | +0.0 |
| `non_transferable_license` | 100.0 | 6 | 100.0 | 2 | +0.0 |
| `notice_period_to_terminate_renewal` | 80.0 | 5 | 100.0 | 4 | -20.0 |
| `post_termination_services` | 100.0 | 2 | 100.0 | 7 | +0.0 |
| `price_restrictions` | — | 0 | 100.0 | 1 | — |
| `renewal_term` | 100.0 | 11 | 100.0 | 2 | +0.0 |
| `revenue_profit_sharing` | 100.0 | 7 | 25.0 | 4 | +75.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 33.3 | 3 | +66.7 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 0.0 | 1 | +0.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 93.1 | 248 | 77.5 | 71 | +15.7 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 30/30 | 100.0 |
| quotes found in the contract | 507/543 | 93.4 |
| values with no grounded evidence | 27/429 | 6.3 |
| false positives, ungrounded (**hallucinated**) | 3/91 | 3.3 |
| false positives, grounded (over-triggers) | 88/91 |  |
| correct fields whose quote wasn't found | 25 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 87.2 | +25.6 |
| text | 63.0 | 88.1 | +25.2 |
| date | 60.0 | 79.3 | +19.3 |
| duration | 81.1 | 90.9 | +9.8 |
| jurisdiction | 83.3 | 92.9 | +9.5 |
| clause | 53.5 | 77.5 | +24.0 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `most_favored_nation` | 66.7 | 0.0 | -66.7 |
| `volume_restriction` | 17.4 | 0.0 | -17.4 |
| `third_party_beneficiary` | 50.0 | 33.3 | -16.7 |
| `rofr_rofo_rofn` | 88.9 | 75.0 | -13.9 |
| `non_disparagement` | 85.7 | 75.0 | -10.7 |
| `competitive_restriction_exception` | 25.0 | 66.7 | +41.7 |
| `no_solicit_of_employees` | 54.5 | 100.0 | +45.5 |
| `effective_date` | 40.0 | 87.2 | +47.2 |
| `warranty_duration` | 34.3 | 90.9 | +56.6 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
