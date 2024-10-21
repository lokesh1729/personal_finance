import csv
import math
import os

from common import (
    fix_date_format_df,
    auto_detect_category,
    write_result,
    parse_str_to_float,
    check_csv_header_df,
    remove_empty_columns,
    clean_string,
    write_result,
    write_result_df,
)

from fuzzywuzzy import fuzz


def rename_columns(df, target_columns):
    """
    Reads a CSV file and modifies it based on matching columns.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pd.DataFrame: A modified DataFrame with updated column values.
    """
    df = df.set_axis(target_columns, axis=1, copy=False)
    return df


def clean_file(filename):
    df = remove_empty_columns(filename)
    df = rename_columns(df, ["Date", "Transaction Details", "Amount", "Type"])
    return df


def sbi_cc_fix_date_format_df(df):
    import ipdb

    ipdb.set_trace()
    if check_csv_header_df(df, "Date"):
        df = fix_date_format_df(df, "Date", "%d %b %y")
    return df


def sbi_cc_fix_date_format(file_path, rewrite=False):
    fix_date_format(file_path, "Date", "%d %b %y", rewrite=rewrite)


def clean_rows(df):
    for index, row in df.iterrows():
        if isinstance(row["Date"], float) and math.isnan(row["Date"]):
            if (
                "markup" in row["Transaction Details"].lower()
                or "forgn" in row["Transaction Details"].lower()
                or "igst" in row["Transaction Details"].lower()
            ):
                df.at[index, "Date"] = df.at[index - 1, "Date"]
            else:
                df.drop(index=index, inplace=True)
    return df


def sbi_credit_card_adapter(filename, out_filename):
    df = clean_file(filename)
    df = clean_rows(df)
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
                    "txn_amount": parse_str_to_float(row[columns[2]]),
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
    write_result(out_filename, result)
    temp_file_name, _ = os.path.splitext(filename)
    modified_filename = "%s_modified.csv" % temp_file_name
    write_result_df(modified_filename, df)
