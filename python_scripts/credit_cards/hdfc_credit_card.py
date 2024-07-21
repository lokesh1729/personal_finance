import csv
import datetime
import os

from common import *


def hdfc_cc_fix_date_format(file_path, rewrite=False):
    fix_date_format(file_path, "Date", "%d/%m/%Y", rewrite=rewrite)


def hdfc_cc_upi_fix_date_format(file_path, rewrite=False):
    fix_date_format(file_path, "Date", "%d/%m/%Y %H:%M:%S", rewrite=rewrite)


def hdfc_credit_card_adapter(file_name, output):
    hdfc_cc_fix_date_format(file_name, rewrite=True)
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row[columns[3]].lower():
                category, tags, notes = auto_detect_category(row[columns[1]])
                result.append(
                    {
                        "txn_date": convert_date_format(row[columns[0]], "%d/%m/%Y", "%Y-%m-%d"),
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
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    result = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row[columns[3]].lower():
                category, tags, notes = auto_detect_category(row[columns[1]])
                result.append(
                    {
                        "txn_date": convert_date_format(row["Date"], "%d/%m/%Y %H:%M:%S", "%Y-%m-%d"),
                        "account": "HDFC Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": category,
                        "tags": tags,
                        "notes": notes,
                    }
                )
    write_result(output_filename, result)
