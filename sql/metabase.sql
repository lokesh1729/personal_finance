-- get the table

select * from metabase_table where db_id = 2 and active = true and name = 'mutual_funds';

-- get the questions
select * from report_card where table_id = 27 or dataset_query ilike '%niyomoney_transactions%';