from common import *


def kotak_fix_date_format(file_path, rewrite=False):
    output_file = file_path
    if check_csv_header(file_path, "Transaction Date"):
        output_file = fix_date_format(
            file_path, "Transaction Date", "%d-%m-%Y", rewrite=rewrite
        )
    new_cols = [
        "Transaction Date",
        "Value Date",
        "Description",
        "Chq / Ref No.",
        "Debit",
        "Credit",
        "Balance",
    ]
    if all([check_csv_header(file_path, header) for header in new_cols]):
        return
    result = []
    with open(output_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            debit = None
            credit = None
            if "Dr / Cr" in row:
                debit = row["Amount"] if row["Dr / Cr"] == "DR" else ""
                credit = row["Amount"] if row["Dr / Cr"] == "CR" else ""
            if "Credit" in row and "Debit" in row:
                debit = row["Debit"]
                credit = row["Credit"]
            if credit is None or debit is None:
                raise ValueError("Invalid data format")
            result.append(
                {
                    new_cols[0]: convert_date_format(
                        row[new_cols[0]], "%d-%m-%Y", "%Y-%m-%d"
                    ),
                    new_cols[1]: convert_date_format(
                        row[new_cols[1]], "%d-%m-%Y", "%Y-%m-%d"
                    ),
                    new_cols[2]: row[new_cols[2]],
                    new_cols[3]: row[new_cols[3]],
                    new_cols[4]: debit,
                    new_cols[5]: credit,
                    new_cols[6]: row[new_cols[6]],
                }
            )
    with open(output_file, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_cols)
        writer.writeheader()
        for each_row in result:
            writer.writerow(each_row)


def kotak_bank_account_adapter(file_name, output):
    kotak_fix_date_format(file_name, rewrite=True)
    columns = [
        "Transaction Date",
        "Value Date",
        "Description",
        "Chq / Ref No.",
        "Debit",
        "Credit",
        "Balance",
    ]
    result = []
    with open(file_name, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            category, tags, notes = auto_detect_category(row[columns[2]])
            result.append(
                {
                    "txn_date": convert_date_format(
                        row[columns[0]], "%d-%m-%Y", "%Y-%m-%d"
                    ),
                    "account": "Kotak Bank Account",
                    "txn_type": "Debit" if row[columns[4]] != "" else "Credit",
                    "txn_amount": parse_str_to_float(row[columns[4]])
                    if row[columns[4]] != ""
                    else parse_str_to_float(row[columns[5]]),
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
    write_result(output, result)
