import math
import os

import pandas as pd

from common import (
    fix_date_format_df,
    auto_detect_category,
    parse_str_to_float,
    check_csv_header_df,
    remove_empty_columns,
    write_result,
    write_result_df,
    rename_columns
)


def clean(df):
    df = remove_empty_columns(df)
    df = rename_columns(df, ["Date", "Transaction Details", "Amount", "Type"])
    df = clean_rows(df)
    return df


def sbi_cc_fix_date_format_df(df):
    if check_csv_header_df(df, "Date"):
        df = fix_date_format_df(df, "Date", "%d %b %y")
    return df


def clean_rows(df):
    indices_to_drop = []
    for index, row in df.iterrows():
        if isinstance(row["Date"], float) and math.isnan(row["Date"]):
            if (
                "markup" in row["Transaction Details"].lower()
                or "forgn" in row["Transaction Details"].lower()
                or "igst" in row["Transaction Details"].lower()
            ):
                df.at[index, "Date"] = df.at[index - 1, "Date"]
            else:
                indices_to_drop.append(index)
    if indices_to_drop:
        df.drop(indices_to_drop, inplace=True)
    return df


def sbi_credit_card_adapter(filename, out_filename):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)
    df = clean(df)
    df = sbi_cc_fix_date_format_df(df)
    columns = ["Date", "Transaction Details", "Amount", "Type"]
    result = []
    for index, row in df.iterrows():
        if row[columns[3]] == "D":
            category, tags, notes = auto_detect_category(row[columns[1]])
            result.append(
                {
                    "txn_date": row[columns[0]],
                    "account": "SBI Credit Card",
                    "txn_type": "Debit",
                    "txn_amount": row[columns[2]],
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
    write_result(out_filename, result)
    temp_file_name, _ = os.path.splitext(filename)
    modified_filename = "%s_modified.csv" % temp_file_name
    write_result_df(modified_filename, df)
