import csv
import os
import datetime

from common import *


def idfc_fix_date_format(file_path):
    output_file = fix_date_format(file_path, "Transaction Date", "%d-%b-%Y")
    fix_date_format(output_file, "Value Date", "%d-%b-%Y", rewrite=True)
