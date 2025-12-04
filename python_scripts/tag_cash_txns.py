import psycopg2
import os
import argparse
from datetime import datetime, date
from typing import List, Tuple

# Environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


def check_existing_tags(
    conn, atm_id: int, atm_amount: float, tolerance: float
) -> Tuple[bool, float]:
    """
    Check if transactions already tagged with this ATM ID sum within tolerance.
    Returns (already_sufficient: bool, current_sum: float)
    """
    query = f"""
        SELECT COALESCE(SUM(txn_amount), 0) as tagged_sum
        FROM transactions 
        WHERE tags LIKE '%#{atm_id}#%' 
          AND account = 'Cash' 
          AND txn_type = 'Debit';
    """
    with conn.cursor() as cur:
        cur.execute(query)
        result = cur.fetchone()
        tagged_sum = result[0] if result else 0.0

    shortfall = atm_amount - tagged_sum
    already_sufficient = shortfall <= tolerance

    return already_sufficient, tagged_sum


def fetch_atm_withdrawals(
    conn, from_date: str, to_date: str
) -> List[Tuple[int, date, float]]:
    query = f"""
        SELECT id, txn_date, txn_amount 
        FROM transactions 
        WHERE txn_date BETWEEN '{from_date}' AND '{to_date}' 
          AND category = 'ATM Withdrawal'
        ORDER BY txn_date, id;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return [(row[0], row[1], row[2]) for row in cur.fetchall()]


def fetch_cash_debits(
    conn, start_date: date, from_date: str, to_date: str
) -> List[Tuple[int, date, float]]:
    date_str = start_date.strftime("%Y-%m-%d")
    query = f"""
        SELECT id, txn_date, txn_amount 
        FROM transactions 
        WHERE txn_date >= '{date_str}' 
          AND txn_date BETWEEN '{from_date}' AND '{to_date}'
          AND account = 'Cash' 
          AND txn_type = 'Debit' 
          AND category != 'Others'
          AND (tags IS NULL OR tags = '' OR tags NOT LIKE '%#%%#')
        ORDER BY txn_date, id;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return [(row[0], row[1], row[2]) for row in cur.fetchall()]


def find_matching_transactions(
    atm_amount: float,
    cash_transactions: List[Tuple[int, date, float]],
    tolerance: float = 100.0,
) -> List[int]:
    """Pure greedy: largest first until within tolerance."""
    target = atm_amount
    sorted_cash = sorted(cash_transactions, key=lambda x: x[2], reverse=True)

    matching_ids = []
    current_sum = 0.0

    for tid, tdate, tamt in sorted_cash:
        if current_sum + tamt > target + tolerance:
            continue
        matching_ids.append(tid)
        current_sum += tamt
        if abs(target - current_sum) <= tolerance:
            break

    if current_sum <= target + tolerance:
        return matching_ids
    return []


def generate_update_queries(
    atm_id: int, matching_ids: List[int], atm_amount: float, matched_sum: float
) -> str:
    ids_str = ", ".join(map(str, matching_ids))
    shortfall = atm_amount - matched_sum
    return f"""-- ATM #{atm_id}# (₹{atm_amount:.0f}) → ₹{matched_sum:.0f} (shortfall: ₹{shortfall:.0f})
UPDATE transactions SET tags = COALESCE(tags, '') || '#{atm_id}#' 
WHERE id IN ({ids_str});"""


def parse_dates(date_str: str) -> str:
    """Validate and parse date string."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Date must be in YYYY-MM-DD format: {date_str}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Tag cash debits with ATM withdrawal IDs"
    )
    parser.add_argument(
        "--from-date",
        "-f",
        type=parse_dates,
        default="2020-11-25",
        help="Start date for ATM withdrawals (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--to-date",
        "-t",
        type=parse_dates,
        default="2021-08-14",
        help="End date for ATM withdrawals (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--output", "-o", default="atm_tagging_updates.sql", help="Output SQL file name"
    )
    parser.add_argument(
        "--tolerance",
        "-T",
        type=float,
        default=100.0,
        help="Matching tolerance in Rs (default: 100)",
    )

    args = parser.parse_args()

    if datetime.strptime(args.from_date, "%Y-%m-%d") > datetime.strptime(
        args.to_date, "%Y-%m-%d"
    ):
        raise ValueError("from-date must be before to-date")

    conn = get_db_connection()
    print("✅ Connected to database")
    print(f"📅 Date range: {args.from_date} to {args.to_date}")

    atm_withdrawals = fetch_atm_withdrawals(conn, args.from_date, args.to_date)
    print(f"📥 Found {len(atm_withdrawals)} ATM Withdrawals")

    if not atm_withdrawals:
        print("❌ No ATM withdrawals found in date range")
        conn.close()
        return

    update_queries = []
    successful_matches = 0
    skipped_already_tagged = 0
    used_cash_ids = set()

    for atm_id, atm_date, atm_amount in atm_withdrawals:
        print(f"\n🔍 ATM #{atm_id} ({atm_date}): ₹{atm_amount:.0f}")

        # NEW: Check existing tags first
        already_sufficient, tagged_sum = check_existing_tags(
            conn, atm_id, atm_amount, args.tolerance
        )
        if already_sufficient:
            print(
                f"   ⏭️  SKIPPED: Already tagged sum ₹{tagged_sum:.0f} within tolerance"
            )
            skipped_already_tagged += 1
            continue

        print(
            f"   📊 Existing tagged sum: ₹{tagged_sum:.0f} (needs ₹{atm_amount-tagged_sum:.0f} more)"
        )

        # Fetch untagged cash debits
        cash_debits = fetch_cash_debits(conn, atm_date, args.from_date, args.to_date)

        # Prevent tagging the same cash transaction under multiple ATMs
        if used_cash_ids:
            cash_debits = [t for t in cash_debits if t[0] not in used_cash_ids]

        print(
            f"   📈 {len(cash_debits)} untagged cash debits available (after excluding already used)"
        )

        matching_ids = find_matching_transactions(
            atm_amount - tagged_sum, cash_debits, args.tolerance
        )

        if matching_ids:
            # Mark these cash txns as used so they aren't reused for another ATM
            used_cash_ids.update(matching_ids)

            matched_sum = sum([t[2] for t in cash_debits if t[0] in matching_ids])
            total_sum = tagged_sum + matched_sum
            query = generate_update_queries(atm_id, matching_ids, atm_amount, total_sum)
            update_queries.append(query)
            successful_matches += 1
            print(
                f"   ✅ Matched {len(matching_ids)} NEW txns (total: ₹{total_sum:.0f})"
            )
        else:
            print(f"   ❌ No additional match found")

    # Save UPDATE queries
    with open(args.output, "w") as f:
        f.write(f"-- ATM Withdrawal Tagging Updates\n")
        f.write(f"-- Date Range: {args.from_date} to {args.to_date}\n")
        f.write(f"-- Tolerance: ±₹{args.tolerance}\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n\n")
        for query in update_queries:
            f.write(query + "\n")

    print(f"\n📊 SUMMARY:")
    print(f"   ✅ New matches: {successful_matches}")
    print(f"   ⏭️  Skipped (already sufficient): {skipped_already_tagged}")
    print(f"   📄 Total ATMs processed: {len(atm_withdrawals)}")
    print(f"💾 Generated {len(update_queries)} UPDATE queries → {args.output}")
    print("⚠️  REVIEW BEFORE EXECUTING!")

    conn.close()


if __name__ == "__main__":
    main()
