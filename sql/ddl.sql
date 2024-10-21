-- public.capital_gains_cams definition

-- Drop table

-- DROP TABLE public.capital_gains_cams;

CREATE TABLE public.capital_gains_cams (
	"AMC Name" varchar(50) NULL,
	"Folio No" varchar(50) NULL,
	"Asset Class" varchar(50) NULL,
	"Scheme Name" varchar(256) NULL,
	"Description" varchar(50) NULL,
	"Redemption Date" date NULL,
	"Redemption Units" float4 NULL,
	"Redemption Amount" float4 NULL,
	"Redemption Unit Price" float4 NULL,
	"STT" float4 NULL,
	"Purchase Description" varchar(50) NULL,
	"Purchased Date" date NULL,
	"Purchased Units" float4 NULL,
	"Redeemed Units" float4 NULL,
	"Purchased Unit Price" float4 NULL,
	"Indexed Cost" int4 NULL,
	"Short Term Capital Gains" int4 NULL,
	"Long Term Capital Gains With Index" int4 NULL,
	"Long Term Capital Gains Without Index" float4 NULL,
	"Tax Percentage On Capital Gains" int4 NULL,
	"Tax Deducted On Capital Gains" int4 NULL,
	"Tax Surcharge On Capital Gains" int4 NULL,
	id serial4 NOT NULL,
	CONSTRAINT capital_gains_cams_pk PRIMARY KEY (id)
);
CREATE INDEX capital_gains_cams_date_idx ON public.capital_gains_cams USING btree ("Redemption Date");
CREATE INDEX capital_gains_cams_purchased_date_idx ON public.capital_gains_cams USING btree ("Purchased Date");


-- public.capital_gains_kfintech definition

-- Drop table

-- DROP TABLE public.capital_gains_kfintech;

CREATE TABLE public.capital_gains_kfintech (
	"Fund Name" varchar(50) NULL,
	"Folio Number" text NULL,
	"Scheme Name" varchar(128) NULL,
	"Purchased Date" date NULL,
	"Current Units" float4 NULL,
	"Source Scheme units" float4 NULL,
	"Purchased Unit Price" float4 NULL,
	"Purchased Amount" float4 NULL,
	"Redemption Date" date NULL,
	"Redeemed Units" float4 NULL,
	"Redeemed Amount" float4 NULL,
	"Redeemed Unit Price" float4 NULL,
	"Short Term" float4 NULL,
	"Indexed Cost" float4 NULL,
	"Long Term With Index" float4 NULL,
	"Long Term Without Index" float4 NULL,
	id serial4 NOT NULL,
	CONSTRAINT capital_gains_kfintech_pk PRIMARY KEY (id)
);
CREATE INDEX capital_gains_kfintech_purchased_date_idx ON public.capital_gains_kfintech USING btree ("Purchased Date");
CREATE INDEX capital_gains_kfintech_redemption_date_idx ON public.capital_gains_kfintech USING btree ("Redemption Date");

-- public.dividends definition

-- Drop table

-- DROP TABLE public.dividends;

CREATE TABLE public.dividends (
	"Symbol" text NOT NULL,
	"ISIN" text NOT NULL,
	"Date" date NOT NULL,
	"Quantity" int4 NOT NULL,
	"Dividend Per Share" float4 NOT NULL,
	"Net Dividend Amount" float4 NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT dividends_pk PRIMARY KEY (id),
	CONSTRAINT dividends_unique UNIQUE ("Symbol", "ISIN", "Date", "Quantity", "Dividend Per Share", "Net Dividend Amount")
);
CREATE INDEX dividends_date_idx ON public.dividends USING btree ("Date");
CREATE INDEX dividends_net_dividend_amount_idx ON public.dividends USING btree ("Net Dividend Amount");
CREATE INDEX dividends_symbol_idx ON public.dividends USING btree ("Symbol");


-- public.equitas_transactions definition

-- Drop table

-- DROP TABLE public.equitas_transactions;

