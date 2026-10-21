# Eval report: `20261021-034055-llm-gpt-5.6-terra-single-v4-pypdf-clean-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-terra-single-v4-pypdf-clean | experiment | 30/30 | `d58915e` | 2026-10-21 03:40 | $0.0819 | 15.7s / 24.2s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 90.9 | 88.2 | **89.6** | 84-95 | 89.6 | 84-95 |
| text | 1 | 30 | 83.3 | 83.3 | **83.3** | 70-97 | 83.3 | 70-97 |
| date | 3 | 66 | 98.2 | 84.8 | **91.1** | 87-95 | 87.4 | 79-93 |
| duration | 2 | 21 | 95.2 | 95.2 | **95.2** | 88-100 | 96.2 | 90-100 |
| jurisdiction | 1 | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 91.2 | 85-98 |
| clause | 33 | 215 | 67.5 | 88.8 | **76.7** | 72-81 | 70.3 | 62-75 |
| all fields | 41 | 427 | 77.6 | 88.5 | **82.7** | 80-85 | 74.1 | 68-78 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 95.0 | 96.2 | **95.6** | 92-99 | 95.5 | 92-99 |
| duration | 2 | 22 | 80.8 | 95.5 | **87.5** | 74-96 | 89.0 | 77-96 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 67.5 | 88.8 | **76.7** | 72-81 | 70.3 | 62-75 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 71.7 | 74.5 | **73.1** | 63-81 | 66.0 | 51-73 |
| ip_and_licensing | 10 | 51 | 72.1 | 86.3 | **78.6** | 70-86 | 65.2 | 53-78 |
| liability_and_risk | 5 | 39 | 62.3 | 97.4 | **76.0** | 67-85 | 71.9 | 62-79 |
| restrictive_covenants | 6 | 29 | 65.9 | 93.1 | **77.1** | 65-87 | 76.4 | 53-88 |
| term_and_termination | 4 | 45 | 65.7 | 97.8 | **78.6** | 71-85 | 80.0 | 70-87 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 14.3 | 100.0 | **25.0** | 0-63 | 25.0 | 25.0 |
| `third_party_beneficiary` | clause | presence | 2 | 14.3 | 100.0 | **25.0** | 0-53 | 25.0 | 18.2 |
| `volume_restriction` | clause | presence | 2 | 20.0 | 50.0 | **28.6** | 0-67 | 28.6 | 0.0 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 28.2 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 38.5 | **55.6** | 24-80 | 55.6 | 26.3 |
| `affiliate_license_licensee` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 36.4 |
| `competitive_restriction_exception` | clause | presence | 4 | 40.0 | 100.0 | **57.1** | 20-82 | 57.1 | 25.0 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 42.9 |
| `uncapped_liability` | clause | presence | 6 | 42.9 | 100.0 | **60.0** | 32-82 | 60.0 | 42.9 |
| `expiration_date` | date | value | 19 | 90.0 | 47.4 | **62.1** | 37-79 | 92.0 |  |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 0.0 |
| `non_compete` | clause | presence | 6 | 66.7 | 66.7 | **66.7** | 22-92 | 66.7 | 41.7 |
| `change_of_control` | clause | presence | 8 | 58.3 | 87.5 | **70.0** | 40-89 | 70.0 | 43.8 |
| `covenant_not_to_sue` | clause | presence | 7 | 71.4 | 71.4 | **71.4** | 33-94 | 71.4 | 66.7 |
| `ip_ownership_assignment` | clause | presence | 9 | 66.7 | 88.9 | **76.2** | 50-93 | 76.2 | 38.9 |
| `warranty_duration` | clause | presence | 6 | 71.4 | 83.3 | **76.9** | 40-100 | 76.9 | 60.0 |
| `joint_ip_ownership` | clause | presence | 3 | 100.0 | 66.7 | **80.0** | 0-100 | 80.0 | 40.0 |
| `non_transferable_license` | clause | presence | 8 | 66.7 | 100.0 | **80.0** | 50-96 | 80.0 | 44.4 |
| `revenue_profit_sharing` | clause | presence | 11 | 81.8 | 81.8 | **81.8** | 57-96 | 81.8 | 44.4 |
| `document_name` | text | value | 30 | 83.3 | 83.3 | **83.3** | 70-97 | 100.0 |  |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 20.0 |
| `license_grant` | clause | presence | 14 | 77.8 | 100.0 | **87.5** | 73-97 | 87.5 | 55.2 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 22.9 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 28.6 |
| `parties` | entity_list | value | 68 | 90.9 | 88.2 | **89.6** | 84-95 | 100.0 |  |
| `governing_law` | jurisdiction | value | 27 | 86.7 | 96.3 | **91.2** | 85-98 | 98.1 |  |
| `exclusivity` | clause | presence | 11 | 84.6 | 100.0 | **91.7** | 77-100 | 91.7 | 74.3 |
| `renewal_term` | duration | value | 13 | 92.3 | 92.3 | **92.3** | 80-100 | 83.9 |  |
| `audit_rights` | clause | presence | 13 | 86.7 | 100.0 | **92.9** | 80-100 | 92.9 | 62.2 |
| `cap_on_liability` | clause | presence | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 97.7 | 58.2 |
| `agreement_date` | date | value | 26 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 68.7 |
| `effective_date` | date | value | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 94.5 |  |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 50.0 |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 50.0 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 44.4 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 100.0 | 100.0 | **100.0** | 100-100 | 94.1 |  |
| `termination_for_convenience` | clause | presence | 7 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 60.0 |
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
| `covenant_not_to_sue` | 83.3 | 6 | 0.0 | 1 | +83.3 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 62.5 | 8 | +37.5 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 83.3 | 6 | +16.7 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 100.0 | 1 | +0.0 |
| `minimum_commitment` | 41.7 | 12 | 0.0 | 1 | +41.7 |
| `most_favored_nation` | 100.0 | 1 | — | 0 | — |
| `no_solicit_of_customers` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `no_solicit_of_employees` | 100.0 | 2 | 100.0 | 1 | +0.0 |
| `non_compete` | 50.0 | 4 | 100.0 | 2 | -50.0 |
| `non_disparagement` | 100.0 | 1 | 100.0 | 2 | +0.0 |
| `non_transferable_license` | 100.0 | 6 | 100.0 | 2 | +0.0 |
| `notice_period_to_terminate_renewal` | 80.0 | 5 | 100.0 | 4 | -20.0 |
| `post_termination_services` | 100.0 | 2 | 100.0 | 7 | +0.0 |
| `price_restrictions` | — | 0 | 100.0 | 1 | — |
| `renewal_term` | 100.0 | 11 | 100.0 | 2 | +0.0 |
| `revenue_profit_sharing` | 100.0 | 7 | 50.0 | 4 | +50.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 100.0 | 2 | — | 0 | — |
| `uncapped_liability` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 94.0 | 248 | 81.7 | 71 | +12.3 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 25/30 | 83.3 |
| quotes found in the contract | 578/580 | 99.7 |
| values with no grounded evidence | 2/448 | 0.4 |
| false positives, ungrounded (**hallucinated**) | 0/101 | 0.0 |
| false positives, grounded (over-triggers) | 101/101 |  |
| correct fields whose quote wasn't found | 2 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 89.6 | +27.9 |
| text | 63.0 | 83.3 | +20.4 |
| date | 60.0 | 91.1 | +31.1 |
| duration | 81.1 | 95.2 | +14.2 |
| jurisdiction | 83.3 | 91.2 | +7.9 |
| clause | 53.5 | 76.7 | +23.2 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `third_party_beneficiary` | 50.0 | 25.0 | -25.0 |
| `minimum_commitment` | 78.8 | 55.6 | -23.2 |
| `covenant_not_to_sue` | 85.7 | 71.4 | -14.3 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `non_transferable_license` | 85.7 | 80.0 | -5.7 |
| `joint_ip_ownership` | 28.6 | 80.0 | +51.4 |
| `expiration_date` | 10.0 | 62.1 | +52.1 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `effective_date` | 40.0 | 100.0 | +60.0 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
