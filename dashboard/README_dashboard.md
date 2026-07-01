# Bluestock MF Analytics — Streamlit Dashboard

## Run Locally

```bash
cd bluestock_mf_capstone
pip install -r dashboard/requirements_dashboard.txt
streamlit run dashboard/app.py
```

The app opens at `http://localhost:8501`

## Pages

| Page | Description |
|------|-------------|
| Industry Overview | AUM growth, folio count, SIP milestone KPIs |
| Fund Performance | Risk-return scatter, NAV vs benchmark, fund scorecard |
| Investor Analytics | State-wise flows, demographics, payment modes |
| SIP & Market Trends | Dual-axis SIP+NIFTY chart, category heatmap |

## Data Sources
All data loaded from `data/processed/` (cleaned CSVs from Day 2).
No internet connection required after setup.

## Filters (Sidebar)
- Fund House (10 AMCs)
- Sub-Category (12 types: Large Cap, Mid Cap, Small Cap, Liquid, etc.)
- Plan Type (Regular / Direct)

Filters apply to Pages 2 and 3.
