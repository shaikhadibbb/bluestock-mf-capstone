# Tableau Dashboard Build Guide (Mac Compatible)

Since Microsoft Power BI Desktop does not run natively on macOS, this guide provides a step-by-step layout configuration to build a professional, publication-quality dashboard in **Tableau Public** or **Tableau Desktop** (which run natively on Mac) using the processed CSV datasets in `data/processed/`.

---

## 1. Data Source Setup
1. Open Tableau and connect to the Text File: `data/processed/clean_fund_master.csv`.
2. Go to the Data Source tab and add connections to the following files by joining them on the Logical canvas:
   - **`clean_performance.csv`**: Join on `Amfi Code` = `Amfi Code` (Inner Join)
   - **`clean_transactions.csv`**: Join on `Amfi Code` = `Amfi Code` (Left Join)
   - **`clean_nav.csv`**: Join on `Amfi Code` = `Amfi Code` (Left Join)

---

## 2. Calculated Fields & Measures
Define the following calculated fields in the left-hand Data Pane:

1. **Composite Scorecard Score:**
   - **Name:** `Composite Score`
   - **Formula:** 
     ```tableau
     ([Return 3Yr Pct] * 0.3) + 
     ([Sharpe Ratio] * 5 * 0.25) + 
     ((100 + [Max Drawdown Pct]) * 0.2) + 
     ((2.5 - [Expense Ratio Pct]) * 10 * 0.15)
     ```
2. **Transaction Value in Crore:**
   - **Name:** `Amount (₹ Crore)`
   - **Formula:** `[Amount Inr] / 10000000`

---

## 3. Worksheet Configurations

### Sheet 1: Total AUM & AMC Rankings
- **Columns:** `Sum(Aum Crore)`
- **Rows:** `Fund House` (Sorted descending by `Aum Crore`)
- **Marks:** Color (Blue palette), Label (AUM in ₹ Cr)
- **Filters:** `Category`, `Plan`

### Sheet 2: Risk vs. Return Matrix (Scatter)
- **Columns:** `Std Dev Ann Pct` (Avg or dimension)
- **Rows:** `Return 3Yr Pct` (Avg or dimension)
- **Marks:** Shape (Circle), Color (`Category`), Label (`Scheme Name`), Size (`Aum Crore`)
- **Constant Lines:** Reference Line on X-Axis at `15%` (Avg Volatility), Reference Line on Y-Axis at `11.5%` (Avg Return).
- **Filters:** `Category`, `Plan`, `Fund House`

### Sheet 3: NAV vs. Benchmark Indexed Growth
- **Columns:** `Date` (Continuous Day)
- **Rows:** `NAV` (or indexed return measure)
- **Color:** `Scheme Name`
- **Filters:** `Date` (Range filter), `Scheme Name`

### Sheet 4: Transaction Value by State (Map)
- **Columns (Map longitude):** Generated Longitude
- **Rows (Map latitude):** Generated Latitude
- **Marks:** Detail (`State`), Color (`Amount (₹ Crore)`), Tooltip (`Amount (₹ Crore)`)
- **Filters:** `State` (Multi-select), `Transaction Type`

### Sheet 5: Investor Age Segment vs. Avg SIP
- **Columns:** `Age Group` (Sorted `18-25` to `56+`)
- **Rows:** `Average(Amount Inr)`
- **Marks:** Color (Red palette), Label (`Avg Amount Inr`)
- **Filters:** `Transaction Type` (Filtered to `SIP` only), `State`

---

## 4. Dashboard Assembly (4 Pages)

Create 4 Dashboards (size 1280x720) in your workbook tab:

### Page 1: Industry Overview
- **KPI Tiles:** Add text card KPI tiles for Total Industry AUM, Active Folios, and Scheme count.
- **Visuals:** Add *Total AUM & AMC Rankings* Sheet.
- **Interactive Slicers:** `Category` and `Plan` (set to "Apply to all worksheets using this data source").

### Page 2: Fund Performance & Scorecard
- **Visuals:** Add the *Risk vs. Return Matrix* (Scatter) on the left, and a Table Visual of the *Composite Scorecard* ranking on the right.
- **Interactive Slicers:** `Fund House`, `Category`, `Plan`, and `Date Range`.

### Page 3: Investor Analytics
- **Visuals:** Add *Transaction Value by State* (Map) on the left, and *Investor Age Segment vs. Avg SIP* on the right.
- **Interactive Slicers:** `State` (Dropdown) and `City Tier` (T30/B30).

### Page 4: SIP & Market Trends
- **Visuals:** Add a dual-axis chart comparing monthly aggregate SIP inflows against index level.
- **Interactive Slicers:** `Date Range`.
