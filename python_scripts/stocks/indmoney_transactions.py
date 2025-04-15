import os
import csv
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

import psycopg2
from psycopg2 import IntegrityError, errors
from dotenv import load_dotenv


def load_env():
    """Load environment variables from .env file."""
    load_dotenv()


def parse_date(raw_date: str) -> str:
    """Convert '19 Jan 2022, 10:14 PM' to 'YYYY-MM-DD HH:MM AM/PM' format."""
    dt = datetime.strptime(raw_date, "%d %b %Y, %I:%M %p")
    return dt.strftime("%Y-%m-%d %I:%M %p")


def parse_float(value: str) -> float:
    """Convert string to float rounded to 2 decimal places."""
    if not value.strip():
        return 0.0
    return float(Decimal(value.replace(',', '')).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def read_csv(file_path: str) -> list[tuple]:
    """Parse and prepare records from CSV file."""
    records = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            record = (
                row["Stock Name"],
                row["Stock Symbol"],
                parse_date(row["Order Placed Time"]),
                parse_date(row["Order Execution Time"]),
                row["Broker Reference Id"],
                row["Transaction Type"],
                row["Order Type"],
                parse_float(row["Quantity"]),
                parse_float(row["Price ($)"]),
                parse_float(row["Order Amount ($)"]),
                parse_float(row["Brokerage ($)"]),
            )
            records.append(record)
    return records


def insert_batches(records: list[tuple], connection, batch_size: int = 10):
    """Insert records in batches; stop on unique/integrity violation."""
    insert_query = """
    INSERT INTO indmoney_transactions 
    (stock_name, stock_symbol, order_placed_time, order_execution_time, broker_reference_id, 
     transaction_type, order_type, quantity, price_in_dollars, order_amount_in_dollars, brokerage)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with connection.cursor() as cursor:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                cursor.executemany(insert_query, batch)
                connection.commit()
            except (errors.UniqueViolation, IntegrityError) as e:
                print(f"Database error: {e}. Stopping batch insert.")
                connection.rollback()
                break


def get_db_connection():
    """Establish DB connection using env variables."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


def main(csv_file_path: str):
    load_env()
    records = read_csv(csv_file_path)
    with get_db_connection() as conn:
        insert_batches(records, conn)


if __name__ == "__main__":
    main("/Users/lokeshsanapalli/projects/personal_finance/statements/stocks/ind_money_report.csv")
