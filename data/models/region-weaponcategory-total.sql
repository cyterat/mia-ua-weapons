WITH RegWepTot AS(
    SELECT
        region,
        weaponcategory,
        COUNT(report) AS total
    FROM
        read_parquet('{processed_path}')
    GROUP BY
        region,
        weaponcategory
)

SELECT
    region,
    weaponcategory,
    total,
    DENSE_RANK() OVER(PARTITION BY region ORDER BY total DESC) AS local_rank,
    DENSE_RANK() OVER(ORDER BY total DESC) AS country_rank,
    COALESCE(CAST(LOG(total) / LOG(100) AS FLOAT), 0) AS total_log100,
    CAST(SUM(total) OVER(PARTITION BY region) AS INTEGER) AS total_region,
    CAST(SUM(total) OVER() AS INTEGER) AS total_country

FROM
    RegWepTot
ORDER BY
    region ASC,
    weaponcategory ASC;
