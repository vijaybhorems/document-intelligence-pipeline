-- Split sizes and composition.
SELECT
    s.split,
    count(*)                         AS contracts,
    count(DISTINCT d.contract_type)  AS contract_types,
    median(d.text_chars)::INT        AS median_chars,
    max(d.text_chars)                AS max_chars
FROM splits s
JOIN documents d USING (doc_id)
GROUP BY ALL
ORDER BY contracts DESC;
