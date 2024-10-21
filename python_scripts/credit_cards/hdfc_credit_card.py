import csv

from common import (
    fix_date_format,
    rename_csv_columns,
    convert_date_format,
    auto_detect_category,
    parse_str_to_float,
    write_result,
    check_csv_header,
)


def hdfc_cc_fix_date_format(file_path, rewrite=False):
    if check_csv_header(file_path, "DATE"):
        fix_date_format(file_path, "DATE", "%d/%m/%Y", rewrite=rewrite)


def hdfc_cc_upi_fix_date_format(file_path, rewrite=False):
    if check_csv_header(file_path, "DATE"):
        fix_date_format(file_path, "DATE", "%d/%m/%Y %H:%M:%S", rewrite=rewrite)


def hdfc_credit_card_adapter(filename, output):
    hdfc_cc_fix_date_format(filename, rewrite=True)
    column_mapping = {
        "Transaction type": None,
        "Primary / Addon Customer Name": None,
        "DATE": "Date",
        "Description": "Description",
        "AMT": "Amount",
        "Debit / Credit": "Debit / Credit",
    }
    if all([check_csv_header(filename, header) for header in column_mapping.keys()]):
        rename_csv_columns(filename, filename, column_mapping)
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    result = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row[columns[3]].lower():
                category, tags, notes = auto_detect_category(row[columns[1]])
                result.append(
                    {
                        "txn_date": convert_date_format(
                            row[columns[0]], "%d/%m/%Y", "%Y-%m-%d"
                        ),
                        "account": "HDFC Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": category,
                        "tags": tags,
                        "notes": notes,
                    }
                )
    write_result(output, result)


def hdfc_upi_credit_card_adapter(filename, output_filename):
    hdfc_cc_upi_fix_date_format(filename, rewrite=True)
    column_mapping = {
        "Transaction type": None,
        "Primary / Addon Customer Name": None,
        "Base NeuCoins": None,
        "DATE": "Date",
        "Description": "Description",
        "AMT": "Amount",
        "Debit / Credit": "Debit / Credit",
    }
    if all([check_csv_header(filename, header) for header in column_mapping.keys()]):
        rename_csv_columns(filename, filename, column_mapping)
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    result = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row[columns[3]].lower():
                category, tags, notes = auto_detect_category(row[columns[1]])
                result.append(
                    {
                        "txn_date": convert_date_format(
                            row[columns[0]], "%d/%m/%Y %H:%M:%S", "%Y-%m-%d"
                        ),
                        "account": "HDFC Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": category,
                        "tags": tags,
                        "notes": notes,
                    }
                )
    write_result(output_filename, result)
