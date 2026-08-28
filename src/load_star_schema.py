import pandas as pd
from config import get_engine


def load_star_schema():

    print("Starting star schema loading...")

    engine = get_engine()

    print("Clearing existing star schema...")

    with engine.begin() as connection:
        connection.exec_driver_sql(
            "TRUNCATE TABLE fact_sales, dim_customer, dim_product, dim_date CASCADE"
        )

    print("Existing star schema cleared.")

    # ---------------------------------------------------------
    # Read cleaned data
    # ---------------------------------------------------------

    print("Reading cleaned CSV...")

    df = pd.read_csv(
        "data/processed/cleaned_sales.csv",
        parse_dates=["invoice_date"]
    )

    print(f"Cleaned rows loaded: {len(df)}")

    # ---------------------------------------------------------
    # DIM CUSTOMER
    # ---------------------------------------------------------

    print("Loading dim_customer...")

    dim_customer = (
        df[
            [
                "customer_id",
                "country",
                "customer_segment"
            ]
        ]
        .drop_duplicates("customer_id")
        .copy()
    )

    dim_customer.to_sql(
        "dim_customer",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000
    )

    print(
        f"dim_customer loaded: {len(dim_customer)} rows"
    )

    # ---------------------------------------------------------
    # DIM PRODUCT
    # ---------------------------------------------------------

    print("Loading dim_product...")

    dim_product = (
        df[
            [
                "stock_code",
                "description"
            ]
        ]
        .drop_duplicates("stock_code")
        .copy()
    )

    dim_product.to_sql(
        "dim_product",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000
    )

    print(
        f"dim_product loaded: {len(dim_product)} rows"
    )

    # ---------------------------------------------------------
    # DIM DATE
    # ---------------------------------------------------------

    print("Loading dim_date...")

    dates = pd.DataFrame({
        "date_key": df["invoice_date"].dt.normalize().unique()
    })

    dates["date_key"] = pd.to_datetime(
        dates["date_key"]
    )

    dates["day"] = dates["date_key"].dt.day

    dates["month"] = dates["date_key"].dt.month

    dates["month_name"] = (
        dates["date_key"].dt.month_name()
    )

    dates["quarter"] = (
        dates["date_key"].dt.quarter
    )

    dates["year"] = (
        dates["date_key"].dt.year
    )

    dates["weekday_name"] = (
        dates["date_key"].dt.day_name()
    )

    dates.to_sql(
        "dim_date",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000
    )

    print(
        f"dim_date loaded: {len(dates)} rows"
    )

    # ---------------------------------------------------------
    # FACT SALES
    # ---------------------------------------------------------

    print("Loading fact_sales...")

    fact_sales = df[
        [
            "invoice_no",
            "stock_code",
            "customer_id",
            "quantity",
            "unit_price",
            "total_order_value"
        ]
    ].copy()

    fact_sales["date_key"] = (
        df["invoice_date"].dt.normalize()
    )

    fact_sales = fact_sales[
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

    fact_sales.to_sql(
        "fact_sales",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi"
    )

    print(
        f"fact_sales loaded: {len(fact_sales)} rows"
    )

    print()
    print("Star schema loaded successfully!")


if __name__ == "__main__":
    load_star_schema()