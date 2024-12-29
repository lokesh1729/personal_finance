import csv
import os
import datetime
import functools
import re
from typing import Dict


def parse_str_to_float(in_val):
    if isinstance(in_val, float):
        return in_val
    return float("".join(in_val.strip().split(",")))


def auto_detect_category(description):
    result = []
    with open("config/category_mapping.csv", "r") as fp:
        reader: csv.DictReader[Dict[str, str]] = csv.DictReader(fp)
        for row in reader:
            pattern = re.compile(r"^.*(%s).*$" % row["keyword"].lower())
            match = re.match(pattern, description.lower())
            if match is not None and match.group(1):
                result.append(
                    (
                        row["keyword"],
                        row["category"],
                        row["tags"],
                        row["notes"] if row["notes"] else match.group(1),
                    )
                )
    if len(result) > 1 and not all(list(map(lambda x: x[1] == result[0][1], result))):
        most_relevant = functools.reduce(
            lambda acc, curr: acc if len(acc[0]) > len(curr[0]) else curr,
            result,
            ("", "", "", ""),
        )
        print(
            "'%s' detected multiple categories='%s' most_relevant=%s"
            % (description, result, most_relevant)
        )
        return most_relevant[1], most_relevant[2], most_relevant[3]
    if len(result) > 0:
        return result[0][1], result[0][2], result[0][3]
    return None, None, None


def clean_string(input_string: str) -> str:
    """
    Cleans the input string by replacing special characters with spaces,
    reducing multiple spaces to a single space, and trimming the string.

    Parameters:
    input_string (str): The string to be cleaned.

    Returns:
    str: The cleaned string.
    """
    # Replace all special characters with spaces
    string_with_spaces = re.sub(r"[^a-zA-Z0-9]", " ", input_string)

    # Replace multiple spaces with a single space
    single_space_string = re.sub(r"\s+", " ", string_with_spaces)

    # Trim leading and trailing spaces
    cleaned_string = single_space_string.strip()

    return cleaned_string


def is_valid_date(date_string, fmt):
    """
    Check if the given string is a valid date in the format dd/mm/yy.

    Parameters:
    date_string (str): The date string to check.

    Returns:
    bool: True if the date string is valid, False otherwise.
    """
    try:
        if isinstance(date_string, datetime.datetime):
            return True
        # Try to parse the date string using strptime
        datetime.datetime.strptime(date_string, fmt)
        return True
    except ValueError:
        # If ValueError is raised, the date is not valid
        return False


def convert_date_format(value, existing_format, new_format):
    try:
        return datetime.datetime.strptime(value, existing_format).strftime(new_format)
    except ValueError:
        return datetime.datetime.strptime(value, new_format).strftime(new_format)


def fix_date_format(
    file_path, date_column, input_date_format, output_date_format="%Y-%m-%d", rewrite=False
):
    result = []
    with open(file_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        for row in reader:
            result.append(
                {
                    **row,
                    date_column: convert_date_format(row[date_column].strip(), input_date_format, output_date_format)
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
