# TODO : write usage and description
import datetime
import os
import json
import pickle

import pandas as pd
import requests
import logging
from typing import List, Dict
from psycopg2.extras import execute_batch
import psycopg2
from dotenv import load_dotenv

from common import convert_date_format, auto_detect_category, write_result, parse_str_to_float

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Constants
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0"
PICKLE_FILE = "zaggle.pickle"
ZAGGLE_AUTH_URL = "https://api.zaggle.in/api/v1/auth/basic"
ZAGGLE_SET_TOKEN_URL = "https://app.zaggle.in/api/setToken"
ZAGGLE_CARD_DETAILS_URL = "https://api.zaggle.in/api/v1/profile/user_balances"
ZAGGLE_TRANSACTIONS_URL = "https://api.zaggle.in/api/v1/narada/last_transactions"
DEVICE_ID = "f335108fe5ae"
CLIENT_NAME = "WebBrowser"
CLIENT_VERSION = "WebBrowser"


def get_token() -> dict:
    load_dotenv()

    username = os.getenv("ZAGGLE_USERNAME")
    password = os.getenv("ZAGGLE_PASSWORD")
    phone = os.getenv("ZAGGLE_PHONE")
    device_id = os.getenv("ZAGGLE_DEVICE_ID", DEVICE_ID)

    data = {
        "username": username,
        "password": password,
        "device_id": device_id,
        "client_name": CLIENT_NAME,
        "client_version": CLIENT_VERSION,
        "phone": phone
    }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://app.zaggle.in/",
        "Origin": "https://app.zaggle.in",
        "DNT": "1",
        "Connection": "keep-alive"
    }

    response = requests.post(ZAGGLE_AUTH_URL, headers=headers, data=data)
    print(f"Request: {response.request.__dict__}")
    response.raise_for_status()
    logger.info(f"Received token response: {response.text}")
    resp_data = response.json()

    token = resp_data["token"]
    client_id = resp_data["user"]["user_client_id"]

    # Call setToken
    set_token_data = {
        "token": token,
        "device_id": device_id,
        "client_id": client_id
    }

    requests.post(ZAGGLE_SET_TOKEN_URL, headers=headers, data=set_token_data)

    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(set_token_data, f)

    return set_token_data


def fetch_token_data():
    with open(PICKLE_FILE, "rb") as f:
        try:
            return pickle.load(f)
        except (EOFError, IOError) as exc:
            logger.info(f"Exception in loading pickle file: {exc}")
            token_data = ""
    if token_data == "":
        return get_token()


def logout():
    token_data = fetch_token_data()

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://app.zaggle.in/",
        "Origin": "https://app.zaggle.in",
        "DNT": "1",
        "Connection": "keep-alive",
        "Authorization": f"Token token={token_data['token']};client_key=client_key;device_id={token_data['device_id']};client_id={token_data['client_id']}"
    }

    response = requests.delete("https://api.zaggle.in/api/v1/auth", headers=headers)

    if response.status_code == 204:
        logger.info("Logout successful.")
    else:
        logger.error(f"Logout returned status: {response.status_code} text: {response.text}")


def fetch_card_details() -> str:
    token_data = fetch_token_data()

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://app.zaggle.in/",
        "Origin": "https://app.zaggle.in",
        "DNT": "1",
        "Connection": "keep-alive",
        "Authorization": f"Token token={token_data['token']};client_key=client_key;device_id={token_data['device_id']};client_id={token_data['client_id']}"
    }

    response = requests.get(ZAGGLE_CARD_DETAILS_URL, headers=headers)

    if response.status_code == 401:
        logger.warning("Token expired. Re-authenticating...")
        token_data = get_token()
        return fetch_card_details()

    response.raise_for_status()
    data = response.json()
    return data["expense_cards"][0]["id"]

