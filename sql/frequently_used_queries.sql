
select * from transactions where (tags ilike '%#' || 2407 || '%') or (id = 2407) order by txn_date asc;

select * from transactions where txn_date between '2024-02-01' and '2024-03-31';

select * from transactions where account = 'Cash' order by txn_date desc;

select * from transactions order by id desc limit 10;

select * from walnut_transactions where tags ilike '%investmentredemption%';

select * from transactions where tags ilike '%investmentredemption%' order by txn_date asc limit 10;

