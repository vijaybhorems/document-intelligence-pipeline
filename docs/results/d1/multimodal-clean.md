# Eval report: `20261021-030850-llm-gpt-5.6-luna-single-v4-multimodal-clean-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-multimodal-clean | experiment | 30/30 | `c7c64ff` | 2026-10-21 03:08 | $0.0108 | 18.1s / 25.0s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 92.4 | 89.7 | **91.0** | 86-97 | 91.0 | 86-97 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 93.3 | 84.8 | **88.9** | 81-95 | 87.0 | 77-94 |
| duration | 2 | 21 | 91.3 | 100.0 | **95.5** | 85-100 | 96.4 | 89-100 |
| jurisdiction | 1 | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 91.2 | 85-98 |
| clause | 33 | 215 | 68.8 | 88.4 | **77.4** | 73-81 | 67.9 | 60-73 |
| all fields | 41 | 427 | 78.4 | 89.0 | **83.3** | 81-86 | 72.2 | 66-77 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 92.9 | 98.7 | **95.7** | 92-98 | 95.7 | 92-98 |
| duration | 2 | 22 | 81.5 | 100.0 | **89.8** | 76-98 | 91.9 | 83-98 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 68.8 | 88.4 | **77.4** | 73-81 | 67.9 | 60-73 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 69.6 | 76.5 | **72.9** | 64-80 | 57.9 | 48-67 |
| ip_and_licensing | 10 | 51 | 75.4 | 90.2 | **82.1** | 73-89 | 67.1 | 55-81 |
| liability_and_risk | 5 | 39 | 73.9 | 87.2 | **80.0** | 68-89 | 69.0 | 49-83 |
| restrictive_covenants | 6 | 29 | 67.5 | 93.1 | **78.3** | 68-88 | 77.4 | 57-88 |
| term_and_termination | 4 | 45 | 60.3 | 97.8 | **74.6** | 67-81 | 74.0 | 63-82 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `most_favored_nation` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 11.1 | 100.0 | **20.0** | 0-55 | 20.0 | 20.0 |
| `volume_restriction` | clause | presence | 2 | 20.0 | 50.0 | **28.6** | 0-67 | 28.6 | 20.0 |
| `third_party_beneficiary` | clause | presence | 2 | 25.0 | 50.0 | **33.3** | 0-80 | 33.3 | 25.0 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 17.4 |
| `uncapped_liability` | clause | presence | 6 | 41.7 | 83.3 | **55.6** | 25-80 | 55.6 | 43.5 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 40.0 |
| `change_of_control` | clause | presence | 8 | 43.8 | 87.5 | **58.3** | 31-77 | 58.3 | 45.7 |
| `affiliate_license_licensee` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 50.0 |
| `competitive_restriction_exception` | clause | presence | 4 | 50.0 | 100.0 | **66.7** | 29-91 | 66.7 | 21.1 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `non_compete` | clause | presence | 6 | 66.7 | 66.7 | **66.7** | 25-92 | 66.7 | 40.0 |
| `expiration_date` | date | value | 19 | 84.6 | 57.9 | **68.8** | 46-85 | 94.3 |  |
| `revenue_profit_sharing` | clause | presence | 11 | 72.7 | 72.7 | **72.7** | 46-90 | 72.7 | 35.3 |
| `liquidated_damages` | clause | presence | 4 | 75.0 | 75.0 | **75.0** | 0-100 | 75.0 | 54.5 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 60.0 | **75.0** | 0-100 | 75.0 | 20.0 |
| `non_transferable_license` | clause | presence | 8 | 66.7 | 100.0 | **80.0** | 50-96 | 80.0 | 40.0 |
| `ip_ownership_assignment` | clause | presence | 9 | 69.2 | 100.0 | **81.8** | 62-96 | 81.8 | 48.6 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 69.2 | **81.8** | 61-96 | 81.8 | 40.9 |
| `warranty_duration` | clause | presence | 6 | 83.3 | 83.3 | **83.3** | 50-100 | 83.3 | 55.6 |
| `covenant_not_to_sue` | clause | presence | 7 | 85.7 | 85.7 | **85.7** | 57-100 | 85.7 | 52.6 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 40.0 |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `termination_for_convenience` | clause | presence | 7 | 77.8 | 100.0 | **87.5** | 62-100 | 87.5 | 60.9 |
| `exclusivity` | clause | presence | 11 | 78.6 | 100.0 | **88.0** | 71-100 | 88.0 | 70.6 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 17.6 |
| `license_grant` | clause | presence | 14 | 82.4 | 100.0 | **90.3** | 76-100 | 90.3 | 48.1 |
| `parties` | entity_list | value | 68 | 92.4 | 89.7 | **91.0** | 86-97 | 100.0 |  |
| `governing_law` | jurisdiction | value | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 98.1 |  |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 98.2 |  |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 78-100 | 83.9 |  |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 60.5 |
| `cap_on_liability` | clause | presence | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 97.6 | 49.4 |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `effective_date` | date | value | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 94.5 |  |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 |  |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 0.0 | 1 | — | 0 | — |
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
| `insurance` | 80.0 | 5 | — | 0 | — |
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
| `rofr_rofo_rofn` | 100.0 | 2 | 33.3 | 3 | +66.7 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 95.2 | 248 | 80.3 | 71 | +14.9 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 30/30 | 100.0 |
| quotes found in the contract | 545/546 | 99.8 |
| values with no grounded evidence | 0/447 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/97 | 0.0 |
| false positives, grounded (over-triggers) | 97/97 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 91.0 | +29.4 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 88.9 | +28.9 |
| duration | 81.1 | 95.5 | +14.4 |
| jurisdiction | 83.3 | 91.2 | +7.9 |
| clause | 53.5 | 77.4 | +23.9 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `most_favored_nation` | 66.7 | 0.0 | -66.7 |
| `third_party_beneficiary` | 50.0 | 33.3 | -16.7 |
| `rofr_rofo_rofn` | 88.9 | 75.0 | -13.9 |
| `change_of_control` | 70.6 | 58.3 | -12.3 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `warranty_duration` | 34.3 | 83.3 | +49.0 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `expiration_date` | 10.0 | 68.8 | +58.8 |
| `effective_date` | 40.0 | 100.0 | +60.0 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
