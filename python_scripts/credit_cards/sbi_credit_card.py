import csv
import os
import datetime

from common.utils import *
from common.constants import *


def sbi_cc_fix_date_format(file_path):
    fix_date_format_core(file_path, "Date", "%d %b %y")


def sbi_credit_card_adapter(file_name, output):
    columns = ["Date", "Transaction Details", "Amount", "Type"]
    columns.extend(EXTRA_FIELDS)
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[columns[4]] != "":
                result.append(
                    {
                        "txn_date": convert_date_format(
                            row[columns[0]], "%d %b %y", "%Y-%m-%d"
                        ),
                        "account": "SBI Credit Card",
                        "txn_type": "Debit" if row[columns[3]] == "D" else "Credit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": CATEGORY_MAPPING[row[columns[4]]],
                        "tags": row[columns[5]],
                        "notes": row[columns[6]],
                    }
                )
    write_result(output, result)
