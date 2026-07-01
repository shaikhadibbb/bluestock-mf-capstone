# Data Dictionary: Mutual Fund Analytics Platform

This document describes the schema, columns, data types, and constraints for the SQLite relational database (`bluestock_mf.db`) designed for the Mutual Fund Analytics Capstone.

---

## 1. Dimension Tables

### `dim_fund`
Stores metadata and scheme-level properties for all 40 mutual fund schemes.
- **Primary Key:** `amfi_code`

| Column Name | Data Type | Constraints | Description |
|:---|:---|:---|:---|
| `amfi_code` | INTEGER | PRIMARY KEY | Unique AMFI code representing the mutual fund scheme. |
| `fund_house` | TEXT | NOT NULL | Asset Management Company (AMC) name. |
| `scheme_name` | TEXT | NOT NULL | Full name of the mutual fund scheme. |
| `category` | TEXT | NOT NULL | Asset class category (e.g. Equity, Debt, Hybrid). |
| `sub_category` | TEXT | | Sub-classification (e.g. Large Cap, Small Cap, Gilt, Liquid). |
| `plan` | TEXT | NOT NULL | Plan distribution type (Regular or Direct). |
| `launch_date` | TEXT | | Scheme inception date (YYYY-MM-DD). |
| `benchmark` | TEXT | |Mapped benchmark index name (e.g. NIFTY 100 TRI). |
| `expense_ratio_pct` | REAL | | Annual management cost as a percentage of AUM. |
| `exit_load_pct` | REAL | | Fee charged on early redemption. |
| `min_sip_amount` | INTEGER | | Minimum amount required for a monthly SIP. |
| `min_lumpsum_amount`| INTEGER | | Minimum amount required for a single investment. |
| `fund_manager` | TEXT | | Lead fund manager name. |
| `risk_category` | TEXT | | Risk rating as per AMFI (e.g. Very High, Moderate, Low). |
| `sebi_category_code`| TEXT | | SEBI scheme classification code. |

### `dim_date`
Calendar dimension used to facilitate time-series grouping and date filters.
- **Primary Key:** `date`

| Column Name | Data Type | Constraints | Description |
|:---|:---|:---|:---|
| `date` | TEXT | PRIMARY KEY | Date key formatted as YYYY-MM-DD. |
| `year` | INTEGER | NOT NULL | Calendar year. |
| `month` | INTEGER | NOT NULL | Month number (1–12). |
| `day` | INTEGER | NOT NULL | Day of the month (1–31). |
| `quarter` | INTEGER | NOT NULL | Calendar quarter (1–4). |
| `day_of_week` | INTEGER | NOT NULL | Day index (0 = Monday, 6 = Sunday). |
| `is_weekend` | INTEGER | NOT NULL | Boolean flag (1 = Weekend, 0 = Weekday). |

---

## 2. Fact Tables

### `fact_nav`
Stores historical daily net asset value (NAV) prices.
- **Composite Primary Key:** (`amfi_code`, `nav_date`)
- **Foreign Keys:** 
  - `amfi_code` references `dim_fund(amfi_code)`
  - `nav_date` references `dim_date(date)`

| Column Name | Data Type | Constraints | Description |
|:---|:---|:---|:---|
| `amfi_code` | INTEGER | REFERENCES dim_fund | Mapped scheme AMFI code. |
| `nav_date` | TEXT | REFERENCES dim_date | Date of the NAV record. |
| `nav` | REAL | NOT NULL | Daily Net Asset Value (NAV) price. |

### `fact_transactions`
Stores simulated retail investor transactions.
- **Primary Key:** `tx_id`
- **Foreign Keys:**
  - `amfi_code` references `dim_fund(amfi_code)`
  - `transaction_date` references `dim_date(date)`

| Column Name | Data Type | Constraints | Description |
|:---|:---|:---|:---|
| `tx_id` | TEXT | PRIMARY KEY | Unique transaction ID. |
| `investor_id` | TEXT | NOT NULL | Unique retail investor identifier. |
| `amfi_code` | INTEGER | REFERENCES dim_fund | Mapped scheme AMFI code. |
| `transaction_date` | TEXT | REFERENCES dim_date | Date transaction occurred. |
| `transaction_type` | TEXT | NOT NULL | Type of transaction (SIP, Lumpsum, Redemption). |
| `amount_inr` | REAL | NOT NULL | Transaction value in Indian Rupees. |
| `units` | REAL | NOT NULL | Mutual fund units bought/sold. |
| `age` | INTEGER | | Investor age. |
| `gender` | TEXT | | Investor gender. |
| `city` | TEXT | | Investor residential city. |
| `state` | TEXT | | Investor residential state. |
| `city_tier` | TEXT | | Geographic tier (T30 = Top 30 Cities, B30 = Beyond 30). |
| `payment_mode` | TEXT | | Payment channel (UPI, Net Banking, Mandate). |
| `kyc_status` | TEXT | | Investor KYC verification status. |

