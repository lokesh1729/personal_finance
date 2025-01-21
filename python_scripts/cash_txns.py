import csv
import sys

from common import convert_date_format


# Read input from STDIN
def read_input():
    print("Enter data as comma-separated values (Date,Amount,Category,Tags,Notes):")
    data = []
    for line in sys.stdin:
        # Strip whitespace and split by comma
        if line.strip():
            data.append(line.strip().split(","))
    return data

# Map input to dictionary
def map_to_dict(data):
    keys = ["Date", "Amount", "Category", "Tags", "Notes"]
    mapped_data = []
    for row in data:
        if len(row) == len(keys):
            mapped_data.append(dict(zip(keys, row)))
        else:
            print(f"Error: Row {row} does not match the expected format and will be skipped.")
    return mapped_data

# Transform data and write to CSV
def write_to_csv(mapped_data, output_file="output.csv"):
    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["txn_date", "account", "txn_type", "txn_amount", "category", "tags", "notes"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write rows
        for item in mapped_data:
            try:
                txn_date = convert_date_format(item["Date"], "%b %d %Y", "%Y-%m-%d")
            except ValueError:
                txn_date = convert_date_format(item["Date"], "%d %b %Y", "%Y-%m-%d")
            amount = float(item["Amount"].lower().split("rs")[1].strip()) if "rs" in item["Amount"].lower() else float(item["Amount"])
            category = item["Category"]
            tags = item["Tags"]
            notes = item["Notes"]

            writer.writerow({
                "txn_date": txn_date,
                "account": "Cash",
                "txn_type": "Debit" if amount > 0 else "Credit",
                "txn_amount": abs(amount),
                "category": category,
                "tags": tags,
                "notes": notes
            })

# Main function
def main():
    data = read_input()
    mapped_data = map_to_dict(data)
    write_to_csv(mapped_data)
    print("Data has been written to 'output.csv'.")

if __name__ == "__main__":
    main()
