import csv
import datetime
import os

from common import *


def hdfc_cc_fix_date_format(file_path):
    fix_date_format(file_path, "Date", "%d/%m/%Y")


def hdfc_cc_upi_fix_date_format(file_path):
    fix_date_format(file_path, "Date", "%d/%m/%Y %H:%M:%S")


def hdfc_credit_card_adapter(file_name, output):
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    columns.extend(EXTRA_FIELDS)
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[columns[4]] != "" and "cr" not in row[columns[3]].lower():
                result.append(
                    {
                        "txn_date": datetime.datetime.strptime(
                            row[columns[0]], "%d/%m/%Y"
                        ).strftime("%Y-%m-%d"),
                        "account": "HDFC Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": CATEGORY_MAPPING[row[columns[4]]],
                        "tags": row[columns[5]],
                        "notes": row[columns[6]],
                    }
                )
    write_result(output, result)


def hdfc_upi_credit_card_adapter(file_name, output):
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    columns.extend(EXTRA_FIELDS)
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[columns[4]] != "" and "cr" not in row[columns[3]].lower():
                result.append(
                    {
                        "txn_date": datetime.datetime.strptime(
                            row["Date"], "%d/%m/%Y %H:%M:%S"
                        ).strftime("%Y-%m-%d"),
                        "account": "HDFC Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": CATEGORY_MAPPING[row[columns[4]]],
                        "tags": row[columns[5]],
                        "notes": row[columns[6]],
                    }
                )
    write_result(output, result)
