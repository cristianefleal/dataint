-- Criação da tabela para a dimensão de data
CREATE TABLE impacta.public.dim_date (
    full_date DATE,
    day_of_week VARCHAR(20),
    day int,
    month int,
    year INT,
    quarter INT,
    is_holiday BOOLEAN
);

SET total_time = (SELECT DATEDIFF(DAY, '2023-01-01', '2024-01-01'));

INSERT INTO impacta.public.dim_date (full_date, day_of_week, day, month, year, quarter, is_holiday)
WITH dates_cte AS (
    SELECT DATEADD(DAY, seq8(), TO_DATE('2023-01-01')) AS full_date
    FROM TABLE(GENERATOR(ROWCOUNT => $total_time))
)
SELECT
    full_date,
    DAYNAME(full_date) AS day_of_week,
    DAY(full_date),
    month(full_date) AS month,
    YEAR(full_date) AS year,
    CEIL(TO_NUMBER(TO_CHAR(full_date, 'MM')) / 3) AS quarter,
    CASE WHEN full_date IN ('2023-01-01', '2023-12-25') THEN TRUE ELSE FALSE END AS is_holiday
FROM dates_cte;

-- Verificação dos dados inseridos
SELECT * FROM impacta.public.dim_date ORDER BY full_date LIMIT 100;