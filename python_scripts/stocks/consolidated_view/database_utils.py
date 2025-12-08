"""
Database utilities for table creation, archival, and data insertion.
"""
import os
import re
import psycopg2
import random
import string
import logging
from datetime import datetime
from typing import List, Dict
from psycopg2.extras import execute_batch

# Get logger for this module
logger = logging.getLogger(__name__)


def generate_random_suffix(length: int = 6) -> str:
    """Generate a random alphanumeric suffix."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def validate_identifier(name: str) -> str:
    """
    Validate that a string is a safe SQL identifier (table name, trigger name, etc.).
    Only allows alphanumeric characters and underscores.
    
    Args:
        name: The identifier to validate
        
    Returns:
        The validated identifier
        
    Raises:
        ValueError: If the identifier contains invalid characters
    """
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"Invalid SQL identifier: '{name}'. Only alphanumeric characters and underscores are allowed.")
    return name


def get_db_connection():
    """Establish and return a PostgreSQL DB connection using environment variables."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )


def archive_table_if_exists(conn, table_name: str) -> str:
    """
    Archive an existing table by renaming it with timestamp suffix.
    If the table exists but is empty, skip rotation and reuse the table.
    
    Returns:
        - "archived": table was archived (need to create new table)
        - "empty": table exists but is empty (reuse existing table, no need to create)
        - "not_exists": table doesn't exist (need to create new table)
    
    Note: This does NOT commit - caller must handle transaction.
    """
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """, (table_name,))
    
    table_exists = cursor.fetchone()[0]
    
    if not table_exists:
        return "not_exists"
    
    # Check if table is empty
    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
    row_count = cursor.fetchone()[0]
    
    if row_count == 0:
        logger.info(f"Table '{table_name}' exists but is empty, reusing without rotation")
        return "empty"
    
    # Table exists and has data - archive it
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M")
    archive_table_name = f"{table_name}_archive_{timestamp}"
    
    # Rename the table
    cursor.execute(f'ALTER TABLE "{table_name}" RENAME TO "{archive_table_name}";')
    logger.info(f"Archived table '{table_name}' to '{archive_table_name}'")
    return "archived"


def ensure_trigger_function_exists(conn):
    """
    Ensure the trigger_set_timestamp function exists in the database.
    Creates it if it doesn't exist.
    """
    cursor = conn.cursor()
    
    try:
        # Check if the function exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_proc 
                WHERE proname = 'trigger_set_timestamp'
            );
        """)
        
        function_exists = cursor.fetchone()[0]
        
        if not function_exists:
            # Create the function
            cursor.execute("""
                CREATE OR REPLACE FUNCTION public.trigger_set_timestamp()
                RETURNS trigger
                LANGUAGE plpgsql
                AS $function$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $function$;
            """)
            logger.info("Created trigger function 'trigger_set_timestamp'")
    finally:
        cursor.close()


