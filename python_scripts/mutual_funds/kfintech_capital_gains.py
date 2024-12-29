from common.csv_utils import rename_csv_columns
from common.utils import fix_date_format

if __name__ == "__main__":
    base_path = '/Users/lokeshsanapalli/projects/personal_finance/statements/mutual funds/'
    input_filename = 'fy23-24 capital gains (kfintech).csv'
    output_filename = 'fy23-24 capital gains (kfintech) converted.csv'
    column_mapping = {
        'Fund': None,
        'Fund Name': 'Fund Name',
        ' Fund Name': 'Fund Name',
        'Folio Number': 'Folio Number',
        'Scheme Name': 'Scheme Name',
        'Trxn.Type': None,
        'Purchased Date': 'Purchased Date',
        'Current Units': 'Current Units',
        'Source Scheme units': 'Source Scheme Units',
        'Original Purchase Cost': 'Purchased Unit Price',
        'Original Cost Amount': 'Purchased Amount',
        'Grandfathered\nNAV as on 31/01/2018': None,
        'GrandFathered Cost Value': None,
        'IT Applicable\nNAV': None,
        'IT Applicable\nCost Value': None,
        'Redemption Date': 'Redemption Date',
        'Units': 'Redeemed Units',
        'Amount': 'Redeemed Amount',
        'Price': 'Redeemed Unit Price',
        'Tax Perc': None,
        'Tax': None,
        'Short Term': 'Short Term',
        'Indexed Cost': 'Indexed Cost',
        'Long Term With Index': 'Long Term With Index',
        'Long Term Without Index': 'Long Term Without Index',
    }
    rename_csv_columns(base_path + input_filename, base_path + output_filename, column_mapping)
    fix_date_format(base_path + output_filename, 'Purchased Date', '%d/%m/%Y', rewrite=True)
    fix_date_format(base_path + output_filename, 'Redemption Date', '%d/%m/%Y', rewrite=True)
