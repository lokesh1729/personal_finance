import os
import csv

import pandas as pd
import xlrd
import openpyxl
import argparse
import magic


def is_valid_date(date_string):
    # Simple regex to check if the date looks like DD MMM YYYY or a valid date format
    return date_string != ""


def is_valid_number(value):
    # Check if the value is a number or empty
    try:
        if value == "" or value is None or pd.isna(value):
            return False
        float(value)
        return True
    except ValueError:
        return False


def is_valid_row(row):
    # Check if row has valid data, assuming it has 7 columns like ['Txn Date', 'Value Date', ...]
    if len(row) != 7:
        return False

    # Validate 'Txn Date' and 'Value Date'
    if not is_valid_date(row[0]) or not is_valid_date(row[1]):
        return False

    # Validate 'Debit', 'Credit', and 'Balance' as numbers
    if row[4] != "" and is_valid_number(row[4]):
        return False
    if not (
        is_valid_number(row[4]) and is_valid_number(row[5]) and is_valid_number(row[6])
    ):
        return False

    return True


def detect_file_type(file_path):
    # Use magic to detect the file type
    file_type = magic.from_file(file_path, mime=True)
    return file_type


def process_csv(file_path, output_writer):
    # Process CSV file
    with open(file_path, mode="r", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if is_valid_row(row):
                output_writer.writerow(row)


def process_xls(file_path, output_writer):
    # Process .xls file using xlrd
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)  # Assuming data is in the first sheet
    for row_idx in range(sheet.nrows):
        row = sheet.row_values(row_idx)
        if is_valid_row(row):
            output_writer.writerow(row)


def process_xlsx(file_path, output_writer):
    # Process .xlsx file using openpyxl
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active  # Assuming data is in the first sheet
    for row in sheet.iter_rows(values_only=True):
        if is_valid_row(row):
            output_writer.writerow(row)


def convert_file_to_csv(file_path, output_dir):
    file_type = detect_file_type(file_path)
    output_file = os.path.join(
        output_dir,
        os.path.basename(file_path).replace(".xls", ".csv").replace(".xlsx", ".csv"),
    )

    with open(output_file, mode="w", newline="") as f:
        output_writer = csv.writer(f)
        try:
            if "spreadsheet" in file_type:
                if file_path.endswith(".xls"):
                    process_xls(file_path, output_writer)
                elif file_path.endswith(".xlsx"):
                    process_xlsx(file_path, output_writer)
            elif "csv" in file_type or "text" in file_type:
                process_csv(file_path, output_writer)
            else:
                print(
                    f"Unsupported file format: {file_path} (detected type: {file_type})"
                )
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Converted {file_path} to {output_file}")


def process_directory(directory_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Walk through each file in the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            import ipdb

            ipdb.set_trace()
            file_path = os.path.join(root, file)
            convert_file_to_csv(file_path, output_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Convert files (.xls/.xlsx/.csv) to .csv, skipping invalid rows"
    )
    parser.add_argument("directory", help="Directory containing files")
    parser.add_argument(
        "--output", default="csv_output", help="Output directory for .csv files"
    )

    args = parser.parse_args()

    process_directory(args.directory, args.output)


if __name__ == "__main__":
    main()
