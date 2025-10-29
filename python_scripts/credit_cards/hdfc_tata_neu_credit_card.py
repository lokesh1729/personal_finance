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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('hdfc_credit_card.log')
    ]
)
logger = logging.getLogger(__name__)


def create_df(each_filename):
    """Create and process DataFrame from CSV file with new HDFC format"""
    df = pd.read_csv(each_filename, header=None)
    df = remove_empty_columns(df)

    # Process each row to extract transaction data
    processed_rows = []

    for index, row in df.iterrows():
        # Get the raw string from the first column
        raw_string = str(row[0]) if len(row) > 0 else ""

        # Skip empty rows
        if not raw_string or raw_string.strip() == "":
            continue

        try:
            # Cleanup
            cleaned_string = raw_string.replace("SANAPALLI LOKESH", "").replace("\r", "")

            # Extract transaction date
            date_pattern = r'(\d{2}/\d{2}/\d{4})\s*\|\s*(\d{2}:\d{2})'
            date_match = re.search(date_pattern, cleaned_string)

            if not date_match:
                logger.error(f"Could not find date pattern in string: {raw_string}")
                continue

            date_str = date_match.group(1) + " " + date_match.group(2)
            # Convert date format from DD/MM/YYYY HH:MM to YYYY-MM-DD HH:MM:SS
            try:
                formatted_date = convert_date_format(date_str, "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S")
            except:
                logger.error(f"Could not convert date format for: {date_str}")
                continue

            # Remove date from string
            cleaned_string = re.sub(date_pattern, "", cleaned_string).strip()

            # Check for credit transaction pattern
            credit_pattern = r'\+\s{2}C'
            is_credit = bool(re.search(credit_pattern, cleaned_string))

            # Remove credit pattern from string
            cleaned_string = re.sub(credit_pattern, "", cleaned_string).strip()

            # Extract transaction amount (take the last occurrence)
            amount_pattern = r'([\d,]+\.?\d*[l]?)'
            amount_matches = re.findall(amount_pattern, cleaned_string)

            if not amount_matches:
                logger.error(f"Could not find amount pattern in string: {raw_string}")
                continue

            amount_str = amount_matches[-1]  # Take the last occurrence
            # Remove 'l' suffix if present
            amount_str = amount_str.rstrip('l')
            # Remove commas and convert to float
            try:
                amount = float(amount_str.replace(',', ''))
            except:
                logger.error(f"Could not convert amount to float: {amount_str}")
                continue

            # Determine transaction type
            txn_type = "Credit" if is_credit else "Debit"

            # Remove the last amount occurrence from string
            # Find the last occurrence and remove it
            last_amount_match = re.search(amount_pattern + r'(?!.*' + amount_pattern + r')', cleaned_string)
            if last_amount_match:
                cleaned_string = cleaned_string[:last_amount_match.start()] + cleaned_string[last_amount_match.end():]
            cleaned_string = cleaned_string.strip()

            # Remaining string is transaction description
            description = cleaned_string.strip()
            
            # Extract Neu Coins pattern like +135C or -200D
            neu_coin_pattern = r'([+-]\s+(\d+)[CD])'
            neu_coin_match = re.search(neu_coin_pattern, description)
            neu_coins = neu_coin_match.group(2) if neu_coin_match else ""
            # Remove the neu coins token from the description (only the first occurrence)
            if neu_coin_match:
                description = re.sub(neu_coin_pattern, "", description, count=1).strip()

            # Create processed row with proper columns
            processed_rows.append({
                "Date": formatted_date,
                "Description": description,
                "Amount": amount,
                "Debit / Credit": txn_type,
                "neucoins": neu_coins
            })

        except Exception as e:
            logger.exception(f"Error processing row {index}: {raw_string}")
            continue

    # Create new DataFrame with processed data
    processed_df = pd.DataFrame(processed_rows)

    # Create intermediate modified file
    df.to_csv(each_filename, index=False, header=False)
    temp_file_name, _ = os.path.splitext(each_filename)
    modified_file = "%s_modified.csv" % temp_file_name
    processed_df.to_csv(modified_file, index=False, header=True)

    return processed_df


def hdfc_credit_card_processor(filename, output):
    # Process the file with new format and get cleaned DataFrame
    df = create_df(filename)
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    result = []
    for index, row in df.iterrows():
        if row[columns[3]] == "Debit":
            category, tags, notes = auto_detect_category(row[columns[1]])
            result.append(
                {
                    "txn_date": row[columns[0]],
                    "account": "HDFC Credit Card",
                    "txn_type": row[columns[3]],
                    "txn_amount": parse_str_to_float(row[columns[2]]),
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
        for each_filename in extract_tables_from_pdf(filename, [728, 162, 728 + 88, 162 + 418],
                                                     [246, 18, 246 + 144, 18 + 561], "lattice"):
            try:
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                hdfc_credit_card_processor(each_filename, output_file)
            except Exception:
                logger.exception(f"Exception in processing file {each_filename}. Skipping...")
