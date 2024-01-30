select * from transactions WHERE "Date" >= '2023-06-01' AND "Date" <= '2023-06-30';

select * from transactions WHERE "Date" >= '2023-07-01' AND "Date" <= '2023-07-31';

select * from transactions WHERE "Date" >= '2023-08-01' AND "Date" <= '2023-08-31';

select * from transactions WHERE "Date" >= '2023-05-01' AND "Date" <= '2023-05-31';

select * from transactions WHERE "Amount" = '16,488.00' AND "Category" = 'Loan';


select * from transactions WHERE "Category" = 'Loan' AND "Date" >= '2023-06-01' AND "Date" <= '2023-06-30';


ALTER TABLE transactions RENAME COLUMN "Date" TO "txn_date";

ALTER TABLE transactions RENAME COLUMN "Account" TO "account";

ALTER TABLE transactions RENAME COLUMN "Type" TO "txn_type";

ALTER TABLE transactions RENAME COLUMN "Amount" TO "txn_amount";

ALTER TABLE transactions RENAME COLUMN "Category" TO "category";

ALTER TABLE transactions RENAME COLUMN "Tags" TO "tags";

ALTER TABLE transactions RENAME COLUMN "Notes" TO "notes";

ALTER TABLE transactions ADD COLUMN created_at timestamp DEFAULT NOW();

ALTER TABLE transactions ADD COLUMN updated_at timestamp;

ALTER TABLE transactions ALTER COLUMN txn_amount TYPE FLOAT USING txn_amount::double precision;

ALTER TABLE walnut_transactions ALTER COLUMN amount TYPE FLOAT USING amount::double precision;

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


ALTER TABLE walnut_transactions RENAME COLUMN "DATE" TO "txn_date";

ALTER TABLE walnut_transactions RENAME COLUMN "TIME" TO "txn_time";

ALTER TABLE walnut_transactions RENAME COLUMN "DR/CR" TO "txn_type";

ALTER TABLE walnut_transactions RENAME COLUMN "PLACE" TO "place";

ALTER TABLE walnut_transactions RENAME COLUMN "AMOUNT" TO "amount";

ALTER TABLE walnut_transactions RENAME COLUMN "ACCOUNT" TO "account";

ALTER TABLE walnut_transactions RENAME COLUMN "EXPENSE" TO "expense";

ALTER TABLE walnut_transactions RENAME COLUMN "INCOME" TO "income";

ALTER TABLE walnut_transactions RENAME COLUMN "CATEGORY" TO "category";

ALTER TABLE walnut_transactions RENAME COLUMN "TAGS" TO "tags";

ALTER TABLE walnut_transactions RENAME COLUMN "NOTE" TO "notes";

-- rename tables

ALTER TABLE hdfc_transactions1 RENAME TO hdfc_transactions;

ALTER TABLE kotak_transactions1 RENAME TO kotak_transactions;

SELECT DISTINCT account FROM walnut_transactions; 

SELECT DISTINCT category FROM walnut_transactions ORDER BY category;

SELECT DISTINCT category FROM transactions ORDER BY category DESC;

SELECT DISTINCT expense FROM walnut_transactions;
	
SELECT DISTINCT income FROM walnut_transactions;

SELECT DISTINCT account FROM transactions;

-- modifying to enum types

CREATE TYPE account_type AS ENUM ('IndusInd Credit Card',
'SBI Credit Card',
'Equitas Bank Account',
'Ola Money Postpaid',
'Kotak Bank Account',
'DBS Bank Account',
'Amazon Pay',
'HDFC Credit Card',
'Others',
'Fi Bank Account',
'Cash',
'Freecharge',
'Paytm Wallet',
'Paytm Food Wallet',
'ICICI Credit Card',
'IDFC First Bank Account',
'Simpl',
'HDFC Bank Account',
'SBI Bank Account',
'Slice Credit Card',
'Citi Bank Account'
);

ALTER TYPE account_type ADD VALUE 'Kotak Credit Card';


ALTER TABLE transactions
   ALTER COLUMN account TYPE account_type USING account::account_type;

ALTER TABLE transactions
   ALTER COLUMN account TYPE varchar(255);


CREATE TYPE txn_enum_type AS ENUM ('Credit', 'Debit', 'Others');

ALTER TABLE transactions ALTER COLUMN txn_type TYPE txn_enum_type USING txn_type::txn_enum_type;

CREATE TYPE txn_category_type AS ENUM ('Maintenance',
'Life Style',
'Household',
'Dividend',
'Food & Dining',
'Bills',
'Entertainment',
'Donation',
'Others',
'Health',
'Travel',
'Salary',
'Misc',
'Groceries',
'Interest',
'Fruits & Vegetables',
'Gifts',
'Ramya',
'Rent',
'Refund',
'Productivity',
'Personal Care',
'Loan',
'Egg & Meat',
'Investments',
'Shopping',
'Cashback'
);

ALTER TYPE txn_category_type ADD VALUE 'Fuel';

ALTER TABLE transactions ALTER COLUMN category TYPE txn_category_type USING category::txn_category_type;

-- Pivot tables


CREATE EXTENSION IF NOT EXISTS tablefunc;


