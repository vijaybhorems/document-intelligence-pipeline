-- Quality, cost and latency by route and model from eval runs: the data behind the
-- D1/D2 Pareto charts (SPEC §9.3). Headline F1 = presence for clauses, value for typed
-- fields (dip.eval.scorer), micro-averaged over every field of every contract.
WITH f1 AS (
    SELECT run_id,
           2 * sum(tp) / nullif(2 * sum(tp) + sum(fp) + sum(fn), 0) AS micro_f1
    FROM eval_field_results
    WHERE metric = CASE WHEN field_type = 'clause' THEN 'presence' ELSE 'value' END
    GROUP BY run_id
)
SELECT
    r.model,
    coalesce(r.route, 'txt')         AS route,
    coalesce(r.variant, 'clean')     AS variant,
    r.prompt_version,
    r.strategy,
    coalesce(r.context, 'full')      AS context,
    r.split,
    count(*)                         AS runs,
    round(100 * avg(f1.micro_f1), 1) AS micro_f1,
    round(avg((r.cost_usd + r.compute_usd) / r.n_docs), 5) AS cost_per_contract_usd,
    round(avg(r.latency_p50_s), 1)   AS p50_seconds,
    round(avg(r.latency_p95_s), 1)   AS p95_seconds
FROM eval_runs AS r
JOIN f1 USING (run_id)
WHERE r.model IS NOT NULL            -- LLM runs only, not baselines
  AND r.derived_from IS NULL         -- re-validated copies would double count
  AND r.n_predicted = r.n_docs       -- complete runs
  AND r.split = $split
GROUP BY ALL
ORDER BY variant, micro_f1 DESC
