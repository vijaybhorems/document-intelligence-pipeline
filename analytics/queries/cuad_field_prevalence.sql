-- Per-field prevalence across all 510 contracts, rarest first.
-- Rare fields have tiny support in a 102-contract test set (see cuad_test_support.sql).
SELECT
    field,
    field_type,
    field_group,
    count(*) FILTER (present)                             AS contracts,
    round(100.0 * count(*) FILTER (present) / count(*), 1) AS pct_present,
    sum(n_spans)                                          AS spans,
    median(span_chars) FILTER (present)::INT              AS median_span_chars
FROM gold_fields
GROUP BY ALL
ORDER BY pct_present, field;
