import csv
import datetime

from pathlib import Path

import pandas as pd


def convert_date_format(value, existing_format, new_format):
    try:
        if isinstance(value, datetime.datetime):
            return value.strftime(new_format)
        return datetime.datetime.strptime(value, existing_format).strftime(new_format)
    except ValueError:
        return datetime.datetime.strptime(value, new_format).strftime(new_format)


def fix_date_format(
    file_path,
    date_column,
    input_date_format,
    output_date_format="%Y-%m-%d",
    rewrite=False,
):
    result = []
    with open(file_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        for row in reader:
            result.append(
                {
                    **row,
                    date_column: convert_date_format(
                        row[date_column].strip(), input_date_format, output_date_format
                    ),
                }
            )
    if rewrite:
        output_file = file_path
    else:
        temp_file_name, _ = os.path.splitext(file_path)
        output_file = "%s_output.csv" % temp_file_name
    with open(output_file, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for each_row in result:
            writer.writerow(each_row)
    return output_file


def fix_date_format_df(
    df: pd.DataFrame,
    date_column: str,
    input_date_format: str,
    output_date_format: str = "%Y-%m-%d",
) -> pd.DataFrame:
    """
    Fixes the date format in a specified column of a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the date column.
    date_column (str): The name of the column with dates to fix.
    input_date_format (str): The current format of the dates in the column.
    output_date_format (str): The desired output format for the dates.

    Returns:
    pd.DataFrame: A DataFrame with the updated date formats.
    """

    def handle(val):
        try:
            return convert_date_format(val, input_date_format, output_date_format)
        except Exception:
            return val

    # Apply the date conversion function to the specified column
    df[date_column] = df[date_column].apply(handle)

    return df


def rename_csv_columns(input_filename, output_filename, column_mapping):
    """
    Maps columns in an existing CSV file to a new CSV file based on the provided column mapping.

    Args:
        input_filename (str): The filename of the existing CSV file.
        output_filename (str): The filename of the new CSV file to be created.
        column_mapping (dict): A dictionary where the keys are the existing column names and the values are the new column names
    """
    # Read the existing CSV file
    with open(input_filename, mode="r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        # Create a new list of fieldnames based on the column_mapping
        new_fieldnames = list(
            filter(
                lambda item: item is not None,
                [column_mapping.get(field) for field in fieldnames],
            )
        )

        # Write to a new CSV file with the updated column names
        with open(output_filename, mode="w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
            writer.writeheader()

            for row in reader:
                # Create a new row dictionary with updated column names
                new_row = {
                    column_mapping.get(key): value
                    for key, value in row.items()
                    if column_mapping.get(key) is not None
                }
                writer.writerow(new_row)


def check_csv_header(file_name, header_name):
    """
    Checks if a specific header is present in a CSV file.

    Parameters:
    - file_name (str): The name of the CSV file.
    - header_name (str): The name of the header to check.

    Returns:
    - bool: True if the header is present, False otherwise.
    """
    try:
        with open(file_name, mode="r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Read the first row as headers
            return header_name in headers
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def check_csv_header_df(df: pd.DataFrame, header_name: str) -> bool:
    """
    Checks if the specified header is present in the DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to check.
    header_name (str): The name of the header to check for.

    Returns:
    bool: True if the header is present, False otherwise.
    """
    # Check if the header exists in the DataFrame columns
    return header_name in df.columns


def remove_empty_columns(df):
    """
    Reads a CSV file and removes any empty columns.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pd.DataFrame: A DataFrame with empty columns removed.
    """
    # Remove empty columns
    return df.dropna(axis=1, how="all")


def remove_empty_rows(df):
    return df.dropna(how="all")


def remove_named_columns(df, columns):
    return df.drop(columns=columns, inplace=True)


def rename_columns(df, target_columns):
    """
    Reads a CSV file and modifies it based on matching columns.

    Parameters:
    df (pd.DataFrame): The path to the CSV file.
    target_columns: List of columns

    Returns:
    pd.DataFrame: A modified DataFrame with updated column values.
    """
    df = df.set_axis(target_columns, axis=1, copy=False)
    return df


def has_headers(output):
    has_header = False
    if not Path(output).exists():
        with open(output, "w") as fp:
            pass
    with open(output, "rb") as csvfile:
        sniffer = csv.Sniffer()
        sample = csvfile.read(2048).decode("utf-8")
        try:
            has_header = sniffer.has_header(sample)
        except csv.Error as exc:
            print("Exception : %s" % exc)
            pass
        csvfile.seek(0)
    return has_header


def write_result(out_filename, result, headers=None, append=False):
    if headers is None:
        output_columns = [
            "txn_date",
            "account",
            "txn_type",
            "txn_amount",
            "category",
            "tags",
            "notes",
        ]
    else:
        output_columns = headers
    headers_exist = has_headers(out_filename)
    with open(out_filename, "a+" if append else "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=output_columns)
        if not headers_exist:
            writer.writeheader()
        for each_row in result:
            writer.writerow(each_row)


def write_result_df(out_filename, df):
    df.to_csv(out_filename, index=False, header=True)
