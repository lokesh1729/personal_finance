import csv
import os
import datetime

from common import *


def equitas_fix_date_format(file_path):
    fix_date_format(file_path, "Date", "%d-%b-%Y")


def equitas_bank_account_adapter(file_name, output):
    columns = [
        "Date",
        "Reference No. / Cheque No.",
        "Narration",
        "Withdrawal",
        "Deposit",
        "Dr / Cr",
        "Balance",
    ]
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category, tags, notes = auto_detect_category(columns[1])
            result.append(
                {
                    "txn_date": convert_date_format(row[columns[0]], "%B %-d, %Y", "%Y-%m-%d"),
                    "account": "Kotak Bank Account",
                    "txn_type": "Debit" if row[columns[5]] == "DR" else "Credit",
                    "txn_amount": parse_str_to_float(row[columns[4]]),
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
    write_result(output, result)
