import csv
import datetime
import os

from common import *


def kotak_cc_fix_date_format(file_path, rewrite=False):
    fix_date_format(file_path, "Date", "%d/%m/%Y", rewrite=rewrite)


def kotak_credit_card_adapter(filename, out_filename):
    kotak_cc_fix_date_format(filename, rewrite=True)
    columns = ["Date", "Transaction details", "Amount (Rs.)"]
    result = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row[columns[2]].lower():
                category, tags, notes = auto_detect_category(columns[1])
                result.append(
                    {
                        "txn_date": convert_date_format(row[columns[0]], "%d/%m/%Y", "%Y-%m-%d"),
                        "account": "Kotak Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": category,
                        "tags": tags,
                        "notes": notes,
                    }
                )
    write_result(out_filename, result)
