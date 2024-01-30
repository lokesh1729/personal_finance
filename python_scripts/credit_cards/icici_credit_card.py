import csv
import os
import datetime

from common.utils import *
from common.constants import *


def icici_cc_fix_date_format(file_path):
    fix_date_format_core(file_path, "Date", "%d/%m/%Y")


def icici_credit_card_adapter(file_name, output):
    columns = ["Date", "Transaction Details", "Amount", "Type"]
    columns.extend(EXTRA_FIELDS)
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[columns[4]] != "" and "cr" not in row[columns[2]].lower():
                result.append(
                    {
                        "txn_date": datetime.datetime.strptime(
                            row[columns[0].split()[0]], "%d %b %y"
                        ).strftime("%Y-%m-%d"),
                        "account": "ICICI Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": parse_str_to_float(row[columns[2]]),
                        "category": CATEGORY_MAPPING[row[columns[4]]],
                        "tags": row[columns[5]],
                        "notes": row[columns[6]],
                    }
                )
    write_result(output, result)
