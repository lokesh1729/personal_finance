import csv
import os
import datetime

from common import *
from common.csv import rename_csv_columns


def equitas_fix_date_format_df(df):
    if check_csv_header_df(df, "Date"):
        df = fix_date_format_df(df, "Date", "%d-%b-%Y")
    return df


def is_na_or_empty(val):
    return pd.isna(val) or val is None or val == ''


def valid_date(val):
    return is_valid_date(val, "%d-%b-%Y")


def valid_number(val):
    return isinstance(val, int) or isinstance(val, float) or isinstance(parse_str_to_float(val), float)


def clean_columns(df):
    """
        Cleans the column names of the given DataFrame by renaming specific columns.

        Parameters:
        df (pd.DataFrame): The input DataFrame with columns to be cleaned.

        Returns:
        pd.DataFrame: A DataFrame with cleaned column names.
        """
    # Define a mapping for the old column names to new column names
    column_mapping = {
        "Withdrawal\nINR": "Withdrawal",
        "Deposit\nINR": "Deposit",
        "ClosingBalance\nINR": "Closing Balance"
    }

    # Rename the columns using the mapping
    df.rename(columns=column_mapping, inplace=True)

    return df


def clean(df):
    df = remove_empty_rows(df)
    df = remove_empty_columns(df)
    indices_to_drop = []
    for index, row in df.iterrows():
        if is_na_or_empty(row["Date"]) or is_na_or_empty(row["Narration"]) or is_na_or_empty(row["Reference No. / Cheque No."]):
            indices_to_drop.append(index)
            continue
        if not valid_date(row["Date"]) or not valid_number(row["ClosingBalance\nINR"]):
            indices_to_drop.append(index)
            continue
        row["ClosingBalance\nINR"] = parse_str_to_float(row["ClosingBalance\nINR"])
        row["Withdrawal\nINR"] = parse_str_to_float(row["Withdrawal\nINR"])
        row["Deposit\nINR"] = parse_str_to_float(row["Deposit\nINR"])
    if indices_to_drop:
        df.drop(indices_to_drop, inplace=True)
    df = equitas_fix_date_format_df(df)
    df = clean_columns(df)
    return df


def equitas_bank_account_adapter(file_name, output):
    columns = ["Date", "Reference No. / Cheque No.", "Narration", "Withdrawal\nINR", "Deposit\nINR", "ClosingBalance\nINR"]
    df = pd.read_csv(file_name)
    df = clean(df)
    result = []
    manual_correction = []
    for index, row in df.iterrows():
        category, tags, notes = auto_detect_category(row[columns[2]])
        if category:
            txn_amount = row["Withdrawal"] if row["Withdrawal"] > 0 \
                else row["Deposit"] * -1
            result.append(
                {
                    "txn_date": row[columns[0]],
                    "account": "Equitas Bank Account",
                    "txn_type": "Debit" if txn_amount > 0 else "Credit",
                    "txn_amount": txn_amount,
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
        else:
            manual_correction.append(row)
    write_result(output, result)
    temp_file_name, _ = os.path.splitext(file_name)
    modified_filename = "%s_modified.csv" % temp_file_name
    manual_filename = "%s_manual.csv" % temp_file_name
    write_result_df(modified_filename, df)
    write_result_df(manual_filename, pd.DataFrame(manual_correction))