def create_updated_at_trigger(conn, table_name: str):
    """
    Create a trigger on the specified table to automatically update the updated_at column.
    Only creates the trigger if it doesn't already exist.
    """
    # Validate table_name to prevent SQL injection
    validate_identifier(table_name)
    
    cursor = conn.cursor()
    
    try:
        # Ensure the trigger function exists
        ensure_trigger_function_exists(conn)
        
        # PostgreSQL folds unquoted identifiers to lowercase, so we lowercase the trigger name
        # to ensure the existence check matches what's stored in pg_trigger.tgname
        trigger_name = f"set_timestamp_{table_name}".lower()
        
        # Check if trigger already exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_trigger
                WHERE tgname = %s
            );
        """, (trigger_name,))
        
        trigger_exists = cursor.fetchone()[0]
        
        if trigger_exists:
            logger.info(f"Trigger '{trigger_name}' already exists on table '{table_name}', skipping creation")
            return
        
        # Create the trigger
        cursor.execute(f"""
            CREATE TRIGGER {trigger_name}
            BEFORE UPDATE ON "{table_name}"
            FOR EACH ROW EXECUTE FUNCTION trigger_set_timestamp();
        """)
        logger.info(f"Created trigger '{trigger_name}' on table '{table_name}'")
    finally:
        cursor.close()


def create_stocks_portfolio_table(conn):
    """
    Create stocks_portfolio table with the specified schema.
    Archives existing table if it has data. Reuses empty table if exists.
    Note: This does NOT commit - caller must handle transaction.
    """
    cursor = conn.cursor()
    
    # Archive existing table if it exists and has data
    archive_result = archive_table_if_exists(conn, "stocks_portfolio")
    
    # If table exists but is empty, reuse it
    if archive_result == "empty":
        return
    
    # Create the table with random suffix for unique constraint
    random_suffix = generate_random_suffix()
    create_table_query = f"""
    CREATE TABLE public.stocks_portfolio (
        id SERIAL PRIMARY KEY,
        "Symbol" VARCHAR(50) NULL,
        "ISIN" VARCHAR(50) NULL,
        "Quantity" FLOAT4 NULL,
        "Average Price" FLOAT4 NULL,
        "Unrealized P&L" FLOAT4 NULL,
        "Unrealized P&L Pct." FLOAT4 NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        CONSTRAINT stocks_portfolio_unique_{random_suffix} UNIQUE ("Symbol")
    );
    """
    
    cursor.execute(create_table_query)
    logger.info("Created table 'stocks_portfolio'")
    
    # Create trigger for updated_at
    create_updated_at_trigger(conn, "stocks_portfolio")


def create_groww_mutual_funds_portfolio_table(conn):
    """
    Create groww_mutual_funds_portfolio table with the specified schema.
    Archives existing table if it has data. Reuses empty table if exists.
    Note: This does NOT commit - caller must handle transaction.
    """
    cursor = conn.cursor()
    
    # Archive existing table if it exists and has data
    archive_result = archive_table_if_exists(conn, "groww_mutual_funds_portfolio")
    
    # If table exists but is empty, reuse it
    if archive_result == "empty":
        return
    
    # Create the table with random suffix for unique constraint
    random_suffix = generate_random_suffix()
    create_table_query = f"""
    CREATE TABLE public.groww_mutual_funds_portfolio (
        id SERIAL PRIMARY KEY,
        "Scheme Name" VARCHAR(512) NULL,
        "AMC" VARCHAR(256) NULL,
        "Category" VARCHAR(128) NULL,
        "Sub-category" VARCHAR(128) NULL,
        "Folio No." VARCHAR(128) NULL,
        "Source" VARCHAR(128) NULL,
        "Units" FLOAT4 NULL,
        "Invested Value" FLOAT4 NULL,
        "Current Value" FLOAT4 NULL,
        "Returns" FLOAT4 NULL,
        "XIRR" FLOAT4 NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        CONSTRAINT groww_mutual_funds_portfolio_unique_constraint_{random_suffix} UNIQUE ("Scheme Name", "Folio No.")
    );
    """
    
    cursor.execute(create_table_query)
    logger.info("Created table 'groww_mutual_funds_portfolio'")
    
    # Create trigger for updated_at
    create_updated_at_trigger(conn, "groww_mutual_funds_portfolio")


def create_mutual_fund_stock_details_table(conn):
    """
    Create mutual_fund_stock_details table with the specified schema.
    Archives existing table if it has data. Reuses empty table if exists.
    Note: This does NOT commit - caller must handle transaction.
    """
    cursor = conn.cursor()
    
    # Archive existing table if it exists and has data
    archive_result = archive_table_if_exists(conn, "mutual_fund_stock_details")
    
    # If table exists but is empty, reuse it
    if archive_result == "empty":
        return
    
    # Create the table
    create_table_query = """
    CREATE TABLE public.mutual_fund_stock_details (
        id SERIAL PRIMARY KEY,
        mf_name VARCHAR(512) NULL,
        mf_amc VARCHAR(128) NULL,
        mf_category VARCHAR(128) NULL,
        mf_sub_category VARCHAR(128) NULL,
        mf_units VARCHAR(128) NULL,
        folio_no VARCHAR(100) NULL,
        stock_name VARCHAR(512) NULL,
        sector_name VARCHAR(128) NULL,
        percentage_holding_in_company FLOAT4 NULL,
        mf_invested_amount FLOAT4 NULL,
        stock_invested_amount FLOAT4 NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    cursor.execute(create_table_query)
    logger.info("Created table 'mutual_fund_stock_details'")
    
    # Create trigger for updated_at
    create_updated_at_trigger(conn, "mutual_fund_stock_details")


def insert_stocks_portfolio_data(conn, records: List[Dict]):
    """
    Insert data into stocks_portfolio table.
    Note: This does NOT commit - caller must handle transaction.
    """
    if not records:
        logger.warning("No records to insert into stocks_portfolio")
        return
    
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO stocks_portfolio (
        "Symbol", "ISIN", "Quantity", "Average Price",
        "Unrealized P&L", "Unrealized P&L Pct."
    ) VALUES (
        %(Symbol)s, %(ISIN)s, %(Quantity)s, %(Average Price)s,
        %(Unrealized P&L)s, %(Unrealized P&L Pct.)s
    )
    ON CONFLICT ("Symbol") DO UPDATE SET
        "ISIN" = EXCLUDED."ISIN",
        "Quantity" = EXCLUDED."Quantity",
        "Average Price" = EXCLUDED."Average Price",
        "Unrealized P&L" = EXCLUDED."Unrealized P&L",
        "Unrealized P&L Pct." = EXCLUDED."Unrealized P&L Pct.",
        updated_at = NOW();
    """
    
    execute_batch(cursor, insert_query, records)
    logger.info(f"Inserted {len(records)} records into stocks_portfolio")


def insert_groww_mutual_funds_portfolio_data(conn, records: List[Dict]):
    """
    Insert data into groww_mutual_funds_portfolio table.
    Note: This does NOT commit - caller must handle transaction.
    """
    if not records:
        logger.warning("No records to insert into groww_mutual_funds_portfolio")
        return
    
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO groww_mutual_funds_portfolio (
        "Scheme Name", "AMC", "Category", "Sub-category", "Folio No.",
        "Source", "Units", "Invested Value", "Current Value", "Returns", "XIRR"
    ) VALUES (
        %(Scheme Name)s, %(AMC)s, %(Category)s, %(Sub-category)s, %(Folio No.)s,
        %(Source)s, %(Units)s, %(Invested Value)s, %(Current Value)s, %(Returns)s, %(XIRR)s
    )
    ON CONFLICT ("Scheme Name", "Folio No.") DO UPDATE SET
        "AMC" = EXCLUDED."AMC",
        "Category" = EXCLUDED."Category",
        "Sub-category" = EXCLUDED."Sub-category",
        "Source" = EXCLUDED."Source",
        "Units" = EXCLUDED."Units",
        "Invested Value" = EXCLUDED."Invested Value",
        "Current Value" = EXCLUDED."Current Value",
        "Returns" = EXCLUDED."Returns",
        "XIRR" = EXCLUDED."XIRR",
        updated_at = NOW();
    """
    
    execute_batch(cursor, insert_query, records)
    logger.info(f"Inserted {len(records)} records into groww_mutual_funds_portfolio")


def insert_mutual_fund_stock_details_data(conn, records: List[Dict]):
    """
    Insert data into mutual_fund_stock_details table.
    Note: This does NOT commit - caller must handle transaction.
    """
    if not records:
        logger.warning("No records to insert into mutual_fund_stock_details")
        return
    
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO mutual_fund_stock_details (
        mf_name, mf_amc, mf_category, mf_sub_category, mf_units, folio_no,
        stock_name, sector_name, percentage_holding_in_company,
        mf_invested_amount, stock_invested_amount
    ) VALUES (
        %(mf_name)s, %(mf_amc)s, %(mf_category)s, %(mf_sub_category)s, %(mf_units)s, %(folio_no)s,
        %(stock_name)s, %(sector_name)s, %(percentage_holding_in_company)s,
        %(mf_invested_amount)s, %(stock_invested_amount)s
    );
    """
    
    execute_batch(cursor, insert_query, records)
    logger.info(f"Inserted {len(records)} records into mutual_fund_stock_details")

