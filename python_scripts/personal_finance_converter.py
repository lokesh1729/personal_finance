import argparse

from bank_accounts import *
from credit_cards import *


def bank_account_adapter(account_type):
    if account_type == Account.HDFC_BANK_ACCOUNT.name:
        return hdfc_bank_account_adapter
    elif account_type == Account.KOTAK_BANK_ACCOUNT.name:
        return kotak_bank_account_adapter
    elif account_type == Account.SBI_CREDIT_CARD.name:
        return sbi_credit_card_adapter
    elif account_type == Account.SBI2_CREDIT_CARD.name:
        return sbi2_credit_card_adapter
    elif account_type == Account.HDFC_CREDIT_CARD.name:
        return hdfc_credit_card_adapter
    elif account_type == Account.KOTAK_CREDIT_CARD.name:
        return kotak_credit_card_adapter
    elif account_type == Account.ICICI_CREDIT_CARD.name:
        return icici_credit_card_adapter
    elif account_type == Account.EQUITAS_BANK_ACCOUNT.name:
        return equitas_bank_account_adapter


def main():
    parser = argparse.ArgumentParser(
        prog="A program to convert bank statements to the preferred format",
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
    parser.add_argument(
        "-o",
        "--output",
        help="Absolute file path to the output file",
        dest="output",
        required=False,
    )
    args = parser.parse_args()
    temp_file_name, _ = os.path.splitext(args.path)
    output_file = "%s_output.csv" % temp_file_name
    bank_account_adapter(args.type)(args.path, args.output if args.output else output_file)


if __name__ == "__main__":
    main()
