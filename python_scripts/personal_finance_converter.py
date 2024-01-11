import argparse
import csv
import datetime
import os


from enum import Enum


class Account(Enum):
	HDFC_BANK_ACCOUNT = 1
	KOTAK_BANK_ACCOUNT = 2
	HDFC_CREDIT_CARD = 3
	SBI_CREDIT_CARD = 4
	ICICI_CREDIT_CARD = 5
	KOTAK_CREDIT_CARD = 6
	EQUITAS_BANK_ACCOUNT = 7


OUTPUT_COLUMNS = ["Date", "Account", "Type", "Amount", "Category", "Tags", "Notes"]

CATEGORY_MAPPING = {
	"Salary": "Salary",
	"salary": "Salary",
	"sal": "Salary",
	"Cashback": "Cashback",
	"cb": "Cashback",
	"cashback": "Cashback",
	"Refund": "Refund",
	"ref": "Refund",
	"Dividend": "Dividend",
	"div": "Dividend",
	"dividend": "Dividend",
	"Interest": "Interest",
	"interest": "Interest",
	"int": "Interest",
	"Loan": "Loan",
	"loan": "Loan",
	"Investments": "Investments",
	"inv": "Investments",
	"investments": "Investments",
	"Rent": "Rent",
	"rent": "Rent",
	"Bills": "Bills",
	"bills": "Bills",
	"bil": "Bills",
	"Groceries": "Groceries",
	"gro": "Groceries",
	"groceries": "Groceries",
	"Fruits & Vegetables": "Fruits & Vegetables",
	"fv": "Fruits & Vegetables",
	"fruits & vegetables": "Fruits & Vegetables",
	"Food & Dining": "Food & Dining",
	"fd": "Food & Dining",
	"Ramya": "Ramya",
	"ramya": "Ramya",
	"Household": "Household",
	"household": "Household",
	"hh": "Household",
	"Personal Care": "Personal Care",
	"pc": "Personal Care",
	"personal care": "Personal Care",
	"Egg & Meat": "Egg & Meat",
	"em": "Egg & Meat",
	"egg & meat": "Egg & Meat",
	"Shopping": "Shopping",
	"shopping": "Shopping",
	"shop": "Shopping",
	"Travel": "Travel",
	"travel": "Travel",
	"tv": "Travel",
	"Health": "Health",
	"health": "Health",
	"Entertainment": "Entertainment",
	"entertainment": "Entertainment",
	"et": "Entertainment",
	"Donation": "Donation",
	"donation": "Donation",
	"dt": "Donation",
	"Gifts": "Gifts",
	"gifts": "Gifts",
	"Productivity": "Productivity",
	"productivity": "Productivity",
	"pv": "Productivity",
	"Others": "Others",
	"others": "Others",
	"ot": "Others",
	"Misc": "Misc",
	"misc": "Misc",
	"Maintenance": "Maintenance",
	"maintenance": "Maintenance",
	"mt": "Maintenance",
	"Life Style": "Life Style",
	"life style": "Life Style",
	"lifestyle": "Life Style",
	"ls": "Life Style"
}


def hdfc_bank_account_adapter(file_name):
	columns = ["Date", "Narration", "Chq./Ref.No.", "Value Dt", "Withdrawal Amt.", "Deposit Amt.", "Closing Balance", "Category", "Tags", "Notes"]
	result = []
	with open(file_name, "r") as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			result.append({
				"Date": datetime.datetime.strptime(row["Date"], "%B %-d, %Y").strftime("%A, %B %-d, %Y"),
				"Account": "HDFC Bank Account",
				"Type": "Debit" if row["Withdrawal Amt."] != "" else "Credit",
				"Amount": row["Withdrawal Amt."] if row["Withdrawal Amt."] != "" else row["Deposit Amt."],
				"Category": CATEGORY_MAPPING[row["Category"]],
				"Tags": row["Tags"],
				"Notes": row["Notes"],
			})
	with open(os.path.join(os.path.dirname(file_name), "output.csv"), "w") as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=OUTPUT_COLUMNS)
		write.writeheader()
		for each_row in result:
			writer.writerow(each_row)


def kotak_bank_account_adapter(file_name):
	pass


def bank_account_adapter(account_type):
	if account_type == Account.HDFC_BANK_ACCOUNT.name:
		return hdfc_bank_account_adapter
	elif account_type == Account.KOTAK_BANK_ACCOUNT.name:
		return kotak_bank_account_adapter


def main():
	parser = argparse.ArgumentParser(prog="A program to convert bank statements to the preferred format", description="Takes the type of bank statement and outputs the converted format")
	parser.add_argument("-t", "--type", help="Type of the bank statement.", dest="type", choices=list(map(lambda k: k.name, Account)))
	parser.add_argument("-p", "--path", help="File path of the bank statement.", dest="path")
	args = parser.parse_args()
	bank_account_adapter(args.type)(args.path)


if __name__ == '__main__':
	main()
