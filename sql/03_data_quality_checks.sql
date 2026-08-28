-- =========================================================
-- SALES PIPELINE DATA QUALITY CHECKS
-- =========================================================


-- 1. Check total fact rows
SELECT
    COUNT(*) AS total_fact_rows
FROM fact_sales;


-- 2. Check NULL customer IDs
SELECT
    COUNT(*) AS null_customer_ids
FROM fact_sales
WHERE customer_id IS NULL;


-- 3. Check NULL product IDs
SELECT
    COUNT(*) AS null_product_ids
FROM fact_sales
WHERE stock_code IS NULL;


-- 4. Check NULL dates
SELECT
    COUNT(*) AS null_dates
FROM fact_sales
WHERE date_key IS NULL;


-- 5. Check invalid quantities
SELECT
    COUNT(*) AS invalid_quantities
FROM fact_sales
WHERE quantity <= 0;


-- 6. Check invalid unit prices
SELECT
    COUNT(*) AS invalid_prices
FROM fact_sales
WHERE unit_price <= 0;


-- 7. Check invalid revenue
SELECT
    COUNT(*) AS invalid_revenue
FROM fact_sales
WHERE total_order_value <= 0;


-- 8. Check orphan customers
SELECT
    COUNT(*) AS orphan_customers
FROM fact_sales f
LEFT JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- 9. Check orphan products
SELECT
    COUNT(*) AS orphan_products
FROM fact_sales f
LEFT JOIN dim_product p
    ON f.stock_code = p.stock_code
WHERE p.stock_code IS NULL;


-- 10. Check orphan dates
SELECT
    COUNT(*) AS orphan_dates
FROM fact_sales f
LEFT JOIN dim_date d
    ON f.date_key = d.date_key
WHERE d.date_key IS NULL;


-- 11. Verify revenue calculation
SELECT
    COUNT(*) AS incorrect_revenue_rows
FROM fact_sales
WHERE total_order_value <>
      ROUND(quantity * unit_price, 2);


-- 12. Check duplicate transaction lines
SELECT
    invoice_no,
    stock_code,
    customer_id,
    date_key,
    quantity,
    unit_price,
    COUNT(*) AS duplicate_count
FROM fact_sales
GROUP BY
    invoice_no,
    stock_code,
    customer_id,
    date_key,
    quantity,
    unit_price
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;