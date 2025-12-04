-- ATM Withdrawal Tagging Updates
-- Date Range: 2025-04-01 to 2025-11-30
-- Tolerance: ±₹100.0
-- Generated: 2025-12-03T09:43:41.699283

-- ATM #9927# (₹13042) → ₹13041 (shortfall: ₹1)
UPDATE transactions SET tags = COALESCE(tags, '') || '#9927#' 
WHERE id IN (10367);