CREATE TABLE public.equitas_transactions (
	"Date" date NOT NULL,
	"Reference No. / Cheque No." varchar(50) NOT NULL,
	"Narration" varchar(128) NOT NULL,
	"Withdrawal" float8 NULL,
	"Deposit" float8 NULL,
	"Closing Balance" float8 NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT equitas_transactions_pk PRIMARY KEY (id),
	CONSTRAINT equitas_transactions_unique UNIQUE ("Date", "Reference No. / Cheque No.", "Narration", "Closing Balance")
);
CREATE INDEX equitas_transactions_date_idx ON public.equitas_transactions USING btree ("Date");
CREATE INDEX equitas_transactions_deposit_idx ON public.equitas_transactions USING btree ("Deposit");
CREATE INDEX equitas_transactions_withdrawal_idx ON public.equitas_transactions USING btree ("Withdrawal");


-- public.fastag_transaction_details definition

-- Drop table

-- DROP TABLE public.fastag_transaction_details;

CREATE TABLE public.fastag_transaction_details (
	"TRANSACTION DATE" date NOT NULL,
	"TRANSACTION TIME" varchar(50) NOT NULL,
	"TRANSACTION ID" varchar(50) NOT NULL,
	"PLAZA" varchar(50) NOT NULL,
	"VEH REG NO" varchar(50) NOT NULL,
	"AMOUNT" int4 NOT NULL,
	"TAG VEH.CLASS" int4 NOT NULL,
	"LANE DIRECTION" varchar(50) NOT NULL,
	"RECON DATE TIME" date NOT NULL,
	"VEH_CLASS_DESC" varchar(50) NOT NULL,
	CONSTRAINT fastag_transaction_details_pk PRIMARY KEY ("TRANSACTION ID"),
	CONSTRAINT fastag_transaction_details_unique UNIQUE ("TRANSACTION DATE", "TRANSACTION TIME", "PLAZA", "VEH REG NO", "AMOUNT", "TAG VEH.CLASS", "LANE DIRECTION", "RECON DATE TIME", "VEH_CLASS_DESC")
);
CREATE INDEX fastag_transaction_details_transaction_date_idx ON public.fastag_transaction_details USING btree ("TRANSACTION DATE");


-- public.fastag_wallet_statement definition

-- Drop table

-- DROP TABLE public.fastag_wallet_statement;

CREATE TABLE public.fastag_wallet_statement (
	"TXN DATE & TIME" date NOT NULL,
	"TXN ID" varchar(50) NOT NULL,
	"VEH REG NO" varchar(50) NOT NULL,
	"MERCHANT ID" varchar(50) NOT NULL,
	"DESCRIPTION" varchar(128) NOT NULL,
	"OPENING BALANCE" int4 NOT NULL,
	"CLOSING BALANCE" int4 NOT NULL,
	"TXN AMOUNT" int4 NOT NULL,
	"CR/DR" varchar(50) NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT fastag_wallet_statement_pk PRIMARY KEY (id),
	CONSTRAINT fastag_wallet_statement_unique UNIQUE ("TXN DATE & TIME", "TXN ID", "VEH REG NO", "MERCHANT ID", "DESCRIPTION", "OPENING BALANCE", "CLOSING BALANCE", "TXN AMOUNT", "CR/DR")
);
CREATE INDEX fastag_wallet_statement_txn_date_time_idx ON public.fastag_wallet_statement USING btree ("TXN DATE & TIME");


-- public.groww_transactions definition

-- Drop table

-- DROP TABLE public.groww_transactions;

CREATE TABLE public.groww_transactions (
	"Scheme Name" text NOT NULL,
	"Transaction Type" varchar(50) NOT NULL,
	"Units" float4 NOT NULL,
	"NAV" float4 NOT NULL,
	"Amount" float4 NOT NULL,
	"Date" date NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT groww_transactions_pk PRIMARY KEY (id),
	CONSTRAINT groww_transactions_unique UNIQUE ("Scheme Name", "Transaction Type", "Units", "NAV", "Amount", "Date")
);
CREATE INDEX groww_transactions_date_idx ON public.groww_transactions USING btree ("Date");


-- public.hdfc_credit_card definition

-- Drop table

-- DROP TABLE public.hdfc_credit_card;

CREATE TABLE public.hdfc_credit_card (
	"Date" date NOT NULL,
	"Description" varchar(128) NOT NULL,
	"Amount" float4 NOT NULL,
	"Debit / Credit" varchar(50) NULL,
	id serial4 NOT NULL,
	CONSTRAINT hdfc_credit_card2_pk PRIMARY KEY (id)
);
CREATE INDEX hdfc_credit_card_date_idx2 ON public.hdfc_credit_card USING btree ("Date");


