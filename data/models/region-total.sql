WITH AllRecords AS (
    SELECT
        COUNT(report) AS grand_total
    FROM 
        read_parquet('{processed_path}')
)

SELECT
    region,
    COUNT(report) AS total,
    COUNT(report) FILTER(WHERE report = 'Loss') AS loss,
    COUNT(report) FILTER(WHERE report = 'Theft') AS theft,
    CAST(COUNT(report) AS FLOAT) / AllRecords.grand_total AS total_pct,
    CAST(COUNT(report) FILTER(WHERE report = 'Loss') AS FLOAT) / COUNT(report) AS loss_pct,
    CAST(COUNT(report) FILTER(WHERE report = 'Theft') AS FLOAT) / COUNT(report) AS theft_pct
FROM 
    read_parquet('{processed_path}'),
    AllRecords
GROUP BY
    region,
    AllRecords.grand_total
ORDER BY
    total DESC;
