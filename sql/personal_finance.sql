-- To update `updated_at` column automatically

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

	
ALTER TABLE payoneer_transactions ALTER COLUMN "Date" TYPE DATE using "Date"::DATE;

UPDATE payoneer_transactions SET "INR" = REPLACE("INR", ',', '');

UPDATE paypal_transactions SET "Gross" = regexp_replace("Gross", '\s', '', 'g');

SELECT * from hdfc_credit_card WHERE EXTRACT('Day' FROM "Date") BETWEEN 1 and 12 and EXTRACT('Month' FROM "Date") BETWEEN 1 and 12;

UPDATE hdfc_transactions SET "Withdrawal Amt." = null WHERE "Withdrawal Amt." = '';

ALTER TABLE equitas_transactions  ALTER COLUMN "Date" TYPE DATE using "Date"::DATE;

ALTER TABLE equitas_transactions  ALTER COLUMN "Debit" TYPE DATE using "Debit"::FLOAT;

UPDATE groww_transactions  SET "Amount" = REPLACE("Amount", ',', '');

update hdfc_credit_card  set "Amount" = REPLACE("Amount", ',', '');

update kotak_transactions set "Debit" = null where "Debit" = '';

update mutual_funds set "PRICE" = 0 where "PRICE" is null;

-- find duplicate transactions in a month
select
	DATE_TRUNC('month', "txn_date") as txn_month,
	account,
	txn_type,
	txn_amount,
	category,
	string_agg(tags::text, ':::') as tags,
	string_agg(id::text,
	',') as ids,
	string_agg(notes::text, ':::') as notes
from
	transactions t
group by
	DATE_TRUNC('month', "txn_date"),
	account,
	txn_type,
	txn_amount,
	category
having
	count(id) > 1;


-- mutual funds delete duplicates
select
	"MF_NAME",
	"FOLIO_NUMBER",
	"TRADE_DATE",
	"AMOUNT" ,
	"UNITS" ,
	"PRICE",
	string_agg(id::text, ',') as ids
from
	mutual_funds mf
where mf."AMOUNT" > 0
group by
	"MF_NAME",
	"FOLIO_NUMBER",
	"TRADE_DATE",
	"AMOUNT" ,
	"UNITS" ,
	"PRICE" 
having
	count(id) > 1;


-- find duplicate transactions
select
	txn_date,
	account,
	txn_type,
	txn_amount,
	category,
	string_agg(tags::text, ':::') as tags,
	string_agg(id::text,',') as ids,
	string_agg(notes::text, ':::') as notes
from
	transactions t
group by
	txn_date,
	account,
	txn_type,
	txn_amount,
	category
having
	count(id) > 1;


select
	txn_date,
	account,
	txn_type,
	txn_amount,
	category,
	tags,
	notes,
	string_agg(id::text,
	',') as ids
from
	walnut_transactions wt
group by
	txn_date,
	account,
	txn_type,
	txn_amount,
	category,
	tags,
	notes
having
	count(*) > 1;

ALTER TABLE transactions RENAME COLUMN "Date" TO "txn_date";

ALTER TABLE transactions ADD COLUMN created_at timestamp DEFAULT NOW();

ALTER TABLE transactions ADD COLUMN updated_at timestamp;

ALTER TYPE account_type ADD VALUE 'Kotak Credit Card';

ALTER TABLE public.transactions ALTER COLUMN tags set DEFAULT '';

ALTER TABLE public.transactions ALTER COLUMN tags SET NOT null;

CREATE TYPE txn_enum_type AS ENUM ('Credit', 'Debit', 'Others');

ALTER TABLE transactions ALTER COLUMN txn_type TYPE txn_enum_type USING txn_type::txn_enum_type;



begin;
ALTER TYPE account_type RENAME TO old_account_type;
CREATE TYPE account_type AS ENUM (
'HDFC Bank Account',
'Kotak Bank Account',
'Equitas Bank Account',
'Cash',
'HDFC Credit Card',
'Kotak Credit Card',
'SBI Credit Card',
'ICICI Credit Card',
'Others',
'Amazon Pay',
'IDFC First Bank Account',
'Fi Bank Account',
'SBI Bank Account',
'Freecharge',
'Paytm Wallet',
'Paytm Food Wallet',
'Ola Money Postpaid',
'Simpl',
'IndusInd Credit Card',
'Slice Credit Card',
'DBS Bank Account',
'Citi Bank Account'
);
alter table transactions alter column account type account_type using account::TEXT::account_type;
drop type old_account_type;
commit;

-- modifying to enum types

-- begin;

CREATE TYPE txn_category_type AS ENUM (
'Salary',
'Investments',
'Loan',
'Rent',
'Bills',
'Groceries',
'Fruits & Vegetables',
'Food & Dining',
'Egg & Meat',
'Household',
'Health',
'Personal Care',
'Shopping',
'Life Style',
'Maintenance',
'Fuel',
'Travel',
'Gifts',
'Productivity',
'Entertainment',
'Donation',
'Misc',
'ATM Withdrawal',
'Dividend',
'Interest',
'Refund',
'Ramya',
'Cashback',
'Others'
);



-- get enum values

select e.enumlabel as enum_value
from pg_type t 
   join pg_enum e on t.oid = e.enumtypid  
   join pg_catalog.pg_namespace n ON n.oid = t.typnamespace where t.typname = 'txn_category_type' order by enum_value;
  
SELECT unnest(enum_range(NULL::txn_category_type)) as category;


ALTER TABLE transactions ALTER COLUMN category TYPE txn_category_type USING category::text::txn_category_type;
