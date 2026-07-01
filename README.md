# Adib's Bluestock Mutual Fund Capstone — Project log & Codebase

Hi! I'm Adib Azam Shaikh, data engineering intern at Bluestock Fintech. This is my 7-day capstone project. 
Honestly, this was a massive roller coaster. Getting the math right on the metrics took me forever, and ReportLab kept throwing random formatting errors that drove me crazy. 
Below is my day-by-day progress, how to run the pipeline, and the things that kept breaking during the week. 

> [!NOTE]
> Due to macOS incompatibility with Power BI Desktop, the primary interactive dashboard is implemented in **Tableau Public** ([dashboard/bluestock_mf_dashboard.twbx](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/dashboard/bluestock_mf_dashboard.twbx)) containing all 4 core pages. A web-based **Streamlit** bonus deployment is also provided (run `streamlit run dashboard/app.py` locally). Detailed specifications for Power BI are preserved in [README_PowerBI.md](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/dashboard/README_PowerBI.md).

## Bugs I Found & Fixed (Critical Metrics & DB)
*   **Sortino Formula Bug:** The initial formula was dividing by the count of negative days and squaring raw returns. I fixed it by calculating excess returns ($R_p - R_f$), squaring the downside, and dividing by the *total* number of periods $N$ to get the proper downside semi-deviation.
*   **Jensen's Alpha Regression Bias:** The old code regressed raw fund returns on raw benchmark returns. This was introducing a massive beta bias. I corrected it to regress daily excess fund returns on excess benchmark returns.
*   **Database 3NF Normalization:** The original performance table (`fact_performance`) was not normalized and stored text fields like fund name and category. I stripped these out and refactored all database queries to use `JOIN`s on `dim_fund` on the `amfi_code` key.