-- public.hdfc_transactions definition

-- Drop table

-- DROP TABLE public.hdfc_transactions;

CREATE TABLE public.hdfc_transactions (
	"Date" date NOT NULL,
	"Narration" text NOT NULL,
	"Chq./Ref.No." text NOT NULL,
	"Value Dt" text NOT NULL,
	"Withdrawal Amt." float8 NULL,
	"Deposit Amt." int4 NULL,
	"Closing Balance" float4 NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT hdfc_transactions_pk PRIMARY KEY (id)
);
CREATE INDEX hdfc_transactions_date_idx ON public.hdfc_transactions USING btree ("Date");
CREATE INDEX hdfc_transactions_deposit_amt__idx ON public.hdfc_transactions USING btree ("Deposit Amt.");
CREATE INDEX hdfc_transactions_withdrawal_amt__idx ON public.hdfc_transactions USING btree ("Withdrawal Amt.");


-- public.icici_credit_card definition

-- Drop table

-- DROP TABLE public.icici_credit_card;

CREATE TABLE public.icici_credit_card (
	"Date" date NOT NULL,
	"Sr.No." varchar(100) NOT NULL,
	"Transaction Details" varchar(255) NOT NULL,
	"Reward Point" float4 NULL,
	"Intl.Amount" float4 NULL,
	"Amount" float4 NOT NULL,
	"Type" varchar(50) NULL,
	id serial4 NOT NULL,
	CONSTRAINT icici_credit_card_new_pk PRIMARY KEY (id)
);
CREATE INDEX icici_credit_card_date_idx ON public.icici_credit_card USING btree ("Date");


-- public.idfc_transactions definition

-- Drop table

-- DROP TABLE public.idfc_transactions;

CREATE TABLE public.idfc_transactions (
	"Transaction Date" date NOT NULL,
	"Value Date" date NOT NULL,
	"Particulars" varchar(128) NOT NULL,
	"Cheque No." varchar(50) NULL,
	"Debit" float8 NULL,
	"Credit" float8 NULL,
	"Balance" float8 NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT idfc_transactions_pk PRIMARY KEY (id)
);
CREATE INDEX idfc_transactions_credit_idx ON public.idfc_transactions USING btree ("Credit");
CREATE INDEX idfc_transactions_debit_idx ON public.idfc_transactions USING btree ("Debit");
CREATE INDEX idfc_transactions_transaction_date_idx ON public.idfc_transactions USING btree ("Transaction Date");

-- public.kotak_credit_card definition

-- Drop table

-- DROP TABLE public.kotak_credit_card;

CREATE TABLE public.kotak_credit_card (
	"Date" date NOT NULL,
	"Transaction details" varchar(64) NOT NULL,
	"Spends Area" varchar(50) NULL,
	"Amount (Rs.)" varchar(50) NOT NULL,
	id serial4 NOT NULL,
	"Transaction Type" varchar NULL,
	CONSTRAINT kotak_credit_card_pk PRIMARY KEY (id)
);
CREATE INDEX kotak_credit_card_date_idx ON public.kotak_credit_card USING btree ("Date");

-- public.kotak_transactions definition

-- Drop table

-- DROP TABLE public.kotak_transactions;

CREATE TABLE public.kotak_transactions (
	"Transaction Date" date NOT NULL,
	"Value Date" date NOT NULL,
	"Description" text NOT NULL,
	"Chq / Ref No." text NOT NULL,
	"Debit" float4 NULL,
	"Credit" float4 NULL,
	"Balance" text NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT kotak_transactions_pk PRIMARY KEY (id)
);
CREATE INDEX kotak_transactions_transaction_date_idx ON public.kotak_transactions USING btree ("Transaction Date");


-- public.mutual_funds definition

-- Drop table

-- DROP TABLE public.mutual_funds;

CREATE TABLE public.mutual_funds (
	"MF_NAME" text NOT NULL,
	"INVESTOR_NAME" text NOT NULL,
	"PAN" text NOT NULL,
	"FOLIO_NUMBER" text NOT NULL,
	"PRODUCT_CODE" text NULL,
	"SCHEME_NAME" text NOT NULL,
	"Type" text NULL,
	"TRADE_DATE" date NOT NULL,
	"TRANSACTION_TYPE" text NOT NULL,
	"DIVIDEND_RATE" text NULL,
	"AMOUNT" float4 NOT NULL,
	"UNITS" float4 NOT NULL,
	"PRICE" float4 NOT NULL,
	"BROKER" text NULL,
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	CONSTRAINT mutual_funds_pk PRIMARY KEY (id)
);


