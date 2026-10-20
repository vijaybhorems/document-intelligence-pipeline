-- Contracts per type, with length. Types drive split stratification.
SELECT
    d.contract_type,
    count(*)                      AS contracts,
    median(d.text_chars)::INT     AS median_chars,
    median(t.pages)::INT          AS median_pages,
    max(t.pages)                  AS max_pages
FROM documents d
JOIN text_layer t USING (doc_id)
GROUP BY ALL
ORDER BY contracts DESC, d.contract_type;
