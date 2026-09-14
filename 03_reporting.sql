-- Part 1, Task 5: CASE WHEN tiering, date-based report, derived fields
-- Database: bigbasket_capstone.db

-- (a) Tier every product by its total Delivered revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.amount_inr) AS total_revenue,
    CASE
        WHEN SUM(o.amount_inr) >= 3000 THEN 'High'
        WHEN SUM(o.amount_inr) >= 1000 THEN 'Medium'
        ELSE 'Low'
    END AS revenue_tier
FROM orders o
INNER JOIN products p ON p.product_id = o.product_id
WHERE o.status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC;

-- (b) Monthly-by-category business report (Delivered orders only)
-- This exact query's full result set is exported, unmodified, to
-- monthly_category_revenue.csv -- the fixed input for Parts 2 and 3.
SELECT
    p.category,
    strftime('%Y-%m', o.order_date) AS month,
    COUNT(*) AS order_count,
    SUM(o.amount_inr) AS total_revenue,
    AVG(o.amount_inr) AS avg_revenue
FROM orders o
INNER JOIN products p ON p.product_id = o.product_id
WHERE o.status = 'Delivered'
GROUP BY p.category, strftime('%Y-%m', o.order_date)
ORDER BY p.category, month;

-- (c) Derived fields: variance and percentage_variance against category_targets
-- SQLite integer-division note: total_revenue and target_revenue_inr are both
-- INTEGER columns. Writing the percentage formula as
--   (total_revenue - target_revenue_inr) / target_revenue_inr
-- alone truncates to an integer (almost always 0) *before* the * 100 ever runs.
-- The formula below multiplies by 100.0 first (a REAL literal), which forces
-- floating-point division for the whole expression, so the true percentage
-- comes through instead of a truncated 0.
SELECT
    cat_rev.category,
    cat_rev.total_revenue,
    ct.target_revenue_inr,
    (ct.target_revenue_inr - cat_rev.total_revenue) AS variance,
    ((cat_rev.total_revenue - ct.target_revenue_inr) * 100.0) / ct.target_revenue_inr AS percentage_variance,
    CASE
        WHEN cat_rev.total_revenue >= ct.target_revenue_inr THEN 'Above Target'
        WHEN ((ct.target_revenue_inr - cat_rev.total_revenue) * 100.0) / ct.target_revenue_inr <= 15 THEN 'Below Target - Watch'
        ELSE 'Below Target - Critical'
    END AS status_tag
FROM (
    SELECT p.category, SUM(o.amount_inr) AS total_revenue
    FROM orders o
    INNER JOIN products p ON p.product_id = o.product_id
    WHERE o.status = 'Delivered'
    GROUP BY p.category
) cat_rev
INNER JOIN category_targets ct ON ct.category = cat_rev.category
ORDER BY percentage_variance ASC;
