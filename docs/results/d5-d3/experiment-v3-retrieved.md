# Eval report: `20261020-231401-llm-gpt-5.6-luna-single-v3-retrieved-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v3-retrieved | experiment | 30/30 | `8cb756f` | 2026-10-20 23:14 | $0.0053 | 14.9s / 21.2s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 84.8 | 82.4 | **83.6** | 74-92 | 83.6 | 74-92 |
| text | 1 | 30 | 84.0 | 70.0 | **76.4** | 60-90 | 76.4 | 60-90 |
| date | 3 | 66 | 91.7 | 66.7 | **77.2** | 67-86 | 76.9 | 66-85 |
| duration | 2 | 21 | 84.0 | 100.0 | **91.3** | 80-98 | 90.9 | 78-98 |
| jurisdiction | 1 | 27 | 89.3 | 92.6 | **90.9** | 83-98 | 90.9 | 83-98 |
| clause | 33 | 215 | 68.5 | 85.1 | **75.9** | 72-80 | 68.1 | 61-73 |
| all fields | 41 | 427 | 76.3 | 82.0 | **79.0** | 76-82 | 71.0 | 65-75 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 83.3 | **90.9** | 82-98 | 90.9 | 82-98 |
| date | 3 | 79 | 93.1 | 84.8 | **88.7** | 83-94 | 88.6 | 83-94 |
| duration | 2 | 22 | 73.3 | 100.0 | **84.6** | 70-94 | 85.6 | 73-94 |
| jurisdiction | 1 | 27 | 96.3 | 96.3 | **96.3** | 90-100 | 96.3 | 90-100 |
| clause | 33 | 215 | 68.5 | 85.1 | **75.9** | 72-80 | 68.1 | 61-73 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 67.3 | 72.5 | **69.8** | 59-78 | 60.3 | 49-70 |
| ip_and_licensing | 10 | 51 | 73.3 | 86.3 | **79.3** | 71-86 | 71.1 | 57-84 |
| liability_and_risk | 5 | 39 | 76.2 | 82.1 | **79.0** | 68-88 | 60.0 | 41-71 |
| restrictive_covenants | 6 | 29 | 66.7 | 89.7 | **76.5** | 65-86 | 75.4 | 54-86 |
| term_and_termination | 4 | 45 | 62.0 | 97.8 | **75.9** | 69-81 | 75.1 | 65-81 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `most_favored_nation` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `third_party_beneficiary` | clause | presence | 2 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 9.1 | 100.0 | **16.7** | 0-44 | 16.7 | 15.4 |
| `post_termination_services` | clause | presence | 9 | 34.6 | 100.0 | **51.4** | 30-70 | 51.4 | 21.9 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 44.4 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 33.3 |
| `volume_restriction` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 0.0 |
| `change_of_control` | clause | presence | 8 | 50.0 | 87.5 | **63.6** | 35-83 | 63.6 | 37.5 |
| `affiliate_license_licensor` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `competitive_restriction_exception` | clause | presence | 4 | 50.0 | 100.0 | **66.7** | 29-91 | 66.7 | 20.0 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 50.0 | **66.7** | 0-100 | 66.7 | 40.0 |
| `minimum_commitment` | clause | presence | 13 | 87.5 | 53.8 | **66.7** | 35-86 | 66.7 | 30.0 |
| `non_compete` | clause | presence | 6 | 66.7 | 66.7 | **66.7** | 25-92 | 66.7 | 40.0 |
| `uncapped_liability` | clause | presence | 6 | 55.6 | 83.3 | **66.7** | 29-91 | 66.7 | 52.6 |
| `non_transferable_license` | clause | presence | 8 | 58.3 | 87.5 | **70.0** | 40-91 | 70.0 | 44.4 |
| `expiration_date` | date | value | 19 | 91.7 | 57.9 | **71.0** | 48-87 | 92.3 |  |
| `warranty_duration` | clause | presence | 6 | 62.5 | 83.3 | **71.4** | 36-93 | 71.4 | 47.6 |
| `non_disparagement` | clause | presence | 3 | 60.0 | 100.0 | **75.0** | 0-100 | 75.0 | 16.7 |
| `agreement_date` | date | value | 26 | 89.5 | 65.4 | **75.6** | 59-89 | 85.1 |  |
| `revenue_profit_sharing` | clause | presence | 11 | 80.0 | 72.7 | **76.2** | 50-92 | 76.2 | 41.2 |
| `document_name` | text | value | 30 | 84.0 | 70.0 | **76.4** | 60-90 | 90.9 |  |
| `ip_ownership_assignment` | clause | presence | 9 | 72.7 | 88.9 | **80.0** | 56-96 | 80.0 | 43.8 |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 71.4 | **83.3** | 50-100 | 83.3 | 35.3 |
| `parties` | entity_list | value | 68 | 84.8 | 82.4 | **83.6** | 74-92 | 100.0 |  |
| `effective_date` | date | value | 21 | 94.1 | 76.2 | **84.2** | 70-95 | 88.5 |  |
| `exclusivity` | clause | presence | 11 | 83.3 | 90.9 | **87.0** | 67-100 | 87.0 | 62.5 |
| `license_grant` | clause | presence | 14 | 77.8 | 100.0 | **87.5** | 73-97 | 87.5 | 46.4 |
| `termination_for_convenience` | clause | presence | 7 | 77.8 | 100.0 | **87.5** | 60-100 | 87.5 | 60.9 |
| `audit_rights` | clause | presence | 13 | 91.7 | 84.6 | **88.0** | 71-100 | 88.0 | 57.1 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 17.6 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 80.0 | 100.0 | **88.9** | 67-100 | 90.0 |  |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 34.8 |
| `governing_law` | jurisdiction | value | 27 | 89.3 | 92.6 | **90.9** | 83-98 | 96.3 |  |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 80-100 | 81.2 |  |
| `cap_on_liability` | clause | presence | 21 | 95.2 | 95.2 | **95.2** | 87-100 | 95.2 | 44.2 |
| `anti_assignment` | clause | presence | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 97.7 | 63.6 |
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
| `audit_rights` | 91.7 | 12 | 0.0 | 1 | +91.7 |
| `cap_on_liability` | 100.0 | 13 | 87.5 | 8 | +12.5 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 83.3 | 6 | 0.0 | 1 | +83.3 |
| `document_name` | 83.3 | 30 | — | 0 | — |
| `exclusivity` | 90.9 | 11 | — | 0 | — |
| `expiration_date` | 94.4 | 18 | 87.5 | 8 | +6.9 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 83.3 | 6 | +16.7 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 66.7 | 3 | 0.0 | 1 | +66.7 |
| `minimum_commitment` | 58.3 | 12 | 0.0 | 1 | +58.3 |
| `most_favored_nation` | 0.0 | 1 | — | 0 | — |
| `no_solicit_of_customers` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `no_solicit_of_employees` | 100.0 | 2 | 100.0 | 1 | +0.0 |
| `non_compete` | 50.0 | 4 | 100.0 | 2 | -50.0 |
| `non_disparagement` | 100.0 | 1 | 100.0 | 2 | +0.0 |
| `non_transferable_license` | 100.0 | 6 | 50.0 | 2 | +50.0 |
| `notice_period_to_terminate_renewal` | 100.0 | 5 | 100.0 | 4 | +0.0 |
| `post_termination_services` | 100.0 | 2 | 100.0 | 7 | +0.0 |
| `price_restrictions` | — | 0 | 100.0 | 1 | — |
| `renewal_term` | 100.0 | 11 | 100.0 | 2 | +0.0 |
| `revenue_profit_sharing` | 100.0 | 7 | 25.0 | 4 | +75.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 0.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 90.7 | 248 | 77.5 | 71 | +13.3 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 30/30 | 100.0 |
| quotes found in the contract | 524/524 | 100.0 |
| values with no grounded evidence | 1/421 | 0.2 |
| false positives, ungrounded (**hallucinated**) | 0/98 | 0.0 |
| false positives, grounded (over-triggers) | 98/98 |  |
| correct fields whose quote wasn't found | 1 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 83.6 | +21.9 |
| text | 63.0 | 76.4 | +13.4 |
| date | 60.0 | 77.2 | +17.2 |
| duration | 81.1 | 91.3 | +10.2 |
| jurisdiction | 83.3 | 90.9 | +7.6 |
| clause | 53.5 | 75.9 | +22.4 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `most_favored_nation` | 66.7 | 0.0 | -66.7 |
| `third_party_beneficiary` | 50.0 | 0.0 | -50.0 |
| `agreement_date` | 92.0 | 75.6 | -16.4 |
| `non_transferable_license` | 85.7 | 70.0 | -15.7 |
| `minimum_commitment` | 78.8 | 66.7 | -12.1 |
| `no_solicit_of_employees` | 54.5 | 100.0 | +45.5 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `affiliate_license_licensor` | 8.7 | 66.7 | +58.0 |
| `expiration_date` | 10.0 | 71.0 | +61.0 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
