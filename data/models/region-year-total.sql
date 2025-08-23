WITH AllRecords AS (
    SELECT
        COUNT(report) AS grand_total
    FROM 
        read_parquet('{processed_path}')
)

SELECT
    region,
    DATE_TRUNC('year', date) + INTERVAL 1 YEAR - INTERVAL 1 DAY AS date,
    COUNT(report) FILTER (WHERE report = 'Loss') AS loss,
    COUNT(report) FILTER (WHERE report = 'Theft') AS theft,
    COUNT(report) AS total,
    COALESCE(CAST(COUNT(report) FILTER (WHERE report = 'Loss') AS FLOAT) 
             / NULLIF(COUNT(report), 0), 0) AS loss_pct,   -- local %
    COALESCE(CAST(COUNT(report) FILTER (WHERE report = 'Theft') AS FLOAT) 
             / NULLIF(COUNT(report), 0), 0) AS theft_pct, -- local %
    COALESCE(CAST(COUNT(report) AS FLOAT) 
             / NULLIF(AllRecords.grand_total, 0), 0) AS total_pct  -- global %
FROM 
    read_parquet('{processed_path}'),
    AllRecords
GROUP BY
    1,
    2,
    AllRecords.grand_total
ORDER BY
    region ASC,
    date ASC;