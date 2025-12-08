"""
File processing utilities for Excel and CSV files.
"""
import pandas as pd
import os
import sys
from typing import List, Dict, Optional

# Add python_scripts to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
python_scripts_dir = os.path.dirname(os.path.dirname(script_dir))
if python_scripts_dir not in sys.path:
    sys.path.insert(0, python_scripts_dir)

from common.utils import safe_float


def detect_file_type(file_path: str) -> str:
    """Detect file type based on extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.xlsx' or ext == '.xls':
        return 'excel'
    elif ext == '.csv':
        return 'csv'
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def is_zerodha_file(file_path: str) -> bool:
    """Check if the Excel file is from Zerodha by checking for specific sheets."""
    try:
        excel_file = pd.ExcelFile(file_path)
        required_sheets = ["Equity", "Mutual Funds", "Combined"]
        return all(sheet in excel_file.sheet_names for sheet in required_sheets)
    except Exception:
        return False


def remove_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove columns that are completely empty."""
    return df.dropna(axis=1, how='all')


def remove_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows that are completely empty and reset index."""
    return df.dropna(axis=0, how='all').reset_index(drop=True)


def find_header_row(df: pd.DataFrame, expected_headers: List[str]) -> Optional[int]:
    """
    Find the row index where the expected headers are found (case-insensitive).
    Returns None if headers are not found.
    """
    # Convert expected headers to lowercase for case-insensitive comparison
    expected_headers_lower = [h.lower() for h in expected_headers]
    
    for idx, row in df.iterrows():
        # Convert row values to lowercase for case-insensitive comparison
        row_values_lower = [str(val).strip().lower() if pd.notna(val) else "" for val in row.values]
        found_headers = [h for h in expected_headers_lower if h in row_values_lower]
        if len(found_headers) >= len(expected_headers_lower):
            return idx
    
    return None


def process_mutual_fund_holdings_file(file_path: str) -> List[Dict]:
    """
    Process mutual fund holdings file (Excel or CSV) and return list of dictionaries.
    Expected headers: Scheme Name, AMC, Category, Sub-category, Folio No.,
    Source, Units, Invested Value, Current Value, Returns, XIRR
    """
    file_type = detect_file_type(file_path)
    
    if file_type == 'excel':
        # Try to read from "Mutual Funds" sheet first, otherwise read first sheet
        try:
            df = pd.read_excel(file_path, sheet_name="Mutual Funds")
        except:
            df = pd.read_excel(file_path, sheet_name=0)
    else:
        df = pd.read_csv(file_path)
    
    # Remove empty columns and rows
    df = remove_empty_columns(df)
    df = remove_empty_rows(df)
    
    # Expected headers for mutual fund holdings
    expected_headers = [
        "Scheme Name", "AMC", "Category", "Sub-category", "Folio No.",
        "Source", "Units", "Invested Value", "Current Value", "Returns", "XIRR"
    ]
    
    # Find header row
    header_row = find_header_row(df, expected_headers)
    if header_row is None:
        raise ValueError("Could not find expected headers in the file")
    
    # Set headers and remove rows before header
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)
    
    # Remove empty rows again after header processing
    df = remove_empty_rows(df)
    
    # Prepare records
    records = []
    for _, row in df.iterrows():
        # Skip if Scheme Name is empty
        if pd.isna(row.get("Scheme Name")) or str(row.get("Scheme Name")).strip() == "":
            continue
        
        record = {
            "Scheme Name": str(row.get("Scheme Name", "")).strip(),
            "AMC": str(row.get("AMC", "")).strip() if pd.notna(row.get("AMC")) else None,
            "Category": str(row.get("Category", "")).strip() if pd.notna(row.get("Category")) else None,
            "Sub-category": str(row.get("Sub-category", "")).strip() if pd.notna(row.get("Sub-category")) else None,
            "Folio No.": str(row.get("Folio No.", "")).strip() if pd.notna(row.get("Folio No.")) else None,
            "Source": str(row.get("Source", "")).strip() if pd.notna(row.get("Source")) else None,
            "Units": safe_float(row.get("Units")),
            "Invested Value": safe_float(row.get("Invested Value")),
            "Current Value": safe_float(row.get("Current Value")),
            "Returns": safe_float(row.get("Returns")),
            "XIRR": safe_float(row.get("XIRR"))
        }
        records.append(record)
    
    return records

