# Eval report: `20261021-030755-llm-gpt-5.6-luna-single-v4-pypdf-scanned-experiment`

| system | split | contracts | git | created (UTC) | cost/contract | p50 / p95 |
|---|---|---|---|---|---|---|
| llm-gpt-5.6-luna-single-v4-pypdf-scanned | experiment | 30/30 | `c7c64ff` | 2026-10-21 03:07 | $0.0024 | 5.3s / 5.9s |

Percentages. **Headline metric**: presence for clauses, value for typed fields. Micro pools TP/FP/FN across fields; macro averages per-field F1, so rare fields count equally. CIs: 1,000 bootstrap resamples of contracts.

## Headline by field type

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 68 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| text | 1 | 30 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| date | 3 | 66 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| duration | 2 | 21 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| jurisdiction | 1 | 27 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| clause | 33 | 215 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| all fields | 41 | 427 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |

## Presence by field type

Did the system find the field at all? For typed fields this includes clauses that mention the field without a derivable value.

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| entity_list | 1 | 30 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| text | 1 | 30 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| date | 3 | 79 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| duration | 2 | 22 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| jurisdiction | 1 | 27 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| clause | 33 | 215 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |

## Clause families (presence)

|  | fields | support | P | R | micro F1 | 95% CI | macro F1 | 95% CI |
|---|---|---|---|---|---|---|---|---|
| commercial_terms | 8 | 51 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| ip_and_licensing | 10 | 51 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| liability_and_risk | 5 | 39 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| restrictive_covenants | 6 | 29 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |
| term_and_termination | 4 | 45 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0-0 |

## Per field

Sorted by headline F1, worst first. Support = gold positives in this split.

| field | type | metric | support | P | R | F1 | 95% CI | presence F1 | span F1 |
|---|---|---|---|---|---|---|---|---|---|
| `affiliate_license_licensee` | clause | presence | 3 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `affiliate_license_licensor` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `agreement_date` | date | value | 26 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `anti_assignment` | clause | presence | 21 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `audit_rights` | clause | presence | 13 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `cap_on_liability` | clause | presence | 21 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `change_of_control` | clause | presence | 8 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `competitive_restriction_exception` | clause | presence | 4 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `covenant_not_to_sue` | clause | presence | 7 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `document_name` | text | value | 30 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `effective_date` | date | value | 21 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `exclusivity` | clause | presence | 11 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `expiration_date` | date | value | 19 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `governing_law` | jurisdiction | value | 27 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `insurance` | clause | presence | 5 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `ip_ownership_assignment` | clause | presence | 9 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `irrevocable_or_perpetual_license` | clause | presence | 4 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `joint_ip_ownership` | clause | presence | 3 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `license_grant` | clause | presence | 14 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `liquidated_damages` | clause | presence | 4 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `minimum_commitment` | clause | presence | 13 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `most_favored_nation` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `no_solicit_of_customers` | clause | presence | 2 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `no_solicit_of_employees` | clause | presence | 3 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `non_compete` | clause | presence | 6 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `non_disparagement` | clause | presence | 3 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `non_transferable_license` | clause | presence | 8 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `notice_period_to_terminate_renewal` | duration | value | 8 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `parties` | entity_list | value | 68 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `post_termination_services` | clause | presence | 9 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `price_restrictions` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `renewal_term` | duration | value | 13 | — | 0.0 | **0.0** | 0-0 | 0.0 |  |
| `revenue_profit_sharing` | clause | presence | 11 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `rofr_rofo_rofn` | clause | presence | 5 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `source_code_escrow` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `termination_for_convenience` | clause | presence | 7 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `third_party_beneficiary` | clause | presence | 2 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `uncapped_liability` | clause | presence | 6 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `unlimited_all_you_can_eat_license` | clause | presence | 1 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `volume_restriction` | clause | presence | 2 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |
| `warranty_duration` | clause | presence | 6 | — | 0.0 | **0.0** | 0-0 | 0.0 | 0.0 |

## Phrasing slice (presence recall)

Canonical = gold text contains the field's obvious wording (`canonical_cues` in the registry). A large gap means the system only finds clauses phrased the expected way.

