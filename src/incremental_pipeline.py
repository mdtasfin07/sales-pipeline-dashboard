import pandas as pd
from sqlalchemy import text

from config import get_engine


def read_query(engine, query):
    with engine.connect() as connection:
        return pd.read_sql(
            text(query),
            connection
        )


def process_new_sales():

    print("Starting incremental pipeline...")

    engine = get_engine()

    # ---------------------------------------------------------
    # 1. Find synthetic records not already in fact_sales
    # ---------------------------------------------------------

    new_sales = read_query(
        engine,
        """
        SELECT
            r.invoice_no,
            r.stock_code,
            r.description,
            r.quantity,
            r.invoice_date,
            r.unit_price,
            r.customer_id,
            r.country
        FROM raw_sales r
        LEFT JOIN fact_sales f
            ON r.invoice_no = f.invoice_no
        WHERE r.invoice_no LIKE 'SYN%'
          AND f.invoice_no IS NULL
        """
    )

    if new_sales.empty:

        print("No new sales found.")

        return

    print(
        f"New records found: {len(new_sales)}"
    )

    # ---------------------------------------------------------
    # 2. Clean new records
    # ---------------------------------------------------------

    new_sales["invoice_date"] = pd.to_datetime(
        new_sales["invoice_date"],
        errors="coerce"
    )

    new_sales["quantity"] = pd.to_numeric(
        new_sales["quantity"],
        errors="coerce"
    )

    new_sales["unit_price"] = pd.to_numeric(
        new_sales["unit_price"],
        errors="coerce"
    )

    new_sales["customer_id"] = (
        new_sales["customer_id"]
        .astype(str)
        .str.replace(".0", "", regex=False)
    )

    new_sales = new_sales.dropna(
        subset=[
            "invoice_no",
            "stock_code",
            "customer_id",
            "invoice_date"
        ]
    )

    new_sales = new_sales[
        (new_sales["quantity"] > 0) &
        (new_sales["unit_price"] > 0)
    ]

    # ---------------------------------------------------------
    # 3. Calculate revenue
    # ---------------------------------------------------------

    new_sales["total_order_value"] = (
        new_sales["quantity"] *
        new_sales["unit_price"]
    )

    # ---------------------------------------------------------
    # 4. Update product dimension
    # ---------------------------------------------------------

    products = new_sales[
        [
            "stock_code",
            "description"
        ]
    ].drop_duplicates("stock_code")

    existing_products = read_query(
        engine,
        """
        SELECT stock_code
        FROM dim_product
        """
    )

    new_products = products[
        ~products["stock_code"].isin(
            existing_products["stock_code"]
        )
    ]

    if not new_products.empty:

        new_products.to_sql(
            "dim_product",
            engine,
            if_exists="append",
            index=False
        )

        print(
            f"New products added: {len(new_products)}"
        )

    # ---------------------------------------------------------
    # 5. Update customer dimension
    # ---------------------------------------------------------

    customers = new_sales[
        [
            "customer_id",
            "country"
        ]
    ].drop_duplicates("customer_id")

    existing_customers = read_query(
        engine,
        """
        SELECT customer_id
        FROM dim_customer
        """
    )

    new_customers = customers[
        ~customers["customer_id"].isin(
            existing_customers["customer_id"]
        )
    ].copy()

    if not new_customers.empty:

        new_customers["customer_segment"] = "Low Value"

        new_customers.to_sql(
            "dim_customer",
            engine,
            if_exists="append",
            index=False
        )

        print(
            f"New customers added: {len(new_customers)}"
        )

    # ---------------------------------------------------------
    # 6. Update date dimension
    # ---------------------------------------------------------

    new_dates = pd.DataFrame(
        {
            "date_key":
                new_sales["invoice_date"]
                .dt.normalize()
                .drop_duplicates()
        }
    )

    new_dates["day"] = (
        new_dates["date_key"].dt.day
    )

    new_dates["month"] = (
        new_dates["date_key"].dt.month
    )

    new_dates["month_name"] = (
        new_dates["date_key"].dt.month_name()
    )

    new_dates["quarter"] = (
        new_dates["date_key"].dt.quarter
    )

    new_dates["year"] = (
        new_dates["date_key"].dt.year
    )

    new_dates["weekday_name"] = (
        new_dates["date_key"].dt.day_name()
    )

    existing_dates = read_query(
        engine,
        """
        SELECT date_key
        FROM dim_date
        """
    )

    existing_dates["date_key"] = pd.to_datetime(
        existing_dates["date_key"]
    )

    new_dates = new_dates[
        ~new_dates["date_key"].isin(
            existing_dates["date_key"]
        )
    ]

    if not new_dates.empty:

        new_dates.to_sql(
            "dim_date",
            engine,
            if_exists="append",
            index=False
        )

        print(
            f"New dates added: {len(new_dates)}"
        )

    # ---------------------------------------------------------
    # 7. Insert into fact_sales
    # ---------------------------------------------------------

    fact = new_sales[
        [
            "invoice_no",
            "stock_code",
            "customer_id",
            "quantity",
            "unit_price",
            "total_order_value"
        ]
    ].copy()

    fact["date_key"] = (
        new_sales["invoice_date"]
        .dt.normalize()
    )

    fact = fact[
        [
            "invoice_no",
            "stock_code",
            "customer_id",
            "date_key",
            "quantity",
            "unit_price",
            "total_order_value"
        ]
    ]

    fact.to_sql(
        "fact_sales",
        engine,
        if_exists="append",
        index=False,
        chunksize=1000,
        method="multi"
    )

    print(
        f"Inserted {len(fact)} rows into fact_sales."
    )

    print(
        "Incremental pipeline completed successfully."
    )


if __name__ == "__main__":
    process_new_sales()