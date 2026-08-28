import schedule
import time
import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src"
    )
)

from generate_synthetic import generate_daily_batch
from incremental_pipeline import process_new_sales


def job():

    print()
    print("=" * 60)
    print("DAILY SALES PIPELINE STARTED")
    print("=" * 60)

    # Generate new sales
    generate_daily_batch(50)

    # Process new sales
    process_new_sales()

    print("=" * 60)
    print("DAILY SALES PIPELINE FINISHED")
    print("=" * 60)


# Run every day at 09:00
schedule.every().day.at("09:00").do(job)


if __name__ == "__main__":

    print("Daily scheduler started.")
    print("Scheduled time: 09:00 every day")
    print("Waiting for scheduled job...")

    while True:

        schedule.run_pending()

        time.sleep(60)