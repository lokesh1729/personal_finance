import csv
import os
import datetime

from common import *


def hdfc_fix_date_format(file_path):
    fix_date_format_core(file_path, "Date", "%d/%m/%y")


def hdfc_bank_account_adapter(file_name, output):
    columns = [
        "Date",
        "Narration",
        "Chq./Ref.No.",
        "Value Dt",
        "Withdrawal Amt.",
        "Deposit Amt.",
        "Closing Balance",
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
                        "account": "HDFC Bank Account",
                        "txn_type": "Debit" if row[columns[4]] != "" else "Credit",
                        "txn_amount": parse_str_to_float(row[columns[4]])
                        if row[columns[4]] != ""
                        else parse_str_to_float(row[columns[5]]),
                        "category": CATEGORY_MAPPING[row[columns[7]]],
                        "tags": row[columns[8]],
                        "notes": row[columns[9]],
                    }
                )
    write_result(output, result)
