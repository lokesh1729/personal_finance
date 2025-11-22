import argparse
import json
import os
import re
import time
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from common import utils

# Load environment variables from .env
load_dotenv()

def parse_netscape_cookies(filename):
    """Parse cookies from a Netscape HTTP Cookie File format."""
    cookies = []

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            # Skip comments and empty lines
            if line.startswith('#') or line.strip() == '':
                continue

            # Split the line by tabs
            try:
                fields = line.strip().split('\t')

                # Netscape format has these fields:
                # domain, flag, path, secure, expiration, name, value
                if len(fields) >= 7:
                    domain = fields[0]
                    path = fields[2]
                    secure = fields[3].lower() == 'true'
                    # Handle expiry as float or int (convert to int for timestamp)
                    expiry = None
                    if fields[4] != '0':
                        try:
                            expiry = int(float(fields[4]))
                        except (ValueError, TypeError):
                            expiry = None
                    name = fields[5]
                    value = fields[6]

                    cookie = {
                        'domain': domain,
                        'path': path,
                        'secure': secure,
                        'name': name,
                        'value': value
                    }

                    if expiry:
                        cookie['expiry'] = expiry

                    cookies.append(cookie)
            except Exception as e:
                print(f"Error parsing cookie line: {line.strip()}")
                print(f"Error details: {e}")

    except Exception as e:
        print(f"Error reading cookie file: {e}")

    return cookies


