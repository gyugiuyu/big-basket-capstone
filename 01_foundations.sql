-- Part 1, Task 3: Foundational queries
-- Database: bigbasket_capstone.db

-- 1. SELECT / WHERE — all orders placed by customers in Bengaluru
SELECT o.order_id, o.order_date, c.name, c.city, o.amount_inr
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE c.city = 'Bengaluru';

-- 2. DISTINCT — every distinct product category
SELECT DISTINCT category
FROM products;

-- 3. ORDER BY + LIMIT — the 5 highest-value orders by amount_inr
SELECT order_id, amount_inr, status
FROM orders
ORDER BY amount_inr DESC
LIMIT 5;

-- 4. Alias (AS) — renaming an aggregate/column in the output
SELECT COUNT(*) AS total_orders
FROM orders;

-- 5. IN — orders whose payment_mode is one of a 2-mode list
SELECT order_id, payment_mode, amount_inr
FROM orders
WHERE payment_mode IN ('UPI', 'Credit Card');

-- 6. BETWEEN — orders with amount_inr in the range 100 to 300 (inclusive)
SELECT order_id, amount_inr
FROM orders
WHERE amount_inr BETWEEN 100 AND 300;

-- 6b. NOT BETWEEN — orders with amount_inr outside that same range
SELECT order_id, amount_inr
FROM orders
WHERE amount_inr NOT BETWEEN 100 AND 300;

-- 7. IS NULL — orders with no rating recorded
-- (these are exactly the Cancelled/Pending orders, since only Delivered orders get rated)
SELECT order_id, status, rating
FROM orders
WHERE rating IS NULL;
