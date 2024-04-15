{{
  config(materialized='table')
}}

with symbol_hist_data as
(
  select *
  from {{ source('original','stock_data') }}
)
select
  -- identifiers
  {{ dbt_utils.generate_surrogate_key(['dispatching_base_num', 'pickup_datetime']) }} as tripid,
  transaction_date,
  open,
  high,
  low,
  close,
  volume,
  symbol
from symbol_hist_data