SELECT * FROM crosstab(
	'SELECT CONCAT(to_char(txn_date, ''YYYY''), ''-'', to_char(txn_date, ''MM'')) as year_month, category, sum(txn_amount) FROM transactions GROUP BY to_char(txn_date, ''YYYY''), to_char(txn_date, ''MM''), category ORDER BY CONCAT(to_char(txn_date, ''YYYY''), ''-'', to_char(txn_date, ''MM'')), category DESC',
	'SELECT DISTINCT category from transactions ORDER BY category'
) AS ct (year_month text, "Maintenance" text,"Life Style" text,"Household" text,"Dividend" text,"Food & Dining" text,"Bills" text,"Entertainment" text,"Donation" text,"Others" text,"Health" text,"Travel" text,"Salary" text,"Misc" text,"Groceries" text,"Interest" text,"Fruits & Vegetables" text,"Gifts" text,"Ramya" text,"Rent" text,"Refund" text,"Productivity" text,"Personal Care" text,"Loan" text,"Egg & Meat" text,"Investments" text,"Shopping" text,"Cashback" text);


SELECT CONCAT(to_char(txn_date, 'YYYY'), '-', to_char(txn_date, 'MM')), category, sum(txn_amount) FROM transactions WHERE category in ('Maintenance',
'Life Style',
'Household',
'Food & Dining',
'Bills',
'Entertainment',
'Donation',
'Health',
'Travel',
'Fuel',
'Misc',
'Groceries',
'Fruits & Vegetables',
'Gifts',
'Productivity',
'Personal Care',
'Egg & Meat',
'Shopping'
) GROUP BY to_char(txn_date, 'YYYY'), to_char(txn_date, 'MM'), category ORDER BY CONCAT(to_char(txn_date, 'YYYY'), '-', to_char(txn_date, 'MM')) DESC;	


SELECT * FROM transactions WHERE category = 'Bills' AND notes ilike '%water%';

SELECT * FROM transactions WHERE tags ilike '%RealEstate%' ORDER BY txn_date;

SELECT * FROM transactions WHERE notes ilike '%estate%' ORDER BY txn_date;

SELECt * FROM transactions WHERE txn_date < '2022-05-01';

SELECT * FROM walnut_transactions WHERE category = 'CREDIT';

SELECT * FROM walnut_transactions WHERE account = 'Flipkart Pay Later';

SELECT * FROM walnut_transactions WHERE tags ilike '%itr%' or notes ilike '%itr%' ORDER BY txn_date;

SELECT * FROM transactions WHERE tags ilike '%income%' or notes ilike '%income tax%' ORDER BY txn_date;

UPDATE walnut_transactions SET category = 'SHOPPING' WHERE category = 'UNKNOWN';

SET datestyle = "ISO, DMY";

SHOW datestyle;

ALTER TABLE payoneer_transactions ALTER COLUMN "Date" TYPE DATE using "Date"::DATE;

UPDATE payoneer_transactions SET "INR" = REPLACE("INR", ',', '');

UPDATE paypal_transactions SET "Gross" = regexp_replace("Gross", '\s', '', 'g');

select * from paypal_transactions;

ALTER TABLE payoneer_transactions ALTER COLUMN "INR" TYPE float USING "INR"::float;

ALTER TABLE hdfc_transactions  ALTER COLUMN "Withdrawal Amt." TYPE float USING "Withdrawal Amt."::float;


SELECT * FROM transactions WHERE tags ilike '%hair%' ORDER BY txn_date DESC;

SELECT * FROM "public"."transactions" WHERE "txn_amount" > 13000 AND "txn_amount" < 15000 and "txn_type" = 'Credit';

SELECT * FROM "public"."transactions" WHERE "txn_date" between '2022-03-08' AND '2022-03-15';

SELECT * FROM transactions WHERE (notes ilike '%loan%' or category = 'Loan') and tags not in ('#PlotLoan', '#PersonalLoan', '#CarLoan');

SELECT * FROM transactions WHERE notes ilike '%satya%';

SELECT * FROM transactions WHERE category = 'Othres' and (tags ilike '%loan%' or notes ilike '%loan%');


SELECT * FROM walnut_transactions WHERE tags ilike '%fiver%' or notes ilike '%fiver%';

SELECT * FROM transactions WHERE tags ilike '%fiver%' or notes ilike '%fiver%';

SELECT * from hdfc_credit_card WHERE EXTRACT('Day' FROM "Date") BETWEEN 1 and 12 and EXTRACT('Month' FROM "Date") BETWEEN 1 and 12;

SELECT * FROM paypal_transactions ORDER BY "Date" ASC;


update hdfc_transactions set "Withdrawal Amt." = null where "Withdrawal Amt." = '';

ALTER TABLE equitas_transactions  ALTER COLUMN "Date" TYPE DATE using "Date"::DATE;

ALTER TABLE equitas_transactions  ALTER COLUMN "Debit" TYPE DATE using "Debit"::FLOAT;

UPDATE idfc_transactions SET "Balance" = REPLACE("Balance", ',', '');

update idfc_transactions set "Balance" = null where "Balance" = '';


