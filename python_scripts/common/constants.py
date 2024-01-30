from enum import Enum


class Account(Enum):
    HDFC_BANK_ACCOUNT = 1
    KOTAK_BANK_ACCOUNT = 2
    HDFC_CREDIT_CARD = 3
    SBI_CREDIT_CARD = 4
    ICICI_CREDIT_CARD = 5
    KOTAK_CREDIT_CARD = 6
    EQUITAS_BANK_ACCOUNT = 7
    HDFC_UPI_CREDIT_CARD = 8
    PAYTM_WALLET = 9
    IDFC_BANK_ACCOUNT = 10
    FASTAG_WALLET = 11


OUTPUT_COLUMNS = [
    "txn_date",
    "account",
    "txn_type",
    "txn_amount",
    "category",
    "tags",
    "notes",
]

EXTRA_FIELDS = ["Category", "Tags", "Notes"]

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
    "INV": "Investments",
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
    "FD": "Food & Dining",
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
    "ls": "Life Style",
    "LS": "Life Style",
    "Fuel": "Fuel",
    "fuel": "Fuel",
    "F": "Fuel",
    "f": "Fuel",
}
