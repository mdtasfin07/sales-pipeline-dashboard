import csv
import os
import sys

import psycopg2
from dotenv import load_dotenv


# Add project src directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def ingest_raw_csv(csv_path="data/raw/online_retail_II.csv"):

    print("Starting raw data ingestion...")

    connection = get_connection()
    cursor = connection.cursor()

    cursor = connection.cursor()

    cursor.execute("TRUNCATE TABLE raw_sales")

    connection.commit()

    print("raw_sales table cleared.")

    try:
        with open(csv_path, "r", encoding="ISO-8859-1", newline="") as file:

            reader = csv.reader(file)

            # Skip CSV header
            header = next(reader)

            print("CSV columns:")
            print(header)

            rows = []

            for row in reader:

                if len(row) < 8:
                    continue

                rows.append((
                    row[0],
                    row[1],
                    row[2],
                    row[3] if row[3] else None,
                    row[4] if row[4] else None,
                    row[5] if row[5] else None,
                    row[6] if row[6] else None,
                    row[7]
                ))

                if len(rows) >= 5000:
                    cursor.executemany(
                        """
                        INSERT INTO raw_sales
                        (
                            invoice_no,
                            stock_code,
                            description,
                            quantity,
                            invoice_date,
                            unit_price,
                            customer_id,
                            country
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        rows
                    )

                    connection.commit()

                    print(f"Loaded {len(rows)} rows...")

                    rows = []

            # Insert remaining rows
            if rows:
                cursor.executemany(
                    """
                    INSERT INTO raw_sales
                    (
                        invoice_no,
                        stock_code,
                        description,
                        quantity,
                        invoice_date,
                        unit_price,
                        customer_id,
                        country
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    rows
                )

                connection.commit()

                print(f"Loaded final {len(rows)} rows.")

        print("Raw data ingestion completed successfully.")

    except Exception as e:

        connection.rollback()

        print("ERROR during ingestion:")
        print(e)

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    ingest_raw_csv()