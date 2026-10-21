# Eval report: `20261020-225806-llm-gpt-5.6-luna-single-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single | experiment | 30/30 | `96b1a5f` | 2026-10-20 22:58 | $0.0060 | 14.2s / 21.3s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 92.4 | 89.7 | **91.0** | 85-96 | 91.0 | 85-96 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 91.8 | 84.8 | **88.2** | 83-93 | 86.8 | 80-92 |
| duration | 2 | 21 | 91.3 | 100.0 | **95.5** | 87-100 | 95.2 | 85-100 |
| jurisdiction | 1 | 27 | 81.2 | 96.3 | **88.1** | 81-95 | 88.1 | 81-95 |
| clause | 33 | 215 | 68.2 | 88.8 | **77.2** | 73-81 | 70.6 | 62-75 |
| all fields | 41 | 427 | 77.4 | 89.2 | **82.9** | 80-85 | 74.3 | 68-77 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 92.9 | 98.7 | **95.7** | 93-98 | 95.7 | 92-98 |
| duration | 2 | 22 | 78.6 | 100.0 | **88.0** | 74-96 | 89.3 | 78-97 |
| jurisdiction | 1 | 27 | 96.3 | 96.3 | **96.3** | 90-100 | 96.3 | 90-100 |
| clause | 33 | 215 | 68.2 | 88.8 | **77.2** | 73-81 | 70.6 | 62-75 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 65.5 | 74.5 | **69.7** | 61-77 | 63.7 | 47-71 |
| ip_and_licensing | 10 | 51 | 78.0 | 90.2 | **83.6** | 76-89 | 69.5 | 57-82 |
| liability_and_risk | 5 | 39 | 70.0 | 89.7 | **78.7** | 67-87 | 71.4 | 59-82 |
| restrictive_covenants | 6 | 29 | 67.5 | 93.1 | **78.3** | 68-87 | 77.5 | 58-88 |
| term_and_termination | 4 | 45 | 61.6 | 100.0 | **76.3** | 67-83 | 76.0 | 65-83 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 10.0 | 100.0 | **18.2** | 0-50 | 18.2 | 16.7 |
| `third_party_beneficiary` | clause | presence | 2 | 16.7 | 50.0 | **25.0** | 0-67 | 25.0 | 20.0 |
| `volume_restriction` | clause | presence | 2 | 16.7 | 50.0 | **25.0** | 0-62 | 25.0 | 0.0 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 14.7 |
| `uncapped_liability` | clause | presence | 6 | 41.7 | 83.3 | **55.6** | 25-80 | 55.6 | 56.0 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 30.8 |
| `competitive_restriction_exception` | clause | presence | 4 | 44.4 | 100.0 | **61.5** | 25-89 | 61.5 | 19.0 |
| `affiliate_license_licensee` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 50.0 |
| `change_of_control` | clause | presence | 8 | 50.0 | 100.0 | **66.7** | 40-86 | 66.7 | 38.9 |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `revenue_profit_sharing` | clause | presence | 11 | 66.7 | 72.7 | **69.6** | 42-88 | 69.6 | 29.4 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 53.8 | **70.0** | 40-90 | 70.0 | 40.0 |
| `non_compete` | clause | presence | 6 | 80.0 | 66.7 | **72.7** | 25-100 | 72.7 | 40.0 |
| `expiration_date` | date | value | 19 | 92.3 | 63.2 | **75.0** | 53-89 | 98.1 |  |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 60.0 | **75.0** | 0-100 | 75.0 | 38.1 |
| `joint_ip_ownership` | clause | presence | 3 | 100.0 | 66.7 | **80.0** | 0-100 | 80.0 | 40.0 |
| `ip_ownership_assignment` | clause | presence | 9 | 69.2 | 100.0 | **81.8** | 59-96 | 81.8 | 50.0 |
| `warranty_duration` | clause | presence | 6 | 83.3 | 83.3 | **83.3** | 50-100 | 83.3 | 55.6 |
| `non_transferable_license` | clause | presence | 8 | 72.7 | 100.0 | **84.2** | 57-100 | 84.2 | 40.0 |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 0.0 |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `termination_for_convenience` | clause | presence | 7 | 77.8 | 100.0 | **87.5** | 60-100 | 87.5 | 60.9 |
| `exclusivity` | clause | presence | 11 | 78.6 | 100.0 | **88.0** | 71-100 | 88.0 | 68.6 |
| `governing_law` | jurisdiction | value | 27 | 81.2 | 96.3 | **88.1** | 81-95 | 96.3 |  |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 17.6 |
| `license_grant` | clause | presence | 14 | 82.4 | 100.0 | **90.3** | 76-100 | 90.3 | 52.6 |
| `parties` | entity_list | value | 68 | 92.4 | 89.7 | **91.0** | 85-96 | 100.0 |  |
| `agreement_date` | date | value | 26 | 92.3 | 92.3 | **92.3** | 80-100 | 98.2 |  |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 85.7 | **92.3** | 67-100 | 92.3 | 66.7 |
| `cap_on_liability` | clause | presence | 21 | 90.9 | 95.2 | **93.0** | 83-100 | 93.0 | 49.4 |
| `effective_date` | date | value | 21 | 90.9 | 95.2 | **93.0** | 83-100 | 90.9 |  |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 94.7 |  |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 59.1 |
| `renewal_term` | duration | value | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 83.9 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 66.7 |
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
| `cap_on_liability` | 100.0 | 13 | 87.5 | 8 | +12.5 |
| `change_of_control` | 100.0 | 5 | 100.0 | 3 | +0.0 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 6 | 0.0 | 1 | +100.0 |
| `document_name` | 100.0 | 30 | — | 0 | — |
| `exclusivity` | 100.0 | 11 | — | 0 | — |
| `expiration_date` | 100.0 | 18 | 100.0 | 8 | +0.0 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 100.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 100.0 | 3 | 100.0 | 1 | +0.0 |
| `minimum_commitment` | 58.3 | 12 | 0.0 | 1 | +58.3 |
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
| `revenue_profit_sharing` | 100.0 | 7 | 25.0 | 4 | +75.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 33.3 | 3 | +66.7 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 50.0 | 2 | — | 0 | — |
| `uncapped_liability` | 80.0 | 5 | 100.0 | 1 | -20.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 94.8 | 248 | 84.5 | 71 | +10.3 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 29/30 | 96.7 |
| quotes found in the contract | 557/557 | 100.0 |
| values with no grounded evidence | 0/451 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/102 | 0.0 |
| false positives, grounded (over-triggers) | 102/102 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 91.0 | +29.4 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 88.2 | +28.2 |
| duration | 81.1 | 95.5 | +14.4 |
| jurisdiction | 83.3 | 88.1 | +4.8 |
| clause | 53.5 | 77.2 | +23.7 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `third_party_beneficiary` | 50.0 | 25.0 | -25.0 |
| `rofr_rofo_rofn` | 88.9 | 75.0 | -13.9 |
| `minimum_commitment` | 78.8 | 70.0 | -8.8 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `change_of_control` | 70.6 | 66.7 | -3.9 |
| `joint_ip_ownership` | 28.6 | 80.0 | +51.4 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `effective_date` | 40.0 | 93.0 | +53.0 |
| `expiration_date` | 10.0 | 75.0 | +65.0 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
