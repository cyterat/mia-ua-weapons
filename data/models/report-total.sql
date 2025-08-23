SELECT
    report,
    COUNT(*) AS total
FROM 
    read_parquet('{processed_path}')
GROUP BY
    report
ORDER BY
    report ASC;