# Eval report: `20261020-231956-llm-gpt-5.6-luna-single+validate-warn-reask-dev`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single+validate-warn-reask | dev | 80/80 | `d4edc66` | 2026-10-20 23:19 | $0.0060 (incl. $0.0005 re-ask) | 14.2s / 21.3s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 217 | 85.9 | 89.9 | **87.8** | 79-94 | 87.8 | 79-94 |
| text | 1 | 80 | 88.8 | 88.8 | **88.8** | 81-95 | 88.8 | 81-95 |
| date | 3 | 180 | 87.8 | 83.9 | **85.8** | 81-90 | 85.0 | 80-89 |
| duration | 2 | 44 | 83.0 | 100.0 | **90.7** | 84-96 | 91.0 | 85-96 |
| jurisdiction | 1 | 71 | 87.2 | 95.8 | **91.3** | 87-96 | 91.3 | 87-96 |
| clause | 33 | 582 | 69.7 | 88.7 | **78.1** | 75-80 | 73.9 | 67-77 |
| all fields | 41 | 1174 | 77.4 | 89.0 | **82.8** | 81-85 | 76.7 | 72-79 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 80 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| text | 1 | 80 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 100-100 |
| date | 3 | 206 | 92.2 | 98.1 | **95.1** | 93-97 | 95.1 | 93-97 |
| duration | 2 | 46 | 73.0 | 100.0 | **84.4** | 76-91 | 85.5 | 78-91 |
| jurisdiction | 1 | 70 | 100.0 | 97.1 | **98.6** | 96-100 | 98.6 | 96-100 |
| clause | 33 | 582 | 69.7 | 88.7 | **78.1** | 75-80 | 73.9 | 67-77 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 133 | 63.6 | 77.4 | **69.8** | 64-75 | 63.2 | 54-69 |
| ip_and_licensing | 10 | 132 | 75.8 | 90.2 | **82.4** | 77-86 | 78.3 | 64-86 |
| liability_and_risk | 5 | 96 | 72.5 | 90.6 | **80.6** | 75-86 | 72.9 | 64-79 |
| restrictive_covenants | 6 | 81 | 68.9 | 90.1 | **78.1** | 71-84 | 78.9 | 69-85 |
| term_and_termination | 4 | 140 | 68.7 | 95.7 | **80.0** | 76-84 | 77.9 | 72-83 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `price_restrictions` | clause | presence | 2 | 6.5 | 100.0 | **12.1** | 0-28 | 12.1 | 11.1 |
| `volume_restriction` | clause | presence | 11 | 26.3 | 45.5 | **33.3** | 10-55 | 33.3 | 14.6 |
| `third_party_beneficiary` | clause | presence | 5 | 30.0 | 60.0 | **40.0** | 0-67 | 40.0 | 42.1 |
| `most_favored_nation` | clause | presence | 4 | 50.0 | 50.0 | **50.0** | 0-86 | 50.0 | 40.0 |
| `minimum_commitment` | clause | presence | 25 | 71.4 | 40.0 | **51.3** | 30-68 | 51.3 | 21.5 |
| `competitive_restriction_exception` | clause | presence | 12 | 39.3 | 91.7 | **55.0** | 33-72 | 55.0 | 27.5 |
| `post_termination_services` | clause | presence | 29 | 42.0 | 100.0 | **59.2** | 47-71 | 59.2 | 20.0 |
| `uncapped_liability` | clause | presence | 19 | 47.2 | 89.5 | **61.8** | 44-74 | 61.8 | 51.5 |
| `affiliate_license_licensor` | clause | presence | 4 | 50.0 | 100.0 | **66.7** | 25-92 | 66.7 | 17.4 |
| `non_disparagement` | clause | presence | 6 | 55.6 | 83.3 | **66.7** | 33-90 | 66.7 | 26.1 |
| `source_code_escrow` | clause | presence | 2 | 100.0 | 50.0 | **66.7** | 0-100 | 66.7 | 0.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 3 | 66.7 | 66.7 | **66.7** | 0-100 | 66.7 | 66.7 |
| `change_of_control` | clause | presence | 23 | 60.0 | 91.3 | **72.4** | 58-84 | 72.4 | 47.8 |
| `warranty_duration` | clause | presence | 12 | 71.4 | 83.3 | **76.9** | 53-92 | 76.9 | 56.4 |
| `expiration_date` | date | value | 52 | 90.0 | 69.2 | **78.3** | 67-87 | 97.1 |  |
| `non_transferable_license` | clause | presence | 22 | 64.7 | 100.0 | **78.6** | 65-89 | 78.6 | 41.5 |
| `ip_ownership_assignment` | clause | presence | 19 | 70.8 | 89.5 | **79.1** | 64-90 | 79.1 | 37.5 |
| `covenant_not_to_sue` | clause | presence | 16 | 85.7 | 75.0 | **80.0** | 63-93 | 80.0 | 48.8 |
| `termination_for_convenience` | clause | presence | 26 | 75.9 | 84.6 | **80.0** | 68-90 | 80.0 | 65.6 |
| `affiliate_license_licensee` | clause | presence | 9 | 87.5 | 77.8 | **82.4** | 55-100 | 82.4 | 50.0 |
| `non_compete` | clause | presence | 19 | 77.3 | 89.5 | **82.9** | 69-94 | 82.9 | 48.5 |
| `joint_ip_ownership` | clause | presence | 7 | 100.0 | 71.4 | **83.3** | 50-100 | 83.3 | 40.0 |
| `no_solicit_of_customers` | clause | presence | 5 | 71.4 | 100.0 | **83.3** | 44-100 | 83.3 | 35.3 |
| `rofr_rofo_rofn` | clause | presence | 13 | 90.9 | 76.9 | **83.3** | 62-97 | 83.3 | 15.2 |
| `exclusivity` | clause | presence | 30 | 83.9 | 86.7 | **85.2** | 75-94 | 85.2 | 49.0 |
| `revenue_profit_sharing` | clause | presence | 26 | 85.2 | 88.5 | **86.8** | 75-96 | 86.8 | 44.0 |
| `effective_date` | date | value | 58 | 86.4 | 87.9 | **87.2** | 80-94 | 91.5 |  |
| `parties` | entity_list | value | 217 | 85.9 | 89.9 | **87.8** | 79-94 | 100.0 |  |
| `license_grant` | clause | presence | 39 | 80.9 | 97.4 | **88.4** | 81-95 | 88.4 | 46.4 |
| `document_name` | text | value | 80 | 88.8 | 88.8 | **88.8** | 81-95 | 100.0 |  |
| `agreement_date` | date | value | 70 | 87.7 | 91.4 | **89.5** | 82-96 | 96.6 |  |
| `renewal_term` | duration | value | 26 | 81.2 | 100.0 | **89.7** | 80-97 | 80.6 |  |
| `liquidated_damages` | clause | presence | 10 | 90.0 | 90.0 | **90.0** | 71-100 | 90.0 | 50.0 |
| `governing_law` | jurisdiction | value | 71 | 87.2 | 95.8 | **91.3** | 87-96 | 98.6 |  |
| `irrevocable_or_perpetual_license` | clause | presence | 11 | 84.6 | 100.0 | **91.7** | 75-100 | 91.7 | 55.8 |
| `notice_period_to_terminate_renewal` | duration | value | 18 | 85.7 | 100.0 | **92.3** | 82-100 | 90.5 |  |
| `insurance` | clause | presence | 23 | 91.7 | 95.7 | **93.6** | 86-100 | 93.6 | 32.7 |
| `audit_rights` | clause | presence | 29 | 90.6 | 100.0 | **95.1** | 88-100 | 95.1 | 47.5 |
| `cap_on_liability` | clause | presence | 50 | 96.0 | 96.0 | **96.0** | 92-99 | 96.0 | 52.1 |
| `anti_assignment` | clause | presence | 62 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 65.9 |
| `no_solicit_of_employees` | clause | presence | 9 | 100.0 | 100.0 | **100.0** | 100-100 | 100.0 | 81.8 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 75.0 | 8 | 100.0 | 1 | -25.0 |
| `affiliate_license_licensor` | 100.0 | 3 | 100.0 | 1 | +0.0 |
| `anti_assignment` | 100.0 | 60 | 100.0 | 2 | +0.0 |
| `audit_rights` | 100.0 | 28 | 100.0 | 1 | +0.0 |
| `cap_on_liability` | 100.0 | 25 | 92.0 | 25 | +8.0 |
| `change_of_control` | 92.3 | 13 | 90.0 | 10 | +2.3 |
| `competitive_restriction_exception` | 100.0 | 5 | 85.7 | 7 | +14.3 |
| `covenant_not_to_sue` | 100.0 | 11 | 20.0 | 5 | +80.0 |
| `document_name` | 100.0 | 79 | 100.0 | 1 | +0.0 |
| `exclusivity` | 85.2 | 27 | 100.0 | 3 | -14.8 |
| `expiration_date` | 97.7 | 44 | 95.8 | 24 | +1.9 |
| `governing_law` | 100.0 | 66 | 66.7 | 3 | +33.3 |
| `insurance` | 95.7 | 23 | — | 0 | — |
| `ip_ownership_assignment` | 87.5 | 8 | 90.9 | 11 | -3.4 |
| `irrevocable_or_perpetual_license` | 100.0 | 11 | — | 0 | — |
| `joint_ip_ownership` | 83.3 | 6 | 0.0 | 1 | +83.3 |
| `license_grant` | 100.0 | 33 | 83.3 | 6 | +16.7 |
| `liquidated_damages` | 85.7 | 7 | 100.0 | 3 | -14.3 |
| `minimum_commitment` | 47.4 | 19 | 16.7 | 6 | +30.7 |
| `most_favored_nation` | 100.0 | 2 | 0.0 | 2 | +100.0 |
| `no_solicit_of_customers` | 100.0 | 2 | 100.0 | 3 | +0.0 |
| `no_solicit_of_employees` | 100.0 | 7 | 100.0 | 2 | +0.0 |
| `non_compete` | 87.5 | 16 | 100.0 | 3 | -12.5 |
| `non_disparagement` | 100.0 | 3 | 66.7 | 3 | +33.3 |
| `non_transferable_license` | 100.0 | 14 | 100.0 | 8 | +0.0 |
| `notice_period_to_terminate_renewal` | 100.0 | 10 | 100.0 | 9 | +0.0 |
| `post_termination_services` | 100.0 | 9 | 100.0 | 20 | +0.0 |
| `price_restrictions` | 100.0 | 1 | 100.0 | 1 | +0.0 |
| `renewal_term` | 100.0 | 20 | 100.0 | 7 | +0.0 |
| `revenue_profit_sharing` | 100.0 | 20 | 50.0 | 6 | +50.0 |
| `rofr_rofo_rofn` | 100.0 | 2 | 72.7 | 11 | +27.3 |
| `source_code_escrow` | 100.0 | 1 | 0.0 | 1 | +100.0 |
| `termination_for_convenience` | 90.9 | 11 | 80.0 | 15 | +10.9 |
| `third_party_beneficiary` | 60.0 | 5 | — | 0 | — |
| `uncapped_liability` | 85.7 | 14 | 100.0 | 5 | -14.3 |
| `unlimited_all_you_can_eat_license` | 66.7 | 3 | — | 0 | — |
| `volume_restriction` | 42.9 | 7 | 50.0 | 4 | -7.1 |
| `warranty_duration` | 100.0 | 9 | 33.3 | 3 | +66.7 |
| **all** | 94.6 | 632 | 83.6 | 213 | +11.1 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 80/80 | 100.0 |
| quotes found in the contract | 1477/1477 | 100.0 |
| values with no grounded evidence | 0/1198 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/258 | 0.0 |
| false positives, grounded (over-triggers) | 258/258 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.

## Compared with `20261020-203205-keyword-dev` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 52.1 | 87.8 | +35.7 |
| text | 55.9 | 88.8 | +32.9 |
| date | 52.0 | 85.8 | +33.8 |
| duration | 70.0 | 90.7 | +20.7 |
| jurisdiction | 75.6 | 91.3 | +15.6 |
| clause | 55.2 | 78.1 | +22.8 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `minimum_commitment` | 70.6 | 51.3 | -19.3 |
| `third_party_beneficiary` | 45.5 | 40.0 | -5.5 |
| `volume_restriction` | 35.5 | 33.3 | -2.2 |
| `change_of_control` | 74.4 | 72.4 | -2.0 |
| `non_disparagement` | 66.7 | 66.7 | +0.0 |
| `warranty_duration` | 28.9 | 76.9 | +48.0 |
| `affiliate_license_licensor` | 13.8 | 66.7 | +52.9 |
| `affiliate_license_licensee` | 28.6 | 82.4 | +53.8 |
| `joint_ip_ownership` | 23.0 | 83.3 | +60.4 |
| `expiration_date` | 14.0 | 78.3 | +64.2 |
