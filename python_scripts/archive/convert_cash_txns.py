import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql, IntegrityError

from common import convert_date_format

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME')
}


# Read input from STDIN
def read_input():
    print("Enter data as comma-separated values (Date,Amount,Category,Tags,Notes):")
    data = []
    for line in sys.stdin:
        # Strip whitespace and split by comma
        if line.strip():
            data.append(line.strip().split(","))
    return data


# Map input to dictionary
def map_to_dict(data):
    keys = ["Date", "Amount", "Category", "Tags", "Notes"]
    mapped_data = []
    for row in data:
        if len(row) == len(keys):
            mapped_data.append(dict(zip(keys, row)))
        else:
            print(f"Error: Row {row} does not match the expected format and will be skipped.")
    return mapped_data


# Transform data for database insertion
def transform_data(mapped_data):
    transformed = []
    for item in mapped_data:
        try:
            try:
                txn_date = convert_date_format(item["Date"], "%d %b %Y", "%Y-%m-%d")
            except ValueError:
                txn_date = convert_date_format(item["Date"], "%d %B %Y", "%Y-%m-%d")

            amount_str = item["Amount"].lower()
            if "rs" in amount_str:
                amount = float(amount_str.split("rs")[1].strip())
            else:
                amount = float(amount_str)

            transformed.append({
                "txn_date": txn_date,
                "account": "Cash",
                "txn_type": "Debit" if amount > 0 else "Credit",
                "txn_amount": abs(amount),
                "category": item["Category"].strip(),
                "tags": item["Tags"],
                "notes": item["Notes"]
            })
        except Exception as e:
            print(f"Error transforming row {item}: {str(e)}")
    return transformed


# Write data to PostgreSQL database
def write_to_db(transformed_data):
    conn = None
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Prepare the SQL statement
        insert_sql = sql.SQL("""
            INSERT INTO transactions (
                txn_date, account, txn_type, txn_amount, 
                category, tags, notes
            ) VALUES (
                %(txn_date)s, %(account)s, %(txn_type)s, %(txn_amount)s,
                %(category)s, %(tags)s, %(notes)s
            )
        """)

        # Insert each row
        success_count = 0
        for row in transformed_data:
            try:
                cursor.execute(insert_sql, row)
                conn.commit()
                success_count += 1
            except IntegrityError as e:
                conn.rollback()
                if 'unique constraint' in str(e).lower():
                    print(f"Skipping duplicate row: {row} - {str(e)}")
                else:
                    print(f"Integrity error for row {row}: {str(e)}")
            except Exception as e:
                conn.rollback()
                print(f"Error inserting row {row}: {str(e)}")

        print(f"Successfully inserted {success_count} out of {len(transformed_data)} records.")

    except Exception as e:
        print(f"Database error: {str(e)}")
    finally:
        if conn is not None:
            conn.close()


# Main function
def main():
    data = read_input()
    mapped_data = map_to_dict(data)
    transformed_data = transform_data(mapped_data)
    write_to_db(transformed_data)


if __name__ == "__main__":
    main()