### `fact_performance`
Stores normalized historical risk and return ratios.
- **Primary Key:** `amfi_code`
- **Foreign Keys:**
  - `amfi_code` references `dim_fund(amfi_code)`

| Column Name | Data Type | Constraints | Description |
|:---|:---|:---|:---|
| `amfi_code` | INTEGER | PRIMARY KEY, REFERENCES dim_fund | Mapped scheme AMFI code. |
| `return_1yr_pct` | REAL | | Annual return over the past 1 year (%). |
| `return_3yr_pct` | REAL | | Annualized return over the past 3 years (%). |
| `return_5yr_pct` | REAL | | Annualized return over the past 5 years (%). |
| `benchmark_3yr_pct` | REAL | | Benchmark return over the past 3 years (%). |
| `alpha` | REAL | | Jensen's Alpha relative to the benchmark (%). |
| `beta` | REAL | | Systematic market risk factor (Beta). |
| `sharpe_ratio` | REAL | | Sharpe risk-adjusted return ratio. |
| `sortino_ratio` | REAL | | Sortino downside risk-adjusted return ratio. |
| `std_dev_ann_pct` | REAL | | Annualized daily volatility (%). |
| `max_drawdown_pct` | REAL | | Maximum peak-to-trough loss percentage (%). |
| `aum_crore` | REAL | | Total Assets Under Management in ₹ Crore. |
| `expense_ratio_pct` | REAL | | Fund expense ratio percentage (%). |
| `morningstar_rating`| INTEGER | | Morningstar quantitative rating (1–5). |
| `risk_grade` | TEXT | | Qualitative risk profile description. |

### `fact_portfolio`
Stores top stock holdings for each equity fund.
- **Composite Primary Key:** (`amfi_code`, `stock_symbol`)
- **Foreign Keys:**
  - `amfi_code` references `dim_fund(amfi_code)`

| Column Name | Data Type | Constraints | Description |
|:---|:---|:---|:---|
| `amfi_code` | INTEGER | REFERENCES dim_fund | Mapped scheme AMFI code. |
| `stock_name` | TEXT | NOT NULL | Stock company name. |
| `stock_symbol` | TEXT | NOT NULL | Exchange ticker symbol. |
| `sector` | TEXT | | Economic sector (e.g. Financial Services, IT). |
| `weight_pct` | REAL | NOT NULL | Percentage allocation in the fund portfolio. |
| `shares_held` | INTEGER | | Number of shares held in the portfolio. |
| `market_value_crore`| REAL | | Total holding value in ₹ Crore. |

### `fact_aum`
Stores assets under management growth for the top 10 AMCs.
- **Composite Primary Key:** (`fund_house`, `date`)
- **Foreign Keys:**
  - `date` references `dim_date(date)`

| Column Name | Data Type | Constraints | Description |
|:---|:---|:---|:---|
| `fund_house` | TEXT | NOT NULL | AMC name. |
| `date` | TEXT | REFERENCES dim_date | Date of AUM reporting (Quarter-end). |
| `aum_lakh_crore` | REAL | | AUM value in ₹ Lakh Crore. |
| `aum_crore` | REAL | | AUM value in ₹ Crore. |

### `fact_sip_industry`
Stores macro industry-level monthly SIP inflows and active accounts.
- **Primary Key:** `month`
- **Foreign Keys:**
  - `month` references `dim_date(date)` (First day of month)

| Column Name | Data Type | Constraints | Description |
|:---|:---|:---|:---|
| `month` | TEXT | PRIMARY KEY | Month identifier formatted as YYYY-MM. |
| `sip_inflow_crore` | REAL | | Total industry SIP inflows in ₹ Crore. |
| `active_sip_accounts_crore`| REAL | | Active SIP accounts nationwide in Crores. |
| `new_sip_registered_lakh`| REAL | | New SIP registrations in Lakhs. |
| `yoy_growth_pct` | REAL | | Year-over-Year inflow growth rate (%). |
