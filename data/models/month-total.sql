SELECT
    DATE_TRUNC('month', date) AS date,
    COUNT(report) AS total
FROM 
    read_parquet('{processed_path}')
GROUP BY
    1
ORDER BY
    1 ASC;