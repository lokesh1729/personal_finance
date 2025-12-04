import psycopg2
import os
import re
from typing import List, Tuple, Dict

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


def fetch_tagged_transactions(conn) -> List[Tuple[int, str]]:
    """Fetch transactions with multiple ATM tags using regex."""
    query = """
        SELECT id, tags
        FROM transactions
        WHERE tags ~ '.*#[0-9]+#.*#[0-9]+#';
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


def parse_tagged_transactions(tagged_: List[Tuple[int, str]]) -> Dict[int, List[int]]:
    """Parse into id -> list of tag IDs."""
    transactions = {}
    for txn_id, tags_str in tagged_:
        if not tags_str or tags_str.strip() == "":
            transactions[txn_id] = []
            continue

        # Extract #123# format tags using regex
        tag_ids = re.findall(r"#(\d+)#", str(tags_str))
        transactions[txn_id] = [int(tag_id) for tag_id in tag_ids]

    return transactions


def fetch_transaction_details(conn, txn_id: int) -> Dict:
    """Fetch full details for a single transaction."""
    query = """
        SELECT id, txn_date, account, txn_type, txn_amount, category, tags, notes, created_at, updated_at
        FROM transactions 
        WHERE id = %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (txn_id,))
        row = cur.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "txn_date": row[1],
            "account": row[2],
            "txn_type": row[3],
            "txn_amount": row[4],
            "category": row[5],
            "tags": row[6] or "",
            "notes": row[7] or "",
            "created_at": row[8],
            "updated_at": row[9],
        }


def print_transaction_details(conn, txn: Dict, related_txns: List[int]):
    """Pretty print transaction details."""
    print(f"\n{'='*80}")
    print(f"🆔 Transaction ID: {txn['id']}")
    print(f"📅 Date: {txn['txn_date']}")
    print(f"💰 Amount: ₹{txn['txn_amount']:.0f}")
    print(f"🏦 Account: {txn['account']}")
    print(f"🔄 Type: {txn['txn_type']}")
    print(f"📂 Category: {txn['category']}")
    print(f"🏷️  Tags: {txn['tags']}")
    print(f"📝 Notes: {txn['notes']}")
    print(f"⏰ Created: {txn['created_at']}")
    print(f"🔄 Updated: {txn['updated_at']}")

    if related_txns:
        print(f"\n🔗 Related Transactions: {', '.join(map(str, related_txns))}")
        # Show related transaction details
        print("\n📋 Related Transaction Details:")
        for rel_id in sorted(related_txns):
            rel_details = fetch_transaction_details(conn, rel_id)
            if rel_details:
                print(f"   🆔 #{rel_id}")
                print(
                    f"      📅 {rel_details['txn_date']} | 📂 {rel_details['category']}"
                )
                print(
                    f"      🔄 {rel_details['txn_type']} | 💰 ₹{rel_details['txn_amount']:.0f}"
                )
                print(
                    f"      🏷️  {rel_details['tags']}{'...' if len(rel_details['tags']) > 100 else ''}"
                )
                print(
                    f"      📝 {rel_details['notes']}{'...' if len(rel_details['notes']) > 50 else ''}"
                )
                print()
            else:
                print(f"   🆔 #{rel_id}: ❌ Not found")
    else:
        print("\nℹ️  No related transaction tags found")


def main():
    conn = get_db_connection()
    print("✅ Connected to database")

    # Fetch transactions with multiple ATM tags dynamically
    tagged_data = fetch_tagged_transactions(conn)
    print(f"📥 Found {len(tagged_data)} transactions with multiple ATM tags")

    if not tagged_data:
        print("❌ No transactions found with multiple ATM tags")
        conn.close()
        return

    # Parse into dict: txn_id -> list_of_atm_ids
    transactions = parse_tagged_transactions(tagged_data)

    print(f"\n📊 Processing {len(transactions)} tagged transactions")

    # Print each transaction one by one
    for txn_id, rel_ids in transactions.items():
        print(f"\n{'='*80}")
        print(f"🔍 PROCESSING TRANSACTION #{txn_id}")
        print(f"{'='*80}")

        # Fetch full transaction details
        txn_details = fetch_transaction_details(conn, txn_id)
        if not txn_details:
            print(f"❌ Transaction #{txn_id} not found!")
            continue

        # Print details with related transactions
        print_transaction_details(conn, txn_details, rel_ids)

    conn.close()
    print(f"\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
