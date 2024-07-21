import csv
import os
import datetime

from common.utils import *
from common.constants import *


def sbi_cc_fix_date_format(file_path, rewrite=False):
    fix_date_format(file_path, "Date", "%d %b %y", rewrite=rewrite)


def sbi_credit_card_adapter(filename, out_filename):
    sbi_cc_fix_date_format(filename, rewrite=True)
    columns = ["Date", "Transaction Details", "Amount", "Type"]
    result = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[columns[3]] == "D":
                category, tags, notes = auto_detect_category(row[columns[1]])
                result.append(
                    {
                        "txn_date": row[columns[0]],
                        "account": "SBI Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": category,
                        "tags": tags,
                        "notes": notes,
                    }
                )
    write_result(out_filename, result)
