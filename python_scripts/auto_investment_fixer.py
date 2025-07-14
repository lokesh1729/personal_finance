import argparse
import csv
import re
import logging
from collections import defaultdict
from typing import Dict

from common import parse_str_to_float

# Set up logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger("auto-investment-fixer")

EXPECTED_INVESTMENTS = {
    'niyomoney': 42000.0,
    'groww': 8000.0,
    'groww2': 2000.0,
    'us_stocks': 5000.0,
    'stocks': 25000.0
}

def auto_investment_fixer(hdfc_filepath, kotak_filepath):
    hdfc_to_kotak = 0
    kotak_to_investments = 0
    investments = defaultdict(float)

    # Process HDFC transactions
    with open(hdfc_filepath, 'r') as fp:
        reader: csv.DictReader[Dict[str, str]] = csv.DictReader(fp)
        for row in reader:
            pattern = re.compile(r'^.*\b(%s)\b.*$' % "NEFT DR-KKBK0008122-LOKESH SANAPALLI".lower())
            match = re.match(pattern, row["Narration"].lower())
            if match is not None and match.group(1):
                log.debug("HDFC :: Found a match. row='%s'" % row)
                hdfc_to_kotak += parse_str_to_float(row["Withdrawal Amt."])

    # Process Kotak transactions
    with open(kotak_filepath, 'r') as fp:
        reader: csv.DictReader[Dict[str, str]] = csv.DictReader(fp)
        patterns = {
            "niyomoney": "CTRAZORPAY-NIYOMONEY",
            "groww": "INDIAN CLEARING CORP",
            "groww2": "GROWW INVEST TECH",
            "us_stocks": "CASHFREE PAYMENTS",
            "stocks": "ZERODHA",
            "amma": "AMMA"
        }
        for row in reader:
            for key, value in patterns.items():
                pattern = re.compile(r'^.*(%s).*$' % value.lower())
                match = re.match(pattern, row["Description"].lower())
                if match is not None and match.group(1):
                    log.debug("Kotak :: Found a match. row='%s'" % row)
                    amount = parse_str_to_float(row["Debit"])
                    kotak_to_investments += amount
                    investments[key] += amount

    log.debug("Total HDFC to kotak=%s", hdfc_to_kotak)
    log.debug("Total kotak to investments=%s", kotak_to_investments)
    log.debug("Total diff=%s", hdfc_to_kotak - kotak_to_investments)

    # Log deviations
    for key, expected_amount in EXPECTED_INVESTMENTS.items():
        actual_amount = investments.get(key, 0.0)
        if round(actual_amount, 2) != round(expected_amount, 2):
            log.info("Deviation for '%s': expected=%.2f, actual=%.2f, diff=%.2f",
                     key, expected_amount, actual_amount, actual_amount - expected_amount)

def main():
    parser = argparse.ArgumentParser(description="Auto investment fixer")
    parser.add_argument('--hdfc', type=str, help='Path to hdfc bank account', required=True)
    parser.add_argument('--kotak', type=str, help='Path to kotak bank account', required=True)
    args = parser.parse_args()
    auto_investment_fixer(args.hdfc, args.kotak)

if __name__ == "__main__":
    main()
