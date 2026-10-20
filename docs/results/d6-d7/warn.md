# Eval report: `20261020-223601-llm-gpt-5.6-luna-single+validate-warn-dev`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single+validate-warn | dev | 80/80 | `7f3bd9e` | 2026-10-20 22:36 | $0.0048 | 12.8s / 16.8s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 217 | 86.3 | 90.3 | **88.3** | 79-94 | 88.3 | 79-94 |
| text | 1 | 80 | 85.0 | 85.0 | **85.0** | 76-92 | 85.0 | 76-92 |
| date | 3 | 180 | 87.2 | 83.3 | **85.2** | 81-89 | 84.0 | 79-88 |
| duration | 2 | 44 | 84.6 | 100.0 | **91.7** | 86-97 | 91.8 | 86-97 |
| jurisdiction | 1 | 71 | 90.9 | 98.6 | **94.6** | 91-98 | 94.6 | 91-98 |
| clause | 33 | 582 | 67.6 | 85.9 | **75.6** | 73-78 | 71.8 | 65-75 |
| all fields | 41 | 1174 | 76.3 | 87.6 | **81.5** | 80-84 | 75.0 | 70-78 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 80 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 80 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 206 | 92.7 | 98.1 | **95.3** | 93-97 | 95.3 | 93-97 |
| duration | 2 | 46 | 71.9 | 100.0 | **83.6** | 75-90 | 84.9 | 77-91 |
| jurisdiction | 1 | 70 | 100.0 | 98.6 | **99.3** | 98-100 | 99.3 | 98-100 |
| clause | 33 | 582 | 67.6 | 85.9 | **75.6** | 73-78 | 71.8 | 65-75 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 133 | 67.1 | 75.2 | **70.9** | 65-76 | 62.0 | 54-68 |
| ip_and_licensing | 10 | 132 | 75.7 | 87.1 | **81.0** | 76-85 | 76.3 | 62-84 |
| liability_and_risk | 5 | 96 | 60.3 | 79.2 | **68.5** | 59-75 | 64.3 | 53-72 |
| restrictive_covenants | 6 | 81 | 65.8 | 90.1 | **76.0** | 70-82 | 79.4 | 71-86 |
| term_and_termination | 4 | 140 | 67.3 | 97.1 | **79.5** | 75-84 | 78.4 | 73-83 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `price_restrictions` | clause | presence | 2 | 8.3 | 100.0 | **15.4** | 0-34 | 15.4 | 12.9 |
| `volume_restriction` | clause | presence | 11 | 13.3 | 18.2 | **15.4** | 0-34 | 15.4 | 0.0 |
| `third_party_beneficiary` | clause | presence | 5 | 28.6 | 80.0 | **42.1** | 13-67 | 42.1 | 43.5 |
| `most_favored_nation` | clause | presence | 4 | 40.0 | 50.0 | **44.4** | 0-80 | 44.4 | 54.5 |
| `competitive_restriction_exception` | clause | presence | 12 | 32.4 | 100.0 | **49.0** | 30-67 | 49.0 | 28.1 |
| `uncapped_liability` | clause | presence | 19 | 35.7 | 78.9 | **49.2** | 33-63 | 49.2 | 38.4 |
| `minimum_commitment` | clause | presence | 25 | 71.4 | 40.0 | **51.3** | 31-68 | 51.3 | 23.9 |
| `post_termination_services` | clause | presence | 29 | 40.8 | 100.0 | **58.0** | 46-69 | 58.0 | 18.0 |
| `affiliate_license_licensor` | clause | presence | 4 | 50.0 | 75.0 | **60.0** | 0-91 | 60.0 | 9.5 |
| `covenant_not_to_sue` | clause | presence | 16 | 88.9 | 50.0 | **64.0** | 37-84 | 64.0 | 43.2 |
| `warranty_duration` | clause | presence | 12 | 52.6 | 83.3 | **64.5** | 42-81 | 64.5 | 45.5 |
| `source_code_escrow` | clause | presence | 2 | 100.0 | 50.0 | **66.7** | 0-100 | 66.7 | 0.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 66.7 |
| `change_of_control` | clause | presence | 23 | 59.5 | 95.7 | **73.3** | 59-85 | 73.3 | 40.4 |
| `expiration_date` | date | value | 52 | 86.8 | 63.5 | **73.3** | 62-83 | 95.6 |  |
| `non_disparagement` | clause | presence | 6 | 71.4 | 83.3 | **76.9** | 43-100 | 76.9 | 20.0 |
| `non_transferable_license` | clause | presence | 22 | 64.7 | 100.0 | **78.6** | 64-90 | 78.6 | 40.0 |
| `ip_ownership_assignment` | clause | presence | 19 | 69.2 | 94.7 | **80.0** | 67-91 | 80.0 | 36.4 |
| `liquidated_damages` | clause | presence | 10 | 80.0 | 80.0 | **80.0** | 53-96 | 80.0 | 43.2 |
| `non_compete` | clause | presence | 19 | 80.0 | 84.2 | **82.1** | 68-94 | 82.1 | 52.3 |
| `joint_ip_ownership` | clause | presence | 7 | 100.0 | 71.4 | **83.3** | 50-100 | 83.3 | 32.0 |
| `no_solicit_of_customers` | clause | presence | 5 | 71.4 | 100.0 | **83.3** | 44-100 | 83.3 | 33.3 |
| `revenue_profit_sharing` | clause | presence | 26 | 84.6 | 84.6 | **84.6** | 72-94 | 84.6 | 35.6 |
| `termination_for_convenience` | clause | presence | 26 | 75.8 | 96.2 | **84.7** | 73-93 | 84.7 | 67.6 |
| `document_name` | text | value | 80 | 85.0 | 85.0 | **85.0** | 76-92 | 100.0 |  |
| `exclusivity` | clause | presence | 30 | 83.9 | 86.7 | **85.2** | 75-94 | 85.2 | 52.0 |
| `cap_on_liability` | clause | presence | 50 | 95.1 | 78.0 | **85.7** | 77-92 | 85.7 | 44.0 |
| `irrevocable_or_perpetual_license` | clause | presence | 11 | 83.3 | 90.9 | **87.0** | 67-100 | 87.0 | 50.0 |
| `parties` | entity_list | value | 217 | 86.3 | 90.3 | **88.3** | 79-94 | 100.0 |  |
| `license_grant` | clause | presence | 39 | 80.9 | 97.4 | **88.4** | 80-95 | 88.4 | 45.3 |
| `affiliate_license_licensee` | clause | presence | 9 | 88.9 | 88.9 | **88.9** | 67-100 | 88.9 | 40.0 |
| `effective_date` | date | value | 58 | 86.9 | 91.4 | **89.1** | 82-95 | 93.0 |  |
| `agreement_date` | date | value | 70 | 87.7 | 91.4 | **89.5** | 82-96 | 97.3 |  |
| `renewal_term` | duration | value | 26 | 83.9 | 100.0 | **91.2** | 83-98 | 79.4 |  |
| `rofr_rofo_rofn` | clause | presence | 13 | 100.0 | 84.6 | **91.7** | 76-100 | 91.7 | 15.4 |
| `notice_period_to_terminate_renewal` | duration | value | 18 | 85.7 | 100.0 | **92.3** | 82-100 | 90.5 |  |
| `governing_law` | jurisdiction | value | 71 | 90.9 | 98.6 | **94.6** | 91-98 | 99.3 |  |
| `audit_rights` | clause | presence | 29 | 90.6 | 100.0 | **95.1** | 88-100 | 95.1 | 48.3 |
| `anti_assignment` | clause | presence | 62 | 98.4 | 96.8 | **97.6** | 94-100 | 97.6 | 62.6 |
| `insurance` | clause | presence | 23 | 100.0 | 95.7 | **97.8** | 93-100 | 97.8 | 33.3 |
| `no_solicit_of_employees` | clause | presence | 9 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 81.8 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 87.5 | 8 | 100.0 | 1 | -12.5 |
| `affiliate_license_licensor` | 66.7 | 3 | 100.0 | 1 | -33.3 |
| `anti_assignment` | 98.3 | 60 | 50.0 | 2 | +48.3 |
| `audit_rights` | 100.0 | 28 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 96.0 | 25 | 60.0 | 25 | +36.0 |
| `change_of_control` | 100.0 | 13 | 90.0 | 10 | +10.0 |
| `competitive_restriction_exception` | 100.0 | 5 | 100.0 | 7 | +0.0 |
| `covenant_not_to_sue` | 72.7 | 11 | 0.0 | 5 | +72.7 |
| `document_name` | 100.0 | 79 | 100.0 | 1 | +0.0 |
| `exclusivity` | 85.2 | 27 | 100.0 | 3 | -14.8 |
| `expiration_date` | 97.7 | 44 | 91.7 | 24 | +6.1 |
| `governing_law` | 100.0 | 66 | 100.0 | 3 | +0.0 |
| `insurance` | 95.7 | 23 | — | 0 | — |
| `ip_ownership_assignment` | 87.5 | 8 | 100.0 | 11 | -12.5 |
| `irrevocable_or_perpetual_license` | 90.9 | 11 | — | 0 | — |
| `joint_ip_ownership` | 83.3 | 6 | 0.0 | 1 | +83.3 |
| `license_grant` | 100.0 | 33 | 83.3 | 6 | +16.7 |
| `liquidated_damages` | 85.7 | 7 | 66.7 | 3 | +19.0 |
| `minimum_commitment` | 52.6 | 19 | 0.0 | 6 | +52.6 |
| `most_favored_nation` | 100.0 | 2 | 0.0 | 2 | +100.0 |
| `no_solicit_of_customers` | 100.0 | 2 | 100.0 | 3 | +0.0 |
| `no_solicit_of_employees` | 100.0 | 7 | 100.0 | 2 | +0.0 |
| `non_compete` | 81.2 | 16 | 100.0 | 3 | -18.8 |
| `non_disparagement` | 100.0 | 3 | 66.7 | 3 | +33.3 |
| `non_transferable_license` | 100.0 | 14 | 100.0 | 8 | +0.0 |
| `notice_period_to_terminate_renewal` | 100.0 | 10 | 100.0 | 9 | +0.0 |
| `post_termination_services` | 100.0 | 9 | 100.0 | 20 | +0.0 |
| `price_restrictions` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `renewal_term` | 100.0 | 20 | 100.0 | 7 | +0.0 |
| `revenue_profit_sharing` | 90.0 | 20 | 66.7 | 6 | +23.3 |
| `rofr_rofo_rofn` | 100.0 | 2 | 81.8 | 11 | +18.2 |
| `source_code_escrow` | 100.0 | 1 | 0.0 | 1 | +100.0 |
| `termination_for_convenience` | 90.9 | 11 | 100.0 | 15 | -9.1 |
| `third_party_beneficiary` | 80.0 | 5 | — | 0 | — |
| `uncapped_liability` | 71.4 | 14 | 100.0 | 5 | -28.6 |
| `unlimited_all_you_can_eat_license` | 66.7 | 3 | — | 0 | — |
| `volume_restriction` | 0.0 | 7 | 50.0 | 4 | -50.0 |
| `warranty_duration` | 100.0 | 9 | 33.3 | 3 | +66.7 |
| **all** | 92.9 | 632 | 81.2 | 213 | +11.7 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 79/80 | 98.8 |
| quotes found in the contract | 1457/1459 | 99.9 |
| values with no grounded evidence | 1/1197 | 0.1 |
| false positives, ungrounded (**hallucinated**) | 0/274 | 0.0 |
| false positives, grounded (over-triggers) | 274/274 |  |
| correct fields whose quote wasn't found | 1 |  |

