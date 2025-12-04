# TODO : write usage and description
import os
import argparse
import xlrd
import csv

from common import convert_date_format


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--path",
        help="Absolute file path to the mutual funds statement in XLS format.",
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
    output_file = f"{temp_file_name}_output.csv"
    data = []

    # Open the XLS file using xlrd
    workbook = xlrd.open_workbook(args.path)
    if "Consolidated Account Statement" not in workbook.sheet_names():
        raise ValueError("Sheet named 'Consolidated Account Statement' not found in the file.")

    sheet = workbook.sheet_by_name("Consolidated Account Statement")

    # Extract headers
    headers = [sheet.cell_value(0, col) for col in range(sheet.ncols)]

    # Process rows
    for row_idx in range(1, sheet.nrows):
        row_values = sheet.row_values(row_idx)
        row_dict = dict(zip(headers, row_values))
        curr_row = {}
        for key, value in mapping.items():
            if value is not None:
                if value == "TRADE_DATE":
                    curr_row[key] = convert_date_format(row_dict.get(value, value), "%d-%b-%Y", "%Y-%m-%d")
                else:
                    curr_row[key] = row_dict.get(value, value)
            else:
                curr_row[key] = row_dict.get(value)
        data.append(curr_row)

    # Write the processed data to a CSV file
    with open(output_file, "w", newline="") as fp:
        writer = csv.DictWriter(fp, list(mapping.keys()))
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    main()
