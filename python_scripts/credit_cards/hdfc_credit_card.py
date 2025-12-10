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
        logging.FileHandler('logs/hdfc_credit_card.log')
    ]
)
logger = logging.getLogger(__name__)


def create_df(each_filename):
    """Create and process DataFrame from CSV file with new HDFC format"""
    df = pd.read_csv(each_filename)
    # Replace standalone "EMI" cells with NaN before dropping empty columns
    df = df.replace(r"^\s*EMI\s*$", np.nan, regex=True).infer_objects(copy=False)
    df = remove_empty_columns(df)
    
    # Set headers from first row: DATE & TIME, TRANSACTION DESCRIPTION, REWARDS, AMOUNT
    if len(df) > 0:
        # Use first row as headers
        df.columns = df.iloc[0]
        # Drop the first row (header row)
        df = df.drop(df.index[0])
        df = df.reset_index(drop=True)
    
    # Accumulate cleaned rows then build the DataFrame once (avoids concat warnings)
    processed_rows = []
    
    # Process each row
    for index, row in df.iterrows():
        try:
            # Get date from "DATE & TIME" column
            date_time_str = str(row.get("DATE & TIME", "")).strip()
            if not date_time_str or date_time_str.lower() == "nan":
                continue
            
            # Convert date from "25/09/2025| 11:04" format to "yyyy-mm-dd hh:mm"
            # Replace "|" with space and clean up
            date_time_str = date_time_str.replace("|", " ").strip()
            # Remove extra spaces
            date_time_str = re.sub(r'\s+', ' ', date_time_str)
            
            # Extract date using regex pattern dd/mm/yyyy
            date_match = re.search(r'\d{2}/\d{2}/\d{4}', date_time_str)
            if not date_match:
                logger.error(f"Could not extract date from: {date_time_str}")
                continue
            
            try:
                # Parse extracted date in format "dd/mm/yyyy"
                formatted_date = convert_date_format(date_match.group(), "%d/%m/%Y", "%Y-%m-%d")
            except Exception as e:
                logger.error(f"Could not convert date format for: {date_time_str}, error: {e}")
                continue
            
            # Get description
            description = str(row.get("TRANSACTION DESCRIPTION", "")).strip()
            if description.lower() == "nan":
                description = ""
            
            # Get rewards and convert to float (handles "+ 10" / "- 5" formats)
            rewards_str = str(row.get("REWARDS", "")).strip()
            rewards_value = 0.0
            if rewards_str and rewards_str.lower() != "nan":
                rewards_clean = rewards_str.replace(',', '')
                # Remove spaces after leading sign if present (e.g., "+ 10" -> "+10")
                rewards_clean = re.sub(r'^([+-])\s+', r'\1', rewards_clean)
                try:
                    rewards_value = float(rewards_clean)
                except ValueError as e:
                    logger.error(f"Could not convert rewards to float: {rewards_str}, error: {e}")
                    continue
            
            # Get amount
            amount_str = str(row.get("AMOUNT", "")).strip()
            if not amount_str or amount_str.lower() == "nan":
                continue
            
            # Check if "+" is present to determine Debit/Credit
            is_credit = "+" in amount_str
            
            # Remove "C" prefix with spaces around it
            amount_str = re.sub(r'\s*C\s*', '', amount_str, flags=re.IGNORECASE)
            amount_str = amount_str.strip()
            
            # Remove commas and convert to float
            try:
                amount = float(amount_str.replace(',', ''))
            except ValueError as e:
                logger.error(f"Could not convert amount to float: {amount_str}, error: {e}")
                continue
            
            # Determine transaction type
            txn_type = "Credit" if is_credit else "Debit"

            # Credit rows should carry negative amounts upfront
            amount = -abs(amount) if txn_type == "Credit" else abs(amount)

            processed_rows.append({
                "Date": formatted_date,
                "Description": description,
                "Rewards": rewards_value,
                "Amount": amount,
                "Debit / Credit": txn_type,
            })
            
        except Exception as e:
            logger.exception(f"Error processing row {index}: {row}")
            continue
    
    new_df = pd.DataFrame(processed_rows, columns=["Date", "Description", "Rewards", "Amount", "Debit / Credit"])

    # Output to _modified.csv
    temp_file_name, _ = os.path.splitext(each_filename)
    modified_file = "%s_modified.csv" % temp_file_name
    new_df.to_csv(modified_file, index=False, header=True)
    
    return new_df


def hdfc_credit_card_processor(filename, output):
    # Read already-normalized CSV produced by create_df (Date, Description, Rewards, Amount, Debit / Credit)

    try:
        df = pd.read_csv(
            filename,
            usecols=["Date", "Description", "Rewards", "Amount", "Debit / Credit"],
        )
    except Exception:
        df = create_df(filename)
    if df.empty:
        df = create_df(filename)

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


def hdfc_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        hdfc_credit_card_processor(filename, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "HDFC_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(filename, [702, 161, 692+129, 162+405], [262, 18, 262+248, 18+542], "stream"):
            try:
                create_df(each_filename)
            except Exception:
                logger.exception(f"Exception in processing file {each_filename}. Skipping...")
