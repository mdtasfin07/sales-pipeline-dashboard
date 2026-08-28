from ingest_raw import ingest_raw_csv
from clean_transform import clean_sales_data
from load_star_schema import load_star_schema


def run_pipeline():

    print("=" * 60)
    print("SALES DATA PIPELINE STARTED")
    print("=" * 60)

    print("\n[1/3] RAW INGESTION")
    ingest_raw_csv()

    print("\n[2/3] CLEANING & TRANSFORMATION")
    clean_sales_data()

    print("\n[3/3] STAR SCHEMA LOADING")
    load_star_schema()

    print("\n" + "=" * 60)
    print("SALES DATA PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()