import csv
import os
import datetime

from common.utils import *
from common.constants import *


def icici_cc_fix_date_format(file_path, rewrite=False):
    fix_date_format(file_path, "Date", "%d/%m/%Y", rewrite=rewrite)


def icici_credit_card_adapter(filename, out_filename):
    icici_cc_fix_date_format(filename, rewrite=True)
