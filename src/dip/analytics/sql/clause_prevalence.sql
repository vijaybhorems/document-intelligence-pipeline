-- Clause prevalence by contract type (SPEC §9.3): of the contracts of each type, how
-- many contain each clause. One record per document: the latest extraction.
SELECT
    r.contract_type,
    f.clause_family,
    f.field                        AS clause,
    count(*)                       AS contracts,
    count(*) FILTER (WHERE f.present) AS with_clause,
    round(avg(f.present::INTEGER), 3) AS prevalence
FROM latest_records AS r
JOIN record_fields AS f USING (record_id)
WHERE f.field_type = 'clause'
GROUP BY ALL
HAVING count(*) >= $min_contracts
ORDER BY r.contract_type, prevalence DESC, clause
