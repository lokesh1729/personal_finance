import argparse
import os
import pandas as pd


def validate_headers(files):
    header = None
    for file in files:
        df = pd.read_csv(file, nrows=0)  # Read only the headers
        if header is None:
            header = df.columns
        elif not header.equals(df.columns):
            raise ValueError(f"Headers do not match for file: {file}")
    return header


def merge_csv_files(input_files, output_file):
    validate_headers(input_files)
    dataframes = [pd.read_csv(file) for file in input_files]
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_csv(output_file, index=False)
    print(f"Merged CSV saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Merge multiple CSV files with the same headers.")
    parser.add_argument('input_files', metavar='input_files', type=str, nargs='+', help='Paths to input CSV files')
    parser.add_argument('--output', '-o', type=str, help='Output file name (optional)')

    args = parser.parse_args()
    input_files = args.input_files
    output_file = args.output if args.output else os.path.join('/tmp', os.path.basename(input_files[0]).replace('.csv',
                                                                                                                '_output.csv')
                                                               )

    merge_csv_files(input_files, output_file)


if __name__ == "__main__":
    main()