-- public.niyomoney_transactions definition

-- Drop table

-- DROP TABLE public.niyomoney_transactions;

CREATE TABLE public.niyomoney_transactions (
	"Goal Name" varchar(50) NOT NULL,
	"Folio no" varchar(50) NOT NULL,
	"Mutual Fund" varchar(128) NOT NULL,
	"Instruction Date" date NOT NULL,
	"NAV Date" date NOT NULL,
	"Buy/Sell" varchar(50) NOT NULL,
	"Transaction Type" varchar(50) NOT NULL,
	"Payment Type" varchar(50) NOT NULL,
	"Amount" int4 NOT NULL,
	"NAV" float4 NOT NULL,
	"Units" float4 NOT NULL,
	"Status" varchar(50) NOT NULL,
	"Stamp Duty" int4 NULL,
	"TDS" int4 NULL,
	"LOAD" int4 NULL,
	"Is Rebalance Tx" varchar(50) NULL,
	id serial4 NOT NULL,
	CONSTRAINT niyomoney_transactions_pk PRIMARY KEY (id)
);
CREATE INDEX niyomoney_transactions_goal_name_idx ON public.niyomoney_transactions USING btree ("Goal Name");
CREATE INDEX niyomoney_transactions_instruction_date_idx ON public.niyomoney_transactions USING btree ("Instruction Date");
CREATE INDEX niyomoney_transactions_mutual_fund_idx ON public.niyomoney_transactions USING btree ("Mutual Fund");
CREATE INDEX niyomoney_transactions_transaction_type_idx ON public.niyomoney_transactions USING btree ("Transaction Type");

-- public.paytm_transactions definition

-- Drop table

-- DROP TABLE public.paytm_transactions;

CREATE TABLE public.paytm_transactions (
	"Date" text NOT NULL,
	"Activity" text NOT NULL,
	"Source/Destination" text NOT NULL,
	"Wallet Txn ID" int8 NOT NULL,
	"Comment" text NULL,
	"Debit" float4 NULL,
	"Credit" float4 NULL,
	"Transaction Breakup" text NOT NULL,
	"Status" text NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT paytm_transactions_pk PRIMARY KEY (id),
	CONSTRAINT paytm_transactions_unique UNIQUE ("Date", "Activity", "Source/Destination", "Wallet Txn ID", "Transaction Breakup", "Status")
);
CREATE INDEX paytm_transactions_credit_idx ON public.paytm_transactions USING btree ("Credit");
CREATE INDEX paytm_transactions_date_idx ON public.paytm_transactions USING btree ("Date");
CREATE INDEX paytm_transactions_debit_idx ON public.paytm_transactions USING btree ("Debit");

-- public.sbi_credit_card definition

-- Drop table

-- DROP TABLE public.sbi_credit_card;

CREATE TABLE public.sbi_credit_card (
	"Date" date NOT NULL,
	"Transaction Details" text NOT NULL,
	"Amount" float4 NOT NULL,
	"Type" text NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT sbi_credit_card_pk PRIMARY KEY (id)
);
CREATE INDEX sbi_credit_card_date_idx ON public.sbi_credit_card USING btree ("Date");

-- public.sbi_home_loan definition

-- Drop table

-- DROP TABLE public.sbi_home_loan;

CREATE TABLE public.sbi_home_loan (
	"LAN" varchar(50) NOT NULL,
	"Txn Date" date NOT NULL,
	"Value Date" date NOT NULL,
	"Description" text NOT NULL,
	"Debit" float4 NULL,
	"Credit" float4 NULL,
	"Balance" float8 NOT NULL,
	id serial4 NOT NULL,
	CONSTRAINT sbi_home_loan_pk PRIMARY KEY (id)
);
CREATE INDEX sbi_home_loan_txn_date_idx ON public.sbi_home_loan USING btree ("Txn Date");

-- public.stocks definition

-- Drop table

-- DROP TABLE public.stocks;

