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
    rename_columns, check_file_type, is_valid_date, parse_str_to_float
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
        if not row["Date"] or not is_valid_date(row["Date"], "%d %b %y") or not row["Transaction Details"]:
            indices_to_drop.append(index)
    if indices_to_drop:
        df.drop(indices_to_drop, inplace=True)
    return df


def create_df(filename, drop_first_row=False):
    """Create a cleaned SBI credit card DataFrame, mirroring HDFC adapter flow."""
    extra_empty_column = False
    columns = ["Date", "Transaction Details", "Amount", "Type"]
    df = pd.read_csv(filename, on_bad_lines="skip")
    df = remove_empty_columns(df)

    if drop_first_row and not df.empty:
        df = df.drop(df.index[0]).reset_index(drop=True)

    df.columns = columns

    if extra_empty_column:
        df["Transaction Details"] = df[""].astype(str) + " " + df["Transaction Details"].astype(str)
        df = df.drop("", axis=1)
        df["Transaction Details"] = df["Transaction Details"].str.replace("nan ", "").str.replace(" nan", "").str.strip()

    df = clean(df)
    df = sbi_cc_fix_date_format_df(df)

    temp_file_name, _ = os.path.splitext(filename)
    modified_filename = "%s_modified.csv" % temp_file_name
    write_result_df(modified_filename, df)
    return df


def process_sbi_df(df, out_filename):
    if df is None or df.empty:
        return

    result = []
    for index, row in df.iterrows():
        source_type = str(row.get("Type", "")).strip().upper()
        if source_type in ("D", "M"):
            txn_type = "Debit"
        elif source_type == "C":
            txn_type = "Credit"
        else:
            continue

        transaction_details = str(row.get("Transaction Details", ""))
        category, tags, notes = auto_detect_category(transaction_details)
        amount_value = parse_str_to_float(row.get("Amount"))
        if amount_value is None:
            continue
        if txn_type == "Credit":
            amount_value = -abs(amount_value)
        elif txn_type == "Debit":
            amount_value = abs(amount_value)

        result.append(
            {
                "txn_date": row["Date"],
                "account": "SBI Credit Card",
                "txn_type": txn_type,
                "txn_amount": amount_value,
                "category": category,
                "tags": tags,
                "notes": notes,
            }
        )
    write_result(out_filename, result)


def sbi_credit_card_adapter_old(filename, out_filename):
    df = create_df(filename)
    process_sbi_df(df, out_filename)


def sbi_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        df = pd.read_csv(filename, names=["Date", "Transaction Details", "Amount", "Type"])
        process_sbi_df(df, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "SBI_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(filename, [517, 16, 833, 427], [517, 16, 833, 427], "stream"):
            try:
                df = create_df(each_filename, drop_first_row=True)
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                process_sbi_df(df, output_file)
            except Exception:
                print(f"Exception in processing file {each_filename}. Skipping... Exception={traceback.format_exc()}")


def sbi2_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        df = pd.read_csv(filename, names=["Date", "Transaction Details", "Amount", "Type"])
        process_sbi_df(df, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "SBI2_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(filename, [430, 16, 669, 428], [430, 16, 669, 428], "stream"):
            try:
                df = create_df(each_filename, drop_first_row=True)
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                process_sbi_df(df, output_file)
            except Exception:
                print(f"Exception in processing file {each_filename}. Skipping... Exception={traceback.format_exc()}")


def sbi3_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        df = pd.read_csv(filename, names=["Date", "Transaction Details", "Amount", "Type"])
        process_sbi_df(df, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "SBI3_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(filename, [430, 16, 340+241, 190+408], [430, 16, 340+241, 190+408], "stream"):
            try:
                df = create_df(each_filename, drop_first_row=True)
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                process_sbi_df(df, output_file)
            except Exception:
                print(f"Exception in processing file {each_filename}. Skipping... Exception={traceback.format_exc()}")
