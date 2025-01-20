import argparse

from common import *


def fastag_fix_date_format(file_path):
    base, ext = os.path.splitext(file_path)
    output_filename = f"{base}_output{ext}"
    df = pd.read_csv(file_path)
    df = fix_date_format_df(
        df, "TXN DATE & TIME", "%m/%d/%Y %I:%M:%S %p", "%Y-%m-%d %H:%M:%S"
    )
    write_result_df(output_filename, df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename columns in a CSV file based on a column mapping.")
    parser.add_argument("filename", type=str, help="Path to the input CSV file.")
    args = parser.parse_args()

    # File paths
    input_filename = args.filename
    fastag_fix_date_format(input_filename)
