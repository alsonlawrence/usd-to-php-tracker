-- ============================================================
-- OFW FOREX TRACKER - DATABASE SETUP
-- ============================================================
-- WHAT THIS IS:
--   Creates a simple table to store bank forex rates.
--   Each row = one bank's buying and selling rate for that day.
--
-- HOW TO USE:
--   1. Open MySQL Workbench
--   2. Paste this file into the query editor
--   3. Click ⚡ to run
--   4. Run this ONCE only
-- ============================================================

USE defaultdb;

CREATE TABLE IF NOT EXISTS ofw_bank_rates (

    id               INT AUTO_INCREMENT PRIMARY KEY,

    -- Bank name (e.g. "BPI", "China Bank")
    bank_name        VARCHAR(50),

    -- Buying rate: PHP you RECEIVE per $1 (OFW families want this HIGH)
    usd_buying_rate  DECIMAL(10, 4),

    -- Selling rate: PHP you PAY to GET $1
    usd_selling_rate DECIMAL(10, 4),

    -- Date this was scraped
    date_recorded    DATE,

    -- Exact time of scrape
    scraped_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- ============================================================
-- QUICK CHECK:
-- SELECT * FROM ofw_bank_rates ORDER BY date_recorded DESC;
-- ============================================================
