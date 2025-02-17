import math
import os

from common import *


def hdfc_fix_date_format_df(df):
    if check_csv_header_df(df, "Date"):
        df = fix_date_format_df(df, "Date", "%d/%m/%y")
    return df


def is_na_or_empty(val):
    return pd.isna(val) or val is None or val == ''

def valid_number(val):
    return isinstance(val, int) or isinstance(val, float) or isinstance(parse_str_to_float(val), float)


def clean(df):
    indices_to_drop = []
    for index, row in df.iterrows():
        if (is_na_or_empty(row["Date"]) or is_na_or_empty(row["Chq./Ref.No."]) or (is_na_or_empty(row["Withdrawal Amt."])
                and is_na_or_empty("Deposit Amt."))):
            indices_to_drop.append(index)
            continue
        if not is_valid_date(row["Date"], "%d/%m/%y") or (not valid_number(row["Withdrawal Amt."]) and not valid_number(row["Deposit Amt."])):
            indices_to_drop.append(index)
            continue
    if indices_to_drop:
        df.drop(indices_to_drop, inplace=True)
    df = hdfc_fix_date_format_df(df)
    return df



def hdfc_bank_account_adapter(file_name, output):
    columns = ['Date',
         'Narration',
         'Chq./Ref.No.',
         'Value Dt',
         'Withdrawal Amt.',
         'Deposit Amt.',
         'Closing Balance'
    ]
    df = pd.read_excel(file_name, names=columns)
    df = clean(df)
    result = []
    manual_correction = []
    auto_correction = []
    for index, row in df.iterrows():
        category, tags, notes = auto_detect_category(row[columns[1]])
        if category:
            txn_amount = -1
            if row[columns[4]] != "" and not math.isnan(row[columns[4]]):
                txn_amount = row[columns[4]]
            elif row[columns[5]] != "" and not math.isnan(row[columns[5]]):
                txn_amount = row[columns[5]] * -1
            result.append(
                {
                    "txn_date": row[columns[0]],
                    "account": "HDFC Bank Account",
                    "txn_type": "Debit" if txn_amount > 0 else "Credit",
                    "txn_amount": txn_amount,
                    "category": category,
                    "tags": tags,
                    "notes": notes,
                }
            )
            auto_correction.append(row)
        else:
            manual_correction.append(row)
    write_result(output, result)
    temp_file_name, _ = os.path.splitext(file_name)
    modified_filename = "%s_modified.csv" % temp_file_name
    manual_filename = "%s_manual.csv" % temp_file_name
    auto_filename = "%s_auto.csv" % temp_file_name
    write_result_df(modified_filename, df)
    write_result_df(manual_filename, pd.DataFrame(manual_correction))
    write_result_df(auto_filename, pd.DataFrame(auto_correction))
