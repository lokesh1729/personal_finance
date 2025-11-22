-- get the table

select * from metabase_table where db_id = 2 and active = true and name = 'mutual_funds';

-- get the questions
select * from report_card where table_id = 27 or dataset_query ilike '%niyomoney_transactions%';


-- questions/cards that are not part of any dashboard
SELECT rc.id AS question_id, rc.name AS question_name, rc.description AS question_description
FROM report_card rc
LEFT JOIN report_dashboardcard dc ON rc.id = dc.card_id
WHERE rc.archived is false and rc.name not in ('Categories', 'Transactions with widgets') and dc.card_id IS NULL
ORDER BY rc.name;




SELECT id, dashboard_id, name 
FROM dashboard_tab 
WHERE dashboard_id = 26 AND name = 'Dropshipping';



UPDATE report_dashboardcard 
SET 
    dashboard_id = 26,
    dashboard_tab_id = (
        SELECT id 
        FROM dashboard_tab 
        WHERE dashboard_id = 26 AND name = 'Dropshipping' 
        LIMIT 1
    )
WHERE dashboard_id = 8;





