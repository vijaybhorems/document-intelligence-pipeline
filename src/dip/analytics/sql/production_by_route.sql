-- What the service actually costs and how long it takes, by route and model
-- (SPEC §9.3, §12.1). Every record counts, including re-extractions.
SELECT
    route,
    model,
    count(*)                                   AS records,
    sum(pages)                                 AS pages,
    round(median(cost_usd), 5)                 AS median_cost_usd,
    round(quantile_cont(cost_usd, 0.95), 5)    AS p95_cost_usd,
    round(sum(cost_usd), 4)                    AS total_cost_usd,
    round(median(seconds), 1)                  AS median_seconds,
    round(quantile_cont(seconds, 0.95), 1)     AS p95_seconds,
    round(avg((validation_errors = 0)::INTEGER), 3) AS valid_share
FROM records
WHERE created_at >= now() - to_days($days)
GROUP BY ALL
ORDER BY records DESC
