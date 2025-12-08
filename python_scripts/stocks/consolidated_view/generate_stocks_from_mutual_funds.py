#!/usr/bin/env python3
"""
Generate consolidated view of stocks from stock holdings and mutual fund holdings.

This script processes stock holdings statements and mutual fund holdings statements,
extracts stock information from mutual funds via Groww API, and stores everything
in PostgreSQL database tables.
"""
import argparse
import os
import sys
import logging
from dotenv import load_dotenv
from typing import List, Dict

# Get logger for this module
logger = logging.getLogger(__name__)

# Add python_scripts to path for imports
# script_dir = .../python_scripts/stocks/consolidated_view
# We need to add .../python_scripts to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
python_scripts_dir = os.path.dirname(os.path.dirname(script_dir))
if python_scripts_dir not in sys.path:
    sys.path.insert(0, python_scripts_dir)

from stocks.consolidated_view.database_utils import (
    get_db_connection,
    create_stocks_portfolio_table,
    create_groww_mutual_funds_portfolio_table,
    create_mutual_fund_stock_details_table,
    insert_stocks_portfolio_data,
    insert_groww_mutual_funds_portfolio_data,
    insert_mutual_fund_stock_details_data
)
from stocks.consolidated_view.file_utils import (
    detect_file_type,
    is_zerodha_file,
    process_mutual_fund_holdings_file
)
from stocks.consolidated_view.groww_api import get_mf_stock_holdings
from stocks.consolidated_view import zerodha_handler


def get_vendor_handler(vendor: str):
    """
    Factory method to get the appropriate handler for a vendor.
    
    Args:
        vendor: Vendor name (e.g., "zerodha")
        
    Returns:
        Handler module with process method
    """
    if vendor.lower() == "zerodha":
        return zerodha_handler
    else:
        raise ValueError(f"Unsupported vendor: {vendor}")


def process_stock_holdings(file_path: str, conn) -> List[Dict]:
    """
    Process stock holdings file and insert into database.
    
    Args:
        file_path: Path to stock holdings file
        conn: Database connection
        
    Returns:
        List of dictionaries with stock holding data
    """
    file_type = detect_file_type(file_path)
    
    # Check if it's a Zerodha file (Excel with specific sheets)
    if file_type == 'excel' and is_zerodha_file(file_path):
        vendor = "zerodha"
        handler = get_vendor_handler(vendor)
        records = handler.process(file_path)
    else:
        # For non-Zerodha files, use zerodha handler's process_stock_holdings_file
        # (it's generic enough to handle other formats too)
        records = zerodha_handler.process_stock_holdings_file(file_path)
    
    # Skip table rotation if no records found
    if not records:
        logger.warning("No stock holdings found in file, skipping table rotation")
        return records
    
    # Create table and insert data (transactional - commit handled by caller)
    create_stocks_portfolio_table(conn)
    insert_stocks_portfolio_data(conn, records)
    logger.info(f"Successfully processed {len(records)} stock holdings")
    
    return records


def process_mutual_fund_holdings(file_path: str, conn) -> List[Dict]:
    """
    Process mutual fund holdings file and insert into database.
    
    Args:
        file_path: Path to mutual fund holdings file
        conn: Database connection
        
    Returns:
        List of dictionaries with mutual fund holding data
    """
    records = process_mutual_fund_holdings_file(file_path)
    
    # Skip table rotation if no records found
    if not records:
        logger.warning("No mutual fund holdings found in file, skipping table rotation")
        return records
    
    # Create table and insert data (transactional - commit handled by caller)
    create_groww_mutual_funds_portfolio_table(conn)
    insert_groww_mutual_funds_portfolio_data(conn, records)
    logger.info(f"Successfully processed {len(records)} mutual fund holdings")
    
    return records


