{{
  config(
    schema='bronze',
  )
}}

WITH raw_coffeeshop AS (
    SELECT transaction_id,
           TO_DATE(transaction_date,'DD/MM/YYYY') AS transaction_date,
           transaction_time::time AS transaction_time,
           store_id,
           store_location,
           product_id,
           transaction_qty::int AS transaction_qty,
           unit_price::numeric AS unit_price,
           product_category,
           product_type,
           product_detail,
           size,
           total_bill::numeric AS total_bill,
           month_name,
           day_name,
           hour::int AS hour,
           day_of_week,
           month::int AS month
    FROM {{ source('dw', 'airbyte_daily_raw_coffeeshop') }}
)
SELECT *
FROM raw_coffeeshop