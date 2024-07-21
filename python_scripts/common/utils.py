import os
import csv
import functools
import re
import datetime
from typing import Dict

from pathlib import Path


def has_headers(output):
    has_header = False
    if not Path(output).exists():
        with open(output, 'w') as fp:
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


def write_result(out_filename, result, headers=None, append=True):
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


def parse_str_to_float(in_val):
    return float("".join(in_val.strip().split(",")))


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


def auto_detect_category(description):
    result = []
    with open("config/category_mapping.csv", "r") as fp:
        reader: csv.DictReader[Dict[str, str]] = csv.DictReader(fp)
        for row in reader:
            pattern = re.compile(r'^.*\b(%s)\b.*$' % row["keyword"].lower())
            match = re.match(pattern, description.lower())
            if match is not None and match.group(1):
                result.append((row["keyword"], row["category"], row["tags"], row["notes"]))
    if len(result) > 1 and not all(list(map(lambda x: x[1] == result[0][1], result))):
        most_relevant = functools.reduce(lambda acc, curr: acc if len(acc[0]) > len(curr[0]) else curr, result, ('', '', '', ''))
        print("'%s' detected multiple categories='%s' most_relevant=%s" % (description, result, most_relevant))
        return most_relevant[1], most_relevant[2], most_relevant[3]
    if len(result) > 0:
        return result[0][1], result[0][2], result[0][3]
    return None, None, None
