import common
import csv
import os


def kotak_cc_fix_date_format(file_path, rewrite=False):
    common.fix_date_format(file_path, "Date", "%d/%m/%Y", rewrite=rewrite)


def kotak_credit_card_adapter(filename, out_filename):
    kotak_cc_fix_date_format(filename, rewrite=True)
    columns = ["Date", "Transaction details", "Amount (Rs.)"]
    result = []
    result2 = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "cr" not in row[columns[2]].lower():
                category, tags, notes = common.auto_detect_category(columns[1])
                result.append(
                    {
                        "txn_date": common.convert_date_format(row[columns[0]], "%d/%m/%Y", "%Y-%m-%d"),
                        "account": "Kotak Credit Card",
                        "txn_type": "Debit",
                        "txn_amount": common.parse_str_to_float(row[columns[2]]),
                        "category": category,
                        "tags": tags,
                        "notes": notes,
                    }
                )
                result2.append({
                    "Date": row[columns[0]],
                    "Transaction details": row[columns[1]],
                    "Spends Area": row["Spends Area"],
                    "Transaction Type": "Dr",
                    "Amount (Rs.)": common.parse_str_to_float(row[columns[2]]),
                })
            else:
                result2.append({
                    "Date": row[columns[0]],
                    "Transaction details": row[columns[1]],
                    "Spends Area": row["Spends Area"],
                    "Transaction Type": "Cr",
                    "Amount (Rs.)": common.parse_str_to_float(row[columns[2]].lower().split("cr")[0]),
                })
    common.write_result(out_filename, result)
    temp_file_name, _ = os.path.splitext(filename)
    common.write_result("%s_converted.csv" % temp_file_name, result2, headers=columns + ["Transaction Type", "Spends Area"])
