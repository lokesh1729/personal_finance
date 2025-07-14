import math
import os
import re
import traceback
import pandas as pd

from common import (
    auto_detect_category,
    parse_str_to_float,
    write_result,
    check_csv_header_df,
    fix_date_format_df,
    remove_empty_columns,
    remove_empty_rows,
    remove_named_columns, write_result_df, is_valid_date, check_file_type, remove_lines,
)
from common.pdf import unlock_pdf, extract_tables_from_pdf


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
                break
            elif each_col == "Date":
                if (row[each_col] == each_col or (isinstance(row[each_col], float) and math.isnan(row[each_col]))
                        or
                        not (is_valid_date(row[each_col], "%d/%m/%Y")
                             or is_valid_date(row[each_col], "%d/%m/%Y %H:%M:%S"))
                ):
                    drop_index = True
                    break
        if drop_index:
            indices_to_drop.append(index)
    if indices_to_drop:
        df.drop(indices_to_drop, inplace=True)
    return df

def remove_nan_columns(df):
    # Check if all values in the last column are NaN
    if df.iloc[:, -1].isna().all():
        # Swap the last two columns
        df.columns.values[-1], df.columns.values[-2] = df.columns.values[-2], df.columns.values[-1]
        # Drop the last column
        df.drop(columns=df.columns[-1], inplace=True)
        return df, True
    return df, False


def clean(df, columns):
    df = remove_empty_columns(df)
    df = remove_empty_rows(df)
    df = remove_mismatch_rows(df, columns)
    pattern = re.compile(r'\b\d+(\.\d{1,2})?\b')
    for index, row in df.iterrows():
        df.at[index, 'Description'] = row["Transaction Description"]
        if isinstance(row["Amount (in Rs.)"], str):
            cr_dr = "cr" if "cr" in row["Amount (in Rs.)"].lower() else "dr"
            match = re.match(pattern, row["Amount (in Rs.)"].replace(",", ""))
            if match.groups() is not None:
                amt = match.group(0)
                df.at[index, 'Amount'] = float(amt)
                df.at[index, 'Debit / Credit'] = cr_dr
        else:
            df.at[index, 'Amount'] = float(row["Amount (in Rs.)"])
            df.at[index, 'Debit / Credit'] = "Debit"
    remove_named_columns(df, ["Transaction Description", "Amount (in Rs.)"])
    return df


def hdfc_credit_card_adapter_old(filename, output):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename, header=None, on_bad_lines='skip')
    df, is_modified = remove_nan_columns(df)
    old_columns = ["Date", "Transaction Description", "Amount (in Rs.)"]
    df.columns = old_columns
    df = clean(df, old_columns)
    columns = ["Date", "Description", "Amount", "Debit / Credit"]
    df = hdfc_cc_fix_date_format_df(df)
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


def hdfc_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        hdfc_credit_card_adapter_old(filename, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "HDFC_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(filename, [413, 16, 670, 594], [49, 10, 629, 601], "lattice"):
            try:
                df = pd.read_csv(each_filename, header=None)
                # Drop the first row
                df = df.drop(0)
                df = remove_empty_columns(df)
                df.to_csv(each_filename, index=False, header=False)
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                hdfc_credit_card_adapter_old(each_filename, output_file)
            except Exception:
                print(f"Exception in processing file {each_filename}. Skipping... Exception={traceback.format_exc()}")


def hdfc_upi_credit_card_adapter_old(filename, output):
    # Read the CSV file into a DataFrame
    old_columns = ["Date", "Transaction Description", "NeuCoins", "Amount (in Rs.)"]
    df = pd.read_csv(filename, header=None, on_bad_lines="skip")
    df = remove_empty_columns(df)
    df = remove_empty_rows(df)
    df.columns = old_columns
    df = clean(df, old_columns)
    df = hdfc_cc_fix_date_format_df(df)
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


def hdfc_upi_credit_card_adapter(filename, output):
    if check_file_type(filename) == "CSV":
        hdfc_upi_credit_card_adapter_old(filename, output)
    elif check_file_type(filename) == "PDF":
        unlock_pdf(filename, "HDFC_CREDIT_CARD_PASSWORD")
        for each_filename in extract_tables_from_pdf(filename, [413, 16, 670, 594], [53, 16, 648, 594], "lattice"):
            try:
                df = pd.read_csv(each_filename, header=None)
                # Drop the first row
                df = df.drop(0)
                df = remove_empty_columns(df)
                df.to_csv(each_filename, index=False, header=False)
                temp_file_name, _ = os.path.splitext(each_filename)
                output_file = "%s_output.csv" % temp_file_name
                hdfc_upi_credit_card_adapter_old(each_filename, output_file)
            except Exception:
                print(f"Exception in processing file {each_filename}. Skipping... Exception={traceback.format_exc()}")
