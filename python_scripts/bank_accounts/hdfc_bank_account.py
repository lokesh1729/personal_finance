import shutil
from typing import Dict

from common import *


def hdfc_fix_date_format(filepath, rewrite=False):
    try:
        return fix_date_format(filepath, "Date", "%d/%m/%y", rewrite=rewrite)
    except ValueError:
        print("Maybe the file is already converted to the ISO date format")
        return filepath


def hdfc_bank_account_adapter(file_name, output):
    file_name = hdfc_fix_date_format(file_name, rewrite=True)
    columns = {
        "date": "Date",
        "narration": "Narration",
        "ref": "Chq./Ref.No.",
        "value_date": "Value Dt",
        "withdrawal_amount": "Withdrawal Amt.",
        "deposit_amount": "Deposit Amt.",
        "closing_balance": "Closing Balance",
    }
    aggregated_categories = [
        "Food & Dining",
        "Fruits & Vegetables",
        "Groceries",
        "Egg & Meat",
    ]
    aggregated_result = {}
    result = []
    rows_to_keep = []
    with open(file_name, "r") as csvfile:
        reader: csv.DictReader[Dict[object, object]] = csv.DictReader(csvfile)
        for row in reader:
            category, tags, notes = auto_detect_category(row[columns["narration"]])
            if category is not None and category != "":
                if category not in aggregated_categories:
                    result.append(
                        {
                            "txn_date": row[columns["date"]],
                            "account": "HDFC Bank Account",
                            "txn_type": "Debit" if row[columns["withdrawal_amount"]] != "" else "Credit",
                            "txn_amount": parse_str_to_float(row[columns["withdrawal_amount"]])
                            if row[columns["withdrawal_amount"]] != ""
                            else parse_str_to_float(row[columns["deposit_amount"]]) * -1,
                            "category": category,
                            "tags": tags,
                            "notes": notes,
                        }
                    )
                else:
                    temp = aggregated_result.get(category)
                    if temp is not None:
                        aggregated_result[category] = temp + (
                            parse_str_to_float(row[columns["withdrawal_amount"]])
                            if row[columns["withdrawal_amount"]] != ""
                            else parse_str_to_float(row[columns["deposit_amount"]]) * -1
                        )
                    else:
                        aggregated_result[category] = (
                            parse_str_to_float(row[columns["withdrawal_amount"]])
                            if row[columns["withdrawal_amount"]] != ""
                            else parse_str_to_float(row[columns["deposit_amount"]]) * -1
                        )
            else:
                rows_to_keep.append(row)
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
    temp_file_name, _ = os.path.splitext(file_name)
    output_file = "%s_original.csv" % temp_file_name
    shutil.copyfile(file_name, output_file)
    write_result(file_name, rows_to_keep, headers=list(columns.values()), append=False)
    write_result(output, result, append=False)
