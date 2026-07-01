# Bluestock Mutual Fund Analytics — Power BI Dashboard Specifications

This dashboard serves as the primary visualization interface for the Mutual Fund Analytics Capstone.

## Data Model Relationships
To load the data in Power BI:
1. Import all processed CSVs from `data/processed/` using the Text/CSV connector.
2. Define the following relationships in the Model View:
   - `dim_fund` [amfi_code] `1:N` `fact_nav` [amfi_code] (Single direction filter)
   - `dim_fund` [amfi_code] `1:N` `fact_transactions` [amfi_code] (Single direction filter)
   - `dim_fund` [amfi_code] `1:1` `fact_performance` [amfi_code] (Bidirectional filter)
   - `dim_fund` [amfi_code] `1:N` `fact_portfolio` [amfi_code] (Single direction filter)
   - `dim_date` [date] `1:N` `fact_nav` [nav_date] (Single direction filter)
   - `dim_date` [date] `1:N` `fact_transactions` [transaction_date] (Single direction filter)

---

## Page-by-Page Setup

### Page 1: Industry Overview
*   **KPI Cards:**
    *   *Total Industry AUM:* `SUM(fact_aum[aum_crore])` formatted in lakhs/crores.
    *   *Monthly Inflows:* `SUM(fact_sip_industry[sip_inflow_crore])` for the latest month (Dec 2025 = ₹31,002 Cr).
    *   *Total Folios:* `MAX(fact_sip_industry[active_sip_accounts_crore])` = 9.35 Crore.
    *   *Active Schemes:* `DISTINCTCOUNT(dim_fund[amfi_code])` = 40.
*   **Line Chart:**
    *   *X-Axis:* `fact_aum[date]`
    *   *Y-Axis:* `fact_aum[aum_lakh_crore]`
    *   *Series:* `fact_aum[fund_house]`
*   **Bar Chart:**
    *   *Axis:* `fact_aum[fund_house]`
    *   *Values:* `SUM(fact_aum[aum_lakh_crore])` (Filtered to date = Dec 31, 2025)
*   **Slicers (Interactive):**
    *   `dim_fund[fund_house]` (Dropdown list)
    *   `dim_fund[category]` (Zebra vertical tiles)

---

### Page 2: Fund Performance
*   **Scatter Plot (Risk vs Return):**
    *   *X-Axis:* `fact_performance[std_dev_ann_pct]`
    *   *Y-Axis:* `fact_performance[return_3yr_pct]`
    *   *Details:* `fact_performance[scheme_name]`
    *   *Bubble Size:* `fact_performance[aum_crore]`
*   **Line Chart (NAV vs Benchmark):**
    *   *X-Axis:* `fact_nav[nav_date]`
    *   *Y-Axis:* `fact_nav[nav]` (Or custom indexed return measure)
    *   *Benchmark Y-Axis:* `fact_benchmark_indices[close_value]`
*   **Table Visual (Fund Scorecard):**
    *   *Columns:* `fact_performance[amfi_code]`, `dim_fund[scheme_name]`, `dim_fund[category]`, `fact_performance[sharpe_ratio]`, `fact_performance[alpha]`, `fact_performance[composite_score]`
*   **Slicers (Interactive):**
    *   `dim_fund[fund_house]`
    *   `dim_fund[category]`
    *   `dim_fund[plan]` (Direct/Regular)

---

### Page 3: Investor Analytics
*   **Map / Horizontal Bar Visual:**
    *   *Location:* `fact_transactions[state]`
    *   *Tooltips / Values:* `SUM(fact_transactions[amount_inr])` (Formatted in ₹ Crores)
*   **Donut Chart (Transaction Type Split):**
    *   *Legend:* `fact_transactions[transaction_type]` (SIP / Lumpsum / Redemption)
    *   *Values:* `COUNT(fact_transactions[tx_id])`
*   **Column Chart (Age vs Average SIP):**
    *   *X-Axis:* `fact_transactions[age_group]`
    *   *Y-Axis:* `AVERAGE(fact_transactions[amount_inr])` (Filtered to Type = 'SIP')
*   **Line Chart (Monthly Transaction Volume):**
    *   *X-Axis:* `fact_transactions[transaction_date]` (Grouped by Month)
    *   *Y-Axis:* `COUNT(fact_transactions[tx_id])`
*   **Slicers (Interactive):**
    *   `fact_transactions[state]`
    *   `fact_transactions[age_group]`
    *   `fact_transactions[city_tier]` (T30/B30)

---

### Page 4: SIP & Market Trends
*   **Dual-Axis Chart (SIP Inflows vs NIFTY 50):**
    *   *X-Axis:* `fact_sip_industry[month]`
    *   *Column Values:* `fact_sip_industry[sip_inflow_crore]` (Left Y-Axis)
    *   *Line Values:* `AVERAGE(fact_benchmark_indices[close_value])` (Filtered to Index = 'Nifty50', Right Y-Axis)
*   **Matrix/Heatmap Visual:**
    *   *Rows:* `fact_sip_industry[month]` (Year-Month)
    *   *Columns:* `fact_category_inflows[category]`
    *   *Values:* `SUM(fact_category_inflows[net_inflow_crore])` (Zebra or conditional colors applied)
*   **Bar Chart (Top 5 Categories Inflow FY25):**
    *   *Axis:* `fact_category_inflows[category]`
    *   *Values:* `SUM(fact_category_inflows[net_inflow_crore])` (Filtered to Date Range = FY 2024-25)
*   **Slicers (Interactive):**
    *   `dim_date[year]`
    *   `dim_fund[category]`
