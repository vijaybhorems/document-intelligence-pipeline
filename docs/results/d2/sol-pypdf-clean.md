# Eval report: `20261021-034310-llm-gpt-5.6-sol-single-v4-pypdf-clean-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-sol-single-v4-pypdf-clean | experiment | 30/30 | `d58915e` | 2026-10-21 03:43 | $0.1597 | 25.2s / 38.3s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 95.5 | 92.6 | **94.0** | 90-98 | 94.0 | 90-98 |
| text | 1 | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 86.7 | 73-97 |
| date | 3 | 66 | 93.7 | 89.4 | **91.5** | 87-95 | 89.4 | 82-95 |
| duration | 2 | 21 | 91.3 | 100.0 | **95.5** | 87-100 | 95.2 | 85-100 |
| jurisdiction | 1 | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 92.9 | 87-98 |
| clause | 33 | 215 | 63.9 | 89.8 | **74.7** | 69-79 | 68.6 | 60-75 |
| all fields | 41 | 427 | 75.6 | 90.9 | **82.6** | 80-85 | 73.1 | 66-78 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 79 | 91.8 | 98.7 | **95.1** | 92-98 | 95.1 | 92-98 |
| duration | 2 | 22 | 78.6 | 100.0 | **88.0** | 74-96 | 89.3 | 78-97 |
| jurisdiction | 1 | 27 | 100.0 | 96.3 | **98.1** | 94-100 | 98.1 | 94-100 |
| clause | 33 | 215 | 63.9 | 89.8 | **74.7** | 69-79 | 68.6 | 60-75 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 65.6 | 78.4 | **71.4** | 61-81 | 66.8 | 50-78 |
| ip_and_licensing | 10 | 51 | 71.4 | 88.2 | **78.9** | 72-85 | 64.3 | 53-77 |
| liability_and_risk | 5 | 39 | 56.7 | 97.4 | **71.7** | 62-79 | 69.3 | 57-77 |
| restrictive_covenants | 6 | 29 | 57.8 | 89.7 | **70.3** | 56-83 | 69.9 | 47-83 |
| term_and_termination | 4 | 45 | 66.7 | 97.8 | **79.3** | 72-85 | 80.3 | 69-88 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 7.1 | 100.0 | **13.3** | 0-38 | 13.3 | 10.0 |
| `third_party_beneficiary` | clause | presence | 2 | 14.3 | 100.0 | **25.0** | 0-53 | 25.0 | 22.2 |
| `volume_restriction` | clause | presence | 2 | 20.0 | 50.0 | **28.6** | 0-67 | 28.6 | 0.0 |
| `competitive_restriction_exception` | clause | presence | 4 | 28.6 | 100.0 | **44.4** | 13-71 | 44.4 | 21.4 |
| `uncapped_liability` | clause | presence | 6 | 30.0 | 100.0 | **46.2** | 20-69 | 46.2 | 31.6 |
| `affiliate_license_licensee` | clause | presence | 3 | 40.0 | 66.7 | **50.0** | 0-86 | 50.0 | 30.8 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 24.4 |
| `no_solicit_of_customers` | clause | presence | 2 | 40.0 | 100.0 | **57.1** | 0-100 | 57.1 | 30.8 |
| `non_disparagement` | clause | presence | 3 | 50.0 | 66.7 | **57.1** | 0-100 | 57.1 | 20.0 |
| `joint_ip_ownership` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 36.4 |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 53.8 | **70.0** | 43-90 | 70.0 | 43.9 |
| `expiration_date` | date | value | 19 | 80.0 | 63.2 | **70.6** | 48-86 | 92.6 |  |
| `non_compete` | clause | presence | 6 | 80.0 | 66.7 | **72.7** | 29-100 | 72.7 | 50.0 |
| `non_transferable_license` | clause | presence | 8 | 61.5 | 100.0 | **76.2** | 47-92 | 76.2 | 51.6 |
| `covenant_not_to_sue` | clause | presence | 7 | 83.3 | 71.4 | **76.9** | 40-100 | 76.9 | 63.2 |
| `change_of_control` | clause | presence | 8 | 70.0 | 87.5 | **77.8** | 50-94 | 77.8 | 38.7 |
| `revenue_profit_sharing` | clause | presence | 11 | 81.8 | 81.8 | **81.8** | 57-96 | 81.8 | 43.2 |
| `ip_ownership_assignment` | clause | presence | 9 | 75.0 | 100.0 | **85.7** | 63-100 | 85.7 | 53.7 |
| `document_name` | text | value | 30 | 86.7 | 86.7 | **86.7** | 73-97 | 100.0 |  |
| `license_grant` | clause | presence | 14 | 77.8 | 100.0 | **87.5** | 73-97 | 87.5 | 61.5 |
| `exclusivity` | clause | presence | 11 | 78.6 | 100.0 | **88.0** | 71-100 | 88.0 | 76.9 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 32.4 |
| `liquidated_damages` | clause | presence | 4 | 80.0 | 100.0 | **88.9** | 57-100 | 88.9 | 61.5 |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 52.2 |
| `warranty_duration` | clause | presence | 6 | 100.0 | 83.3 | **90.9** | 60-100 | 90.9 | 80.0 |
| `governing_law` | jurisdiction | value | 27 | 89.7 | 96.3 | **92.9** | 87-98 | 98.1 |  |
| `termination_for_convenience` | clause | presence | 7 | 87.5 | 100.0 | **93.3** | 73-100 | 93.3 | 57.1 |
| `parties` | entity_list | value | 68 | 95.5 | 92.6 | **94.0** | 90-98 | 100.0 |  |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 94.7 |  |
| `cap_on_liability` | clause | presence | 21 | 91.3 | 100.0 | **95.5** | 88-100 | 95.5 | 73.1 |
| `audit_rights` | clause | presence | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 96.3 | 63.8 |
| `renewal_term` | duration | value | 13 | 92.9 | 100.0 | **96.3** | 87-100 | 83.9 |  |
| `effective_date` | date | value | 21 | 95.5 | 100.0 | **97.7** | 91-100 | 94.5 |  |
| `agreement_date` | date | value | 26 | 100.0 | 100.0 | **100.0** | 100-100 | 98.2 |  |
| `anti_assignment` | clause | presence | 21 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 71.4 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 76.9 |
| `no_solicit_of_employees` | clause | presence | 3 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 44.4 |
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
| `expiration_date` | 100.0 | 18 | 87.5 | 8 | +12.5 |
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
| `non_disparagement` | 100.0 | 1 | 50.0 | 2 | +50.0 |
| `non_transferable_license` | 100.0 | 6 | 100.0 | 2 | +0.0 |
| `notice_period_to_terminate_renewal` | 100.0 | 5 | 100.0 | 4 | +0.0 |
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
| `volume_restriction` | 100.0 | 1 | 0.0 | 1 | +100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 95.6 | 248 | 83.1 | 71 | +12.5 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 25/30 | 83.3 |
| quotes found in the contract | 681/683 | 99.7 |
| values with no grounded evidence | 1/476 | 0.2 |
| false positives, ungrounded (**hallucinated**) | 0/122 | 0.0 |
| false positives, grounded (over-triggers) | 122/122 |  |
| correct fields whose quote wasn't found | 1 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 94.0 | +32.4 |
| text | 63.0 | 86.7 | +23.7 |
| date | 60.0 | 91.5 | +31.5 |
| duration | 81.1 | 95.5 | +14.4 |
| jurisdiction | 83.3 | 92.9 | +9.5 |
| clause | 53.5 | 74.7 | +21.2 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `non_disparagement` | 85.7 | 57.1 | -28.6 |
| `third_party_beneficiary` | 50.0 | 25.0 | -25.0 |
| `non_transferable_license` | 85.7 | 76.2 | -9.5 |
| `covenant_not_to_sue` | 85.7 | 76.9 | -8.8 |
| `minimum_commitment` | 78.8 | 70.0 | -8.8 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `warranty_duration` | 34.3 | 90.9 | +56.6 |
| `effective_date` | 40.0 | 97.7 | +57.7 |
| `expiration_date` | 10.0 | 70.6 | +60.6 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
