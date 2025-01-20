import argparse
import os

from common.csv_utils import rename_csv_columns, write_result_df, fix_date_format_df
from common.utils import fix_date_format

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Rename columns and fix date formats in a CSV file.")
    parser.add_argument("filename", type=str, help="Path to the input CSV file.")
    args = parser.parse_args()

    # File paths
    input_filename = args.filename
    base, ext = os.path.splitext(input_filename)
    output_filename = f"{base}_output{ext}"

    # Column mapping
    column_mapping = {
        'Fund': None,
        'Fund Name': 'Fund Name',
        ' Fund Name': 'Fund Name',
        'Folio Number': 'Folio Number',
        'Scheme Name': 'Scheme Name',
        'Trxn.Type': None,
        'Purchased Date': 'Purchased Date',
        'Current Units': 'Current Units',
        'Source Scheme units': 'Source Scheme Units',
        'Original Purchase Cost': 'Purchased Unit Price',
        'Original Cost Amount': 'Purchased Amount',
        'Grandfathered\nNAV as on 31/01/2018': None,
        'GrandFathered Cost Value': None,
        'IT Applicable\nNAV': None,
        'IT Applicable\nCost Value': None,
        'Redemption Date': 'Redemption Date',
        'Units': 'Redeemed Units',
        'Amount': 'Redeemed Amount',
        'Price': 'Redeemed Unit Price',
        'Tax Perc': None,
        'Tax': None,
        'Short Term': 'Short Term',
        'Indexed Cost': 'Indexed Cost',
        'Long Term With Index': 'Long Term With Index',
        'Long Term Without Index': 'Long Term Without Index',
    }

    # Apply column renaming
    df = rename_csv_columns(input_filename, column_mapping)
    df = fix_date_format_df(df, 'Purchased Date', '%d/%m/%Y')
    df = fix_date_format_df(df, 'Redemption Date', '%d/%m/%Y')
    write_result_df(output_filename, df)

    print(f"Processed file saved as: {output_filename}")