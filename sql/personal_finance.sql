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



SELECT
  txn_date,
  account,
  txn_type,
  txn_amount,
  category,
  LOWER(tags) AS tags_normalized,
  LOWER(notes) AS notes_normalized,
  COUNT(*) AS duplicate_count
FROM
  public.transactions
GROUP BY
  txn_date,
  account,
  txn_type,
  txn_amount,
  category,
  LOWER(tags),
  LOWER(notes)
HAVING
  COUNT(*) > 1;





select * from equitas_transactions et where et."Deposit" > 30000 order by et."Date" desc;


select
	*
from
	hdfc_transactions ht
where
	ht."Date" between '2025-01-01' and '2025-01-31'
	and (ht."Withdrawal Amt." > 20000
		or ht."Deposit Amt." > 20000)
order by
	ht."Date" desc;

-- EPF amount

select * from transactions where notes ilike '%epf%'; -- 5851

select * from transactions where tags ilike '#AdhocLoan #Nagendra';

select * from transactions where (tags ilike '%#' || '5851' || '%') or (id = '5851') order by txn_date asc;

-- home interior

select * from transactions where tags ilike '%rupeek%' order by txn_date desc;


-- context save checkpoint

-- EPF and txn tagging is done

-- go back and analyse misc expenses especially credit card bill payments from equitas



-- credit card bill analysis ---> if the bill was paid in june'25 then get the txns from april'25 to may'25
-- except hdfc credit card 26th april to 25th may 2025 and 2nd may to 1st june 2025
-- 


select
	*
from
	equitas_transactions et
where
	(et."Narration" ilike '%cred%'
		or et."Narration" ilike '%cheq%')
	and et."Narration" not ilike '%CREDIT INTEREST CAPITALISED%'
order by et."Date" desc;


select
	*
from
	hdfc_transactions ht
where
	(ht."Narration" ilike '%cred%'
		or ht."Narration" ilike '%cheq%')
	and ht."Narration" not ilike '%credit interest%'
order by ht."Date" desc;


select
	*
from
	hdfc_credit_card hcc
where
	hcc."Date" between '2024-09-26' and '2024-10-25'
	and hcc.neucoins is null
order by
	hcc."Date" desc;



select
	*
from
	hdfc_credit_card hcc
where
	hcc."Debit / Credit" = 'cr' and hcc."Date" between '2024-04-10' and '2024-04-14';

select
	*
from
	sbi_credit_card scc
where
	scc."Type" = 'C' and scc."Date" between '2024-04-10' and '2024-04-14';


select
	*
from
	icici_credit_card icc
where
	icc."Type" = 'CR'
	and icc."Date" between '2024-04-10' and '2024-04-14';



select * from transactions t where t.tags ilike '%#adhocloan%';


select
	*
from
	transactions t
where t.tags ilike '%#Ramya%' or t.category = 'Ramya'
order by t.txn_date desc;



select
	*
from
	transactions t
where
	t.account in ('HDFC Credit Card', 'SBI Credit Card', 'ICICI Credit Card', 'Kotak Credit Card')
	and t.txn_date between '2025-02-26' and '2025-04-01'
	and t.category not in ('Food & Dining', 'Groceries', 'Fuel')
order by t.txn_amount desc;




select
	*
from
	hdfc_transactions ht
where
	ht."Date" between '2025-06-01' and '2025-06-30'
	and ht."Narration" ilike '%cheq digital%';



SELECT
    SUM(
        CASE 
            WHEN ht."Withdrawal Amt." IS NOT NULL THEN ht."Withdrawal Amt."
            ELSE ht."Deposit Amt." * -1
        END
    ) AS total
FROM
    hdfc_transactions ht
WHERE
    ht."Date" BETWEEN '2025-06-01' AND '2025-06-30'
    AND ht."Narration" ILIKE '%cheq digital%';





select
	sum(ht."Withdrawal Amt.")
from
	hdfc_transactions ht
where
	ht."Date" between '2025-04-01' and '2025-04-30'
	and ht."Narration" not ilike '%lokes%'
	and ht."Narration" not ilike '%sanap%'
	and ht."Narration" not ilike '%AMAZONPAYBALANCELOAD%'
	and ht."Narration" not ilike '%cheq digital%'
	and ht."Narration" not ilike '%rupeek%'
	and ht."Narration" not ilike '%RAZORPAY_OZOSTSBWL5TJ78_129237596%'
	and ht."Narration" not ilike '%KMBLDRAOPERATIONS%'
	and ht."Narration" not ilike '%LICHOUSINGFINANCELTD%'
	and ht."Narration" not ilike '%NPS TRUST%'
	and ht."Narration" not ilike '%dubai%'
	and ht."Narration" not ilike '%AMAZONPAYCCBILLPAYMENT%';





-- Cash txns that are not tagged

SELECT
    *
FROM
    transactions
WHERE
    account = 'Cash'
    AND txn_type = 'Debit'
    and category != 'Others'
    AND tags !~ '[0-9]'   -- exclude if tags contain any digit
ORDER BY
    txn_date DESC
LIMIT 100;


-- untracked cash

select
	*
from
	transactions
where
	category = 'Misc'
	and account = 'Cash'
	and tags ilike '%#Untracked%';



-- duplicate txns

select
	txn_amount,
	array_to_string(array_agg(txn_date), ','),
	array_to_string(array_agg(account), ','),
	array_to_string(array_agg(notes), ',')
from
	transactions
group by
	txn_amount
having
	count(*) > 1;



-- cash txns

select
	SUM(txn_amount),
	date_trunc('MONTH', txn_date)
from
	transactions
where
	account = 'Cash'
	and category != 'Others'
group by
	date_trunc('MONTH', txn_date)
order by
	2 desc;









