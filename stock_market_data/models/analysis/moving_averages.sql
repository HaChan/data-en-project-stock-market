SELECT
  symbol,
  transaction_date,
  close,
  AVG(close) OVER (PARTITION BY symbol ORDER BY transaction_date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS moving_avg_20,
  AVG(close) OVER (PARTITION BY symbol ORDER BY transaction_date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) AS moving_avg_50
FROM
  {{ source('original', 'stock_data') }}
