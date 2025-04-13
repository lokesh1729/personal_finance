import math
import os
import traceback

import pandas as pd

from common import (
    fix_date_format_df,
    auto_detect_category,
    check_csv_header_df,
    remove_empty_columns,
    write_result,
    write_result_df,
    rename_columns, check_file_type, is_valid_date
)
from common.pdf import unlock_pdf, extract_tables_from_pdf


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
        if not row["Date"] or not is_valid_date(row["Date"], "%d %b %y") or not row["Transaction Details"]:
            indices_to_drop.append(index)
        if isinstance(row["Date"], float):
            if math.isnan(row["Date"]):
                if (
                    "markup" in row["Transaction Details"].lower()
                    or "forgn" in row["Transaction Details"].lower()
                    or "igst" in row["Transaction Details"].lower()
                ):
                    df.at[index, "Date"] = df.at[index - 1, "Date"]
                else:
                    indices_to_drop.append(index)
            else:
                indices_to_drop.append(index)
    if indices_to_drop:
        df.drop(indices_to_drop, inplace=True)
    return df


def sbi_credit_card_adapter_old(filename, out_filename):
    # Read the CSV file into a DataFrame
    columns = ["Date", "Transaction Details", "Amount", "Type"]
    df = pd.read_csv(filename, header=None, on_bad_lines="skip")
    df.columns = columns
    df = clean(df)
    df = sbi_cc_fix_date_format_df(df)
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


def sbi_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        sbi_credit_card_adapter_old(filename, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "SBI_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(filename, [517, 16, 833, 427], [517, 16, 833, 427], "stream"):
            try:
                df = pd.read_csv(each_filename, header=None)
                # Drop the first row
                df = df.drop(0)
                df = remove_empty_columns(df)
                df.to_csv(each_filename, index=False, header=False)
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                sbi_credit_card_adapter_old(each_filename, output_file)
            except Exception:
                print(f"Exception in processing file {each_filename}. Skipping... Exception={traceback.format_exc()}")


def sbi2_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        sbi_credit_card_adapter_old(filename, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "SBI2_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(filename, [430, 16, 669, 428], [430, 16, 669, 428], "stream"):
            try:
                df = pd.read_csv(each_filename, header=None)
                # Drop the first row
                df = df.drop(0)
                df = remove_empty_columns(df)
                df.to_csv(each_filename, index=False, header=False)
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                sbi_credit_card_adapter_old(each_filename, output_file)
            except Exception:
                print(f"Exception in processing file {each_filename}. Skipping... Exception={traceback.format_exc()}")
