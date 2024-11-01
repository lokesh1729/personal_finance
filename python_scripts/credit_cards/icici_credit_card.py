import os

import pandas as pd

from common import remove_empty_rows, remove_empty_columns, parse_str_to_float, check_csv_header_df, fix_date_format_df, \
    auto_detect_category, write_result, write_result_df


def icici_cc_fix_date_format_df(df):
    if check_csv_header_df(df, "Date"):
        df = fix_date_format_df(df, "Date", "%d/%m/%Y")
    return df


def clean(df):
    indices_to_delete = []
    for index, row in df.iterrows():
        condition = [pd.isna(val) or val == 'HTTP://WWW.AM IN' for val in row]
        if condition and all(condition):
            indices_to_delete.append(index)
    if indices_to_delete:
        df.drop(indices_to_delete, inplace=True)
    df = remove_empty_rows(df)
    df = remove_empty_columns(df)
    return df


def safe_at(df, row_label, col_label):
    """Safely access a value in a DataFrame using .at without raising an exception."""
    if row_label in df.index and col_label in df.columns:
        return df.at[row_label, col_label]
    else:
        return None  # or any default value you prefer


def icici_credit_card_adapter(filename, out_filename):
    df = pd.read_csv(filename, header=None)
    df = clean(df)
    columns = ["Date", "Sr.No.", "Transaction Details", "Reward Points", "Intl Amount", "Amount", "Type"]
    if (safe_at(df, 0, 0) and safe_at(df, 0, 0) == 'Date SerNo.'
            and safe_at(df, 0, 2) and safe_at(df, 0, 2) == 'Transaction Details'):
        new_data = []
        for index, row in df.iterrows():
            if pd.isna(row[2]) and pd.isna(row[5]):
                continue
            try:
                new_data.append({
                    columns[0]: row[0].split(" ")[0],
                    columns[1]: row[0].split(" ")[1],
                    columns[2]: row[2],
                    columns[3]: row[3],
                    columns[4]: 0 if pd.isna(row[4]) else row[4],
                    columns[5]: parse_str_to_float(row[5].lower().split("cr")[0]),
                    columns[6]: "Credit" if "cr" in row[5].lower() else "Debit",
                })
            except (ValueError, KeyError):
                pass
        df = pd.DataFrame(new_data)
    else:
        new_data = []
        for index, row in df.iterrows():
            try:
                new_data.append({
                    columns[0]: row[0],
                    columns[1]: row[1],
                    columns[2]: row[2],
                    columns[3]: row[3],
                    columns[4]: "",
                    columns[5]: parse_str_to_float(row[4].lower().split("cr")[0]),
                    columns[6]: "Credit" if "cr" in row[4].lower() else "Debit",
                })
            except (ValueError, KeyError):
                pass
        df = pd.DataFrame(new_data)
    df = icici_cc_fix_date_format_df(df)
    result = []
    for index, row in df.iterrows():
        if row["Type"] == "Debit":
            category, tags, notes = auto_detect_category(row["Transaction Details"])
            result.append(
                {
                    "txn_date": row["Date"],
                    "account": "HDFC Credit Card",
                    "txn_type": "Debit",
                    "txn_amount": row["Amount"],
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
    write_result(out_filename, result)
    temp_file_name, _ = os.path.splitext(filename)
    modified_filename = "%s_modified.csv" % temp_file_name
    write_result_df(modified_filename, df)
