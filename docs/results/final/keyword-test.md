# Eval report: `20261026-062924-keyword-test`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| keyword | test | 102/102 | `cef1245` (dirty) | 2026-10-26 06:29 | $0.0000 | 0.0s / 0.0s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 302 | 69.1 | 34.8 | **46.3** | 33-60 | 46.3 | 33-60 |
| text | 1 | 102 | 71.6 | 47.1 | **56.8** | 47-66 | 56.8 | 47-66 |
| date | 3 | 237 | 80.4 | 34.6 | **48.4** | 42-55 | 39.1 | 33-45 |
| duration | 2 | 61 | 72.1 | 50.8 | **59.6** | 47-71 | 58.4 | 45-70 |
| jurisdiction | 1 | 92 | 90.8 | 64.1 | **75.2** | 68-82 | 75.2 | 68-82 |
| clause | 33 | 777 | 39.6 | 87.3 | **54.5** | 51-57 | 50.4 | 46-53 |
| all fields | 41 | 1571 | 46.8 | 63.8 | **54.0** | 51-57 | 50.6 | 47-53 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 101 | 100.0 | 75.2 | **85.9** | 80-91 | 85.9 | 80-91 |
| text | 1 | 102 | 100.0 | 65.7 | **79.3** | 72-85 | 79.3 | 72-85 |
| date | 3 | 263 | 99.0 | 38.4 | **55.3** | 50-61 | 47.0 | 42-52 |
| duration | 2 | 67 | 93.2 | 61.2 | **73.9** | 63-83 | 71.7 | 59-81 |
| jurisdiction | 1 | 89 | 100.0 | 66.3 | **79.7** | 72-86 | 79.7 | 72-86 |
| clause | 33 | 777 | 39.6 | 87.3 | **54.5** | 51-57 | 50.4 | 46-53 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 197 | 45.2 | 86.3 | **59.3** | 55-64 | 51.8 | 45-58 |
| ip_and_licensing | 10 | 180 | 33.9 | 89.4 | **49.2** | 43-55 | 50.3 | 41-56 |
| liability_and_risk | 5 | 115 | 33.3 | 87.8 | **48.3** | 42-54 | 42.0 | 36-48 |
| restrictive_covenants | 6 | 106 | 31.0 | 92.5 | **46.4** | 39-53 | 46.8 | 38-55 |
| term_and_termination | 4 | 179 | 60.9 | 82.7 | **70.1** | 66-75 | 64.0 | 57-70 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `expiration_date` | date | value | 71 | 100.0 | 4.2 | **8.1** | 0-18 | 6.5 |  |
| `price_restrictions` | clause | presence | 3 | 4.5 | 100.0 | **8.7** | 0-19 | 8.7 | 0.0 |
| `affiliate_license_licensor` | clause | presence | 5 | 6.9 | 100.0 | **13.0** | 3-24 | 13.0 | 5.2 |
| `third_party_beneficiary` | clause | presence | 6 | 11.5 | 50.0 | **18.8** | 0-37 | 18.8 | 14.6 |
| `most_favored_nation` | clause | presence | 6 | 25.0 | 16.7 | **20.0** | 0-50 | 20.0 | 20.0 |
| `joint_ip_ownership` | clause | presence | 9 | 12.0 | 100.0 | **21.4** | 9-33 | 21.4 | 8.5 |
| `no_solicit_of_customers` | clause | presence | 7 | 14.8 | 57.1 | **23.5** | 6-43 | 23.5 | 5.8 |
| `affiliate_license_licensee` | clause | presence | 12 | 15.3 | 91.7 | **26.2** | 13-39 | 26.2 | 3.0 |
| `competitive_restriction_exception` | clause | presence | 15 | 16.0 | 100.0 | **27.5** | 16-38 | 27.5 | 5.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 3 | 16.7 | 100.0 | **28.6** | 0-52 | 28.6 | 15.0 |
| `warranty_duration` | clause | presence | 15 | 16.9 | 93.3 | **28.6** | 18-40 | 28.6 | 0.0 |
| `effective_date` | date | value | 73 | 65.4 | 23.3 | **34.3** | 22-46 | 48.5 |  |
| `uncapped_liability` | clause | presence | 23 | 24.2 | 95.7 | **38.6** | 27-50 | 38.6 | 1.4 |
| `volume_restriction` | clause | presence | 17 | 26.3 | 88.2 | **40.5** | 26-53 | 40.5 | 11.2 |
| `liquidated_damages` | clause | presence | 12 | 27.0 | 83.3 | **40.8** | 24-58 | 40.8 | 23.4 |
| `parties` | entity_list | value | 302 | 69.1 | 34.8 | **46.3** | 33-60 | 85.9 |  |
| `non_compete` | clause | presence | 23 | 30.7 | 100.0 | **46.9** | 33-58 | 46.9 | 17.1 |
| `ip_ownership_assignment` | clause | presence | 25 | 33.8 | 92.0 | **49.5** | 36-61 | 49.5 | 11.2 |
| `change_of_control` | clause | presence | 24 | 62.5 | 41.7 | **50.0** | 29-68 | 50.0 | 18.9 |
| `irrevocable_or_perpetual_license` | clause | presence | 14 | 36.4 | 85.7 | **51.1** | 32-67 | 51.1 | 37.0 |
| `rofr_rofo_rofn` | clause | presence | 17 | 100.0 | 35.3 | **52.2** | 20-74 | 52.2 | 13.7 |
| `termination_for_convenience` | clause | presence | 42 | 44.4 | 66.7 | **53.3** | 41-64 | 53.3 | 16.2 |
| `notice_period_to_terminate_renewal` | duration | value | 22 | 66.7 | 45.5 | **54.1** | 31-72 | 63.4 |  |
| `document_name` | text | value | 102 | 71.6 | 47.1 | **56.8** | 47-66 | 79.3 |  |
| `revenue_profit_sharing` | clause | presence | 33 | 41.3 | 93.9 | **57.4** | 45-68 | 57.4 | 9.3 |
| `non_disparagement` | clause | presence | 8 | 55.6 | 62.5 | **58.8** | 24-84 | 58.8 | 22.2 |
| `post_termination_services` | clause | presence | 36 | 44.7 | 94.4 | **60.7** | 50-71 | 60.7 | 9.8 |
| `no_solicit_of_employees` | clause | presence | 12 | 44.4 | 100.0 | **61.5** | 42-78 | 61.5 | 30.8 |
| `covenant_not_to_sue` | clause | presence | 20 | 56.0 | 70.0 | **62.2** | 44-77 | 62.2 | 47.4 |
| `exclusivity` | clause | presence | 41 | 46.4 | 95.1 | **62.4** | 52-72 | 62.4 | 25.9 |
| `renewal_term` | duration | value | 39 | 75.0 | 53.8 | **62.7** | 47-77 | 80.0 |  |
| `agreement_date` | date | value | 93 | 84.9 | 66.7 | **74.7** | 66-83 | 85.9 |  |
| `insurance` | clause | presence | 33 | 60.0 | 100.0 | **75.0** | 64-84 | 75.0 | 18.4 |
| `governing_law` | jurisdiction | value | 92 | 90.8 | 64.1 | **75.2** | 68-82 | 79.7 |  |
| `minimum_commitment` | clause | presence | 39 | 73.3 | 84.6 | **78.6** | 69-87 | 78.6 | 30.3 |
| `license_grant` | clause | presence | 58 | 69.0 | 100.0 | **81.7** | 74-88 | 81.7 | 13.3 |
| `audit_rights` | clause | presence | 49 | 70.6 | 98.0 | **82.1** | 73-89 | 82.1 | 34.0 |
| `cap_on_liability` | clause | presence | 59 | 78.8 | 88.1 | **83.2** | 75-89 | 83.2 | 17.4 |
| `non_transferable_license` | clause | presence | 31 | 95.8 | 74.2 | **83.6** | 72-93 | 83.6 | 64.0 |
| `source_code_escrow` | clause | presence | 3 | 75.0 | 100.0 | **85.7** | 0-100 | 85.7 | 25.0 |
| `anti_assignment` | clause | presence | 77 | 86.4 | 98.7 | **92.1** | 88-96 | 92.1 | 24.3 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 100.0 | 8 | 75.0 | 4 | +25.0 |
| `affiliate_license_licensor` | 100.0 | 4 | 100.0 | 1 | +0.0 |
| `anti_assignment` | 100.0 | 75 | 50.0 | 2 | +50.0 |
| `audit_rights` | 100.0 | 48 | 0.0 | 1 | +100.0 |
| `cap_on_liability` | 100.0 | 35 | 70.8 | 24 | +29.2 |
| `change_of_control` | 100.0 | 9 | 6.7 | 15 | +93.3 |
| `competitive_restriction_exception` | 100.0 | 9 | 100.0 | 6 | +0.0 |
| `covenant_not_to_sue` | 100.0 | 13 | 14.3 | 7 | +85.7 |
| `document_name` | 66.7 | 99 | 33.3 | 3 | +33.3 |
| `exclusivity` | 100.0 | 32 | 77.8 | 9 | +22.2 |
| `expiration_date` | 5.8 | 52 | 0.0 | 36 | +5.8 |
| `governing_law` | 68.6 | 86 | 0.0 | 2 | +68.6 |
| `insurance` | 100.0 | 33 | — | 0 | — |
| `ip_ownership_assignment` | 100.0 | 15 | 80.0 | 10 | +20.0 |
| `irrevocable_or_perpetual_license` | 100.0 | 12 | 0.0 | 2 | +100.0 |
| `joint_ip_ownership` | 100.0 | 9 | — | 0 | — |
| `license_grant` | 100.0 | 48 | 100.0 | 10 | +0.0 |
| `liquidated_damages` | 100.0 | 8 | 50.0 | 4 | +50.0 |
| `minimum_commitment` | 100.0 | 29 | 40.0 | 10 | +60.0 |
| `most_favored_nation` | 100.0 | 1 | 0.0 | 5 | +100.0 |
| `no_solicit_of_customers` | 100.0 | 3 | 25.0 | 4 | +75.0 |
| `no_solicit_of_employees` | 100.0 | 10 | 100.0 | 2 | +0.0 |
| `non_compete` | 100.0 | 22 | 100.0 | 1 | +0.0 |
| `non_disparagement` | 100.0 | 5 | 0.0 | 3 | +100.0 |
| `non_transferable_license` | 100.0 | 23 | 0.0 | 8 | +100.0 |
| `notice_period_to_terminate_renewal` | 46.2 | 13 | 58.3 | 12 | -12.2 |
| `post_termination_services` | 100.0 | 10 | 92.3 | 26 | +7.7 |
| `price_restrictions` | 100.0 | 1 | 100.0 | 2 | +0.0 |
| `renewal_term` | 84.8 | 33 | 0.0 | 9 | +84.8 |
| `revenue_profit_sharing` | 100.0 | 20 | 84.6 | 13 | +15.4 |
| `rofr_rofo_rofn` | 100.0 | 4 | 15.4 | 13 | +84.6 |
| `source_code_escrow` | 100.0 | 3 | — | 0 | — |
| `termination_for_convenience` | 100.0 | 17 | 44.0 | 25 | +56.0 |
| `third_party_beneficiary` | 100.0 | 3 | 0.0 | 3 | +100.0 |
| `uncapped_liability` | 100.0 | 19 | 75.0 | 4 | +25.0 |
| `unlimited_all_you_can_eat_license` | 100.0 | 3 | — | 0 | — |
| `volume_restriction` | 100.0 | 9 | 75.0 | 8 | +25.0 |
| `warranty_duration` | 100.0 | 8 | 85.7 | 7 | +14.3 |
| **all** | 85.4 | 831 | 47.4 | 291 | +38.0 |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 102/102 | 100.0 |
| quotes found in the contract | 4335/4335 | 100.0 |
| values with no grounded evidence | 0/2061 | 0.0 |
| false positives, ungrounded (**hallucinated**) | 0/1039 | 0.0 |
| false positives, grounded (over-triggers) | 1039/1039 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.
