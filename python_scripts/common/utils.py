import csv
import os
import datetime
import mimetypes
import functools
import re
from typing import Dict


def parse_str_to_float(in_val):
    if isinstance(in_val, float):
        return in_val
    if not in_val:
        return 0.0
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
                        f'{row["notes"] if row["notes"] else match.group(1)} \n\n source of truth = {description}',
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
    return "Others", "", f"\n\n source of truth = {description}"


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
    except (ValueError, TypeError):
        # If ValueError is raised, the date is not valid
        return False


def check_file_type(file_path):
    """
    Check if the file is a CSV or PDF based on its extension and MIME type.

    :param file_path: Path to the file
    :return: A string indicating the file type ('CSV', 'PDF', or 'Unknown')
    """
    # Get the file extension and MIME type
    mime_type, _ = mimetypes.guess_type(file_path)

    # Check for CSV or PDF based on MIME type
    if mime_type == 'text/csv':
        return 'CSV'
    elif mime_type == 'application/pdf':
        return 'PDF'
    else:
        return 'Unknown'


def remove_lines(file_path: str, num_lines: int, position: str = "start") -> None:
    """
    Remove a specified number of lines from the start or end of a file.

    Parameters:
    - file_path (str): Path to the input file.
    - num_lines (int): Number of lines to remove.
    - position (str): 'start' or 'end' to indicate from where to remove lines.

    Returns:
    - None
    """
    if position not in ("start", "end"):
        raise ValueError("Position must be either 'start' or 'end'.")

    with open(file_path, 'r') as file:
        lines = file.readlines()

    if num_lines >= len(lines):
        # Remove all lines if num_lines is more than or equal to total lines
        remaining_lines = []
    elif position == "start":
        remaining_lines = lines[num_lines:]
    else:  # position == "end"
        remaining_lines = lines[:-num_lines]

    with open(file_path, 'w') as file:
        file.writelines(remaining_lines)