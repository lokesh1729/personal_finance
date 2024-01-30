import os
import csv
import datetime

from .constants import *


def has_headers(output):
    has_header = False
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


def write_result(output, result):
    headers_exist = has_headers(output)
    with open(output, "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=OUTPUT_COLUMNS)
        if not headers_exist:
            writer.writeheader()
        for each_row in result:
            writer.writerow(each_row)


def parse_str_to_float(in_val):
    return float("".join(in_val.strip().split(",")))


def fix_date_format_core(
    file_path, date_column, input_date_format, output_date_format="%Y-%m-%d"
):
    result = []
    headers = None
    with open(file_path, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        for row in reader:
            result.append(
                {
                    **row,
                    date_column: datetime.datetime.strptime(
                        row[date_column].strip(), input_date_format
                    ).strftime(output_date_format),
                }
            )
    temp_file_name, _ = os.path.splitext(file_path)
    output_file = "%s_output.csv" % temp_file_name
    with open(output_file, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for each_row in result:
            writer.writerow(each_row)
