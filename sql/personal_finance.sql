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


select version();



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




select now();

show timezone;



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



-- monthly investments and loans

INSERT in	TO public.transactions (txn_date,account,txn_type,txn_amount,category,tags,notes,created_at,updated_at) values
	 ('2024-04-01','HDFC Bank Account','Debit',12848.0,'Loan','#CarLoan','', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',6000.0,'Investments','','Dhathri SSY', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',2650.0,'Investments','#TaxSaving','tax saving - term insurance', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',40000.0,'Loan','#PlotLoan #Plot33','SBI Plot loan', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',4000.0,'Investments','','tax saving - health insurance', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',4000.0,'Investments','#TaxSaving','tax saving - ELSS mutual funds', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',34000.0,'Investments','','long term - equity mutual funds', NOW(), NOW()),
	 ('2024-04-02','Kotak Bank Account','Debit',26000.0,'Investments','#Stocks','long term - indian stocks', NOW(), NOW()),
	 ('2024-04-02','Kotak Bank Account','Debit',5000.0,'Investments','#USStocks','', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',75000.0,'Investments','','short term - house', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',4200.0,'Investments','#TaxSaving','NPS', NOW(), NOW()),
	 ('2024-04-02','HDFC Bank Account','Debit',30000.0,'Investments','','short term - monthly buffer & emergency fund', NOW(), NOW()),
	 ('2024-04-03','HDFC Bank Account','Debit',33525.0,'Loan','#PlotLoan #Plot34','SBI Plot loan', NOW(), NOW()),
	 ('2024-04-03','HDFC Bank Account','Debit',10000.0,'Investments','','vacation goal', NOW(), NOW()),
	 ('2024-04-05','HDFC Bank Account','Debit',16488.0,'Investments','#PersonalLoan','tataji babai loan - emergency fund / house goal', NOW(), NOW());
	
	


-- related transactions

	/*
with myconstants (txn_id) as (
	values (2801)
) select * from transactions where (tags ilike '%#' || txn_id) or (id = txn_id) order by txn_date asc;
*/

select * from transactions where (tags ilike '%#' || 2407 || '%') or (id = 2407) order by txn_date asc;


select * from transactions where txn_date between '2024-02-01' and '2024-03-31';

select * from transactions where account = 'Cash' order by txn_date desc;

select * from transactions order by id desc limit 10;

select * from walnut_transactions where tags ilike '%investmentredemption%';

select * from transactions where tags ilike '%investmentredemption%' order by txn_date asc limit 10;


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



select distinct category from walnut_transactions wt;

select distinct category from transactions t;



select * from walnut_transactions wt where wt.tags ~ '[0-9]+';


select * from transactions t order by id desc limit 100;





