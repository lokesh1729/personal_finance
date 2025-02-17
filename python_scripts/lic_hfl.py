import argparse

from common.pdf import extract_tables_from_pdf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract table data from LIC HFL Statement.")
    parser.add_argument("filename", type=str, help="Path to the input CSV file.")
    args = parser.parse_args()

    # File paths
    input_filename = args.filename
    extract_tables_from_pdf(input_filename, [150, 21, 796, 575], [150, 21, 796, 575], "stream")
