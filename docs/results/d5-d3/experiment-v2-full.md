# Eval report: `20261020-225626-llm-gpt-5.6-luna-single-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single | experiment | 30/30 | `96b1a5f` | 2026-10-20 22:56 | $0.0066 | 12.3s / 17.4s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 92.5 | 87-98 |
| text | 1 | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 90.0 | 80-100 |
| date | 3 | 66 | 91.9 | 86.4 | **89.1** | 81-95 | 87.6 | 78-94 |
| duration | 2 | 21 | 91.3 | 100.0 | **95.5** | 87-100 | 95.2 | 85-100 |
| jurisdiction | 1 | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 91.2 | 85-98 |
| clause | 33 | 215 | 66.1 | 88.8 | **75.8** | 71-80 | 67.0 | 59-72 |
| all fields | 41 | 427 | 76.8 | 89.9 | **82.8** | 80-85 | 71.7 | 65-76 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 93.9 | 97.5 | **95.7** | 93-98 | 95.6 | 92-98 |
| duration | 2 | 22 | 78.6 | 100.0 | **88.0** | 74-96 | 89.3 | 77-96 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 66.1 | 88.8 | **75.8** | 71-80 | 67.0 | 59-72 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 63.9 | 76.5 | **69.6** | 60-77 | 58.2 | 49-67 |
| ip_and_licensing | 10 | 51 | 69.2 | 88.2 | **77.6** | 67-85 | 64.5 | 51-76 |
| liability_and_risk | 5 | 39 | 70.0 | 89.7 | **78.7** | 69-87 | 68.2 | 51-78 |
| restrictive_covenants | 6 | 29 | 69.2 | 93.1 | **79.4** | 67-88 | 77.2 | 53-87 |
| term_and_termination | 4 | 45 | 60.8 | 100.0 | **75.6** | 66-82 | 74.3 | 62-83 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `most_favored_nation` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 7.7 | 100.0 | **14.3** | 0-40 | 14.3 | 12.5 |
| `third_party_beneficiary` | clause | presence | 2 | 11.1 | 50.0 | **18.2** | 0-50 | 18.2 | 13.3 |
| `volume_restriction` | clause | presence | 2 | 16.7 | 50.0 | **25.0** | 0-63 | 25.0 | 0.0 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 24.7 |
| `competitive_restriction_exception` | clause | presence | 4 | 44.4 | 100.0 | **61.5** | 22-89 | 61.5 | 19.0 |
| `affiliate_license_licensee` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 50.0 |
| `covenant_not_to_sue` | clause | presence | 7 | 62.5 | 71.4 | **66.7** | 33-91 | 66.7 | 40.0 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `no_solicit_of_customers` | clause | presence | 2 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 36.4 |
| `non_disparagement` | clause | presence | 3 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 14.3 |
| `uncapped_liability` | clause | presence | 6 | 55.6 | 83.3 | **66.7** | 33-90 | 66.7 | 50.0 |
| `change_of_control` | clause | presence | 8 | 53.3 | 100.0 | **69.6** | 43-88 | 69.6 | 52.9 |
| `expiration_date` | date | value | 19 | 85.7 | 63.2 | **72.7** | 50-88 | 94.1 |  |
| `non_compete` | clause | presence | 6 | 80.0 | 66.7 | **72.7** | 25-100 | 72.7 | 41.7 |
| `liquidated_damages` | clause | presence | 4 | 75.0 | 75.0 | **75.0** | 0-100 | 75.0 | 66.7 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 61.5 | **76.2** | 50-93 | 76.2 | 42.9 |
| `non_transferable_license` | clause | presence | 8 | 61.5 | 100.0 | **76.2** | 47-92 | 76.2 | 42.9 |
| `revenue_profit_sharing` | clause | presence | 11 | 80.0 | 72.7 | **76.2** | 50-92 | 76.2 | 41.2 |
| `termination_for_convenience` | clause | presence | 7 | 63.6 | 100.0 | **77.8** | 46-96 | 77.8 | 58.3 |
| `ip_ownership_assignment` | clause | presence | 9 | 64.3 | 100.0 | **78.3** | 55-94 | 78.3 | 50.0 |
| `warranty_duration` | clause | presence | 6 | 83.3 | 83.3 | **83.3** | 50-100 | 83.3 | 44.4 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 17.6 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 28.6 |
| `document_name` | text | value | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 100.0 |  |
| `license_grant` | clause | presence | 14 | 82.4 | 100.0 | **90.3** | 76-100 | 90.3 | 53.6 |
| `governing_law` | jurisdiction | value | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 98.1 |  |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 98.2 |  |
| `parties` | entity_list | value | 68 | 93.9 | 91.2 | **92.5** | 87-98 | 100.0 |  |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 75-100 | 94.7 |  |
| `exclusivity` | clause | presence | 11 | 91.7 | 100.0 | **95.7** | 84-100 | 95.7 | 75.0 |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 63.6 |
| `renewal_term` | duration | value | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 83.9 |  |
| `cap_on_liability` | clause | presence | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 97.7 | 56.8 |
| `effective_date` | date | value | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 94.5 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 76.9 |
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
| `covenant_not_to_sue` | 83.3 | 6 | 0.0 | 1 | +83.3 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 75.0 | 8 | +25.0 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 66.7 | 12 | 0.0 | 1 | +66.7 |
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
| **all** | 94.4 | 248 | 83.1 | 71 | +11.3 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 29/30 | 96.7 |
| quotes found in the contract | 587/588 | 99.8 |
| values with no grounded evidence | 0/461 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/109 | 0.0 |
| false positives, grounded (over-triggers) | 109/109 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 92.5 | +30.9 |
| text | 63.0 | 90.0 | +27.0 |
| date | 60.0 | 89.1 | +29.1 |
| duration | 81.1 | 95.5 | +14.4 |
| jurisdiction | 83.3 | 91.2 | +7.9 |
| clause | 53.5 | 75.8 | +22.3 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `most_favored_nation` | 66.7 | 0.0 | -66.7 |
| `third_party_beneficiary` | 50.0 | 18.2 | -31.8 |
| `covenant_not_to_sue` | 85.7 | 66.7 | -19.0 |
| `non_disparagement` | 85.7 | 66.7 | -19.0 |
| `non_transferable_license` | 85.7 | 76.2 | -9.5 |
| `warranty_duration` | 34.3 | 83.3 | +49.0 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `effective_date` | 40.0 | 97.7 | +57.7 |
| `expiration_date` | 10.0 | 72.7 | +62.7 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
