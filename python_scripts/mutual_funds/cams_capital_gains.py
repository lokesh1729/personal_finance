import argparse
import os

from celery.utils.sysinfo import df

from common import rename_csv_columns, write_result_df, fix_date_format_df

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Rename columns in a CSV file based on a column mapping.")
    parser.add_argument("filename", type=str, help="Path to the input CSV file.")
    args = parser.parse_args()

    # File paths
    input_filename = args.filename
    base, ext = os.path.splitext(input_filename)
    output_filename = f"{base}_output{ext}"

    # Column mapping
    column_mapping = {
        'AMC Name': 'AMC Name',
        'Folio No': 'Folio No',
        'ASSET CLASS': 'Asset Class',
        'NAME': None,
        'STATUS': None,
        'PAN': None,
        'GUARDIAN_PAN': None,
        'Scheme Name': 'Scheme Name',
        'Desc': 'Description',
        'Date': 'Redemption Date',
        'Units': 'Redemption Units',
        'Amount': 'Redemption Amount',
        'Price': 'Redemption Unit Price',
        'STT': 'STT',
        'Desc_1': 'Purchase Description',
        'Date_1': 'Purchased Date',
        'PurhUnit': 'Purchased Units',
        'RedUnits': 'Redeemed Units',
        'Unit Cost': 'Unit Cost',
        'Indexed Cost': 'Indexed Cost',
        'Units As On 31/01/2018 (Grandfathered Units)': None,
        'NAV As On 31/01/2018 (Grandfathered NAV)': None,
        'Market Value As On 31/01/2018 (Grandfathered Value)': None,
        'Short Term': 'Short Term Capital Gains',
        'Long Term With Index': 'Long Term Capital Gains With Index',
        'Long Term Without Index': 'Long Term Capital Gains Without Index',
        'Tax Perc': 'Tax Percentage On Capital Gains',
        'Tax Deduct': 'Tax Deducted On Capital Gains',
        'Tax Surcharge': 'Tax Surcharge On Capital Gains',
    }

    # Process the file
    renamed_df = rename_csv_columns(input_filename, column_mapping)
    renamed_df = fix_date_format_df(renamed_df, 'Purchased Date', '%d-%b-%Y')
    renamed_df = fix_date_format_df(renamed_df, 'Redemption Date', '%d-%b-%Y')

    write_result_df(output_filename, renamed_df)
    print(f"Processed file saved as: {output_filename}")