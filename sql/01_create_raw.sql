DROP TABLE IF EXISTS raw_sales;

CREATE TABLE raw_sales (
    invoice_no      VARCHAR(20),
    stock_code      VARCHAR(20),
    description     TEXT,
    quantity        INTEGER,
    invoice_date    TIMESTAMP,
    unit_price      NUMERIC(10,2),
    customer_id     VARCHAR(20),
    country         VARCHAR(100),
    loaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);