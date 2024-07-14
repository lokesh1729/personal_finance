from common import *


def fastag_fix_date_format(file_path):
    fix_date_format(
        file_path, "TXN DATE & TIME", "%m/%d/%Y %I:%M:%S %p", "%Y-%m-%d %H:%M:%S"
    )
