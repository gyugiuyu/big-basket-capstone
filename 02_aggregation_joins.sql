-- Part 1, Task 4: Aggregation, JOIN, and HAVING queries
-- Database: bigbasket_capstone.db

-- (a) INNER JOIN orders -> products, GROUP BY category, Delivered only,
--     with a HAVING filter on total_revenue > 10000
SELECT
    p.category,
    COUNT(*) AS order_count,
    SUM(o.amount_inr) AS total_revenue,
    AVG(o.amount_inr) AS avg_revenue
FROM orders o
INNER JOIN products p ON p.product_id = o.product_id
WHERE o.status = 'Delivered'
GROUP BY p.category
HAVING total_revenue > 10000
ORDER BY total_revenue DESC;

-- (b) LEFT JOIN products -> orders, GROUP BY product, counting orders per product.
--     COUNT(o.order_id) is used deliberately instead of COUNT(*): with a LEFT JOIN,
--     a product with zero matching orders still produces one output row whose order
--     columns are all NULL. COUNT(*) would count that NULL row as 1; COUNT(o.order_id)
--     correctly counts it as 0, since COUNT() of a column ignores NULLs.
-- Exactly one product (Premium Face Cream 50g) has zero orders and must appear
-- here with a count of 0 -- it was deliberately excluded from the popularity
-- weighting in generate_data.py.
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(o.order_id) AS total_orders
FROM products p
LEFT JOIN orders o ON o.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_orders ASC;
