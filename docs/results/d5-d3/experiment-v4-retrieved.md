# Eval report: `20261020-231605-llm-gpt-5.6-luna-single-v4-retrieved-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-retrieved | experiment | 30/30 | `8cb756f` | 2026-10-20 23:16 | $0.0053 | 15.9s / 21.8s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | 86.4 | 83.8 | **85.1** | 76-92 | 85.1 | 76-92 |
| text | 1 | 30 | 80.8 | 70.0 | **75.0** | 59-89 | 75.0 | 59-89 |
| date | 3 | 66 | 92.6 | 75.8 | **83.3** | 73-91 | 83.2 | 72-91 |
| duration | 2 | 21 | 87.5 | 100.0 | **93.3** | 83-100 | 93.5 | 82-100 |
| jurisdiction | 1 | 27 | 83.3 | 92.6 | **87.7** | 80-95 | 87.7 | 80-95 |
| clause | 33 | 215 | 70.3 | 83.7 | **76.4** | 72-81 | 68.9 | 61-75 |
| all fields | 41 | 427 | 77.6 | 82.9 | **80.2** | 77-83 | 72.2 | 67-77 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 30 | 100.0 | 86.7 | **92.9** | 85-98 | 92.9 | 85-98 |
| date | 3 | 79 | 92.2 | 89.9 | **91.0** | 86-95 | 90.9 | 85-95 |
| duration | 2 | 22 | 75.9 | 100.0 | **86.3** | 72-95 | 88.0 | 76-95 |
| jurisdiction | 1 | 27 | 96.3 | 96.3 | **96.3** | 90-100 | 96.3 | 90-100 |
| clause | 33 | 215 | 70.3 | 83.7 | **76.4** | 72-81 | 68.9 | 61-75 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | 71.4 | 68.6 | **70.0** | 59-79 | 64.7 | 49-72 |
| ip_and_licensing | 10 | 51 | 78.2 | 84.3 | **81.1** | 74-87 | 67.1 | 55-87 |
| liability_and_risk | 5 | 39 | 74.4 | 82.1 | **78.0** | 65-89 | 61.9 | 44-74 |
| restrictive_covenants | 6 | 29 | 74.3 | 89.7 | **81.2** | 68-90 | 81.0 | 59-91 |
| term_and_termination | 4 | 45 | 59.5 | 97.8 | **73.9** | 66-81 | 72.7 | 63-80 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensor` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `third_party_beneficiary` | clause | presence | 2 | 0.0 | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | 11.1 | 100.0 | **20.0** | 0-55 | 20.0 | 20.0 |
| `volume_restriction` | clause | presence | 2 | 33.3 | 50.0 | **40.0** | 0-95 | 40.0 | 0.0 |
| `post_termination_services` | clause | presence | 9 | 33.3 | 100.0 | **50.0** | 28-68 | 50.0 | 23.3 |
| `change_of_control` | clause | presence | 8 | 46.7 | 87.5 | **60.9** | 32-81 | 60.9 | 37.5 |
| `minimum_commitment` | clause | presence | 13 | 100.0 | 46.2 | **63.2** | 29-86 | 63.2 | 26.3 |
| `affiliate_license_licensee` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 50.0 |
| `competitive_restriction_exception` | clause | presence | 4 | 50.0 | 100.0 | **66.7** | 25-91 | 66.7 | 28.6 |
| `liquidated_damages` | clause | presence | 4 | 100.0 | 50.0 | **66.7** | 0-100 | 66.7 | 60.0 |
| `most_favored_nation` | clause | presence | 1 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 66.7 |
| `no_solicit_of_customers` | clause | presence | 2 | 50.0 | 100.0 | **66.7** | 0-100 | 66.7 | 36.4 |
| `uncapped_liability` | clause | presence | 6 | 50.0 | 100.0 | **66.7** | 38-89 | 66.7 | 53.8 |
| `non_transferable_license` | clause | presence | 8 | 63.6 | 87.5 | **73.7** | 43-92 | 73.7 | 50.0 |
| `document_name` | text | value | 30 | 80.8 | 70.0 | **75.0** | 59-89 | 92.9 |  |
| `rofr_rofo_rofn` | clause | presence | 5 | 100.0 | 60.0 | **75.0** | 0-100 | 75.0 | 28.6 |
| `revenue_profit_sharing` | clause | presence | 11 | 80.0 | 72.7 | **76.2** | 50-92 | 76.2 | 27.0 |
| `agreement_date` | date | value | 26 | 90.0 | 69.2 | **78.3** | 62-91 | 85.7 |  |
| `expiration_date` | date | value | 19 | 92.9 | 68.4 | **78.8** | 60-91 | 96.2 |  |
| `ip_ownership_assignment` | clause | presence | 9 | 72.7 | 88.9 | **80.0** | 55-96 | 80.0 | 38.7 |
| `joint_ip_ownership` | clause | presence | 3 | 100.0 | 66.7 | **80.0** | 0-100 | 80.0 | 40.0 |
| `non_compete` | clause | presence | 6 | 100.0 | 66.7 | **80.0** | 33-100 | 80.0 | 43.5 |
| `termination_for_convenience` | clause | presence | 7 | 70.0 | 100.0 | **82.4** | 53-100 | 82.4 | 58.3 |
| `covenant_not_to_sue` | clause | presence | 7 | 100.0 | 71.4 | **83.3** | 50-100 | 83.3 | 58.8 |
| `warranty_duration` | clause | presence | 6 | 83.3 | 83.3 | **83.3** | 50-100 | 83.3 | 44.4 |
| `parties` | entity_list | value | 68 | 86.4 | 83.8 | **85.1** | 76-92 | 100.0 |  |
| `non_disparagement` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 20.0 |
| `exclusivity` | clause | presence | 11 | 83.3 | 90.9 | **87.0** | 67-100 | 87.0 | 68.8 |
| `license_grant` | clause | presence | 14 | 77.8 | 100.0 | **87.5** | 72-97 | 87.5 | 48.3 |
| `governing_law` | jurisdiction | value | 27 | 83.3 | 92.6 | **87.7** | 80-95 | 96.3 |  |
| `audit_rights` | clause | presence | 13 | 91.7 | 84.6 | **88.0** | 71-100 | 88.0 | 55.8 |
| `insurance` | clause | presence | 5 | 100.0 | 80.0 | **88.9** | 50-100 | 88.9 | 17.6 |
| `cap_on_liability` | clause | presence | 21 | 95.0 | 90.5 | **92.7** | 82-100 | 92.7 | 42.7 |
| `effective_date` | date | value | 21 | 95.0 | 90.5 | **92.7** | 83-100 | 90.9 |  |
| `renewal_term` | duration | value | 13 | 86.7 | 100.0 | **92.9** | 80-100 | 81.2 |  |
| `notice_period_to_terminate_renewal` | duration | value | 8 | 88.9 | 100.0 | **94.1** | 77-100 | 94.7 |  |
| `anti_assignment` | clause | presence | 21 | 95.5 | 100.0 | **97.7** | 92-100 | 97.7 | 64.6 |
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
| `audit_rights` | 91.7 | 12 | 0.0 | 1 | +91.7 |
| `cap_on_liability` | 100.0 | 13 | 75.0 | 8 | +25.0 |
| `change_of_control` | 100.0 | 5 | 66.7 | 3 | +33.3 |
| `competitive_restriction_exception` | 100.0 | 2 | 100.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 83.3 | 6 | 0.0 | 1 | +83.3 |
| `document_name` | 86.7 | 30 | — | 0 | — |
| `exclusivity` | 90.9 | 11 | — | 0 | — |
| `expiration_date` | 94.4 | 18 | 100.0 | 8 | -5.6 |
| `governing_law` | 100.0 | 26 | — | 0 | — |
| `insurance` | 80.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 3 | 83.3 | 6 | +16.7 |
| `irrevocable_or_perpetual_license` | 100.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 100.0 | 2 | 0.0 | 1 | +100.0 |
| `license_grant` | 100.0 | 12 | 100.0 | 2 | +0.0 |
| `liquidated_damages` | 66.7 | 3 | 0.0 | 1 | +66.7 |
| `minimum_commitment` | 50.0 | 12 | 0.0 | 1 | +50.0 |
| `most_favored_nation` | 100.0 | 1 | — | 0 | — |
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
| `rofr_rofo_rofn` | 100.0 | 2 | 33.3 | 3 | +66.7 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 100.0 | 3 | 100.0 | 4 | +0.0 |
| `third_party_beneficiary` | 0.0 | 2 | — | 0 | — |
| `uncapped_liability` | 100.0 | 5 | 100.0 | 1 | +0.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 100.0 | 1 | -100.0 |
| `warranty_duration` | 100.0 | 5 | 0.0 | 1 | +100.0 |
| **all** | 90.7 | 248 | 76.1 | 71 | +14.7 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 29/30 | 96.7 |
| quotes found in the contract | 522/524 | 99.6 |
| values with no grounded evidence | 2/416 | 0.5 |
| false positives, ungrounded (**hallucinated**) | 0/90 | 0.0 |
| false positives, grounded (over-triggers) | 90/90 |  |
| correct fields whose quote wasn't found | 2 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 85.1 | +23.4 |
| text | 63.0 | 75.0 | +12.0 |
| date | 60.0 | 83.3 | +23.3 |
| duration | 81.1 | 93.3 | +12.3 |
| jurisdiction | 83.3 | 87.7 | +4.4 |
| clause | 53.5 | 76.4 | +22.9 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `third_party_beneficiary` | 50.0 | 0.0 | -50.0 |
| `minimum_commitment` | 78.8 | 63.2 | -15.6 |
| `rofr_rofo_rofn` | 88.9 | 75.0 | -13.9 |
| `agreement_date` | 92.0 | 78.3 | -13.7 |
| `non_transferable_license` | 85.7 | 73.7 | -12.0 |
| `joint_ip_ownership` | 28.6 | 80.0 | +51.4 |
| `effective_date` | 40.0 | 92.7 | +52.7 |
| `irrevocable_or_perpetual_license` | 47.1 | 100.0 | +52.9 |
| `expiration_date` | 10.0 | 78.8 | +68.8 |
| `unlimited_all_you_can_eat_license` | 28.6 | 100.0 | +71.4 |
