import csv
import os
import datetime

from common import *


def idfc_fix_date_format(file_path):
    fix_date_format(file_path, "Transaction Date", "%d-%b-%Y")
    temp_file_name, _ = os.path.splitext(file_path)
    output_file = "%s_output.csv" % temp_file_name
    result = []
    headers = []
    with open(output_file, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        for row in reader:
            result.append(
                {
                    **row,
                    "Value Date": datetime.datetime.strptime(
                        row["Value Date"].strip(), "%d-%b-%Y"
                    ).strftime("%Y-%m-%d"),
                }
            )
    with open(output_file, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for each_row in result:
            writer.writerow(each_row)
