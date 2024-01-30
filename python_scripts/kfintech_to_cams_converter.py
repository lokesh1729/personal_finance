import csv
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--outfile")
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
    data = []
    with open(args.file, "r") as fp:
        for row in csv.DictReader(fp):
            curr_row = {}
            for key, value in mapping.items():
                if value is not None:
                    curr_row[key] = row.get(value, value)
                else:
                    curr_row[key] = row.get(value)
            data.append(curr_row)
    with open(args.outfile, "w") as fp:
        writer = csv.DictWriter(fp, list(mapping.keys()))
        writer.writeheader()
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    main()
