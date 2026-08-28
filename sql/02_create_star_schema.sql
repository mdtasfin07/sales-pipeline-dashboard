DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_date;


CREATE TABLE dim_customer (
    customer_id       VARCHAR(20) PRIMARY KEY,
    country           VARCHAR(100),
    customer_segment  VARCHAR(20)
);


CREATE TABLE dim_product (
    stock_code   VARCHAR(20) PRIMARY KEY,
    description  TEXT
);


CREATE TABLE dim_date (
    date_key       DATE PRIMARY KEY,
    day            INTEGER,
    month          INTEGER,
    month_name     VARCHAR(20),
    quarter        INTEGER,
    year           INTEGER,
    weekday_name   VARCHAR(20)
);


CREATE TABLE fact_sales (
    sales_id            BIGSERIAL PRIMARY KEY,
    invoice_no          VARCHAR(20) NOT NULL,
    stock_code          VARCHAR(20) NOT NULL,
    customer_id         VARCHAR(20) NOT NULL,
    date_key            DATE NOT NULL,
    quantity            INTEGER NOT NULL,
    unit_price          NUMERIC(10,2) NOT NULL,
    total_order_value   NUMERIC(12,2) NOT NULL,

    CONSTRAINT fk_product
        FOREIGN KEY (stock_code)
        REFERENCES dim_product(stock_code),

    CONSTRAINT fk_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customer(customer_id),

    CONSTRAINT fk_date
        FOREIGN KEY (date_key)
        REFERENCES dim_date(date_key)
);