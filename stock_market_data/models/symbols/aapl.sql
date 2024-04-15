{{
  config(materialized='table')
}}

with symbol_hist_data as
(
  select *
  from {{ source('original','stock_data') }}
)
select
  transaction_date,
  open,
  high,
  low,
  close,
  volume,
  symbol
from symbol_hist_data
where symbol = 'AAPL'
