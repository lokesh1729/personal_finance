import csv
import os
import datetime

from common import *
from common.csv import rename_csv_columns


def equitas_fix_date_format(file_path, rewrite=False):
    fix_date_format(file_path, "Date", "%d-%b-%Y", rewrite=rewrite)


def equitas_bank_account_adapter(file_name, output):
    equitas_fix_date_format(file_name, rewrite=True)
    column_mapping = {
        "Date": "Date",
        "Reference No. / Cheque No.": "Reference No. / Cheque No.",
        "Narration": "Narration",
        "Withdrawal\nINR": "Withdrawal",
        "Deposit\nINR": "Deposit",
        "ClosingBalance\nINR": "Closing Balance",
    }
    rename_csv_columns(file_name, output, column_mapping)
