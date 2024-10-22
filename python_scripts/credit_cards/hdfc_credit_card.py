import csv
import math
import os
import re
import pandas as pd

from common import (
    fix_date_format,
    auto_detect_category,
    parse_str_to_float,
    write_result,
    check_csv_header,
    check_csv_header_df,
    fix_date_format_df,
    remove_empty_columns,
    remove_empty_rows,
    remove_named_columns, write_result_df,
)


def hdfc_cc_fix_date_format(file_path, rewrite=False):
    if check_csv_header(file_path, "DATE"):
        fix_date_format(file_path, "DATE", "%d/%m/%Y", rewrite=rewrite)


def hdfc_cc_upi_fix_date_format(file_path, rewrite=False):
    if check_csv_header(file_path, "DATE"):
        fix_date_format(file_path, "DATE", "%d/%m/%Y %H:%M:%S", rewrite=rewrite)


def hdfc_cc_fix_date_format_df(df):
    if check_csv_header_df(df, "Date"):
        df = fix_date_format_df(df, "Date", "%d/%m/%Y")
    return df


def hdfc_cc_upi_fix_date_format_df(df):
    if check_csv_header_df(df, "Date"):
        df = fix_date_format_df(df, "Date", "%d/%m/%Y %H:%M:%S")
    return df


def remove_mismatch_rows(df, columns):
    indices_to_drop = []
    for index, row in df.iterrows():
        drop_index = False
        for each_col in columns:
            if each_col == "NeuCoins":
                continue
            if each_col not in row:
                drop_index = True
            elif each_col == "Date":
                if row[each_col] == each_col or isinstance(row[each_col], float) and math.isnan(row[each_col]):
                    drop_index = True
        if drop_index:
            indices_to_drop.append(index)
    if indices_to_drop:
        df.drop(indices_to_drop, inplace=True)
    return df


def clean_file(df, columns):
    df = remove_mismatch_rows(df, columns)
    df = remove_empty_columns(df)
    df = remove_empty_rows(df)
    pattern = re.compile(r'([0-9]+)')
    for index, row in df.iterrows():
        df.at[index, 'Description'] = row["Transaction Description"]
        match = re.match(pattern, row["Amount (in Rs.)"].replace(",", ""))
        if match.groups() is not None:
            amt = match.group(0)
            cr_dr = "cr" if "cr" in row["Transaction Description"].lower() else "dr"
            df.at[index, 'Amount'] = amt
            df.at[index, 'Debit / Credit'] = cr_dr
    remove_named_columns(df, ["Transaction Description", "Amount (in Rs.)"])
    return df


def hdfc_credit_card_adapter(filename, output):
    # Read the CSV file into a DataFrame
    old_columns = ["Date", "Transaction Description", "Unknown", "Amount (in Rs.)"]
    df = pd.read_csv(filename, header=None, names=old_columns)
    df = clean_file(df, old_columns)
    df = hdfc_cc_fix_date_format_df(df)
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    result = []
    for index, row in df.iterrows():
        if "cr" not in row[columns[3]].lower():
            category, tags, notes = auto_detect_category(row[columns[1]])
            result.append(
                {
                    "txn_date": row[columns[0]],
                    "account": "HDFC Credit Card",
                    "txn_type": "Debit",
                    "txn_amount": parse_str_to_float(row[columns[2]]),
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
    write_result(output, result)
    temp_file_name, _ = os.path.splitext(filename)
    modified_filename = "%s_modified.csv" % temp_file_name
    write_result_df(modified_filename, df)


def hdfc_upi_credit_card_adapter(filename, output):
    # Read the CSV file into a DataFrame
    old_columns = ["Date", "Transaction Description", "Unknown", "NeuCoins", "Amount (in Rs.)"]
    df = pd.read_csv(filename, header=None, names=old_columns)
    df = clean_file(df, old_columns)
    df = hdfc_cc_upi_fix_date_format_df(df)
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    result = []
    for index, row in df.iterrows():
        if "cr" not in row[columns[3]].lower():
            category, tags, notes = auto_detect_category(row[columns[1]])
            result.append(
                {
                    "txn_date": row[columns[0]],
                    "account": "HDFC Credit Card",
                    "txn_type": "Debit",
                    "txn_amount": parse_str_to_float(row[columns[2]]),
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
    write_result(output, result)
    temp_file_name, _ = os.path.splitext(filename)
    modified_filename = "%s_modified.csv" % temp_file_name
    write_result_df(modified_filename, df)
