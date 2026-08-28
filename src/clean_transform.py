import pandas as pd
from config import get_engine


def clean_sales_data():

    print("Starting data cleaning...")

    engine = get_engine()

    # Read raw data from PostgreSQL
    df = pd.read_sql("SELECT * FROM raw_sales", engine)

    original_rows = len(df)

    print(f"Original rows: {original_rows}")

    # ---------------------------------------------------------
    # 1. Convert data types
    # ---------------------------------------------------------

    df["invoice_no"] = df["invoice_no"].astype(str).str.strip()
    df["stock_code"] = df["stock_code"].astype(str).str.strip()
    df["description"] = df["description"].astype("string").str.strip()
    df["country"] = df["country"].astype("string").str.strip()

    df["invoice_date"] = pd.to_datetime(
        df["invoice_date"],
        errors="coerce"
    )

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    )

    df["unit_price"] = pd.to_numeric(
        df["unit_price"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # 2. Remove rows missing important information
    # ---------------------------------------------------------

    df = df.dropna(
        subset=[
            "invoice_no",
            "stock_code",
            "description",
            "invoice_date",
            "customer_id"
        ]
    )

    print(f"After removing missing values: {len(df)}")

    # ---------------------------------------------------------
    # 3. Clean customer IDs
    # ---------------------------------------------------------

    df["customer_id"] = pd.to_numeric(
        df["customer_id"],
        errors="coerce"
    )

    df = df.dropna(subset=["customer_id"])

    df["customer_id"] = (
        df["customer_id"]
        .astype("int64")
        .astype(str)
    )

    # ---------------------------------------------------------
    # 4. Remove cancelled invoices
    # ---------------------------------------------------------

    cancelled = df["invoice_no"].str.startswith("C")

    cancelled_count = cancelled.sum()

    df = df[~cancelled]

    print(f"Cancelled invoice rows removed: {cancelled_count}")

    # ---------------------------------------------------------
    # 5. Remove invalid quantities and prices
    # ---------------------------------------------------------

    before_invalid = len(df)

    df = df[
        (df["quantity"] > 0) &
        (df["unit_price"] > 0)
    ]

    invalid_count = before_invalid - len(df)

    print(f"Invalid quantity/price rows removed: {invalid_count}")

    # ---------------------------------------------------------
    # 6. Remove exact duplicate rows
    # ---------------------------------------------------------

    before_duplicates = len(df)

    df = df.drop_duplicates()

    duplicate_count = before_duplicates - len(df)

    print(f"Duplicate rows removed: {duplicate_count}")

    # ---------------------------------------------------------
    # 7. Create total order value
    # ---------------------------------------------------------

    df["total_order_value"] = (
        df["quantity"] * df["unit_price"]
    )

    # ---------------------------------------------------------
    # 8. Create date-related fields
    # ---------------------------------------------------------

    df["order_date"] = df["invoice_date"].dt.date

    df["order_month"] = (
        df["invoice_date"]
        .dt.to_period("M")
        .astype(str)
    )

    df["order_year"] = df["invoice_date"].dt.year

    # ---------------------------------------------------------
    # 9. Customer segmentation
    # ---------------------------------------------------------

    spend_per_customer = (
        df.groupby("customer_id")["total_order_value"]
        .sum()
    )

    def segment(customer_id):

        spend = spend_per_customer.get(customer_id, 0)

        if spend > 2000:
            return "High Value"

        elif spend > 500:
            return "Mid Value"

        else:
            return "Low Value"

    df["customer_segment"] = (
        df["customer_id"].apply(segment)
    )

    # ---------------------------------------------------------
    # 10. Sort data
    # ---------------------------------------------------------

    df = df.sort_values(
        by="invoice_date"
    ).reset_index(drop=True)

    # ---------------------------------------------------------
    # 11. Save processed CSV
    # ---------------------------------------------------------

    output_path = "data/processed/cleaned_sales.csv"

    df.to_csv(
        output_path,
        index=False
    )

    # ---------------------------------------------------------
    # 12. Print final summary
    # ---------------------------------------------------------

    print()
    print("Cleaning completed successfully.")
    print(f"Original rows: {original_rows}")
    print(f"Final rows: {len(df)}")
    print(f"Rows removed: {original_rows - len(df)}")
    print(f"Processed file: {output_path}")

    return df


if __name__ == "__main__":
    clean_sales_data()