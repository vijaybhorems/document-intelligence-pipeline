# Eval report: `20261021-030530-llm-gpt-5.6-luna-single-v4-pypdf-clean-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-pypdf-clean | experiment | 30/30 | `c7c64ff` | 2026-10-21 03:05 | $0.0074 | 16.6s / 24.4s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 92.4 | 89.7 | **91.0** | 86-97 | 91.0 | 86-97 |
| text | 1 | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 90.0 | 80-100 |
| date | 3 | 66 | 93.4 | 86.4 | **89.8** | 84-94 | 88.3 | 81-94 |
| duration | 2 | 21 | 95.5 | 100.0 | **97.7** | 91-100 | 98.1 | 93-100 |
| jurisdiction | 1 | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 91.2 | 85-98 |
| clause | 33 | 215 | 68.2 | 88.8 | **77.2** | 73-81 | 69.5 | 62-74 |
| all fields | 41 | 427 | 78.3 | 89.7 | **83.6** | 81-86 | 73.9 | 68-78 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 92.9 | 98.7 | **95.7** | 93-98 | 95.7 | 92-98 |
| duration | 2 | 22 | 81.5 | 100.0 | **89.8** | 77-97 | 91.9 | 83-97 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 68.2 | 88.8 | **77.2** | 73-81 | 69.5 | 62-74 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 69.6 | 76.5 | **72.9** | 63-81 | 65.5 | 50-73 |
| ip_and_licensing | 10 | 51 | 79.3 | 90.2 | **84.4** | 77-90 | 68.3 | 58-81 |
| liability_and_risk | 5 | 39 | 71.4 | 89.7 | **79.5** | 68-89 | 69.5 | 49-83 |
| restrictive_covenants | 6 | 29 | 62.8 | 93.1 | **75.0** | 62-85 | 74.7 | 52-85 |
| term_and_termination | 4 | 45 | 59.5 | 97.8 | **73.9** | 65-81 | 73.0 | 61-81 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 11.1 | 100.0 | **20.0** | 0-55 | 20.0 | 20.0 |
| `third_party_beneficiary` | clause | presence | 2 | 16.7 | 50.0 | **25.0** | 0-67 | 25.0 | 36.4 |
| `volume_restriction` | clause | presence | 2 | 20.0 | 50.0 | **28.6** | 0-67 | 28.6 | 22.2 |
| `post_termination_services` | clause | presence | 9 | 32.1 | 100.0 | **48.6** | 27-68 | 48.6 | 13.3 |
| `competitive_restriction_exception` | clause | presence | 4 | 36.4 | 100.0 | **53.3** | 18-80 | 53.3 | 18.2 |
| `uncapped_liability` | clause | presence | 6 | 41.7 | 83.3 | **55.6** | 24-80 | 55.6 | 43.5 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 44.4 |
| `change_of_control` | clause | presence | 8 | 46.7 | 87.5 | **60.9** | 32-81 | 60.9 | 47.1 |
| `non_compete` | clause | presence | 6 | 57.1 | 66.7 | **61.5** | 20-86 | 61.5 | 32.0 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `no_solicit_of_customers` | clause | presence | 2 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 36.4 |
| `expiration_date` | date | value | 19 | 85.7 | 63.2 | **72.7** | 52-88 | 92.6 |  |
| `revenue_profit_sharing` | clause | presence | 11 | 72.7 | 72.7 | **72.7** | 45-92 | 72.7 | 28.6 |
| `non_disparagement` | clause | presence | 3 | 60.0 | 100.0 | **75.0** | 0-100 | 75.0 | 18.2 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 60.0 | **75.0** | 0-100 | 75.0 | 30.0 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 61.5 | **76.2** | 50-92 | 76.2 | 30.0 |
| `termination_for_convenience` | clause | presence | 7 | 70.0 | 100.0 | **82.4** | 53-100 | 82.4 | 60.9 |
| `warranty_duration` | clause | presence | 6 | 83.3 | 83.3 | **83.3** | 50-100 | 83.3 | 55.6 |
| `non_transferable_license` | clause | presence | 8 | 72.7 | 100.0 | **84.2** | 57-100 | 84.2 | 50.0 |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 72.7 |
| `license_grant` | clause | presence | 14 | 77.8 | 100.0 | **87.5** | 72-97 | 87.5 | 52.6 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 17.6 |
| `document_name` | text | value | 30 | 90.0 | 90.0 | **90.0** | 80-100 | 100.0 |  |
| `parties` | entity_list | value | 68 | 92.4 | 89.7 | **91.0** | 86-97 | 100.0 |  |
| `governing_law` | jurisdiction | value | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 98.1 |  |
| `exclusivity` | clause | presence | 11 | 84.6 | 100.0 | **91.7** | 77-100 | 91.7 | 68.6 |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 100.0 |  |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 66.7 |
| `ip_ownership_assignment` | clause | presence | 9 | 90.0 | 100.0 | **94.7** | 80-100 | 94.7 | 46.7 |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 57.1 |
| `renewal_term` | duration | value | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 83.9 |  |
| `cap_on_liability` | clause | presence | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 97.7 | 48.7 |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 64.6 |
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
| `cap_on_liability` | 100.0 | 13 | 100.0 | 8 | +0.0 |
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
| `minimum_commitment` | 66.7 | 12 | 0.0 | 1 | +66.7 |
| `most_favored_nation` | 100.0 | 1 | — | 0 | — |
| `no_solicit_of_customers` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `no_solicit_of_employees` | 100.0 | 2 | 100.0 | 1 | +0.0 |
| `non_compete` | 50.0 | 4 | 100.0 | 2 | -50.0 |
| `non_disparagement` | 100.0 | 1 | 100.0 | 2 | +0.0 |
| `non_transferable_license` | 100.0 | 6 | 100.0 | 2 | +0.0 |
| `notice_period_to_terminate_renewal` | 100.0 | 5 | 100.0 | 4 | +0.0 |
| `post_termination_services` | 100.0 | 2 | 100.0 | 7 | +0.0 |
| `price_restrictions` | — | 0 | 100.0 | 1 | — |
| `renewal_term` | 100.0 | 11 | 100.0 | 2 | +0.0 |
| `revenue_profit_sharing` | 85.7 | 7 | 50.0 | 4 | +35.7 |
| `rofr_rofo_rofn` | 100.0 | 2 | 33.3 | 3 | +66.7 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 94.8 | 248 | 83.1 | 71 | +11.7 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 25/30 | 83.3 |
| quotes found in the contract | 528/528 | 100.0 |
| values with no grounded evidence | 0/451 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/100 | 0.0 |
| false positives, grounded (over-triggers) | 100/100 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 91.0 | +29.4 |
| text | 63.0 | 90.0 | +27.0 |
| date | 60.0 | 89.8 | +29.8 |
| duration | 81.1 | 97.7 | +16.6 |
| jurisdiction | 83.3 | 91.2 | +7.9 |
| clause | 53.5 | 77.2 | +23.7 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `third_party_beneficiary` | 50.0 | 25.0 | -25.0 |
| `rofr_rofo_rofn` | 88.9 | 75.0 | -13.9 |
| `non_disparagement` | 85.7 | 75.0 | -10.7 |
| `change_of_control` | 70.6 | 60.9 | -9.7 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `warranty_duration` | 34.3 | 83.3 | +49.0 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `effective_date` | 40.0 | 100.0 | +60.0 |
| `expiration_date` | 10.0 | 72.7 | +62.7 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
