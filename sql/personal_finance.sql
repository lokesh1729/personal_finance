-- To update `updated_at` column automatically

create or replace
function trigger_set_timestamp()
returns trigger as $$
begin
  NEW.updated_at = NOW();

return new;
end;

$$ language plpgsql;

create trigger set_timestamp
before
update
	on
	hdfc_credit_card
for each row
execute function trigger_set_timestamp();



alter table payoneer_transactions alter column "Date" type DATE
	using "Date"::DATE;

update
	payoneer_transactions
set
	"INR" = replace("INR",
	',',
	'');

update
	paypal_transactions
set
	"Gross" = regexp_replace("Gross",
	'\s',
	'',
	'g');

select
	*
from
	hdfc_credit_card
where
	extract('Day'
from
	"Date") between 1 and 12
	and extract('Month'
from
	"Date") between 1 and 12;

update
	hdfc_transactions
set
	"Withdrawal Amt." = null
where
	"Withdrawal Amt." = '';

alter table equitas_transactions alter column "Date" type DATE
	using "Date"::DATE;

alter table equitas_transactions alter column "Debit" type DATE
	using "Debit"::FLOAT;

update
	groww_transactions
set
	"Amount" = replace("Amount",
	',',
	'');

update
	hdfc_credit_card
set
	"Amount" = replace("Amount",
	',',
	'');

update
	kotak_transactions
set
	"Debit" = null
where
	"Debit" = '';

update
	mutual_funds
set
	"PRICE" = 0
where
	"PRICE" is null;

update
	kotak_transactions
set
	"Balance" = replace("Balance",
	',',
	'');
-- find duplicate transactions in a month
select
	DATE_TRUNC('month',
	"txn_date") as txn_month,
	account,
	txn_type,
	txn_amount,
	category,
	string_agg(tags::text,
	':::') as tags,
	string_agg(id::text,
	',') as ids,
	string_agg(notes::text,
	':::') as notes
from
	transactions t
group by
	DATE_TRUNC('month',
	"txn_date"),
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
	string_agg(id::text,
	',') as ids
from
	mutual_funds mf
where
	mf."AMOUNT" > 0
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
	string_agg(tags::text,
	':::') as tags,
	string_agg(id::text,
	',') as ids,
	string_agg(notes::text,
	':::') as notes
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

alter table transactions rename column "Date" to "txn_date";

alter table transactions add column created_at timestamp default NOW();

alter table transactions add column updated_at timestamp;

alter type account_type add VALUE 'Kotak Credit Card';

alter table public.transactions alter column tags set
default '';

alter table public.transactions alter column tags set
not null;

create type txn_enum_type as enum ('Credit',
'Debit',
'Others');

alter table transactions alter column txn_type type txn_enum_type
	using txn_type::txn_enum_type;

begin;

alter type account_type rename to old_account_type;

create type account_type as enum (
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


alter table transactions alter column account type account_type
	using account::text::account_type;

drop type old_account_type;

commit;

begin;
-- Step 1: Create a new ENUM type with the desired order
create type public."txn_category_type_new" as enum (
    'Salary',
    'Refund',
    'Cashback',
    'Investment Redemption',
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
    'ATM Withdrawal',
    'Ramya',
    'Misc',
    'Others'
);
-- Step 2: Update all columns using the old ENUM type to use the new ENUM type
-- Example: Assuming you have a table `transactions` with a column `category` of type txn_category_type

alter table transactions alter column category type public."txn_category_type_new"
	using category::text::public."txn_category_type_new";
-- Step 3: Drop the old ENUM type
drop type public."txn_category_type";
-- Step 4: Rename the new ENUM type to match the old name
alter type public."txn_category_type_new" rename to "txn_category_type";

alter table transactions alter column category type public."txn_category_type"
	using category::text::public."txn_category_type";

commit;
-- get enum values

select
	e.enumlabel as enum_value
from
	pg_type t
join pg_enum e on
	t.oid = e.enumtypid
join pg_catalog.pg_namespace n on
	n.oid = t.typnamespace
where
	t.typname = 'txn_category_type'
order by
	enum_value;

select
	unnest(enum_range(null::txn_category_type)) as category;

alter table transactions alter column category type txn_category_type
	using category::text::txn_category_type;


with DuplicateEntries as (
select
	id,
	row_number() over (
            partition by 
                "Date",
	"Narration",
	"Deposit Amt.",
	"Value Dt",
	"Withdrawal Amt.",
	"Closing Balance"
order by
	id desc
        ) as row_num
from
	hdfc_transactions
)
delete
from
	hdfc_transactions
where
	id in (
	select
		id
	from
		DuplicateEntries
	where
		row_num > 1
)
	and "Date" > '2024-11-01';

select
	distinct "Chq./Ref.No."
from
	hdfc_transactions;

select
	*
from
	transactions
where
	txn_date between '2023-09-01' and '2023-11-30'
	and category in ('Investments')
order by
	txn_date asc,
	txn_amount asc;

select
	"PLAZA",
	COUNT(*)
from
	fastag_transaction_details ftd
group by
	1
order by
	1 asc;

select
	"PLAZA",
	AVG(ftd."AMOUNT")
from
	fastag_transaction_details ftd
group by
	1
order by
	2 desc;

select
	ndts."Date",
	ndts."Particulars",
	coalesce(cast(ndts."ICICI PRUDENTIAL PENSION FUND SCHEME C - TIER I Amount (Rs)" as real),
	0) +
    coalesce(cast(ndts."ICICI PRUDENTIAL PENSION FUND SCHEME E - TIER I Amount (Rs)" as real),
	0) +
    coalesce(cast(ndts."ICICI PRUDENTIAL PENSION FUND SCHEME G - TIER I Amount (Rs)" as real),
	0) as Total_Amount
from
	nps_detailed_transactions_statement ndts
where
	ndts."Particulars" = ''
	and ndts."Withdrawal / deduction in units towards intermediary charges (R" = '';

select
	array_agg(shl.id)
from
	sbi_home_loan shl
group by
	shl."LAN" ,
	shl."Txn Date" ,
	shl."Value Date" ,
	shl."Description" ,
	shl."Credit" ,
	shl."Debit" ,
	shl."Balance"
having
	count(*) > 1;




CREATE TABLE transactions_new AS
SELECT * FROM transactions;


select
	array_agg(id),
	icc."Amount",
	icc."Date",
	icc."Transaction Details",
	icc."Type"
from
	icici_credit_card icc
group by
	icc."Amount",
	icc."Date",
	icc."Transaction Details",
	icc."Type"
having
	count(*) > 1
order by icc."Date" desc;


with RankedAxisTransactions as (
select
		id,
		row_number() over(partition by txn_date, cheque_ref_no, debit, credit, balance order by id desc) as row_num
from
		axis_bank_transactions
)
delete
from
	axis_bank_transactions
where
	id in (
	select
		id
	from
		RankedAxisTransactions
	where
		row_num > 1
);

with RankedAxisTransactions as (
select
		id,
		row_number() over(partition by txn_date, cheque_ref_no, debit, credit, balance order by id desc) as row_num
from
		axis_bank_transactions
)
select
		id,
		row_num
	from
		RankedAxisTransactions
	where
		row_num > 1;


select distinct "Debit / Credit" from hdfc_credit_card;


