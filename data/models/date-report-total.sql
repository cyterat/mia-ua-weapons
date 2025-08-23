SELECT
    date,
    report,
    COUNT(report) AS total
FROM 
    read_parquet('{processed_path}')
GROUP BY
    1,2
ORDER BY
    date ASC,
    report ASC;