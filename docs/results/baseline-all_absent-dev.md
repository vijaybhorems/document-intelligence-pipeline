# Eval report: `20261020-203039-all_absent-dev`

| system | split | contracts | git | created (UTC) |
|---|---|---|---|---|
| all_absent | dev | 80 | `0da8917` | 2026-10-20 20:30 |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 217 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| text | 1 | 80 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| date | 3 | 180 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| duration | 2 | 44 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| jurisdiction | 1 | 71 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| clause | 33 | 582 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| all fields | 41 | 1174 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 80 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| text | 1 | 80 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| date | 3 | 206 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| duration | 2 | 46 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| jurisdiction | 1 | 70 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| clause | 33 | 582 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 133 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| ip_and_licensing | 10 | 132 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| liability_and_risk | 5 | 96 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| restrictive_covenants | 6 | 81 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| term_and_termination | 4 | 140 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensee` | clause | presence | 9 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `affiliate_license_licensor` | clause | presence | 4 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `agreement_date` | date | value | 70 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `anti_assignment` | clause | presence | 62 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `audit_rights` | clause | presence | 29 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `cap_on_liability` | clause | presence | 50 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `change_of_control` | clause | presence | 23 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `competitive_restriction_exception` | clause | presence | 12 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `covenant_not_to_sue` | clause | presence | 16 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `document_name` | text | value | 80 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `effective_date` | date | value | 58 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `exclusivity` | clause | presence | 30 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `expiration_date` | date | value | 52 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `governing_law` | jurisdiction | value | 71 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `insurance` | clause | presence | 23 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `ip_ownership_assignment` | clause | presence | 19 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `irrevocable_or_perpetual_license` | clause | presence | 11 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `joint_ip_ownership` | clause | presence | 7 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `license_grant` | clause | presence | 39 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `liquidated_damages` | clause | presence | 10 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `minimum_commitment` | clause | presence | 25 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `most_favored_nation` | clause | presence | 4 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `no_solicit_of_customers` | clause | presence | 5 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `no_solicit_of_employees` | clause | presence | 9 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `non_compete` | clause | presence | 19 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `non_disparagement` | clause | presence | 6 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `non_transferable_license` | clause | presence | 22 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `notice_period_to_terminate_renewal` | duration | value | 18 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `parties` | entity_list | value | 217 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `post_termination_services` | clause | presence | 29 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 2 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `renewal_term` | duration | value | 26 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `revenue_profit_sharing` | clause | presence | 26 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `rofr_rofo_rofn` | clause | presence | 13 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 2 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `termination_for_convenience` | clause | presence | 26 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `third_party_beneficiary` | clause | presence | 5 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `uncapped_liability` | clause | presence | 19 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 3 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `volume_restriction` | clause | presence | 11 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `warranty_duration` | clause | presence | 12 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 0.0 | 8 | 0.0 | 1 | +0.0 |
| `affiliate_license_licensor` | 0.0 | 3 | 0.0 | 1 | +0.0 |
| `anti_assignment` | 0.0 | 60 | 0.0 | 2 | +0.0 |
| `audit_rights` | 0.0 | 28 | 0.0 | 1 | +0.0 |
| `cap_on_liability` | 0.0 | 25 | 0.0 | 25 | +0.0 |
| `change_of_control` | 0.0 | 13 | 0.0 | 10 | +0.0 |
| `competitive_restriction_exception` | 0.0 | 5 | 0.0 | 7 | +0.0 |
| `covenant_not_to_sue` | 0.0 | 11 | 0.0 | 5 | +0.0 |
| `document_name` | 0.0 | 79 | 0.0 | 1 | +0.0 |
| `exclusivity` | 0.0 | 27 | 0.0 | 3 | +0.0 |
| `expiration_date` | 0.0 | 44 | 0.0 | 24 | +0.0 |
| `governing_law` | 0.0 | 66 | 0.0 | 3 | +0.0 |
| `insurance` | 0.0 | 23 | — | 0 | — |
| `ip_ownership_assignment` | 0.0 | 8 | 0.0 | 11 | +0.0 |
| `irrevocable_or_perpetual_license` | 0.0 | 11 | — | 0 | — |
| `joint_ip_ownership` | 0.0 | 6 | 0.0 | 1 | +0.0 |
| `license_grant` | 0.0 | 33 | 0.0 | 6 | +0.0 |
| `liquidated_damages` | 0.0 | 7 | 0.0 | 3 | +0.0 |
| `minimum_commitment` | 0.0 | 19 | 0.0 | 6 | +0.0 |
| `most_favored_nation` | 0.0 | 2 | 0.0 | 2 | +0.0 |
| `no_solicit_of_customers` | 0.0 | 2 | 0.0 | 3 | +0.0 |
| `no_solicit_of_employees` | 0.0 | 7 | 0.0 | 2 | +0.0 |
| `non_compete` | 0.0 | 16 | 0.0 | 3 | +0.0 |
| `non_disparagement` | 0.0 | 3 | 0.0 | 3 | +0.0 |
| `non_transferable_license` | 0.0 | 14 | 0.0 | 8 | +0.0 |
| `notice_period_to_terminate_renewal` | 0.0 | 10 | 0.0 | 9 | +0.0 |
| `post_termination_services` | 0.0 | 9 | 0.0 | 20 | +0.0 |
| `price_restrictions` | 0.0 | 1 | 0.0 | 1 | +0.0 |
| `renewal_term` | 0.0 | 20 | 0.0 | 7 | +0.0 |
| `revenue_profit_sharing` | 0.0 | 20 | 0.0 | 6 | +0.0 |
| `rofr_rofo_rofn` | 0.0 | 2 | 0.0 | 11 | +0.0 |
| `source_code_escrow` | 0.0 | 1 | 0.0 | 1 | +0.0 |
| `termination_for_convenience` | 0.0 | 11 | 0.0 | 15 | +0.0 |
| `third_party_beneficiary` | 0.0 | 5 | — | 0 | — |
| `uncapped_liability` | 0.0 | 14 | 0.0 | 5 | +0.0 |
| `unlimited_all_you_can_eat_license` | 0.0 | 3 | — | 0 | — |
| `volume_restriction` | 0.0 | 7 | 0.0 | 4 | +0.0 |
| `warranty_duration` | 0.0 | 9 | 0.0 | 3 | +0.0 |
| **all** | 0.0 | 632 | 0.0 | 213 | — |
