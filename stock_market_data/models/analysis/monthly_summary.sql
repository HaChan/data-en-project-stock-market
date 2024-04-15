SELECT
  symbol,
  DATE_TRUNC('month', transaction_date) AS month,
  AVG(close) AS avg_close_price,
  SUM(volume) AS total_volume,
  AVG(high - low) AS avg_daily_movement
FROM
  {{ source('original', 'stock_data') }}
GROUP BY
  symbol, month
