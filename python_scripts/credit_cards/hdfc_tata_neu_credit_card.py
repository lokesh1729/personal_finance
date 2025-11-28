import logging
import os
import re

import numpy as np
import pandas as pd

from common import (
    auto_detect_category,
    parse_str_to_float,
    write_result,
    remove_empty_columns,
    check_file_type,
)
from common.csv_utils import convert_date_format
from common.pdf import unlock_pdf, extract_tables_from_pdf

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/hdfc_tata_neu_credit_card.log')
    ]
)
logger = logging.getLogger(__name__)


def create_df(each_filename):
    """Create and process DataFrame from CSV file with HDFC Tata Neu format"""
    df = pd.read_csv(each_filename)
    # Replace standalone "EMI" cells with NaN before dropping empty columns
    df = df.replace(r"^\s*EMI\s*$", np.nan, regex=True).infer_objects(copy=False)
    df = remove_empty_columns(df)
    
    # Set headers from first row: DATE & TIME, TRANSACTION DESCRIPTION, BASE NEUCOINS*, AMOUNT
    if len(df) > 0:
        df.columns = df.iloc[0]
        df = df.drop(df.index[0]).reset_index(drop=True)
    
    processed_rows = []
    
    for index, row in df.iterrows():
        try:
            date_time_str = str(row.get("DATE & TIME", "")).strip()
            if not date_time_str or date_time_str.lower() == "nan":
                continue
            
            date_time_str = date_time_str.replace("|", " ").strip()
            date_time_str = re.sub(r'\s+', ' ', date_time_str)
            
            try:
                formatted_date = convert_date_format(date_time_str, "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M")
            except Exception as e:
                logger.error(f"Could not convert date format for: {date_time_str}, error: {e}")
                continue
            
            description = str(row.get("TRANSACTION DESCRIPTION", "")).strip()
            if description.lower() == "nan":
                description = ""
            
            neucoins_str = str(row.get("Base NeuCoins*", "")).strip()
            neucoins_value = 0.0
            if neucoins_str and neucoins_str.lower() != "nan":
                neucoins_clean = neucoins_str.replace(',', '')
                neucoins_clean = re.sub(r'^([+-])\s+', r'\1', neucoins_clean)
                try:
                    neucoins_value = float(neucoins_clean)
                except ValueError as e:
                    logger.error(f"Could not convert neucoins to float: {neucoins_str}, error: {e}")
                    continue
            
            amount_str = str(row.get("AMOUNT", "")).strip()
            if not amount_str or amount_str.lower() == "nan":
                continue
            
            is_credit = "+" in amount_str
            
            # Remove standalone "C" blocks (handles "C ", "+ C ") before conversion
            amount_str = re.sub(r'\s*C\s*', '', amount_str, flags=re.IGNORECASE).strip()
            
            try:
                amount = float(amount_str.replace(',', ''))
            except ValueError as e:
                logger.error(f"Could not convert amount to float: {amount_str}, error: {e}")
                continue
            
            txn_type = "Credit" if is_credit else "Debit"
            amount = -abs(amount) if txn_type == "Credit" else abs(amount)
            
            processed_rows.append({
                "Date": formatted_date,
                "Description": description,
                "NeuCoins": neucoins_value,
                "Amount": amount,
                "Debit / Credit": txn_type,
            })
            
        except Exception as e:
            logger.exception(f"Error processing row {index}: {row}")
            continue
    
    new_df = pd.DataFrame(
        processed_rows,
        columns=["Date", "Description", "Base NeuCoins*", "Amount", "Debit / Credit"],
    )
    
    temp_file_name, _ = os.path.splitext(each_filename)
    modified_file = "%s_modified.csv" % temp_file_name
    new_df.to_csv(modified_file, index=False, header=True)
    
    return new_df


def hdfc_credit_card_processor(filename, output):
    df = pd.read_csv(
        filename,
        usecols=["Date", "Description", "Amount", "Debit / Credit"],
    )

    result = []
    for _, row in df.iterrows():
        source_txn_type = str(row["Debit / Credit"]).strip().title()
        if source_txn_type not in {"Debit", "Credit"}:
            continue

        description = str(row["Description"])
        txn_type = "Credit" if source_txn_type == "Credit" else "Debit"

        amount_value = parse_str_to_float(row["Amount"])
        if amount_value is None:
            continue
        txn_amount = -abs(amount_value) if txn_type == "Credit" else abs(amount_value)

        category, tags, notes = auto_detect_category(description)
        result.append(
            {
                "txn_date": row["Date"],
                "account": "HDFC Credit Card",
                "txn_type": txn_type,
                "txn_amount": txn_amount,
                "category": category,
                "tags": tags,
                "notes": notes,
            }
        )
    write_result(output, result)


def hdfc_tata_neu_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        hdfc_credit_card_processor(filename, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "HDFC_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(
            filename,
            [744, 162, 728 + 72, 162 + 400],
            [262, 18, 262 + 170, 18 + 540],
            "stream",
        ):
            try:
                create_df(each_filename)
            except Exception:
                logger.exception(f"Exception in processing file {each_filename}. Skipping...")