def process_mutual_fund_stocks(mf_records: List[Dict], conn) -> List[Dict]:
    """
    Process mutual funds to extract stock holdings via Groww API.
    
    Args:
        mf_records: List of mutual fund records from the holdings file
        conn: Database connection
        
    Returns:
        List of dictionaries with mutual fund stock details
    """
    all_stock_details = []
    
    for mf_record in mf_records:
        mf_name = mf_record.get("Scheme Name", "")
        if not mf_name:
            continue
        
        logger.info(f"Processing MF: {mf_name}")
        
        # Get stock holdings from Groww API
        holdings = get_mf_stock_holdings(mf_name)
        
        if not holdings:
            logger.warning(f"No holdings found for {mf_name}")
            continue
        
        # Get invested value for calculations
        invested_value = mf_record.get("Invested Value")
        if invested_value is None:
            invested_value = 0.0
        
        # Process each holding
        for holding in holdings:
            # Extract data from holding
            company_name = holding.get("company_name", "")
            sector_name = holding.get("sector_name", "")
            corpus_per = holding.get("corpus_per")
            
            if not company_name:
                continue
            
            # Calculate stock invested amount
            percentage = float(corpus_per) if corpus_per is not None else 0.0
            stock_invested_amount = invested_value * (percentage / 100.0)
            
            stock_detail = {
                "mf_name": mf_name,
                "mf_amc": mf_record.get("AMC"),
                "mf_category": mf_record.get("Category"),
                "mf_sub_category": mf_record.get("Sub-category"),
                "mf_units": str(mf_record.get("Units", "")) if mf_record.get("Units") is not None else None,
                "folio_no": mf_record.get("Folio No."),
                "stock_name": company_name,
                "sector_name": sector_name,
                "percentage_holding_in_company": percentage,
                "mf_invested_amount": invested_value,
                "stock_invested_amount": stock_invested_amount
            }
            all_stock_details.append(stock_detail)
        
        logger.info(f"Found {len(holdings)} stock holdings for {mf_name}")
    
    # Skip table rotation if no records found
    if not all_stock_details:
        logger.warning("No mutual fund stock details found, skipping table rotation")
        return all_stock_details
    
    # Create table and insert data (transactional - commit handled by caller)
    create_mutual_fund_stock_details_table(conn)
    insert_mutual_fund_stock_details_data(conn, all_stock_details)
    logger.info(f"Successfully processed {len(all_stock_details)} mutual fund stock details")
    
    return all_stock_details


def main():
    """Main function to process stock and mutual fund holdings."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Generate consolidated view of stocks from holdings statements"
    )
    parser.add_argument(
        "--mutual-fund-holdings-statement",
        required=True,
        help="Path to mutual fund holdings statement file (CSV or Excel)"
    )
    parser.add_argument(
        "--stock-holdings-statement",
        required=True,
        help="Path to stock holdings statement file (CSV or Excel)"
    )
    
    args = parser.parse_args()
    
    # Validate files exist
    if not os.path.exists(args.mutual_fund_holdings_statement):
        raise FileNotFoundError(f"Mutual fund holdings file not found: {args.mutual_fund_holdings_statement}")
    
    if not os.path.exists(args.stock_holdings_statement):
        raise FileNotFoundError(f"Stock holdings file not found: {args.stock_holdings_statement}")
    
    # Get database connection
    conn = get_db_connection()
    
    try:
        # Process stock holdings
        logger.info("=" * 60)
        logger.info("Processing Stock Holdings...")
        logger.info("=" * 60)
        stock_records = process_stock_holdings(args.stock_holdings_statement, conn)
        
        # Process mutual fund holdings
        logger.info("=" * 60)
        logger.info("Processing Mutual Fund Holdings...")
        logger.info("=" * 60)
        mf_records = process_mutual_fund_holdings(args.mutual_fund_holdings_statement, conn)
        
        # Process mutual fund stocks via API
        logger.info("=" * 60)
        logger.info("Processing Mutual Fund Stock Holdings via Groww API...")
        logger.info("=" * 60)
        mf_stock_details = process_mutual_fund_stocks(mf_records, conn)
        
        # Commit all transactions
        conn.commit()
        
        logger.info("=" * 60)
        logger.info("SUCCESS: All data processed and inserted into database")
        logger.info("=" * 60)
        logger.info(f"Stock holdings: {len(stock_records)} records")
        logger.info(f"Mutual fund holdings: {len(mf_records)} records")
        logger.info(f"Mutual fund stock details: {len(mf_stock_details)} records")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"ERROR: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
