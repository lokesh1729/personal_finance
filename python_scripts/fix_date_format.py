import argparse
import csv
import datetime
import os

from common import *
from bank_accounts import *
from credit_cards import *
from wallets import *


def bank_account_adapter(account_type):
    if account_type == Account.HDFC_BANK_ACCOUNT.name:
        return hdfc_fix_date_format
    elif account_type == Account.KOTAK_BANK_ACCOUNT.name:
        return kotak_fix_date_format
    elif account_type == Account.EQUITAS_BANK_ACCOUNT.name:
        return equitas_fix_date_format
    elif account_type == Account.SBI_CREDIT_CARD.name:
        return sbi_cc_fix_date_format
    elif account_type == Account.HDFC_CREDIT_CARD.name:
        return hdfc_cc_fix_date_format
    elif account_type == Account.HDFC_UPI_CREDIT_CARD.name:
        return hdfc_cc_upi_fix_date_format
    elif account_type == Account.KOTAK_CREDIT_CARD.name:
        return kotak_cc_fix_date_format
    elif account_type == Account.ICICI_CREDIT_CARD.name:
        return icici_cc_fix_date_format
    elif account_type == Account.PAYTM_WALLET.name:
        return paytm_fix_date_format
    elif account_type == Account.IDFC_BANK_ACCOUNT.name:
        return idfc_fix_date_format
    elif account_type == Account.FASTAG_WALLET.name:
        return fastag_fix_date_format


def main():
    parser = argparse.ArgumentParser(
        prog="A program to fix the date formats",
        description="Takes the type of bank statement and outputs the converted format",
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Type of the bank statement.",
        dest="type",
        choices=list(map(lambda k: k.name, Account)),
        required=True,
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Absolute file path to the bank statement.",
        dest="path",
        required=True,
    )
    args = parser.parse_args()
    bank_account_adapter(args.type)(args.path)


if __name__ == "__main__":
    main()
