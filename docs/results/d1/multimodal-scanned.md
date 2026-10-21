# Eval report: `20261021-031118-llm-gpt-5.6-luna-single-v4-multimodal-scanned-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-multimodal-scanned | experiment | 30/30 | `c7c64ff` | 2026-10-21 03:11 | $0.0153 | 18.7s / 25.1s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 93.8 | 89.7 | **91.7** | 86-97 | 91.7 | 86-97 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 90.2 | 83.3 | **86.6** | 79-92 | 83.2 | 74-91 |
| duration | 2 | 21 | 76.9 | 95.2 | **85.1** | 73-95 | 85.0 | 71-94 |
| jurisdiction | 1 | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 92.9 | 87-98 |
| clause | 33 | 215 | 68.8 | 90.2 | **78.1** | 73-82 | 70.5 | 62-76 |
| all fields | 41 | 427 | 77.5 | 89.5 | **83.0** | 80-86 | 73.6 | 67-78 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 91.5 | 94.9 | **93.2** | 89-96 | 93.0 | 88-96 |
| duration | 2 | 22 | 71.0 | 100.0 | **83.0** | 65-93 | 83.5 | 66-93 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 68.8 | 90.2 | **78.1** | 73-82 | 70.5 | 62-76 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 71.7 | 84.3 | **77.5** | 69-84 | 70.3 | 58-75 |
| ip_and_licensing | 10 | 51 | 71.4 | 88.2 | **78.9** | 73-84 | 64.3 | 52-76 |
| liability_and_risk | 5 | 39 | 74.5 | 89.7 | **81.4** | 70-90 | 72.2 | 50-87 |
| restrictive_covenants | 6 | 29 | 60.0 | 93.1 | **73.0** | 60-84 | 73.5 | 54-84 |
| term_and_termination | 4 | 45 | 65.7 | 97.8 | **78.6** | 71-85 | 79.8 | 69-87 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `volume_restriction` | clause | presence | 2 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 10.0 | 100.0 | **18.2** | 0-50 | 18.2 | 16.7 |
| `third_party_beneficiary` | clause | presence | 2 | 33.3 | 50.0 | **40.0** | 0-100 | 40.0 | 50.0 |
| `no_solicit_of_customers` | clause | presence | 2 | 33.3 | 100.0 | **50.0** | 0-86 | 50.0 | 15.4 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 19.4 |
| `competitive_restriction_exception` | clause | presence | 4 | 40.0 | 100.0 | **57.1** | 22-84 | 57.1 | 10.0 |
| `joint_ip_ownership` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 33.3 |
| `expiration_date` | date | value | 19 | 75.0 | 47.4 | **58.1** | 33-76 | 88.0 |  |
| `uncapped_liability` | clause | presence | 6 | 46.2 | 100.0 | **63.2** | 33-85 | 63.2 | 41.7 |
| `affiliate_license_licensee` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 50.0 |
| `non_compete` | clause | presence | 6 | 66.7 | 66.7 | **66.7** | 25-92 | 66.7 | 32.0 |
| `warranty_duration` | clause | presence | 6 | 71.4 | 83.3 | **76.9** | 40-100 | 76.9 | 52.6 |
| `covenant_not_to_sue` | clause | presence | 7 | 75.0 | 85.7 | **80.0** | 50-100 | 80.0 | 50.0 |
| `non_transferable_license` | clause | presence | 8 | 66.7 | 100.0 | **80.0** | 50-96 | 80.0 | 40.0 |
| `exclusivity` | clause | presence | 11 | 68.8 | 100.0 | **81.5** | 63-96 | 81.5 | 48.6 |
| `revenue_profit_sharing` | clause | presence | 11 | 76.9 | 90.9 | **83.3** | 64-97 | 83.3 | 28.6 |
| `change_of_control` | clause | presence | 8 | 72.7 | 100.0 | **84.2** | 62-100 | 84.2 | 48.3 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 72.7 | 100.0 | **84.2** | 59-100 | 85.7 |  |
| `ip_ownership_assignment` | clause | presence | 9 | 75.0 | 100.0 | **85.7** | 63-100 | 85.7 | 25.8 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 54.5 |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 75.0 | **85.7** | 0-100 | 85.7 | 60.0 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 40.0 |
| `renewal_term` | duration | value | 13 | 80.0 | 92.3 | **85.7** | 69-100 | 81.2 |  |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 76.9 | **87.0** | 67-100 | 87.0 | 36.4 |
| `license_grant` | clause | presence | 14 | 77.8 | 100.0 | **87.5** | 73-97 | 87.5 | 42.9 |
| `termination_for_convenience` | clause | presence | 7 | 77.8 | 100.0 | **87.5** | 60-100 | 87.5 | 60.9 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 17.6 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 27.3 |
| `parties` | entity_list | value | 68 | 93.8 | 89.7 | **91.7** | 86-97 | 100.0 |  |
| `governing_law` | jurisdiction | value | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 98.1 |  |
| `cap_on_liability` | clause | presence | 21 | 95.2 | 95.2 | **95.2** | 86-100 | 95.2 | 53.8 |
| `effective_date` | date | value | 21 | 91.3 | 100.0 | **95.5** | 87-100 | 92.9 |  |
| `agreement_date` | date | value | 26 | 96.2 | 96.2 | **96.2** | 87-100 | 98.2 |  |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 51.2 |
| `anti_assignment` | clause | presence | 21 | 100.0 | 95.2 | **97.6** | 91-100 | 97.6 | 61.5 |
| `most_favored_nation` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 60.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 66.7 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 0.0 | 1 | — | 0 | — |
| `anti_assignment` | 95.2 | 21 | — | 0 | — |
| `audit_rights` | 100.0 | 12 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 13 | 87.5 | 8 | +12.5 |
| `change_of_control` | 100.0 | 5 | 100.0 | 3 | +0.0 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 94.4 | 18 | 62.5 | 8 | +31.9 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 75.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 0.0 | 1 | +100.0 |
| `minimum_commitment` | 75.0 | 12 | 100.0 | 1 | -25.0 |
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
| `revenue_profit_sharing` | 100.0 | 7 | 75.0 | 4 | +25.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 66.7 | 3 | +33.3 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 0.0 | 1 | +0.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 94.8 | 248 | 83.1 | 71 | +11.7 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 30/30 | 100.0 |
| quotes found in the contract | 539/545 | 98.9 |
| values with no grounded evidence | 5/457 | 1.1 |
| false positives, ungrounded (**hallucinated**) | 2/104 | 1.9 |
| false positives, grounded (over-triggers) | 102/104 |  |
| correct fields whose quote wasn't found | 3 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 91.7 | +30.1 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 86.6 | +26.6 |
| duration | 81.1 | 85.1 | +4.0 |
| jurisdiction | 83.3 | 92.9 | +9.5 |
| clause | 53.5 | 78.1 | +24.6 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `volume_restriction` | 17.4 | 0.0 | -17.4 |
| `third_party_beneficiary` | 50.0 | 40.0 | -10.0 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `covenant_not_to_sue` | 85.7 | 80.0 | -5.7 |
| `non_transferable_license` | 85.7 | 80.0 | -5.7 |
| `affiliate_license_licensee` | 24.0 | 66.7 | +42.7 |
| `no_solicit_of_employees` | 54.5 | 100.0 | +45.5 |
| `expiration_date` | 10.0 | 58.1 | +48.1 |
| `effective_date` | 40.0 | 95.5 | +55.5 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
