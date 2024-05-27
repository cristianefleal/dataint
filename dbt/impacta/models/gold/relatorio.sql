{{
  config(
    materialized='view',
    schema='gold',
  )
}}

SELECT
    product_category,
    SUM(total_bill) AS total_sales
FROM
    {{ ref('fato_coffeeshop') }} t
JOIN
    {{ ref('dim_produto') }} p
ON
    t.product_id = p.product_id
GROUP BY
    product_category