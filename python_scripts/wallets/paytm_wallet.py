from common import *


def paytm_fix_date_format(file_path):
    fix_date_format_core(file_path, "Date", "%d/%m/%Y %H:%M:%S")
