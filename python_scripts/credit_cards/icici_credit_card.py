import csv
import os
import datetime

from common.utils import *
from common.constants import *


def icici_cc_fix_date_format(file_path, rewrite=False):
    fix_date_format(file_path, "Date", "%d/%m/%Y", rewrite=rewrite)


def icici_credit_card_adapter(filename, out_filename):
    icici_cc_fix_date_format(filename, rewrite=True)
    columns = ["Date", "Transaction Details", "Amount", "Type"]
    result = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row[columns[2]].lower():
                category, tags, notes = auto_detect_category(columns[1])
                result.append(
                    {
                        "txn_date": convert_date_format(row[columns[0].split()[0]], "%d %b %y", "%Y-%m-%d"),
                        "account": "ICICI Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": category,
                        "tags": tags,
                        "notes": notes,
                    }
                )
    write_result(out_filename, result)