def setup_driver(headless=True):
    """Set up and configure the Chrome WebDriver."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")  # New headless implementation

    # Additional options to make the browser more stable
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    # Install and set up ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def inject_cookies(driver, cookies):
    """Inject cookies into the browser session."""
    # First, we need to navigate to the domain
    base_url = "https://www.amazon.in"
    driver.get(base_url)

    # Wait a bit for the page to load
    time.sleep(2)

    # Count successful and failed cookies
    success_count = 0
    failed_count = 0

    # Add each cookie to the browser
    for cookie in cookies:
        try:
            # Only process cookies for amazon.in domain
            if not (cookie['domain'].endswith('.amazon.in') or cookie['domain'] == 'amazon.in'):
                continue

            # Create a simplified cookie to add
            simplified_cookie = {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie.get('path', '/')
            }

            # Add secure flag if it exists
            if cookie.get('secure', False):
                simplified_cookie['secure'] = True

            # Add expiry if it exists
            if 'expiry' in cookie and cookie['expiry']:
                simplified_cookie['expiry'] = cookie['expiry']

            driver.add_cookie(simplified_cookie)
            success_count += 1

        except Exception as e:
            failed_count += 1
            print(f"Failed to add cookie {cookie.get('name')}: {e}")

    print(f"Cookies injected: {success_count} successful, {failed_count} failed")


def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    try:
        # Get database connection parameters from environment variables
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME')

        if not db_user or not db_password or not db_name:
            raise ValueError("Invalid database details passed.")

        # Connect to the database
        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name
        )

        print("Database connection established successfully")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def parse_amount(amount_text):
    """Parse the transaction amount, handling the rupee symbol and +/- sign."""
    try:
        # Split by rupee symbol (₹)
        parts = amount_text.split('₹')
        if len(parts) < 2:
            # Try with Unicode rupee symbol
            parts = amount_text.split('\u20B9')

        if len(parts) < 2:
            print(f"Could not parse amount: {amount_text}")
            return 0.0

        sign = 1
        if '+' in parts[0]:
            sign = 1  # Money received/added
        elif '-' in parts[0]:
            sign = -1  # Money spent/deducted

        # Extract and clean the amount
        amount_str = parts[1].strip().replace(',', '')
        amount = float(amount_str) * sign

        return amount
    except Exception as e:
        print(f"Error parsing amount '{amount_text}': {e}")
        return 0.0


def parse_date(date_str):
    """Convert date from '27 Apr 2025, 01:04 AM' to 'YYYY-MM-DD' format."""
    try:
        # Normalize and clean the date string
        if "credited on:" in date_str.lower():
            date_str = date_str.lower().split("credited on:")[1]
        dt = datetime.strptime(date_str.strip(), '%d %b %Y, %I:%M %p')
        return dt.strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None


def insert_transaction(conn, txn_data):
    """Insert a transaction into the database."""
    
    def parse_order_id_from_html(order_id_str):
        """Parse orderId from HTML link if present, otherwise return as is."""
        if not order_id_str:
            return None
        
        # Check if it's HTML (contains <a> tag)
        if '<a' in order_id_str and '</a>' in order_id_str:
            # Extract text content between <a> tags using regex
            match = re.search(r'<a[^>]*>([^<]+)</a>', order_id_str)
            if match:
                return match.group(1).strip()
        
        # If not HTML, return as is
        return order_id_str.strip() if order_id_str else None
    
    try:
        # Create a cursor
        cursor = conn.cursor()

        # Parse date from the format "27 Apr 2025, 01:04 AM" to "YYYY-MM-DD"
        txn_date = parse_date(txn_data['date_time'])
        if not txn_date:
            return False

        # Parse amount (handle rupee symbol and +/- sign) + for added, - for debited
        txn_amount = parse_amount(txn_data['amount'])

        # Determine transaction type based on amount. Reverse here
        txn_type = "Credit" if txn_amount > 0 else "Debit"

        # Prepare notes
        category, tags, notes = utils.auto_detect_category(txn_data['transaction_details'])
        notes = f"subwallet: {txn_data['subwallet']}\n\n{txn_data['transaction_details']}\n\n" + notes
        
        # Parse and append orderId to notes if available
        order_id = txn_data.get('orderId')
        if order_id:
            parsed_order_id = parse_order_id_from_html(order_id)
            if parsed_order_id:
                notes += f"\norderId: {parsed_order_id}"
        if txn_data.get('usecase'):
            notes += f"\nusecase: {txn_data['usecase']}"
        
        # If category is cashback, txn_amount should be positive
        if category and category.lower() == 'cashback':
            txn_amount = abs(txn_amount)
        
        # If notes contain refund, txn_amount should be negative
        if 'refund' in notes.lower():
            txn_amount = -abs(txn_amount)

        # SQL for inserting a transaction
        insert_sql = """
        INSERT INTO public.transactions
        (txn_date, account, txn_type, txn_amount, category, tags, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (txn_date, account, txn_type, txn_amount, category, tags, notes) DO NOTHING
        RETURNING id;
        """

        # Execute the query
        cursor.execute(insert_sql, (
            txn_date,
            "Amazon Pay",  # Hardcoded account
            txn_type,
            txn_amount * -1 if txn_type == 'Debit' else txn_amount,  # Store absolute value
            category,  # Hardcoded category
            tags,  # Empty tags
            notes
        ))

        # Check if a row was inserted
        result = cursor.fetchone()

        # Commit the transaction
        conn.commit()

        # Close the cursor
        cursor.close()

        if result:
            print(f"Transaction inserted with ID: {result[0]}")
            return True
        else:
            print("Transaction already exists (skipped)")
            return False

    except Exception as e:
        print(f"Error inserting transaction: {e}")
        conn.rollback()
        return False


def process_transactions(driver, conn):
    """Find and process Amazon Pay transactions."""
    transactions_processed = 0
    all_transaction_elements = []

    try:
        # Wait for the transactions container to load
        try:
            transactions_container = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "transactions-desktop"))
            )
        except Exception:
            # If transactions container not found, check for "Switch accounts" page
            print("Transactions container not found, checking for 'Switch accounts' page...")
            driver.save_screenshot("amazon_pay_txns_not_found.png")
            switch_accounts_h1 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[text()='Switch accounts']"))
            )
            print("Found 'Switch accounts' page, clicking on customer name...")
            customer_name_div = driver.find_element(By.CSS_SELECTOR, "div[data-test-id='customerName']")
            customer_name_div.click()
            print("Clicked on customer name. Waiting 5 seconds...")
            time.sleep(5)
            # Wait again for transactions-desktop
            driver.save_screenshot("amazon_pay_after_clicking_on_switch_accounts.png")
            transactions_container = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "transactions-desktop"))
            )
            print("Transaction container found after switching accounts.")

        print("Transaction container found. Processing transactions...")

        # Initial scroll position
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Find all transaction elements within the container
            transaction_elements = driver.find_elements(By.ID, "itemDetailExpandedView")

            # Keep track of new transactions
            new_elements = [elem for elem in transaction_elements if elem not in all_transaction_elements]
            all_transaction_elements.extend(new_elements)

            print(f"Found {len(new_elements)} new transactions, processing...")

            # Process each new transaction
            for elem in new_elements:
                try:
                    # Extract transaction details using the provided XPaths
                    transaction_details = elem.find_element(By.XPATH,
                                                            ".//span[@class='a-size-medium a-color-base']").text.strip()
                    subwallet = elem.find_element(By.XPATH,
                                                  ".//div[@class='a-section payment-details-desktop']//span[@class='a-size-base a-color-tertiary']").text.strip()
                    date_time = elem.find_element(By.XPATH,
                                                  "(.//div[@class='a-column a-span9 a-text-left']/*)[3][self::span]").text.strip()
                    try:
                        amount = elem.find_element(By.XPATH,
                                                   ".//span[@class='a-size-medium a-color-attainable']").text.strip()
                    except NoSuchElementException:
                        amount = elem.find_element(By.XPATH,
                                                   ".//span[@class='a-size-medium a-color-price']").text.strip()

                    # Extract JSON from data-itemdetailexpandedview attribute
                    orderId = None
                    usecase = None
                    marketplaceId = None
                    try:
                        json_data_str = elem.get_attribute("data-itemdetailexpandedview")
                        if json_data_str:
                            json_data = json.loads(json_data_str)
                            orderId = json_data.get("orderId")
                            usecase = json_data.get("useCase")
                            marketplaceId = json_data.get("marketplaceId")
                    except (json.JSONDecodeError, AttributeError) as e:
                        print(f"Error extracting JSON data: {e}")

                    # Create transaction data dictionary
                    txn_data = {
                        "transaction_details": transaction_details,
                        "subwallet": subwallet,
                        "date_time": date_time,
                        "amount": amount,
                        "orderId": orderId,
                        "usecase": usecase,
                        "marketplaceId": marketplaceId
                    }

                    print(f"Fetched Transaction: {transaction_details} | {amount} | {date_time}")

                    # Insert into database
                    if conn:
                        success = insert_transaction(conn, txn_data)
                        if success:
                            transactions_processed += 1

                except NoSuchElementException as e:
                    print(f"Couldn't extract all details from a transaction: {e}")
                except Exception as e:
                    print(f"Error processing transaction: {e}")

            # Scroll down to load more transactions
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # We've reached the end of the page, no more transactions to load
                break
            last_height = new_height

            # Safety check to prevent infinite loops
            if len(all_transaction_elements) > 1000:  # Limit to 1000 transactions
                print("Reached transaction limit (1000). Stopping.")
                break

        print(f"Total transactions found: {len(all_transaction_elements)}")
        print(f"Total transactions processed: {transactions_processed}")

        return transactions_processed

    except Exception as e:
        print(f"Error processing transactions: {e}")
        driver.save_screenshot("amazon_pay_error_process_transactions.png")
        return 0


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Open Amazon Payment Statement page with injected cookies')
    parser.add_argument('--cookie-file', type=str, required=True, help='Path to Netscape HTTP Cookie File')
    parser.add_argument('--no-headless', action='store_true', help='Run Chrome in non-headless mode')
    parser.add_argument('--wait-time', type=int, default=10, help='Time to wait on the page in seconds')
    parser.add_argument('--skip-db', action='store_true', help='Skip database operations')

    args = parser.parse_args()

    # Load cookies from the file
    cookies = parse_netscape_cookies(args.cookie_file)
    if not cookies:
        print("Failed to load cookies or no valid cookies found. Exiting.")
        return
    else:
        print(f"Loaded {len(cookies)} cookies from file")

    # Set up the driver
    driver = setup_driver(headless=not args.no_headless)

    # Connect to database unless skipped
    conn = None
    if not args.skip_db:
        conn = get_db_connection()

    try:
        # Inject cookies
        inject_cookies(driver, cookies)

        # Navigate to the payment statement page
        target_url = "https://www.amazon.in/pay/history?tab=ALL&filter={%22searchWords%22:[],%22paymentInstruments%22:[{%22paymentInstrumentType%22:%22GC%22},{%22paymentInstrumentType%22:%22SVA%22},{%22paymentInstrumentType%22:%22APV%22}]}"
        print(f"Navigating to {target_url}")
        driver.get(target_url)

        # Wait to ensure the page loads properly
        print(f"Waiting {args.wait_time} seconds for page to load...")
        time.sleep(args.wait_time)

        # Print current URL (to check if redirected)
        print(f"Current URL: {driver.current_url}")

        # Process transactions
        transactions_processed = process_transactions(driver, conn)
        print(f"Successfully processed {transactions_processed} transactions")

        # Wait for user input if not in headless mode
        if not args.no_headless:
            input("Press Enter to close the browser...")

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.save_screenshot("amazon_pay_error.png")

    finally:
        # Close database connection if it exists
        if conn:
            conn.close()
            print("Database connection closed")

        # Close the driver
        driver.quit()
        print("Browser closed")


if __name__ == "__main__":
    main()