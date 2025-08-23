SELECT
    weaponcategory,
    COUNT(report) AS total,
    COUNT(*) FILTER(WHERE report == 'Loss') AS loss,
    COUNT(*) FILTER(WHERE report == 'Theft') AS theft
FROM 
    read_parquet('{processed_path}')
WHERE
    weaponcategory NOT NULL
GROUP BY
    weaponcategory
ORDER BY
    total DESC;