import os
import csv
import psycopg2
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from dotenv import load_dotenv


def load_env():
    """Load environment variables from a .env file."""
    load_dotenv()


def parse_date(raw_date: str) -> str:
    """Convert date from '19 Jan 2022, 10:14 PM' to 'YYYY-MM-DD HH:MM AM/PM'."""
    dt = datetime.strptime(raw_date, "%d %b %Y, %I:%M %p")
    return dt.strftime("%Y-%m-%d %I:%M %p")


def parse_float(value: str) -> float:
    """Parse string to float and round to 3 decimal places."""
    if value.strip() == "":
        return 0.0
    rounded = Decimal(value.replace(',', '')).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    return float(rounded)


def read_csv(file_path: str) -> list[tuple]:
    """Read and process CSV data into a list of tuples."""
    records = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            record = (
                parse_date(row["Date"]),
                row["Transaction Type"],
                row["Description"],
                row["Money Movement"],
                parse_float(row["Amount ($)"]),
                parse_float(row["Updated Balance ($)"])
            )
            records.append(record)
    return records


def insert_records_in_batches(records: list[tuple], connection, batch_size=10):
    """Insert records into the table in batches of 10. Stop if any error occurs."""
    with connection.cursor() as cursor:
        insert_query = """
        INSERT INTO indmoney_ledger 
        (date, transaction_type, description, money_movement, amount_in_dollars, updated_balance_in_dollars)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                cursor.executemany(insert_query, batch)
                connection.commit()
            except (psycopg2.errors.UniqueViolation, psycopg2.errors.IntegrityError) as e:
                print(f"Error occurred: {e}. Stopping further processing.")
                connection.rollback()
                break


def get_db_connection():
    """Establish and return a PostgreSQL DB connection using environment variables."""
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
        insert_records_in_batches(records, conn)


if __name__ == "__main__":
    main("/Users/lokeshsanapalli/projects/personal_finance/statements/stocks/ind_money_ledger.csv")
