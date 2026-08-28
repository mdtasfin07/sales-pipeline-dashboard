import random
from datetime import datetime

import pandas as pd
from faker import Faker

from config import get_engine


fake = Faker()


def generate_daily_batch(n_orders=50):

    print("Starting synthetic data generation...")

    engine = get_engine()

    # Get existing products
    existing_products = pd.read_sql(
        """
        SELECT stock_code, description
        FROM dim_product
        """,
        engine
    )

    # Get existing customers
    existing_customers = pd.read_sql(
        """
        SELECT customer_id, country
        FROM dim_customer
        """,
        engine
    )

    if existing_products.empty:
        print("No products found.")
        return

    if existing_customers.empty:
        print("No customers found.")
        return

    rows = []

    for _ in range(n_orders):

        product = existing_products.sample(
            1
        ).iloc[0]

        customer = existing_customers.sample(
            1
        ).iloc[0]

        rows.append(
            {
                "invoice_no": f"SYN{random.randint(100000, 999999)}",

                "stock_code": str(
                    product["stock_code"]
                ),

                "description": product["description"],

                "quantity": random.randint(1, 10),

                "invoice_date": datetime.now(),

                "unit_price": round(
                    random.uniform(1, 50),
                    2
                ),

                "customer_id": str(
                    customer["customer_id"]
                ),

                "country": customer["country"]
            }
        )

    df = pd.DataFrame(rows)

    # Insert into raw table
    df.to_sql(
        "raw_sales",
        engine,
        if_exists="append",
        index=False,
        chunksize=1000
    )

    print(
        f"Inserted {len(df)} synthetic rows."
    )

    print(
        f"Generated at: {datetime.now()}"
    )


if __name__ == "__main__":
    generate_daily_batch()