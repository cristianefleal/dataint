{{
  config(
    schema='silver',
  )
}}

SELECT DISTINCT product_id, product_category, product_type, product_detail, size, unit_price 
FROM {{ ref('raw_coffeeshop') }}