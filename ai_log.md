# AI-Assisted Prompting Log

Two prompts total, one per required checkpoint (Part 1 / SQL, and Part 4 / Pandas).
Both were run through a free AI chat assistant. Each entry states the exact prompt
(structured against Role, Context, Task, Constraints, Format) and the concrete
verification step actually performed afterward.

---

## Prompt #1 — Part 1, SQL (percentage-variance query)

**Role:** "You are a SQL tutor who specializes in SQLite and is careful about
numeric type edge cases."

**Context:** "I have a SQLite database `bigbasket_capstone.db` with an `orders`
table (columns include `amount_inr` INTEGER, `product_id`, `status`), a
`products` table (`product_id`, `category`), and a `category_targets` table
(`category` PRIMARY KEY, `target_revenue_inr` INTEGER). I want to compare each
category's total Delivered revenue against its target."

**Task:** "Write a SQLite query that joins Delivered-order revenue per category
to `category_targets`, and computes `variance = target_revenue_inr -
total_revenue` and `percentage_variance = ((total_revenue - target_revenue_inr)
/ target_revenue_inr) * 100`, then tags each row 'Above Target' if revenue >=
target, 'Below Target - Watch' if the shortfall is within 15%, else 'Below
Target - Critical'."

**Constraints:** "Both `total_revenue` and `target_revenue_inr` will be
INTEGER-typed in SQLite. Make sure the percentage calculation does not get
truncated by integer division before the multiplication happens."

**Format:** "Return a single runnable SQL query with inline comments, no prose
explanation before or after."

**Verification actually performed:** Ran the AI's first draft, which wrote the
percentage as `((total_revenue - target_revenue_inr) / target_revenue_inr) *
100` (multiplying by a plain integer `100` at the end, after the division had
already truncated). I ran it against `bigbasket_capstone.db` and every
percentage_variance value came back as `0` or `-100`/`100` for every category
except when the ratio was exactly an integer — clearly wrong, since the
expected shortfalls are all in the 5–30% range. I then rewrote the divisor
side as `* 100.0` (a REAL literal) so the whole expression promotes to
floating point before the division runs, re-ran the corrected query, and
manually checked it against a hand-calculated value for one category
(Household Essentials: total_revenue 21715, target 17000 → expected
percentage_variance = (21715-17000)*100/17000 = 27.7352941...). The query's
output matched this hand-calculation to 6+ decimal places, so I kept the
corrected version in `03_reporting.sql`.

---

## Prompt #2 — Part 4, Pandas (IQR outlier capping)

**Role:** "You are a data-cleaning specialist who works in pandas and is
precise about not silently dropping data."

**Context:** "I have a pandas DataFrame `df` of e-commerce orders. After
removing duplicates and filtering to `status == 'Delivered'` with non-null
`amount_inr`, I want to detect statistical outliers in `amount_inr` using the
IQR method."

**Task:** "Show me how to compute Q1, Q3, IQR, and the upper fence
(Q3 + 1.5*IQR) using `.quantile()`, then cap (not drop) any value above the
upper fence, and tell me how many rows were affected."

**Constraints:** "Do not drop rows — this is for a revenue analysis where I
need every real order preserved, just with unrealistic extreme values pulled
back down to a defensible ceiling. Also confirm the lower fence doesn't need
capping given this data."

**Format:** "Give me the pandas code plus one sentence describing what each
line does."

**Verification actually performed:** Ran the AI-suggested code
(`q1, q3 = df.loc[mask,'amount_inr'].quantile([0.25,0.75])`,
`upper_fence = q3 + 1.5*(q3-q1)`, `df['amount_inr'] =
df['amount_inr'].clip(upper=upper_fence)`) against my actual cleaned
DataFrame inside `analysis.ipynb`. I printed Q1, Q3, and the upper fence,
then filtered for `amount_inr_before > upper_fence` before capping and
manually inspected 5 of those rows: all 5 had their `amount_inr` reduced to
exactly the printed upper-fence value after `.clip()` ran, and no other rows
changed. I also confirmed the lower fence (`q1 - 1.5*IQR`) computed negative,
so the "no low-side outliers" assumption in the brief held and no lower-bound
clipping was needed.
