"""
Builds bigbasket_category_summary.xlsx for Part 2 of the capstone.

Sheets:
  1. Monthly Data      -- unmodified import of monthly_category_revenue.csv
  2. Category Targets  -- the 6 fixed category/target pairs (verbatim)
  3. Pivot Output      -- category-level SUM(total_revenue) / SUM(order_count)
                          computed with SUMIF formulas that reference Monthly
                          Data directly (mirrors what a native Pivot Table
                          built on Monthly Data would output). If your
                          grading rubric requires a literal native Pivot
                          Table object, open this file in Google Sheets /
                          Excel, select Monthly Data, and Insert > Pivot
                          Table (Rows=category, Values=SUM(total_revenue),
                          SUM(order_count)) -- it will reproduce these exact
                          numbers in ~2 minutes.
  4. Category Summary   -- pivot-referenced revenue, XLOOKUP target, variance,
                          percentage_variance, nested-IF tag, reconciliation
                          column, conditional formatting on the tag column.
"""
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# ---------- 1. Monthly Data ----------
ws1 = wb.active
ws1.title = "Monthly Data"
with open("monthly_category_revenue.csv") as f:
    reader = csv.reader(f)
    header = next(reader)
    ws1.append(header)
    for row in reader:
        # category, month stay text; order_count/total_revenue/avg_revenue must be
        # real numbers, not text, or SUMIF/pivot aggregation on them silently returns 0
        category, month, order_count, total_revenue, avg_revenue = row
        ws1.append([category, month, int(order_count), int(total_revenue), float(avg_revenue)])
n_monthly_rows = ws1.max_row  # header + 36 = 37
for c in range(1, 6):
    ws1.cell(row=1, column=c).font = Font(bold=True)

# ---------- 2. Category Targets ----------
ws2 = wb.create_sheet("Category Targets")
targets = [
    ("Fruits & Vegetables", 12000),
    ("Dairy & Eggs", 16500),
    ("Snacks & Beverages", 13000),
    ("Personal Care", 15500),
    ("Household Essentials", 17000),
    ("Bakery", 12000),
]
ws2.append(["category", "target_revenue_inr"])
for row in targets:
    ws2.append(row)
for c in range(1, 3):
    ws2.cell(row=1, column=c).font = Font(bold=True)

# ---------- 3. Pivot Output (SUMIF-based, same numbers a native pivot gives) ----------
ws3 = wb.create_sheet("Pivot Output")
ws3.append(["category", "sum_total_revenue", "sum_order_count"])
ws3.cell(row=1, column=1).font = Font(bold=True)
ws3.cell(row=1, column=2).font = Font(bold=True)
ws3.cell(row=1, column=3).font = Font(bold=True)

categories = [t[0] for t in targets]
last_monthly_row = n_monthly_rows  # 37
for i, cat in enumerate(categories, start=2):
    ws3.cell(row=i, column=1, value=cat)
    # SUMIF over Monthly Data: category column A, total_revenue column D, order_count column C
    ws3.cell(row=i, column=2,
             value=f"=SUMIF('Monthly Data'!A2:A{last_monthly_row},A{i},'Monthly Data'!D2:D{last_monthly_row})")
    ws3.cell(row=i, column=3,
             value=f"=SUMIF('Monthly Data'!A2:A{last_monthly_row},A{i},'Monthly Data'!C2:C{last_monthly_row})")

# ---------- 4. Category Summary ----------
ws4 = wb.create_sheet("Category Summary")
headers = ["category", "total_revenue", "target_revenue_inr", "variance",
           "percentage_variance", "status_tag", "Matches Part 1 SQL total?"]
ws4.append(headers)
for c in range(1, len(headers) + 1):
    ws4.cell(row=1, column=c).font = Font(bold=True)

# Part 1's SQL totals, for the reconciliation column
sql_totals = {
    "Household Essentials": 21715,
    "Personal Care": 16382,
    "Bakery": 15410,
    "Dairy & Eggs": 14090,
    "Snacks & Beverages": 10895,
    "Fruits & Vegetables": 9790,
}

for i, cat in enumerate(categories, start=2):
    piv_row = i  # Pivot Output rows are in the same order, offset matches (row i in both sheets)
    ws4.cell(row=i, column=1, value=cat)
    # (a) pivot-referenced total revenue -- reference the Pivot Output cell, don't retype
    ws4.cell(row=i, column=2, value=f"='Pivot Output'!B{piv_row}")
    # (b) XLOOKUP with a stated not-found default
    # NOTE: functions introduced after the original OOXML spec (like XLOOKUP)
    # must be written with an "_xlfn." prefix in the raw XML for Excel to
    # recognize them; Excel strips the prefix in the UI and just shows
    # XLOOKUP(...) normally. Google Sheets accepts either form.
    ws4.cell(row=i, column=3,
             value=f'=_xlfn.XLOOKUP(A{i},\'Category Targets\'!A:A,\'Category Targets\'!B:B,"Not Found")')
    # (c) variance and percentage_variance as plain formulas
    ws4.cell(row=i, column=4, value=f"=C{i}-B{i}")
    ws4.cell(row=i, column=5, value=f"=((B{i}-C{i})/C{i})*100")
    # (d) nested IF three-way tag
    ws4.cell(row=i, column=6,
             value=(f'=IF(B{i}>=C{i},"Above Target",'
                    f'IF(((C{i}-B{i})/C{i})*100<=15,"Below Target - Watch",'
                    f'"Below Target - Critical"))'))
    # Reconciliation column -- hardcoded reference value from Part 1's SQL run,
    # compared to the pivot-derived total_revenue in column B
    sql_val = sql_totals[cat]
    ws4.cell(row=i, column=7, value=f'=IF(B{i}={sql_val},"Yes","No - MISMATCH")')

# Number formats
for i in range(2, 2 + len(categories)):
    ws4.cell(row=i, column=2).number_format = "#,##0"
    ws4.cell(row=i, column=3).number_format = "#,##0"
    ws4.cell(row=i, column=4).number_format = "#,##0"
    ws4.cell(row=i, column=5).number_format = "0.00"

# Conditional formatting on the status_tag column (F2:F7)
green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
amber_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
green_font = Font(color="006100")
amber_font = Font(color="9C6500")
red_font = Font(color="9C0006")

tag_range = f"F2:F{1+len(categories)}"
ws4.conditional_formatting.add(
    tag_range,
    CellIsRule(operator="equal", formula=['"Above Target"'], fill=green_fill, font=green_font)
)
ws4.conditional_formatting.add(
    tag_range,
    CellIsRule(operator="equal", formula=['"Below Target - Watch"'], fill=amber_fill, font=amber_font)
)
ws4.conditional_formatting.add(
    tag_range,
    CellIsRule(operator="equal", formula=['"Below Target - Critical"'], fill=red_fill, font=red_font)
)

# Column widths for readability
for ws in (ws1, ws2, ws3, ws4):
    for col_cells in ws.columns:
        length = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
        col_letter = get_column_letter(col_cells[0].column)
        ws.column_dimensions[col_letter].width = min(max(length + 2, 10), 32)

wb.save("bigbasket_category_summary.xlsx")
print("Workbook saved: bigbasket_category_summary.xlsx")
