-- How common is each field type? Prevalence = share of contracts where the field is labelled.
WITH per_field AS (
    SELECT field, field_type, avg(present::INT) AS prevalence
    FROM gold_fields
    GROUP BY ALL
)
SELECT
    field_type,
    count(*)                               AS fields,
    round(100 * avg(prevalence), 1)        AS mean_pct_present,
    round(100 * min(prevalence), 1)        AS min_pct_present,
    round(100 * max(prevalence), 1)        AS max_pct_present,
    arg_min(field, prevalence)             AS rarest_field
FROM per_field
GROUP BY ALL
ORDER BY fields DESC;
