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
    columns.extend(EXTRA_FIELDS)
    aggregated_categories = [
        "Food & Dining",
        "Fruits & Vegetables",
        "Groceries",
        "Egg & Meat",
    ]
    aggregated_result = {}
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[columns[7]] != "":
                if CATEGORY_MAPPING[row[columns[7]]] not in aggregated_categories:
                    result.append(
                        {
                            "txn_date": convert_date_format(
                                row[columns[0]], "%d/%m/%y", "%Y-%m-%d"
                            ),
                            "account": "HDFC Bank Account",
                            "txn_type": "Debit" if row[columns[4]] != "" else "Credit",
                            "txn_amount": parse_str_to_float(row[columns[4]])
                            if row[columns[4]] != ""
                            else parse_str_to_float(row[columns[5]]) * -1,
                            "category": CATEGORY_MAPPING[row[columns[7]]],
                            "tags": row[columns[8]],
                            "notes": row[columns[9]],
                        }
                    )
                else:
                    temp = aggregated_result.get(CATEGORY_MAPPING[row[columns[7]]])
                    if temp is not None:
                        aggregated_result[CATEGORY_MAPPING[row[columns[7]]]] = temp + (
                            parse_str_to_float(row[columns[4]])
                            if row[columns[4]] != ""
                            else parse_str_to_float(row[columns[5]]) * -1
                        )
                    else:
                        aggregated_result[CATEGORY_MAPPING[row[columns[7]]]] = (
                            parse_str_to_float(row[columns[4]])
                            if row[columns[4]] != ""
                            else parse_str_to_float(row[columns[5]]) * -1
                        )
        for key, value in aggregated_result.items():
            result.append(
                {
                    "txn_date": "",
                    "account": "HDFC Bank Account",
                    "txn_type": "Debit",
                    "txn_amount": value,
                    "category": key,
                    "tags": "",
                    "notes": "consolidated amount",
                }
            )

    write_result(output, result)
