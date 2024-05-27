{{
  config(
    schema='silver',
  )
}}

SELECT DISTINCT transaction_id, transaction_date, transaction_time, store_id, product_id, transaction_qty, total_bill  
FROM {{ ref('raw_coffeeshop') }}