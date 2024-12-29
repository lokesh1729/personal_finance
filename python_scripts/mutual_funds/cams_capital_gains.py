from common.csv_utils import rename_csv_columns

if __name__ == "__main__":
    base_path = '/Users/lokeshsanapalli/projects/personal_finance/statements/mutual funds/capital gains/'
    input_filename = 'FY23-24 capital gains.csv'
    output_filename = 'FY23-24 capital gains converted.csv'
    column_mapping = {
        'AMC Name': 'AMC Name',
        'Folio No': 'Folio No',
        'ASSET CLASS': 'Asset Class',
        'NAME': None,
        'STATUS': None,
        'PAN': None,
        'GUARDIAN_PAN': None,
        'Scheme Name': 'Scheme Name',
        'Desc': 'Description',
        'Date': 'Redemption Date',
        'Units': 'Redemption Units',
        'Amount': 'Redemption Amount',
        'Price': 'Redemption Unit Price',
        'STT': 'STT',
        'Desc_1': 'Purchase Description',
        'Date_1': 'Purchase Date',
        'PurhUnit': 'Purchased Units',
        'RedUnits': 'Redeemed Units',
        'Unit Cost': 'Unit Cost',
        'Indexed Cost': 'Indexed Cost',
        'Units As On 31/01/2018 (Grandfathered Units)': None,
        'NAV As On 31/01/2018 (Grandfathered NAV)': None,
        'Market Value As On 31/01/2018 (Grandfathered Value)': None,
        'Short Term': 'Short Term Capital Gains',
        'Long Term With Index': 'Long Term Capital Gains With Index',
        'Long Term Without Index': 'Long Term Capital Gains Without Index',
        'Tax Perc': 'Tax Percentage On Capital Gains',
        'Tax Deduct': 'Tax Deducted On Capital Gains',
        'Tax Surcharge': 'Tax Surcharge On Capital Gains',
    }
    rename_csv_columns(base_path + input_filename, base_path + output_filename, column_mapping)
