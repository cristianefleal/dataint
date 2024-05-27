{{
  config(
    schema='silver',
  )
}}

SELECT DISTINCT store_id, store_location 
FROM {{ ref('raw_coffeeshop') }}