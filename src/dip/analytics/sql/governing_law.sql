-- Governing-law distribution (SPEC §9.3). A contract can name more than one law
-- (e.g. different laws for different obligations); each counts once per contract.
WITH laws AS (
    SELECT document_sha256, unnest(
        CASE WHEN len(governing_law) = 0 THEN [NULL] ELSE governing_law END
    ) AS law
    FROM latest_records
)
SELECT
    coalesce(law, '(not found)')                       AS governing_law,
    count(DISTINCT document_sha256)                     AS contracts,
    round(count(DISTINCT document_sha256) / (SELECT count(*) FROM latest_records), 3) AS share
FROM laws
GROUP BY ALL
ORDER BY contracts DESC, governing_law