| field | canonical R | n | non-canonical R | n | gap |
|---|---|---|---|---|---|
| `affiliate_license_licensee` | 0.0 | 3 | — | 0 | — |
| `affiliate_license_licensor` | 0.0 | 1 | — | 0 | — |
| `anti_assignment` | 0.0 | 21 | — | 0 | — |
| `audit_rights` | 0.0 | 12 | 0.0 | 1 | +0.0 |
| `cap_on_liability` | 0.0 | 13 | 0.0 | 8 | +0.0 |
| `change_of_control` | 0.0 | 5 | 0.0 | 3 | +0.0 |
| `competitive_restriction_exception` | 0.0 | 2 | 0.0 | 2 | +0.0 |
| `covenant_not_to_sue` | 0.0 | 6 | 0.0 | 1 | +0.0 |
| `document_name` | 0.0 | 30 | — | 0 | — |
| `exclusivity` | 0.0 | 11 | — | 0 | — |
| `expiration_date` | 0.0 | 18 | 0.0 | 8 | +0.0 |
| `governing_law` | 0.0 | 26 | — | 0 | — |
| `insurance` | 0.0 | 5 | — | 0 | — |
| `ip_ownership_assignment` | 0.0 | 3 | 0.0 | 6 | +0.0 |
| `irrevocable_or_perpetual_license` | 0.0 | 4 | — | 0 | — |
| `joint_ip_ownership` | 0.0 | 2 | 0.0 | 1 | +0.0 |
| `license_grant` | 0.0 | 12 | 0.0 | 2 | +0.0 |
| `liquidated_damages` | 0.0 | 3 | 0.0 | 1 | +0.0 |
| `minimum_commitment` | 0.0 | 12 | 0.0 | 1 | +0.0 |
| `most_favored_nation` | 0.0 | 1 | — | 0 | — |
| `no_solicit_of_customers` | 0.0 | 1 | 0.0 | 1 | +0.0 |
| `no_solicit_of_employees` | 0.0 | 2 | 0.0 | 1 | +0.0 |
| `non_compete` | 0.0 | 4 | 0.0 | 2 | +0.0 |
| `non_disparagement` | 0.0 | 1 | 0.0 | 2 | +0.0 |
| `non_transferable_license` | 0.0 | 6 | 0.0 | 2 | +0.0 |
| `notice_period_to_terminate_renewal` | 0.0 | 5 | 0.0 | 4 | +0.0 |
| `post_termination_services` | 0.0 | 2 | 0.0 | 7 | +0.0 |
| `price_restrictions` | — | 0 | 0.0 | 1 | — |
| `renewal_term` | 0.0 | 11 | 0.0 | 2 | +0.0 |
| `revenue_profit_sharing` | 0.0 | 7 | 0.0 | 4 | +0.0 |
| `rofr_rofo_rofn` | 0.0 | 2 | 0.0 | 3 | +0.0 |
| `source_code_escrow` | — | 0 | 0.0 | 1 | — |
| `termination_for_convenience` | 0.0 | 3 | 0.0 | 4 | +0.0 |
| `third_party_beneficiary` | 0.0 | 2 | — | 0 | — |
| `uncapped_liability` | 0.0 | 5 | 0.0 | 1 | +0.0 |
| `unlimited_all_you_can_eat_license` | 0.0 | 1 | — | 0 | — |
| `volume_restriction` | 0.0 | 1 | 0.0 | 1 | +0.0 |
| `warranty_duration` | 0.0 | 5 | 0.0 | 1 | +0.0 |
| **all** | 0.0 | 248 | 0.0 | 71 | — |

## Validation

Grounding locates every predicted quote in the contract (SPEC §8.3). A false positive with no grounded quote is a hallucination; one backed by real text is an over-trigger (wrong legal reading). They need different fixes.

|  | count | % |
|---|---|---|
| valid outputs (no L1/L2 issue) | 0/30 | 0.0 |
| quotes found in the contract | 0/0 | — |
| values with no grounded evidence | 0/0 | — |
| false positives, ungrounded (**hallucinated**) | 0/0 | — |
| false positives, grounded (over-triggers) | 0/0 |  |
| correct fields whose quote wasn't found | 0 |  |

Validation issues: none recorded.

## Compared with `20261020-204758-keyword-experiment` (keyword)

| field type | before F1 | after F1 | Δ |
|---|---|---|---|
| entity_list | 61.7 | 0.0 | -61.7 |
| text | 63.0 | 0.0 | -63.0 |
| date | 60.0 | 0.0 | -60.0 |
| duration | 81.1 | 0.0 | -81.1 |
| jurisdiction | 83.3 | 0.0 | -83.3 |
| clause | 53.5 | 0.0 | -53.5 |

Biggest movers (headline F1):

| field | before | after | Δ |
|---|---|---|---|
| `cap_on_liability` | 93.0 | 0.0 | -93.0 |
| `agreement_date` | 92.0 | 0.0 | -92.0 |
| `anti_assignment` | 89.4 | 0.0 | -89.4 |
| `rofr_rofo_rofn` | 88.9 | 0.0 | -88.9 |
| `covenant_not_to_sue` | 85.7 | 0.0 | -85.7 |
| `volume_restriction` | 17.4 | 0.0 | -17.4 |
| `expiration_date` | 10.0 | 0.0 | -10.0 |
| `affiliate_license_licensor` | 8.7 | 0.0 | -8.7 |
| `price_restrictions` | 0.0 | 0.0 | +0.0 |
| `source_code_escrow` | 0.0 | 0.0 | +0.0 |
