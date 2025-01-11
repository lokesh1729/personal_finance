import argparse
import csv
import re
from collections import defaultdict
from typing import Dict



def auto_investment_fixer(hdfc_filepath, kotak_filepath):
    hdfc_to_kotak = 0
    kotak_to_investments = 0
    investments = defaultdict(int)
    with open(hdfc_filepath, 'r') as fp:
        reader: csv.DictReader[Dict[str, str]] = csv.DictReader(fp)
        for row in reader:
            pattern = re.compile(r'^.*\b(%s)\b.*$' % "NEFT DR-KKBK0008122-LOKESH SANAPALLI".lower())
            match = re.match(pattern, row["Narration"].lower())
            if match is not None and match.group(1):
                print("HDFC :: Found a match. row='%s'" % row)
                hdfc_to_kotak += float(row["Withdrawal Amt."])
    with open(kotak_filepath, 'r') as fp:
        reader: csv.DictReader[Dict[str, str]] = csv.DictReader(fp)
        patterns = {
            "niyomoney": "CTRAZORPAY-NIYOMONEY",
            "groww": "INDIAN CLEARING CORP",
            "us_stocks": "CASHFREE PAYMENTS",
            "stocks": "ZERODHA",
            "amma": "AMMA"
        }
        for row in reader:
            for key, value in patterns.items():
                pattern = re.compile(r'^.*(%s).*$' % value.lower())
                match = re.match(pattern, row["Description"].lower())
                if match is not None and match.group(1):
                    print("Kotak :: Found a match. row='%s'" % row)
                    kotak_to_investments += float(row["Debit"])
                    investments[key] += float(row["Debit"])
    print("Total HDFC to kotak=%s" % hdfc_to_kotak)
    print("Total kotak to investments=%s" % kotak_to_investments)
    print("Total diff=%s" % (hdfc_to_kotak - kotak_to_investments))
    print("Investments=%s" % investments)


def main():
    parser = argparse.ArgumentParser(description="Auto investment fixer")
    parser.add_argument('--hdfc', type=str, help='Path to hdfc bank account', required=True)
    parser.add_argument('--kotak', type=str, help='Path to kotak bank account', required=True)
    args = parser.parse_args()
    auto_investment_fixer(args.hdfc, args.kotak)


if __name__ == "__main__":
    main()
