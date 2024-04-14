CREATE TABLE IF NOT EXISTS symbols (
    nasdaq_traded VARCHAR(255),
    symbol VARCHAR(255),
    security_name VARCHAR(255),
    listing_exchange VARCHAR(255),
    market_category VARCHAR(255),
    etf VARCHAR(255),
    round_lot_size DOUBLE PRECISION,
    test_issue VARCHAR(255),
    financial_status VARCHAR(255),
    cqs_symbol VARCHAR(255),
    nasdaq_symbol VARCHAR(255),
    nextshares VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS stock_data (
    transaction_date DATE NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,
    volume BIGINT,
    symbol VARCHAR(10) NOT NULL
) PARTITION BY LIST (Symbol);

CREATE TABLE IF NOT EXISTS etf_data (
    transaction_date DATE NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,
    volume BIGINT,
    symbol VARCHAR(10) NOT NULL
) PARTITION BY LIST (Symbol);
