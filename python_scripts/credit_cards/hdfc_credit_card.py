import csv
import datetime
import os

from common import *


def hdfc_cc_fix_date_format(file_path):
    fix_date_format_core(file_path, "Date", "%d/%m/%Y")


def hdfc_cc_upi_fix_date_format(file_path, date_column):
    fix_date_format_core(file_path, "Date", "%d/%m/%Y %H:%M:%S")


def hdfc_credit_card_adapter(file_name, output):
    columns = ["Date", "Transaction Description", "Amount (in Rs.)"]
    columns.extend(EXTRA_FIELDS)
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row[columns[2]].lower() and row[columns[3]] != "":
                result.append(
                    {
                        "txn_date": datetime.datetime.strptime(
                            row[columns[0]], "%d/%m/%Y"
                        ).strftime("%Y-%m-%d"),
                        "account": "HDFC Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": CATEGORY_MAPPING[row[columns[3]]],
                        "tags": row[columns[4]],
                        "notes": row[columns[5]],
                    }
                )
    write_result(output, result)


def hdfc_upi_credit_card_adapter(file_name, output):
    columns = ["Date", "Transaction Description", "Amount (in Rs.)"]
    columns.extend(EXTRA_FIELDS)
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row["Amount (in Rs.)"].lower() and row["Category"] != "":
                result.append(
                    {
                        "txn_date": datetime.datetime.strptime(
                            row["Date"], "%d/%m/%Y %H:%M:%S"
                        ).strftime("%Y-%m-%d"),
                        "account": "HDFC Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row["Amount (in Rs.)"]),
                        "category": CATEGORY_MAPPING[row["Category"]],
                        "tags": row["Tags"],
                        "notes": row["Notes"],
                    }
                )
    write_result(output, result)