CREATE TABLE public.stocks (
	"Symbol" text NOT NULL,
	"ISIN" text NOT NULL,
	"Trade Date" date NOT NULL,
	"Exchange" text NOT NULL,
	"Segment" text NOT NULL,
	"Series" text NOT NULL,
	"Trade Type" text NOT NULL,
	"Auction" bool NULL,
	"Quantity" int4 NOT NULL,
	"Price" float8 NOT NULL,
	"Trade ID" int8 NOT NULL,
	"Order ID" int8 NOT NULL,
	"Order Execution Time" date NOT NULL,
	CONSTRAINT stocks_pk PRIMARY KEY ("Trade ID", "Order ID")
);
CREATE INDEX stocks_symbol_idx ON public.stocks USING btree ("Symbol");
CREATE INDEX stocks_trade_date_idx ON public.stocks USING btree ("Trade Date");


-- public.transactions definition

-- Drop table

-- DROP TABLE public.transactions;

CREATE TABLE public.transactions (
	txn_date date NOT NULL,
	account public."account_type" NOT NULL,
	txn_type public."txn_enum_type" NOT NULL,
	txn_amount float8 NOT NULL,
	category public."txn_category_type" NOT NULL,
	tags text DEFAULT ''::text NULL,
	notes text DEFAULT ''::text NULL,
	created_at timestamptz DEFAULT now() NOT NULL,
	updated_at timestamptz NULL,
	id serial4 NOT NULL,
	CONSTRAINT transactions_pk PRIMARY KEY (id),
	CONSTRAINT transactions_unique UNIQUE (txn_date, account, txn_type, txn_amount, category, tags, notes)
);
CREATE INDEX transactions_account_idx ON public.transactions USING btree (account);
CREATE INDEX transactions_category_idx ON public.transactions USING btree (category);
CREATE INDEX transactions_notes_idx ON public.transactions USING btree (notes);
CREATE INDEX transactions_tags_idx ON public.transactions USING btree (tags);
CREATE INDEX transactions_txn_amount_idx ON public.transactions USING btree (txn_amount);
CREATE INDEX transactions_txn_date_idx ON public.transactions USING btree (txn_date);
CREATE INDEX transactions_txn_type_idx ON public.transactions USING btree (txn_type);

-- Table Triggers

create trigger set_timestamp before
update
    on
    public.transactions for each row execute function trigger_set_timestamp();


-- public.zerodha_ledger definition

-- Drop table

-- DROP TABLE public.zerodha_ledger;

CREATE TABLE public.zerodha_ledger (
	particulars text NULL,
	posting_date date NULL,
	cost_center varchar(255) NULL,
	voucher_type varchar(255) NULL,
	debit float4 NULL,
	credit float4 NULL,
	net_balance float4 NULL,
	id serial4 NOT NULL,
	CONSTRAINT zerodha_ledger_pk PRIMARY KEY (id)
);
CREATE INDEX zerodha_ledger_posting_date_idx ON public.zerodha_ledger USING btree (posting_date);


-- public.payoneer_transactions definition

-- Drop table

-- DROP TABLE public.payoneer_transactions;

CREATE TABLE public.payoneer_transactions (
	"Date" date NOT NULL,
	"Description" text NULL,
	"Amount" float4 NOT NULL,
	"Currency" text NULL,
	"Status" text NULL,
	"INR" float8 NULL,
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	CONSTRAINT payoneer_transactions_pk PRIMARY KEY (id),
	CONSTRAINT payoneer_transactions_unique UNIQUE ("Date", "Description", "Amount", "Currency", "Status", "INR")
);
CREATE INDEX payoneer_transactions_amount_idx ON public.payoneer_transactions USING btree ("Amount");
CREATE INDEX payoneer_transactions_date_idx ON public.payoneer_transactions USING btree ("Date");


-- public.paypal_transactions definition

-- Drop table

-- DROP TABLE public.paypal_transactions;

CREATE TABLE public.paypal_transactions (
	"Date" date NOT NULL,
	"Type" text NOT NULL,
	"Transaction ID" text NOT NULL,
	"Gross" float8 NOT NULL,
	"Net" float8 NOT NULL,
	"Fee" float8 NULL,
	CONSTRAINT paypal_transactions_pk PRIMARY KEY ("Transaction ID"),
	CONSTRAINT paypal_transactions_unique UNIQUE ("Date", "Type", "Transaction ID", "Gross", "Net", "Fee")
);
CREATE INDEX paypal_transactions_date_idx ON public.paypal_transactions USING btree ("Date");
