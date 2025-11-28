import logging
import os
import re
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
        logging.FileHandler('logs/axis_credit_card.log')
    ]
)
logger = logging.getLogger(__name__)


def create_df(each_filename):
    """Create and process DataFrame from CSV file with Axis credit card format"""
    df = pd.read_csv(each_filename, header=0)
    df = remove_empty_columns(df)
    
    # Create new df by mapping column indices to standard format
    # Index 1 → date, Index 2 → transaction_details, Index 3 → merchant_category, Index 4 → amount
    new_df = pd.DataFrame()
    if len(df.columns) > 4:
        new_df["txn_date"] = df.iloc[:, 1]
        new_df["transaction_details"] = df.iloc[:, 2]
        new_df["merchant_category"] = df.iloc[:, 3]
        new_df["amount"] = df.iloc[:, 4]
    else:
        logger.error(f"Expected at least 5 columns, but found {len(df.columns)} columns")
        return pd.DataFrame()
    
    df = new_df
    
    # Process each row to extract and clean data
    processed_rows = []
    
    for index, row in df.iterrows():
        try:
            # Get txn_date
            txn_date = str(row.get("txn_date", "")).strip()
            if not txn_date or txn_date == "" or txn_date.lower() == "nan":
                logger.warning(f"Row {index}: Missing date, skipping...")
                continue
            
            # Validate and convert date format (must be DD/MM/YYYY)
            try:
                # Check if date is in DD/MM/YYYY format
                date_pattern = r'^\d{2}/\d{2}/\d{4}$'
                if not re.match(date_pattern, txn_date):
                    logger.error(f"Row {index}: Date '{txn_date}' is not in DD/MM/YYYY format, skipping...")
                    continue
                
                # Try to convert date format from DD/MM/YYYY to YYYY-MM-DD
                formatted_date = convert_date_format(txn_date, "%d/%m/%Y", "%Y-%m-%d")
            except Exception as e:
                logger.error(f"Row {index}: Invalid date '{txn_date}': {e}, skipping...")
                continue
            
            # Get transaction_details
            transaction_details = str(row.get("transaction_details", "")).strip()
            if transaction_details.lower() == "nan":
                transaction_details = ""
            
            # Get merchant_category
            merchant_category = str(row.get("merchant_category", "")).strip()
            if merchant_category.lower() == "nan":
                merchant_category = ""
            
            # Get amount and determine txn_type
            amount_str = str(row.get("amount", "")).strip()
            if not amount_str or amount_str.lower() == "nan":
                logger.warning(f"Row {index}: Missing amount, skipping...")
                continue
            
            # Check for Dr or Cr in amount string
            amount_str_upper = amount_str.upper()
            if "DR" in amount_str_upper:
                txn_type = "Debit"
                # Remove "Dr" from amount string
                amount_str = re.sub(r'\s*Dr\s*', '', amount_str, flags=re.IGNORECASE).strip()
            elif "CR" in amount_str_upper:
                txn_type = "Credit"
                # Remove "Cr" from amount string
                amount_str = re.sub(r'\s*Cr\s*', '', amount_str, flags=re.IGNORECASE).strip()
            else:
                # Default to Debit if not specified
                logger.warning(f"Row {index}: No Dr/Cr found in amount '{amount_str}', defaulting to Debit")
                txn_type = "Debit"
            
            # Clean amount string (remove commas, spaces, etc.)
            amount_str = amount_str.replace(',', '').replace(' ', '')
            
            # Convert to float
            try:
                amount = float(amount_str)
            except ValueError as e:
                logger.error(f"Row {index}: Could not convert amount '{amount_str}' to float: {e}")
                continue
            
            # Create processed row
            processed_rows.append({
                "txn_date": formatted_date,
                "transaction_details": transaction_details,
                "merchant_category": merchant_category,
                "amount": amount,
                "txn_type": txn_type
            })
            
        except Exception as e:
            logger.exception(f"Error processing row {index}: {row}")
            continue
    
    # Create new DataFrame with processed data
    processed_df = pd.DataFrame(processed_rows)
    
    # Create intermediate modified file
    temp_file_name, _ = os.path.splitext(each_filename)
    modified_file = "%s_modified.csv" % temp_file_name
    processed_df.to_csv(modified_file, index=False, header=True)
    
    return processed_df


def axis_credit_card_processor(filename, output):
    """Process Axis credit card file and write results"""
    # Process the file and get cleaned DataFrame
    df = create_df(filename)
    
    if df.empty:
        logger.warning(f"No valid transactions found in {filename}")
        return
    
    result = []
    for index, row in df.iterrows():
        # Process all transactions (both Debit and Credit)
        category, tags, notes = auto_detect_category(row["transaction_details"])
        
        # Add merchant category to notes if available
        if row["merchant_category"] and str(row["merchant_category"]).strip() != "":
            notes = f"Merchant Category: {row['merchant_category']}\n{notes}" if notes else f"Merchant Category: {row['merchant_category']}"
        
        result.append(
            {
                "txn_date": row["txn_date"],
                "account": "Axis Credit Card",
                "txn_type": row["txn_type"],
                "txn_amount": parse_str_to_float(row["amount"]),
                "category": category,
                "tags": tags,
                "notes": notes,
            }
        )
    
    write_result(output, result)


def axis_credit_card_adapter(filename, output):
    """Adapter function to handle both CSV and PDF files"""
    if check_file_type(filename) == "CSV":
        axis_credit_card_processor(filename, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "AXIS_CREDIT_CARD_PASSWORD")
        # Extract tables from PDF - adjust coordinates based on actual PDF layout
        # Format: [x1, y1, x2, y2] for table area, [x1, y1, x2, y2] for header area
        # These are placeholder coordinates - adjust based on your PDF layout
        for each_filename in extract_tables_from_pdf(
            filename, 
            [310, 30, 310+308, 560+30],  # Table area coordinates - adjust as needed
            [310, 30, 310+308, 560+30],   # Header area coordinates - adjust as needed
            "lattice"
        ):
            try:
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                axis_credit_card_processor(each_filename, output_file)
            except Exception:
                logger.exception(f"Exception in processing file {each_filename}. Skipping...")

