import csv
import os
import datetime

from common import *


def kotak_fix_date_format(file_path):
    fix_date_format(file_path, "Transaction Date", "%d-%m-%Y")
    temp_file_name, _ = os.path.splitext(file_path)
    output_file = "%s_output.csv" % temp_file_name
    new_cols = [
        "Transaction Date",
        "Value Date",
        "Description",
        "Chq / Ref No.",
        "Debit",
        "Credit",
        "Balance",
    ]
    result = []
    with open(output_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result.append(
                {
                    new_cols[0]: row[new_cols[0]],
                    new_cols[1]: datetime.datetime.strptime(
                        row[new_cols[1]].strip(), "%d-%m-%Y"
                    ).strftime("%Y-%m-%d"),
                    new_cols[2]: row[new_cols[2]],
                    new_cols[3]: row[new_cols[3]],
                    new_cols[4]: row["Amount"] if row["Dr / Cr"] == "DR" else "",
                    new_cols[5]: row["Amount"] if row["Dr / Cr"] == "CR" else "",
                    new_cols[6]: row[new_cols[6]],
                }
            )
    with open(output_file, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_cols)
        writer.writeheader()
        for each_row in result:
            writer.writerow(each_row)


def kotak_bank_account_adapter(file_name, output):
    columns = [
        "Transaction Date",
        "Value Date",
        "Description",
        "Chq / Ref No.",
        "Amount",
        "Dr / Cr",
        "Balance",
    ]
    columns.extend(EXTRA_FIELDS)
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["Category"] != "":
                result.append(
                    {
                        "txn_date": convert_date_format(
                            row[columns[0]], "%d-%m-%Y", "%Y-%m-%d"
                        ),
                        "account": "Kotak Bank Account",
                        "txn_type": "Debit" if row[columns[5]] == "DR" else "Credit",
                        "txn_amount": parse_str_to_float(row[columns[4]]),
                        "category": CATEGORY_MAPPING[row[columns[7]]],
                        "tags": row[columns[8]],
                        "notes": row[columns[9]],
                    }
                )
    write_result(output, result)
