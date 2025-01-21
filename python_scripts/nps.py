import argparse
import os

import pandas as pd
import io


def process_nps_statement(file_content):
    # Split the content into lines
    lines = file_content.split('\n')

    # Initialize lists to store data for both tables
    contributions_data = []
    transactions_data = []

    # Flags to identify which section we're reading
    reading_contributions = False
    reading_transactions = False

    # Column headers for both tables
    contributions_columns = ['Date', 'Particulars', 'Uploaded By', 'Employee Contribution(Rs)',
                             'Employer\'s Contribution(Rs)', 'Total(Rs)']
    transactions_columns = ['Date', 'Particulars', 'Withdrawal/ deduction in units towards intermediary charges (Rs)',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME G - TIER I Amount (Rs)',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME G - TIER I NAV (Rs)',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME G - TIER I Units',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME C - TIER I Amount (Rs)',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME C - TIER I NAV (Rs)',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME C - TIER I Units',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME E - TIER I Amount (Rs)',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME E - TIER I NAV (Rs)',
                            'ICICI PRUDENTIAL PENSION FUND SCHEME E - TIER I Units']

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Check for section headers
        if "Contribution/Redemption Details" in line:
            reading_contributions = True
            reading_transactions = False
            continue
        elif "Transaction Details" in line:
            reading_contributions = False
            reading_transactions = True
            continue

        # Process contributions section
        if reading_contributions:
            # Split the line by comma and check if it matches the expected format
            fields = line.split(',')
            if len(fields) >= 6 and fields[0].strip() and fields[0].lower() != 'date':
                contributions_data.append(fields[:6])  # Take only the first 6 fields

        # Process transactions section
        if reading_transactions:
            # Split the line by comma and check if it matches the expected format
            fields = line.split(',')
            if len(fields) >= 12 and fields[0].strip() and fields[0].lower() != 'date':
                transactions_data.append(fields[:12])  # Take only the first 12 fields

    # Create DataFrames
    contributions_df = pd.DataFrame(contributions_data, columns=contributions_columns)
    transactions_df = pd.DataFrame(transactions_data, columns=transactions_columns)

    return contributions_df, transactions_df


def save_to_csv(contributions_df, transactions_df, base_filename):
    # Save to CSV files
    contributions_df.to_csv(f'{base_filename}_contributions.csv', index=False)
    transactions_df.to_csv(f'{base_filename}_transactions.csv', index=False)


# Example usage
if __name__ == "__main__":
    # Read the file content
    parser = argparse.ArgumentParser(description="Extract transaction statement and detailed transaction CSVs from NPS CSV.")
    parser.add_argument("filename", type=str, help="Path to the input CSV file.")
    args = parser.parse_args()

    # File paths
    input_filename = args.filename
    base, ext = os.path.splitext(input_filename)
    with open(input_filename, 'r') as file:
        file_content = file.read()

    # Process the file
    contributions_df, transactions_df = process_nps_statement(file_content)

    # Save to CSV files
    save_to_csv(contributions_df, transactions_df, base)

    print("Files have been created successfully!")
    print(f"Number of contribution records: {len(contributions_df)}")
    print(f"Number of transaction records: {len(transactions_df)}")