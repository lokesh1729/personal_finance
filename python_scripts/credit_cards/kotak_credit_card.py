import csv
import datetime
import os

from common import *


def kotak_cc_fix_date_format(file_path):
    fix_date_format(file_path, "Date", "%d/%m/%Y")


def kotak_credit_card_adapter(file_name, output):
    columns = ["Date", "Transaction details", "Amount (Rs.)"]
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
                        "account": "Kotak Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": CATEGORY_MAPPING[row[columns[3]]],
                        "tags": row[columns[4]],
                        "notes": row[columns[5]],
                    }
                )
    write_result(output, result)
