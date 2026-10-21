# Eval report: `20261020-230003-llm-gpt-5.6-luna-single-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single | experiment | 30/30 | `96b1a5f` | 2026-10-20 23:00 | $0.0060 | 14.8s / 20.2s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 92.4 | 89.7 | **91.0** | 85-97 | 91.0 | 85-97 |
| text | 1 | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 90.0 | 80-100 |
| date | 3 | 66 | 94.8 | 83.3 | **88.7** | 82-94 | 86.9 | 78-93 |
| duration | 2 | 21 | 87.5 | 100.0 | **93.3** | 82-100 | 93.5 | 82-100 |
| jurisdiction | 1 | 27 | 81.2 | 96.3 | **88.1** | 81-95 | 88.1 | 81-95 |
| clause | 33 | 215 | 70.7 | 89.8 | **79.1** | 74-83 | 71.6 | 62-79 |
| all fields | 41 | 427 | 79.3 | 89.7 | **84.2** | 82-86 | 75.1 | 67-81 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 92.8 | 97.5 | **95.1** | 91-98 | 95.0 | 91-98 |
| duration | 2 | 22 | 75.9 | 100.0 | **86.3** | 72-95 | 88.0 | 76-95 |
| jurisdiction | 1 | 27 | 96.3 | 96.3 | **96.3** | 90-100 | 96.3 | 90-100 |
| clause | 33 | 215 | 70.7 | 89.8 | **79.1** | 74-83 | 71.6 | 62-79 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 70.7 | 80.4 | **75.2** | 66-82 | 61.4 | 52-70 |
| ip_and_licensing | 10 | 51 | 78.3 | 92.2 | **84.7** | 77-91 | 74.3 | 61-88 |
| liability_and_risk | 5 | 39 | 72.3 | 87.2 | **79.1** | 69-88 | 68.5 | 48-83 |
| restrictive_covenants | 6 | 29 | 73.0 | 93.1 | **81.8** | 71-90 | 80.6 | 59-90 |
| term_and_termination | 4 | 45 | 62.0 | 97.8 | **75.9** | 67-83 | 75.3 | 64-84 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `most_favored_nation` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 10.0 | 100.0 | **18.2** | 0-50 | 18.2 | 15.4 |
| `third_party_beneficiary` | clause | presence | 2 | 25.0 | 50.0 | **33.3** | 0-80 | 33.3 | 44.4 |
| `volume_restriction` | clause | presence | 2 | 25.0 | 50.0 | **33.3** | 0-75 | 33.3 | 25.0 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 17.1 |
| `uncapped_liability` | clause | presence | 6 | 41.7 | 83.3 | **55.6** | 23-80 | 55.6 | 50.0 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 44.4 |
| `change_of_control` | clause | presence | 8 | 50.0 | 87.5 | **63.6** | 35-83 | 63.6 | 41.2 |
| `affiliate_license_licensor` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 0.0 |
| `competitive_restriction_exception` | clause | presence | 4 | 50.0 | 100.0 | **66.7** | 29-92 | 66.7 | 20.0 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `no_solicit_of_customers` | clause | presence | 2 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 30.8 |
| `expiration_date` | date | value | 19 | 91.7 | 57.9 | **71.0** | 47-86 | 94.3 |  |
| `non_compete` | clause | presence | 6 | 80.0 | 66.7 | **72.7** | 25-100 | 72.7 | 41.7 |
| `liquidated_damages` | clause | presence | 4 | 75.0 | 75.0 | **75.0** | 0-100 | 75.0 | 66.7 |
| `revenue_profit_sharing` | clause | presence | 11 | 80.0 | 72.7 | **76.2** | 50-92 | 76.2 | 27.0 |
| `non_transferable_license` | clause | presence | 8 | 66.7 | 100.0 | **80.0** | 50-95 | 80.0 | 48.0 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 69.2 | **81.8** | 61-96 | 81.8 | 39.0 |
| `warranty_duration` | clause | presence | 6 | 83.3 | 83.3 | **83.3** | 50-100 | 83.3 | 44.4 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 36.4 |
| `termination_for_convenience` | clause | presence | 7 | 77.8 | 100.0 | **87.5** | 60-100 | 87.5 | 60.9 |
| `governing_law` | jurisdiction | value | 27 | 81.2 | 96.3 | **88.1** | 81-95 | 96.3 |  |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 19.0 |
| `document_name` | text | value | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 100.0 |  |
| `ip_ownership_assignment` | clause | presence | 9 | 81.8 | 100.0 | **90.0** | 71-100 | 90.0 | 56.2 |
| `license_grant` | clause | presence | 14 | 82.4 | 100.0 | **90.3** | 76-100 | 90.3 | 53.6 |
| `parties` | entity_list | value | 68 | 92.4 | 89.7 | **91.0** | 85-97 | 100.0 |  |
| `exclusivity` | clause | presence | 11 | 84.6 | 100.0 | **91.7** | 77-100 | 91.7 | 68.8 |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 98.2 |  |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 66.7 |
| `audit_rights` | clause | presence | 13 | 86.7 | 100.0 | **92.9** | 80-100 | 92.9 | 57.8 |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 78-100 | 81.2 |  |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 94.7 |  |
| `cap_on_liability` | clause | presence | 21 | 95.2 | 95.2 | **95.2** | 86-100 | 95.2 | 51.9 |
| `effective_date` | date | value | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 92.6 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `insurance` | clause | presence | 5 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 22.9 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 76.9 |
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
| `cap_on_liability` | 100.0 | 13 | 87.5 | 8 | +12.5 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 87.5 | 8 | +12.5 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 100.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 75.0 | 12 | 0.0 | 1 | +75.0 |
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
| `revenue_profit_sharing` | 100.0 | 7 | 25.0 | 4 | +75.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 96.0 | 248 | 81.7 | 71 | +14.3 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 29/30 | 96.7 |
| quotes found in the contract | 553/553 | 100.0 |
| values with no grounded evidence | 0/442 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/94 | 0.0 |
| false positives, grounded (over-triggers) | 94/94 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 91.0 | +29.4 |
| text | 63.0 | 90.0 | +27.0 |
| date | 60.0 | 88.7 | +28.7 |
| duration | 81.1 | 93.3 | +12.3 |
| jurisdiction | 83.3 | 88.1 | +4.8 |
| clause | 53.5 | 79.1 | +25.6 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `most_favored_nation` | 66.7 | 0.0 | -66.7 |
| `third_party_beneficiary` | 50.0 | 33.3 | -16.7 |
| `change_of_control` | 70.6 | 63.6 | -7.0 |
| `non_transferable_license` | 85.7 | 80.0 | -5.7 |
| `non_disparagement` | 85.7 | 85.7 | +0.0 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `effective_date` | 40.0 | 97.6 | +57.6 |
| `affiliate_license_licensor` | 8.7 | 66.7 | +58.0 |
| `expiration_date` | 10.0 | 71.0 | +61.0 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
