import csv
import os
import datetime

from common import *


def equitas_fix_date_format(file_path):
    fix_date_format_core(file_path, "Date", "%d-%b-%Y")


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
    columns.append(EXTRA_FIELDS)
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Category"] != "":
                result.append(
                    {
                        "txn_date": datetime.datetime.strptime(
                            row[columns[0]], "%B %-d, %Y"
                        ).strftime("%Y-%m-%d"),
                        "account": "Kotak Bank Account",
                        "txn_type": "Debit" if row[columns[5]] == "DR" else "Credit",
                        "txn_amount": parse_str_to_float(row[columns[4]]),
                        "category": CATEGORY_MAPPING[row[columns[7]]],
                        "tags": row[columns[8]],
                        "notes": row[columns[9]],
                    }
                )
    write_result(output, result)
