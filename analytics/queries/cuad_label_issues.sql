-- Where CUAD's two label sources disagree or the answer couldn't be normalized.
SELECT field, kind, count(*) AS n, any_value(detail)[:80] AS example
FROM label_issues
GROUP BY ALL
ORDER BY n DESC, field;
