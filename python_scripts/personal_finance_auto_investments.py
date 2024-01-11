import csv
import os


OUTPUT_COLUMNS = ["Date", "Account", "Type", "Amount", "Category", "Tags", "Notes"]


def main():
	investments = [
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 4200,
			"Category": "Investments",
			"Tags": "#NPS",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 4000,
			"Category": "Investments",
			"Tags": "#HealthInsurance #TaxSaving #Insurance",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 4000,
			"Category": "Investments",
			"Tags": "#ELSS #TaxSaving",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 6000,
			"Category": "Investments",
			"Tags": "#SSY #Dhathri #TaxSaving",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 2700,
			"Category": "Investments",
			"Tags": "#TermInsurance #TaxSaving #Insurance",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 40000,
			"Category": "Loan",
			"Tags": "#EMI #PlotLoan",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 35000,
			"Category": "Loan",
			"Tags": "#EMI #PlotLoan",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 12848,
			"Category": "Loan",
			"Tags": "#EMI #CarLoan",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 34000,
			"Category": "Investments",
			"Tags": "#MutualFunds #Equity",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 21000,
			"Category": "Investments",
			"Tags": "#Stocks #Equity",
			"Notes": "",
		}
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 5000,
			"Category": "Investments",
			"Tags": "#Stocks #Adhoc",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 10000,
			"Category": "Investments",
			"Tags": "#Gold #KhazanaGoldScheme",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 10000,
			"Category": "Investments",
			"Tags": "#Gold #FixedDeposit #Equitas",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 5000,
			"Category": "Investments",
			"Tags": "#USStocks",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 12000,
			"Category": "Investments",
			"Tags": "#EmergencyFund",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 10000,
			"Category": "Investments",
			"Tags": "#Vacation",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 16488,
			"Category": "Investments",
			"Tags": "#House",
			"Notes": "",
		},
		{
			"Date": "",
			"Account": "HDFC Bank Account",
			"Type": "Debit",
			"Amount": 75000,
			"Category": "Investments",
			"Tags": "#House",
			"Notes": "",
		}
	]
	with open(os.path.join(os.path.dirname(__file__), "personal_finance_auto_investments_result.csv")) as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=OUTPUT_COLUMNS)
		writer.writeheader()




if __name__ == '__main__':
	main()