Validation issues: `exception_without_restriction` 6, `ungrounded_quote` 2, `license_property_without_grant` 1, `unsupported_value` 1.

## Compared with `20261020-211036-llm-gpt-5.6-luna-single-dev` (llm-gpt-5.6-luna-single)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 88.3 | 88.3 | +0.0 |
| text | 85.0 | 85.0 | +0.0 |
| date | 85.2 | 85.2 | +0.0 |
| duration | 91.7 | 91.7 | +0.0 |
| jurisdiction | 94.6 | 94.6 | +0.0 |
| clause | 75.6 | 75.6 | +0.0 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `affiliate_license_licensee` | 88.9 | 88.9 | +0.0 |
| `affiliate_license_licensor` | 60.0 | 60.0 | +0.0 |
| `agreement_date` | 89.5 | 89.5 | +0.0 |
| `anti_assignment` | 97.6 | 97.6 | +0.0 |
| `audit_rights` | 95.1 | 95.1 | +0.0 |
| `third_party_beneficiary` | 42.1 | 42.1 | +0.0 |
| `uncapped_liability` | 49.2 | 49.2 | +0.0 |
| `unlimited_all_you_can_eat_license` | 66.7 | 66.7 | +0.0 |
| `volume_restriction` | 15.4 | 15.4 | +0.0 |
| `warranty_duration` | 64.5 | 64.5 | +0.0 |
