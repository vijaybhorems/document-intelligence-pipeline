-- Positive examples per field in each evaluation split. Fields with < 10 positives in
-- test will have wide confidence intervals: don't over-read their F1 (SPEC §10.4).
PIVOT (
    SELECT g.field, s.split, count(*) FILTER (g.present) AS positives
    FROM gold_fields g
    JOIN splits s USING (doc_id)
    WHERE s.split IN ('test', 'dev', 'experiment')
    GROUP BY ALL
)
ON split IN ('test', 'dev', 'experiment')
USING sum(positives)
ORDER BY test, field;
