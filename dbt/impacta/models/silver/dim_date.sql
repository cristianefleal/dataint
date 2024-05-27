WITH RECURSIVE dates_cte AS (
    SELECT '2023-01-01'::DATE AS full_date
    UNION ALL
    SELECT (full_date + INTERVAL '1 day')::DATE
    FROM dates_cte
    WHERE (full_date + INTERVAL '1 day')::DATE <= '2024-01-01'::DATE
)

SELECT
    full_date,
    TO_CHAR(full_date, 'Day') AS day_of_week,
    EXTRACT(DAY FROM full_date) AS day,
    EXTRACT(MONTH FROM full_date) AS month,
    EXTRACT(YEAR FROM full_date) AS year,
    CEIL(EXTRACT(MONTH FROM full_date) / 3.0) AS quarter,
    CASE WHEN full_date IN ('2023-01-01', '2023-12-25') THEN TRUE ELSE FALSE END AS is_holiday
FROM dates_cte