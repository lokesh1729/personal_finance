import csv
import os
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--path",
        help="Absolute file path to the mutual funds statement.",
        dest="path",
        required=True,
    )
    args = parser.parse_args()
    mapping = {
        "MF_NAME": "SHORT_NAME",
        "INVESTOR_NAME": "Lokesh Sanapalli",
        "PAN": "FGIPS2901D",
        "FOLIO_NUMBER": "FOLIO",
        "PRODUCT_CODE": None,
        "SCHEME_NAME": "SHORT_NAME",
        "Type": None,
        "TRADE_DATE": "TRXN_DATE",
        "TRANSACTION_TYPE": "TRXN_DESC",
        "DIVIDEND_RATE": None,
        "AMOUNT": "TRXN_AMOUNT",
        "UNITS": "TRXN_UNITS",
        "PRICE": "PURCH_PRICE",
        "BROKER": None,
    }
    temp_file_name, _ = os.path.splitext(args.path)
    output_file = "%s_output.csv" % temp_file_name
    data = []
    with open(args.path, "r") as fp:
        for row in csv.DictReader(fp):
            curr_row = {}
            for key, value in mapping.items():
                if value is not None:
                    curr_row[key] = row.get(value, value)
                else:
                    curr_row[key] = row.get(value)
            data.append(curr_row)
    with open(output_file, "w") as fp:
        writer = csv.DictWriter(fp, list(mapping.keys()))
        writer.writeheader()
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    main()
