select DISTINCT account from transactions;

select count(*) from transactions where account = 'Others';

select count(*) from transactions t where t.txn_date between '2018-01-01' and '2025-10-30';

select * from transactions;

select * from public.transactions t where t.txn_amount = 5142.85;



SELECT 
    COUNT(*), 
    DATE_TRUNC('month', t.txn_date) AS "month"
FROM transactions t 
GROUP BY DATE_TRUNC('month', t.txn_date)
ORDER BY 2 DESC;