WITH dim_date AS (
    SELECT DATEADD(DAY, seq8(), TO_DATE('2023-01-01')) AS full_date
    FROM TABLE(GENERATOR(ROWCOUNT => SELECT DATEDIFF(DAY, '2023-01-01', '2024-01-01')))
)
SELECT
    full_date,
    DAYNAME(full_date) AS day_of_week,
    DAY(full_date) As day,
    month(full_date) AS month,
    YEAR(full_date) AS year,
    CEIL(TO_NUMBER(TO_CHAR(full_date, 'MM')) / 3) AS quarter,
    CASE WHEN full_date IN ('2023-01-01', '2023-12-25') THEN TRUE ELSE FALSE END AS is_holiday
FROM dim_date