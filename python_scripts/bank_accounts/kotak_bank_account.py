import os

from common import *


def kotak_fix_date_format_df(df):
    if check_csv_header_df(df, "Transaction Date"):
        df = fix_date_format_df(df, "Transaction Date", "%d-%m-%Y")
    if check_csv_header_df(df, "Value Date"):
        df = fix_date_format_df(df, "Value Date", "%d-%m-%Y")
    return df


def is_na_or_empty(val):
    return pd.isna(val) or val is None or val == ''


def valid_date(val):
    return is_valid_date(val, "%d-%m-%Y")

def valid_number(val):
    return isinstance(val, int) or isinstance(val, float) or isinstance(parse_str_to_float(val), float)


def clean(df):
    indices_to_drop = []
    for index, row in df.iterrows():
        if is_na_or_empty(row["Transaction Date"]) or is_na_or_empty(row["Description"]) or is_na_or_empty(row["Chq / Ref No."]):
            indices_to_drop.append(index)
            continue
        if not valid_date(row["Transaction Date"]) or not valid_number(row["Amount"]):
            indices_to_drop.append(index)
            continue
    if indices_to_drop:
        df.drop(indices_to_drop, inplace=True)
    df = kotak_fix_date_format_df(df)
    return df



def kotak_bank_account_adapter(file_name, output):
    df = pd.read_csv(file_name, header=None, skiprows=13, on_bad_lines="skip")
    # Last column contains the same "Dr / Cr" with all values as "Cr", so drop that
    df.drop(columns=df.columns[-1], inplace=True)
    columns = ["Sl. No.", "Transaction Date", "Value Date", "Description", "Chq / Ref No.", "Amount", "Dr / Cr", "Balance"]
    df.columns = columns
    df = clean(df)
    result = []
    manual_correction = []
    for index, row in df.iterrows():
        category, tags, notes = auto_detect_category(row[columns[3]])
        if category:
            txn_amount = row[columns[5]] if row[columns[6]].lower() == "dr" \
                else row[columns[5]] * -1
            result.append(
                {
                    "txn_date": row[columns[1]],
                    "account": "Kotak Bank Account",
                    "txn_type": "Debit",
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
