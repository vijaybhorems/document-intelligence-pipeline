-- Fields that got worse from run_a to run_b (SPEC §9.3), by headline F1. Compare runs
-- on the same split; a drop smaller than the noise floor (Phase 2) is not a finding.
WITH per_field AS (
    SELECT run_id, field, any_value(field_type) AS field_type,
           2 * sum(tp) / nullif(2 * sum(tp) + sum(fp) + sum(fn), 0) AS f1,
           sum(tp + fn) AS support
    FROM eval_field_results
    WHERE run_id IN ($run_a, $run_b)
      AND metric = CASE WHEN field_type = 'clause' THEN 'presence' ELSE 'value' END
    GROUP BY run_id, field
)
SELECT
    a.field,
    a.field_type,
    a.support,
    round(100 * a.f1, 1)           AS f1_a,
    round(100 * b.f1, 1)           AS f1_b,
    round(100 * (b.f1 - a.f1), 1)  AS delta
FROM per_field AS a
JOIN per_field AS b ON a.field = b.field AND a.run_id = $run_a AND b.run_id = $run_b
WHERE 100 * (coalesce(b.f1, 0) - coalesce(a.f1, 0)) <= -$min_drop  -- F1 points
ORDER BY delta, a.field
