-- Tabela de preços
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    datetime TIMESTAMP,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    ma9 NUMERIC,
    ma21 NUMERIC,
    trend VARCHAR(10)
);

-- Tabela de ordens DEMO (simples)
CREATE TABLE IF NOT EXISTS demo_orders (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    side VARCHAR(10), -- BUY ou SELL
    quantity INT,
    price NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);