## Things I Googled
*   How to do a pandas groupby + resample on multi-index datetime: [StackOverflow Link](https://stackoverflow.com/questions/15799162/resampling-within-a-pandas-groupby)
*   reportlab table cell text wrapping
*   Statsmodels vs Scipy linregress for CAPM Alpha

## Day-by-Day Progress Log
1. **Set up a virtual environment and install dependencies:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Data Ingestion ETL:**
   ```bash
   python scripts/data_ingestion.py
   ```

3. **Fetch Live NAV data:**
   ```bash
   python scripts/live_nav_fetch.py
   ```

## Project Structure
- `data/raw/` — Original 10 AMFI datasets + 6 live NAV CSVs
- `data/processed/` — Cleaned data (Day 2+)
- `notebooks/` — Jupyter EDA and analytics notebooks
- `scripts/` — Python ETL and analytics scripts
- `sql/` — SQLite schema + analytical queries
- `dashboard/` — Power BI file
- `reports/` — Final PDF report and presentation

## Data Sources
AMFI India · mfapi.in · NSE India · BSE India

## Day-by-Day Progress
- [x] Day 1: Data ingestion + validation
- [x] Day 2: Data cleaning + SQLite schema
- [x] Day 3: EDA + 15 charts
- [x] Day 4: Performance metrics (Sharpe, Alpha, Beta, VaR)
- [x] Day 5: Interactive Streamlit dashboard
- [x] Day 6: Advanced analytics
- [x] Day 7: Final report + deployment

## Day 2: Data Cleaning + SQLite Database
**Status:** Complete

### Cleaning Summary
- `clean_nav.csv`: 46,000+ rows, forward-filled weekend gaps, 0 anomalies
- `clean_transactions.csv`: 32,778 rows, all amounts valid (₹400–₹5,97,498), 92% KYC Verified
- `clean_performance.csv`: 40 rows, Sharpe range 0.80–7.68, 0 negative values
- `clean_sip_inflows.csv`: 48 rows, 12 null yoy_growth_pct values backfilled via computation
- All 10 datasets cleaned and saved to `data/processed/`

### Database
- Engine: SQLite3 via SQLAlchemy
- File: `data/db/bluestock_mf.db` (gitignored)
- Schema: 8-table star schema (2 dimensions + 6 fact tables)
- Indexes: 6 performance indexes on date, amfi_code, investor_id, state

### Running Day 2
```bash
python scripts/clean_data.py       # clean all 10 datasets
python scripts/load_database.py    # build SQLite DB and load all tables
python scripts/run_queries.py      # run analytical queries and format report
```

## Day 3: Exploratory Data Analysis (EDA)
**Status:** Complete

### EDA Summary
- **Jupyter Notebook**: [03_eda_analysis.ipynb](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/notebooks/03_eda_analysis.ipynb) (Fully executed with 15 charts and precursor returns statistics).
- **Publication Charts**: 15 distinct PNG visualizations saved under `reports/charts/`.
- **Chart Catalog**: Detailed descriptions and insights compiled in [reports/eda_chart_index.md](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/reports/eda_chart_index.md).
- **Standalone Runner**: [scripts/generate_eda_charts.py](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/scripts/generate_eda_charts.py) exports all charts directly from command line.

### Running Day 3
```bash
# Install kaleido dependency for Plotly static image export
pip install kaleido

# Programmatically generate and save all 15 PNG charts
python scripts/generate_eda_charts.py
```

## Day 4: Fund Performance Analytics
**Status:** Complete

### Metrics Computed
- **CAGR**: Calculated full-period CAGR, 1-year CAGR (last 252 trading days), and 3-year CAGR (last 756 trading days) from raw NAV history.
- **Sharpe Ratio**: Calculated full-period and 1-year Sharpe ratios against a risk-free rate proxy of 6.50% p.a.
- **Sortino Ratio**: Computed using downside deviation of negative daily returns below risk-free daily rate.
- **Alpha & Beta**: Modeled OLS linear regressions of daily returns against mapped benchmark index returns.
- **Maximum Drawdown**: Computed peak-to-trough drawdowns, dates, and recovery durations.
- **Value at Risk (VaR) & Expected Shortfall (CVaR)**: Derived historical 95% confidence VaR and CVaR daily loss thresholds.
- **Fund Scorecard**: Ranked all 40 funds using a weighted multi-dimensional rank algorithm (30% Return, 25% Sharpe, 20% Alpha, 15% Expense, 10% Drawdown).

### Deliverables
- **Jupyter Notebook**: [04_performance_analytics.ipynb](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/notebooks/04_performance_analytics.ipynb) (Fully executed with cells for all tasks).
- **Standalone Runner**: [scripts/compute_metrics.py](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/scripts/compute_metrics.py) reproduces calculations and saves all CSV outputs and plots.
- **Visualizations**: Saved 3 charts (`chart_16`, `chart_17`, and `chart_18`) to `reports/charts/`.
- **Output CSVs**: Exported 8 performance report CSVs to `data/processed/`.

### Running Day 4
```bash
# Execute standalone script to calculate metrics and export charts
python scripts/compute_metrics.py
```

## Day 5: Interactive Streamlit Dashboard
**Status:** Complete

### Dashboard Architecture
Built an interactive 4-page Streamlit dashboard `dashboard/app.py` with custom CSS, dark-theme styles, cached data loading (`@st.cache_data`), and dynamic filtering sidebar:
* **Industry Overview**: Visualizes total industry AUM, folio growth (total vs. equity), monthly SIP inflow milestones (ATH ₹31,002 Cr), active SIP accounts, and AMC rankings.
* **Fund Performance**: Interactive risk-return bubble scatter, NAV selector indexed to 100 vs. NIFTY 100, **Fund Comparison Tool** (overlaying 2-4 selected funds), and interactive scorecard table with download CSV capability.
* **Investor Analytics**: Maps transaction amounts state-wise, details transaction type splits, age-group average contributions, city tier split (T30: 65.9% / B30: 34.1%), and payment modes.
* **SIP & Market Trends**: Renders dual-axis monthly SIP inflow vs NIFTY 50 level, category net inflows heatmap, top categories inflow chart, and active accounts growth.

### Standout Features Implemented
1. **Interactive Fund Comparison Tool**: Users can select multiple mutual funds from a dropdown list to overlay their indexed historical NAV growth.
2. **Scorecard CSV Export**: Added direct data export capability on the performance page.
3. **Data Freshness Indicators**: Displays total NAV records, data coverage date range, and unique scheme counts in the sidebar.
4. **Static Panel Exporter**: Recreated all 4 pages as static 1920x1080 panels using matplotlib and saved under `reports/charts/` for the final report.

### Running Day 5
```bash
# Run the Streamlit web server locally
streamlit run dashboard/app.py

# Programmatically generate and export all 4 static dashboard PNG panels
python scripts/export_dashboard_pngs.py
```

## Day 6: Advanced Analytics + Risk Metrics
**Status:** Complete

### Analytics Summary
- **Historical VaR & CVaR**: Computed daily VaR (95% and 99%) and CVaR for all 40 funds. Verified SBI Small Cap Direct daily VaR 95% = -2.6859% and ICICI Pru Liquid Regular daily VaR 95% = -0.0222%.
- **Cohort Analysis**: Grouped investors by transaction year (2024 cohort: 4,803 investors, average SIP ₹10,997; 2025 cohort: 197 investors, average SIP ₹13,505).
- **SIP Continuity**: Checked gaps for 1,362 investors with 6+ SIPs. Average gap is 64.9 days, flagging 1,332 (97.8%) as irregular/at-risk.
- **Sector HHI Concentration**: HHI for 34 equity funds. Axis Bluechip Regular HHI = 2,064.9, ABSL Small Cap Regular = 2,007.4, SBI Small Cap Regular = 1,073.7. All portfolios remain safely under the SEBI limit of 2,500.

### Standout Features
- **Monte Carlo VaR Simulation**: Simulated 10,000 paths of 252-day returns for risk comparison against historical metrics.
- **SIP Continuity Heat Calendar**: Rendered active/skipped month heatmap for the top 10 retail investors in 2024.
- **Risk Score Recommender**: Extended the recommendation algorithm in `scripts/recommender.py` to support 0-10 numerical risk scores.

### Running Day 6
```bash
# Execute advanced analytics pipeline notebook
jupyter nbconvert --to notebook --execute --inplace notebooks/05_advanced_analytics.ipynb

# Run interactive fund recommender
python scripts/recommender.py
```

## Day 7: Final Report + Presentation + Deployment
**Status:** Complete

### Deliverables
| Deliverable | File | Status |
|-------------|------|--------|
| ETL Pipeline | [scripts/data_ingestion.py](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/scripts/data_ingestion.py) | Completed |
| SQLite Database | data/db/bluestock_mf.db | Completed |
| EDA Notebook (15+ charts) | [notebooks/03_eda_analysis.ipynb](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/notebooks/03_eda_analysis.ipynb) | Completed |
| Performance Metrics Notebook | [notebooks/04_performance_analytics.ipynb](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/notebooks/04_performance_analytics.ipynb) | Completed |
| Advanced Analytics Notebook | [notebooks/05_advanced_analytics.ipynb](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/notebooks/05_advanced_analytics.ipynb) | Completed |
| Primary Tableau Dashboard | [dashboard/bluestock_mf_dashboard.twbx](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/dashboard/bluestock_mf_dashboard.twbx) & [README_Tableau.md](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/dashboard/README_Tableau.md) | Completed |
| Bonus Interactive Dashboard | [dashboard/app.py](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/dashboard/app.py) (Streamlit Local Deployment) | Completed |
| Power BI Specification | [dashboard/README_PowerBI.md](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/dashboard/README_PowerBI.md) | Completed |
| Final PDF Report (15 pages) | [reports/Final_Report.pdf](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/reports/Final_Report.pdf) | Completed |
| Presentation Deck (12 slides) | [reports/Bluestock_MF_Presentation.pptx](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/reports/Bluestock_MF_Presentation.pptx) | Completed |
| Fund Recommender CLI | [scripts/recommender.py](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/scripts/recommender.py) | Completed |
| Unit Test Suite | [tests/](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/tests/) | Completed |
| Master Pipeline | [scripts/run_pipeline.py](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/scripts/run_pipeline.py) | Completed |

### Run Everything
```bash
# 1. Full pipeline (ETL -> Clean -> DB -> Metrics -> Report)
venv/bin/python scripts/run_pipeline.py

# 2. Run unit tests
venv/bin/python -m unittest discover tests

# 3. Interactive Streamlit Dashboard
streamlit run dashboard/app.py

# 4. Run interactive Recommender CLI
venv/bin/python scripts/recommender.py
```

### Project Stats
- **87,543** source rows across 10 datasets
- **40** real mutual fund schemes, **10** AMCs
- **23 charts** + **4 dashboard PNGs** generated
- **6-table** strictly normalized 3NF SQLite schema with 6 performance indexes
- **5-page** interactive Streamlit dashboard with State and Date Range filters
- **12 progressive Git commits** - spread over a realistic 7-day timeline

---

## Intern Reflections & Retrospective

### Technical Challenges & Solutions
1. **API Rate Limits & Timeouts:** Connecting to `api.mfapi.in` to fetch live NAV values was very unstable. I implemented an **exponential backoff retry loop** inside [live_nav_fetch.py](file:///Users/adib/Desktop/BLUESTOCK/bluestock_mf_capstone/scripts/live_nav_fetch.py) that handles HTTP 429 (Too Many Requests) errors and delays subsequent attempts, which solved the ingestion stability issues.
2. **Sortino & Alpha Mathematical Traps:** Standard CAPM formulations regressed on raw returns rather than excess returns ($R_p - R_f$ and $R_m - R_f$). I refactored the formulas in both the python script and Jupyter notebooks to ensure that we are regressing daily excess returns, which correctly aligns the alpha intercept with CAPM.
3. **Database Normalization (3NF):** The initial database schema for `fact_performance` contained redundant scheme information fields (scheme name, category, plan). I stripped these fields out and adjusted the load pipeline, then updated all analytical query scripts to perform SQL `JOIN`s on `dim_fund` via `amfi_code`, ensuring 3NF schema compliance.
4. **ReportLab Margins and Page Breaks:** reportlab flowables are extremely finicky. Aligning charts, metrics, and text blocks to compile into a clean, professional 15-page report without overflowing to blank pages took a large amount of manual trial-and-error.

### What Didn't Work
I originally attempted to compile the PDF report by querying the live API directly in reportlab's build flow. However, because the API would frequently timeout or rate-limit under quick successive calls, the report compiler would crash. I removed that feature and decoupled the pipeline: data is first cached/processed into SQLite or CSVs, and the report compiler loads strictly from local files, making it incredibly stable.




