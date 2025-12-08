"""
Zerodha-specific handler for processing stock holdings.
"""
import os
import sys
import pandas as pd
from typing import List, Dict, Optional
from .file_utils import (
    detect_file_type,
    remove_empty_columns,
    remove_empty_rows,
    find_header_row
)

# Add python_scripts to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
python_scripts_dir = os.path.dirname(os.path.dirname(script_dir))
if python_scripts_dir not in sys.path:
    sys.path.insert(0, python_scripts_dir)

from common.utils import safe_float


def process_stock_holdings_file(file_path: str) -> List[Dict]:
    """
    Process stock holdings file (Excel or CSV) and return list of dictionaries.
    Expected headers: Symbol, ISIN, Sector, Quantity Available, Quantity Discrepant,
    Quantity Long Term, Quantity Pledged (Margin), Quantity Pledged (Loan),
    Average Price, Previous Closing Price, Unrealized P&L, Unrealized P&L Pct.
    """
    file_type = detect_file_type(file_path)
    
    if file_type == 'excel':
        df = pd.read_excel(file_path, sheet_name="Equity")
    else:
        df = pd.read_csv(file_path)
    
    # Remove empty columns and rows
    df = remove_empty_columns(df)
    df = remove_empty_rows(df)
    
    # Expected headers for stock holdings (ISINSector may be one column or separate)
    expected_headers = [
        "Symbol", "ISIN", "Sector", "Quantity Available", "Quantity Discrepant",
        "Quantity Long Term", "Quantity Pledged (Margin)", "Quantity Pledged (Loan)",
        "Average Price", "Previous Closing Price", "Unrealized P&L", "Unrealized P&L Pct."
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
    
    # Prepare records - map to the database schema
    records = []
    for _, row in df.iterrows():
        # Skip if Symbol is empty
        if pd.isna(row.get("Symbol")) or str(row.get("Symbol")).strip() == "":
            continue
        
        # Extract quantity (use Quantity Available if available, otherwise sum of quantities)
        quantity = 0.0
        if "Quantity Available" in row and pd.notna(row.get("Quantity Available")):
            quantity = safe_float(row["Quantity Available"]) or 0.0
        elif "Quantity" in row and pd.notna(row["Quantity"]):
            quantity = safe_float(row["Quantity"]) or 0.0
        
        # Extract Average Price
        avg_price = safe_float(row.get("Average Price")) if "Average Price" in row else None
        
        # Extract ISIN - handle both "ISIN" and "ISINSector" columns
        isin_value = None
        if "ISIN" in row and pd.notna(row.get("ISIN")):
            isin_value = str(row.get("ISIN", "")).strip()
        elif "ISINSector" in row and pd.notna(row.get("ISINSector")):
            # If ISINSector is one column, try to extract just the ISIN part
            isinsector = str(row.get("ISINSector", "")).strip()
            # ISIN is typically 12 characters, so try to extract it
            # This is a heuristic - adjust based on actual data format
            isin_value = isinsector[:12] if len(isinsector) >= 12 else isinsector
        
        record = {
            "Symbol": str(row.get("Symbol", "")).strip(),
            "ISIN": isin_value if isin_value else None,
            "Quantity": quantity,
            "Average Price": avg_price,
            "Unrealized P&L": safe_float(row.get("Unrealized P&L")) if "Unrealized P&L" in row else None,
            "Unrealized P&L Pct.": safe_float(row.get("Unrealized P&L Pct.")) if "Unrealized P&L Pct." in row else None
        }
        records.append(record)
    
    return records


def process(file_path: str) -> List[Dict]:
    """
    Process Zerodha stock holdings file.
    
    Args:
        file_path: Path to the Zerodha Excel file
        
    Returns:
        List of dictionaries with stock holding data
    """
    return process_stock_holdings_file(file_path)

