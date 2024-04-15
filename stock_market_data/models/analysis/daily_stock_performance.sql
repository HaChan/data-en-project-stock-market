WITH base AS (
  SELECT
    symbol,
    transaction_date,
    open,
    close,
    high,
    low,
    volume,
    LAG(volume) OVER (PARTITION BY symbol ORDER BY transaction_date) AS previous_volume
  FROM
    {{ source('original', 'stock_data') }}
)

SELECT
  symbol,
  transaction_date,
  open,
  close,
  high,
  low,
  volume,
  CASE
    WHEN open IS NULL OR open = 0 THEN NULL
    ELSE ROUND(((close - open) / open * 100)::numeric, 2)
  END AS daily_change_pct,
  high - low AS daily_spread,
  CASE
    WHEN previous_volume IS NULL OR previous_volume = 0 THEN NULL
    ELSE ROUND(((volume - previous_volume) / previous_volume * 100)::numeric, 2)
  END AS volume_change_pct
FROM
  base
