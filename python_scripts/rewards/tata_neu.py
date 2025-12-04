"""
Fetches rewards data from tata neu

Usage:

1. Go to tataneu.com
2. Login with your mobile number and OTP (automation is tough because it has akamai bot manager and google ReCaptcha)
3. Go to https://www.tataneu.com/home
4. Open network tools ---> XHR ---> search for customer ---> copy token from authorization header
5. Fill it in the .env file as TATA_NEU_AUTHORIZATION_TOKEN, TATA_NEU_CLIENT_ID, TATA_NEU_CLIENT_SECRET

"""
import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import psycopg2
from psycopg2.extras import execute_batch

def dump_to_database(entries: list[dict]):
    """
    Inserts a list of Tata Neu transaction entries into a PostgreSQL database table.
    """
    # Load DB connection settings from environment variables
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise EnvironmentError("Database environment variables are not properly set.")

    # Define table name
    table_name = "tata_neu_transactions"

    # SQL to insert data
    insert_query = f"""
    INSERT INTO {table_name} (
        transaction_type, created_at, points, points_category,
        program_name, transaction_id, transaction_number,
        txn_amount, txn_gross_amount, txn_date, store
    ) VALUES (
        %(transaction_type)s, %(created_at)s, %(points)s, %(points_category)s,
        %(program_name)s, %(transaction_id)s, %(transaction_number)s,
        %(txn_amount)s, %(txn_gross_amount)s, %(txn_date)s, %(store)s
    );
    """

    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
    )
    cursor = conn.cursor()

    try:
        logger.info("Connecting to PostgreSQL database...")
        logger.info(f"Inserting {len(entries)} records into '{table_name}'...")
        sample_sql = cursor.mogrify(insert_query, entries[0])
        logger.info(f"Sample SQL:\n{sample_sql.decode()}")
        execute_batch(cursor, insert_query, entries)
        conn.commit()
        logger.info("Data successfully inserted into the database.")

    except Exception:
        if conn:
            conn.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Database connection closed.")


def dump_to_database_batch(entries: list[dict]):
    batch_size = 1

    logger.info(f"Processing {len(entries)} entries in batches of {batch_size}...")

    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1} with {len(batch)} entries...")
        dump_to_database(batch)


def fetch_ledger_page(offset: int) -> dict:
    """
    Fetch a single page of ledger data from Tata Digital API.
    """
    AUTH_TOKEN = os.getenv("TATA_NEU_AUTHORIZATION_TOKEN")
    CLIENT_ID = os.getenv("TATA_NEU_CLIENT_ID")
    CLIENT_SECRET = os.getenv("TATA_NEU_CLIENT_SECRET")

    if not all([AUTH_TOKEN, CLIENT_ID, CLIENT_SECRET]):
        raise EnvironmentError("Required environment variables are not set.")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.tataneu.com/',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'anonymous_id': '790d79c6-7ae9-4f9f-8958-41d0ea091d44',
        'request_id': 'a97ee1a8-b568-4189-b394-b5fa8dca52e0',
        'store_id': 'tcp.default',
        'neu-app-version': '5.8.0',
        'content-type': 'application/json',
        'Origin': 'https://www.tataneu.com',
        'DNT': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'authorization': f'Bearer {AUTH_TOKEN}',
        'Connection': 'keep-alive',
        'TE': 'trailers'
    }

    url = (
        "https://api.tatadigital.com/api/v2/np/ledger/getCustomerLedgerInfo"
        "?excludeEvents=DelayedAccrual%2CCustomerRegistration%2CManualPointsConversion%2CCustomerImport"
        "&identifierName=externalId"
        "&source=INSTORE"
        "&getCustomFields=true"
        "&getMaxConversionDetails=true"
        "&getBillDetails=true"
        f"&offset={offset}"
    )

    logger.info(f"Fetching ledger page with offset: {offset}")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logger.error(f"Failed to fetch data. Status code: {response.status_code}")
        response.raise_for_status()

    return response.json()


def extract_entries(page_data: dict) -> list:
    """
    Extract structured entries from a single page of ledger data.
    Pure function: does not mutate external variables.
    """
    entries = []

    for ledger in page_data.get('ledgerEntries', []):
        created_at = ledger.get('ledgerCreatedDate')
        transaction_details = ledger.get('transactionDetails', {})
        store = ledger.get('store')

        for detail in ledger.get('entryDetails', []):
            transaction_type = detail.get('ledgerEntryType')
            points = float(detail.get('points', 0))
            if transaction_type == 'DEBIT':
                points *= -1

            entry = {
                'transaction_type': transaction_type,
                'created_at': created_at,
                'points': points,
                'points_category': detail.get('pointsCategory'),
                'program_name': detail.get('programName'),
                'transaction_id': transaction_details.get('transactionId'),
                'transaction_number': transaction_details.get('transactionNumber'),
                'txn_amount': float(transaction_details.get('amount')) if transaction_details.get('amount') else None,
                'txn_gross_amount': float(transaction_details.get('grossBillAmount')) if transaction_details.get('grossBillAmount') else None,
                'txn_date': transaction_details.get('date'),
                'store': store,
            }
            entries.append(entry)

    return entries


def process():
    """
    Fetch all ledger pages, process them, and return a list of entries.
    """
    first_page = fetch_ledger_page(offset=0)
    page_count = first_page.get('ledgerDetails', {}).get('pageCount', 1)
    logger.info(f"Total page count: {page_count}")

    # Process first page
    try:
        dump_to_database_batch(extract_entries(first_page))
        # Process remaining pages
        for offset in range(1, page_count):
            page_data = fetch_ledger_page(offset=offset)
            dump_to_database_batch(extract_entries(page_data))
    except psycopg2.errors.UniqueViolation as ve:
        logger.error(f"Constraint violation in batch {ve}")
    except psycopg2.errors.IntegrityError as ie:
        logger.error(f"Integrity error in batch {ie}")
    except Exception as e:
        logger.error(f"Unexpected error in batch {e}")


# Example usage
if __name__ == "__main__":
    try:
        process()
    except Exception as e:
        logger.error(f"Failed to complete processing: {e}")
