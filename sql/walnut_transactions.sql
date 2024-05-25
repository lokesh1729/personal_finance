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

ALTER TABLE walnut_transactions ALTER COLUMN amount TYPE FLOAT USING amount::double precision;

SELECT * FROM walnut_transactions WHERE account = 'Flipkart Pay Later';

SELECT * FROM walnut_transactions WHERE tags ilike '%itr%' or notes ilike '%itr%' ORDER BY txn_date;

SELECT * FROM walnut_transactions WHERE tags ilike '%fiver%' or notes ilike '%fiver%';

UPDATE walnut_transactions SET category = 'SHOPPING' WHERE category = 'UNKNOWN';