def fetch_transactions() -> List[Dict]:
    token_data = fetch_token_data()
    ysc_card_id = fetch_card_details()

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://app.zaggle.in/",
        "Origin": "https://app.zaggle.in",
        "DNT": "1",
        "Connection": "keep-alive",
        "Authorization": f"Token token={token_data['token']};client_key=client_key;device_id={token_data['device_id']};client_id={token_data['client_id']}"
    }

    all_transactions = []
    page_no = 1
    count = 25

    while True:
        data = {
            "ysc_card_id": ysc_card_id,
            "page_no": page_no,
            "count": count
        }

        response = requests.post(ZAGGLE_TRANSACTIONS_URL, headers=headers, data=data)

        if response.status_code == 401:
            logger.warning("Token expired during fetch_transactions. Re-authenticating...")
            get_token()
            return fetch_transactions()

        response.raise_for_status()
        resp_data = response.json()
        transactions = resp_data.get("transactions", [])

        if not transactions:
            break

        for t in transactions:
            all_transactions.append({
                "merchant_name": t.get("MerchantName", ""),
                "txn_status": t.get("TransStatus", ""),
                "txn_type": t.get("Description", ""),
                "txn_date": convert_date_format(t["TransactionDate"], "%d-%b-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"),
                "txn_amount": t.get("TransAmt", "0.0"),
                "id": t["id"],
                "closing_balance": t["ClosingBalance"],
                "response_reason": t.get("ResponseReason", "")
            })

        page_no += 1

    return all_transactions


def dump_to_database(entries: List[Dict]):
    load_dotenv()

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise EnvironmentError("Database environment variables are not properly set.")

    table_name = "zaggle_transactions"

    insert_query = f"""
        INSERT INTO {table_name} (
            id, merchant_name, txn_date, txn_type, txn_status, txn_amount, closing_balance, response_reason
        ) VALUES (
            %(id)s, %(merchant_name)s, %(txn_date)s, %(txn_type)s, %(txn_status)s, %(txn_amount)s, %(closing_balance)s, %(response_reason)s
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
        logger.info(f"Inserting {len(entries)} records into '{table_name}'...")
        sample_sql = cursor.mogrify(insert_query, entries[0])
        logger.info(f"Sample SQL:\n{sample_sql.decode()}")
        execute_batch(cursor, insert_query, entries)
        conn.commit()
        logger.info("Data successfully inserted into the database.")
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database insert error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        logger.info("Database connection closed.")


def dump_to_database_batch(entries: List[Dict]):
    if not entries:
        return
    batch_size = 1
    logger.info(f"Processing {len(entries)} entries in batches of {batch_size}...")

    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1} with {len(batch)} entries...")
        try:
            dump_to_database(batch)
        except psycopg2.errors.UniqueViolation as ve:
            logger.error(f"Unique constraint violated: {ve}")
            raise ve
        except psycopg2.errors.IntegrityError as ie:
            logger.error(f"Integrity error: {ie}")
            raise ie
        except Exception as e:
            logger.error(f"Unexpected error in batch: {e}")
            raise e


def transform(transactions):
    if not transactions:
        return
    result = []

    for txn in transactions:
        if txn["response_reason"] == 'APPROVED AND COMPLETED SUCCESSFUL':
            merchant_name = txn["merchant_name"]
            txn_amount = parse_str_to_float(txn["txn_amount"])
            category, tags, notes = auto_detect_category(merchant_name)

            txn_type = ""
            if txn["txn_type"] == "Purchase":
                txn_type = "Debit"
            elif txn["txn_type"] == "Branch TopUp":
                txn_type = "Credit"

            entry = {
                "txn_date": txn["txn_date"],
                "account": "Zaggle Food Card",
                "txn_type": txn_type,
                "txn_amount": txn_amount,
                "category": category if category else "Others",
                "tags": tags if category else "",
                "notes": notes if category else f"source of truth = {merchant_name}",
            }

            result.append(entry)

    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    output_file = f"zaggle_{timestamp}.csv"
    write_result(output_file, result)


def process():
    """
    Fetch Zaggle transactions and insert them into the database in batch size 1.
    """
    transactions = []
    try:
        transactions = fetch_transactions()
        logger.info(f"Fetched {len(transactions)} transactions.")
    except Exception as exc:
        logger.exception(f"Exception in fetching transactions {exc}")
    # finally:
    #     logout()
    try:
        dump_to_database_batch(transactions)
    except Exception as e:
        logger.exception(f"Exception in saving to database: {e}")
    try:
        transform(transactions)
    except Exception as e:
        logger.exception(f"Exception in transforming to file: {e}")



if __name__ == "__main__":
    process()
