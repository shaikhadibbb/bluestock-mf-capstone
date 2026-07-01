import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Set Page Config
st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #0f3460;
        color: white;
        margin-bottom: 20px;
    }
    .kpi-value { font-size: 2.2rem; font-weight: 700; color: #e94560; }
    .kpi-label { font-size: 0.9rem; color: #a8a8b3; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-delta { font-size: 0.85rem; color: #4ecca3; font-weight: 600; margin-top: 5px; }
    .section-header { 
        font-size: 1.3rem; font-weight: 600; 
        border-bottom: 2px solid #e94560; 
        padding-bottom: 8px; margin-top: 25px; margin-bottom: 20px; 
        color: #e94560;
    }
</style>
""", unsafe_allow_html=True)

# ── Data Loading (Cached) ───────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / 'data' / 'processed'

@st.cache_data
def load_data():
    return {
        'master'      : pd.read_csv(PROCESSED / 'clean_fund_master.csv'),
        'nav'         : pd.read_csv(PROCESSED / 'clean_nav.csv', parse_dates=['date']),
        'aum'         : pd.read_csv(PROCESSED / 'clean_aum_by_fund_house.csv', parse_dates=['date']),
        'sip'         : pd.read_csv(PROCESSED / 'clean_sip_inflows.csv'),
        'cat'         : pd.read_csv(PROCESSED / 'clean_category_inflows.csv'),
        'folio'       : pd.read_csv(PROCESSED / 'clean_folio_count.csv'),
        'perf'        : pd.read_csv(PROCESSED / 'clean_performance.csv'),
        'tx'          : pd.read_csv(PROCESSED / 'clean_transactions.csv', parse_dates=['transaction_date']),
        'port'        : pd.read_csv(PROCESSED / 'clean_portfolio_holdings.csv'),
        'bench'       : pd.read_csv(PROCESSED / 'clean_benchmark_indices.csv', parse_dates=['date']),
        'scorecard'   : pd.read_csv(PROCESSED / 'fund_scorecard.csv'),
        'returns'     : pd.read_csv(PROCESSED / 'returns_computed.csv'),
        'var_cvar'    : pd.read_csv(PROCESSED / 'var_cvar_report.csv'),
    }

try:
    data = load_data()
except Exception as e:
    st.error(f"Failed to load processed datasets. Error: {e}")
    st.stop()

# Pre-process dates and index returns globally
if 'daily_return' not in data['nav'].columns:
    data['nav'] = data['nav'].sort_values(['amfi_code', 'date']).reset_index(drop=True)
    data['nav']['daily_return'] = data['nav'].groupby('amfi_code')['nav'].pct_change()
if 'daily_return' not in data['bench'].columns:
    data['bench'] = data['bench'].sort_values(['index_name', 'date']).reset_index(drop=True)
    data['bench']['daily_return'] = data['bench'].groupby('index_name')['close_value'].pct_change()

# Sidebar Navigation & Filters
with st.sidebar:
    st.markdown("## Mutual Fund Analytics")
    st.markdown("*Bluestock Fintech Capstone*")
    st.divider()
    
    page = st.radio(
        "Navigation",
        ["Industry Overview", "Fund Performance", "Investor Analytics", "SIP & Market Trends", "Fund Recommender"]
    )
    
    st.divider()
    st.markdown("### Filter Settings")
    
    # Fund House filter (affects Performance and Investor transactions)
    fund_houses = ['All'] + sorted(data['master']['fund_house'].unique().tolist())
    sel_house = st.selectbox("Fund House", fund_houses)
    
    # Category filter
    categories = ['All'] + sorted(data['master']['category'].unique().tolist())
    sel_cat = st.selectbox("Category", categories)
    
    # Plan filter
    sel_plan = st.radio("Plan Type", ["All", "Regular", "Direct"])
    
    # TODO: Add State filter requested by mentor to segment transaction metrics
    # FIXME: Need to make sure state is not empty in transaction logs
    states = ['All'] + sorted(data['tx']['state'].dropna().unique().tolist())
    sel_state = st.selectbox("State (Investor)", states)
    
    # WIP: Date Range filter for historical plots
    min_date = data['nav']['date'].min().to_pydatetime()
    max_date = data['nav']['date'].max().to_pydatetime()
    sel_dates = st.date_input("Date Range (NAV)", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    st.divider()
    # Standout feature: Data Freshness Indicators
    st.caption("Data last updated: May 29, 2026")
    st.caption(f"{len(data['nav']):,} NAV records loaded")
    st.caption("40 unique schemes active")

# Helper function to filter fund scorecard and metrics data
def apply_filters(df, sel_house, sel_cat, sel_plan):
    df_filtered = df.copy()
    if sel_house != 'All':
        df_filtered = df_filtered[df_filtered['fund_house'] == sel_house]
    if sel_cat != 'All':
        df_filtered = df_filtered[df_filtered['category'] == sel_cat]
    if sel_plan != 'All':
        df_filtered = df_filtered[df_filtered['plan'] == sel_plan]
    return df_filtered

# PAGE 1 — INDUSTRY OVERVIEW
if page == "Industry Overview":
    st.title("Mutual Fund Industry Overview")
    st.caption("As of December 2025 | Sources: AMFI India & Industry Reports")
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">Total Industry AUM</div>'
            '<div class="kpi-value">₹81.00L Cr</div>'
            '<div class="kpi-delta">▲ +14.5% vs Dec 2024</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col2:
        # SIP Inflow Dec 2025: ₹31,002 Cr
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">Monthly SIP Inflow</div>'
            '<div class="kpi-value">₹31,002 Cr</div>'
            '<div class="kpi-delta">▲ +17.2% YoY (Dec 2025)</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col3:
        # Total Folios Dec 2025: 26.12 Cr
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">Total Folios</div>'
            '<div class="kpi-value">26.12 Crore</div>'
            '<div class="kpi-delta">▲ +18.4% YoY (Dec 2025)</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col4:
        # Active SIP Accounts Dec 2025: 9.35 Cr
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">Active SIP Accounts</div>'
            '<div class="kpi-value">9.35 Crore</div>'
            '<div class="kpi-delta">▲ +90.4% vs Jan 2022</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
    st.markdown('<div class="section-header">Industry Asset & AUM Growth Trends</div>', unsafe_allow_html=True)
    
    # Chart 1: Industry AUM Growth Line Chart
    df_aum = data['aum'].copy()
    df_aum_sum = df_aum.groupby('date')['aum_lakh_crore'].sum().reset_index()
    
    fig1 = px.line(
        df_aum_sum, x='date', y='aum_lakh_crore',
        markers=True,
        line_shape='linear',
        color_discrete_sequence=['#e94560'],
        title="Top-10 AMC Industry AUM — Mar 2022 to Dec 2025 (₹ Lakh Crore)"
    )
    
    # Annotate final point
    final_val = df_aum_sum.iloc[-1]['aum_lakh_crore']
    final_date = df_aum_sum.iloc[-1]['date']
    fig1.add_annotation(
        x=final_date, y=final_val,
        text=f"₹{final_val:.2f}L Cr (top-10 AMCs)",
        showarrow=True, arrowhead=1, ax=-90, ay=-30,
        bgcolor="#1a1a2e", bordercolor="#e94560", borderwidth=1, font=dict(color="white")
    )
    
    fig1.update_layout(
        height=400,
        xaxis_title="Reporting Date",
        yaxis_title="AUM (₹ Lakh Crore)",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("*Top-10 AMCs shown. Industry total AUM = ₹81 lakh crore (Dec 2025) per AMFI.")
    
    # Chart 2: AUM by Fund House sorted descending (Dec 2025)
    st.markdown('<div class="section-header">Top-10 Asset Management Companies by AUM</div>', unsafe_allow_html=True)
    df_aum_latest = df_aum[df_aum['date'] == df_aum['date'].max()].sort_values('aum_lakh_crore', ascending=False)
    
    # Color top AMC differently
    colors = ['#e94560' if fh == 'SBI Mutual Fund' else '#0f3460' for fh in df_aum_latest['fund_house']]
    
    fig2 = px.bar(
        df_aum_latest, x='aum_lakh_crore', y='fund_house',
        orientation='h',
        title=f"AUM by Fund House — December 2025",
        color='fund_house',
        color_discrete_sequence=colors,
        labels={'aum_lakh_crore': 'AUM (₹ Lakh Crore)', 'fund_house': 'AMC'}
    )
    fig2.update_layout(
        height=420,
        template="plotly_dark",
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    # Add labels inside/outside bars
    for i, val in enumerate(df_aum_latest['aum_lakh_crore']):
        fig2.add_annotation(
            x=val, y=df_aum_latest['fund_house'].iloc[i],
            text=f" ₹{val:.2f}L Cr",
            showarrow=False, xanchor="left", yanchor="middle",
            font=dict(color="white", size=9)
        )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Chart 3: Folio Count Growth
    st.markdown('<div class="section-header">Industry Folio Count Growth</div>', unsafe_allow_html=True)
    df_folio = data['folio'].copy()
    df_folio['month_dt'] = pd.to_datetime(df_folio['month'] + '-01')
    
    fig3 = go.Figure()
    # Shaded Total Folios
    fig3.add_trace(go.Scatter(
        x=df_folio['month_dt'], y=df_folio['total_folios_crore'],
        fill='tozeroy', fillcolor='rgba(15, 52, 96, 0.15)',
        line=dict(color='#0f3460', width=2),
        name='Total Folios (Crore)'
    ))
    # Equity Folios
    fig3.add_trace(go.Scatter(
        x=df_folio['month_dt'], y=df_folio['equity_folios_crore'],
        line=dict(color='#e94560', width=2),
        name='Equity Folios (Crore)'
    ))
    
    # Add annotations
    fig3.add_annotation(
        x=df_folio['month_dt'].iloc[0], y=df_folio['total_folios_crore'].iloc[0],
        text=f"Start: {df_folio['total_folios_crore'].iloc[0]:.2f} Cr",
        showarrow=True, arrowhead=1, ax=-40, ay=-30
    )
    fig3.add_annotation(
        x=df_folio['month_dt'].iloc[-1], y=df_folio['total_folios_crore'].iloc[-1],
        text=f"End: {df_folio['total_folios_crore'].iloc[-1]:.2f} Cr",
        showarrow=True, arrowhead=1, ax=40, ay=-30
    )
    
    fig3.update_layout(
        height=400,
        title="Industry Folio Count Growth (Crore) — Jan 2022 to Dec 2025",
        xaxis_title="Month",
        yaxis_title="Folios (Crore)",
        template="plotly_dark",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(26,26,46,0.6)")
    )
    st.plotly_chart(fig3, use_container_width=True)

# PAGE 2 — FUND PERFORMANCE
elif page == "Fund Performance":
    st.title("Fund Performance Analytics")
    
    # Apply filters to scorecard and performance datasets
    df_scorecard_filtered = apply_filters(data['scorecard'], sel_house, sel_cat, sel_plan)
    df_perf_filtered = apply_filters(data['perf'], sel_house, sel_cat, sel_plan)
    
    n_funds = len(df_perf_filtered)
    st.caption(f"Showing {n_funds} funds | Filters: House={sel_house} | Category={sel_cat} | Plan={sel_plan}")
    
    # Page Tabs
    tab_overview, tab_comparison = st.tabs(["Performance Matrix & Scorecard", "Fund Comparison Tool"])
    
    with tab_overview:
        # Chart 1: Risk-Return Scatter Plot
        st.markdown('<div class="section-header">Risk-Return Analysis Matrix</div>', unsafe_allow_html=True)
        if n_funds > 0:
            fig1 = px.scatter(
                df_perf_filtered,
                x='std_dev_ann_pct', y='return_3yr_pct',
                size='aum_crore', color='category',
                hover_name='scheme_name',
                hover_data={'fund_house': True, 'sharpe_ratio': True, 'alpha': True, 'aum_crore': ':,'},
                size_max=50,
                title="Risk-Return Matrix — 3yr CAGR vs Annualised Std Dev (Bubble = AUM)"
            )
            # Add benchmark reference line at y = 11.49 (avg benchmark 3yr)
            fig1.add_hline(
                y=11.49, line_dash='dash', line_color='gray',
                annotation_text="Avg Benchmark 3yr (11.49%)", annotation_position="top right"
            )
            fig1.update_layout(
                height=500,
                xaxis_title="Risk — Annualised Standard Deviation (%)",
                yaxis_title="Return — 3yr CAGR (%)",
                template="plotly_dark"
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("No funds match current filters.")
            
        # Single Fund NAV selector
        st.markdown('<div class="section-header">Individual NAV Performance vs Benchmark</div>', unsafe_allow_html=True)
        if n_funds > 0:
            fund_options = df_perf_filtered['scheme_name'].tolist()
            sel_fund_name = st.selectbox("Select Fund for NAV Plot", fund_options)
            sel_fund_code = df_perf_filtered[df_perf_filtered['scheme_name'] == sel_fund_name]['amfi_code'].values[0]
            
            # Get NAV and benchmark data
            df_fund_nav = data['nav'][data['nav']['amfi_code'] == sel_fund_code].sort_values('date')
            df_nifty = data['bench'][data['bench']['index_name'] == 'Nifty100'].sort_values('date')
            
            # Apply Date Range filter (slicer)
            if isinstance(sel_dates, (list, tuple)) and len(sel_dates) == 2:
                start_dt, end_dt = pd.to_datetime(sel_dates[0]), pd.to_datetime(sel_dates[1])
                df_fund_nav = df_fund_nav[(df_fund_nav['date'] >= start_dt) & (df_fund_nav['date'] <= end_dt)]
                df_nifty = df_nifty[(df_nifty['date'] >= start_dt) & (df_nifty['date'] <= end_dt)]
                
            # Normalise to 100 at common start date
            if not df_fund_nav.empty and not df_nifty.empty:
                common_start = max(df_fund_nav['date'].min(), df_nifty['date'].min())
                fund_base = df_fund_nav[df_fund_nav['date'] >= common_start].iloc[0]['nav'] if not df_fund_nav[df_fund_nav['date'] >= common_start].empty else df_fund_nav.iloc[0]['nav']
                bench_base = df_nifty[df_nifty['date'] >= common_start].iloc[0]['close_value'] if not df_nifty[df_nifty['date'] >= common_start].empty else df_nifty.iloc[0]['close_value']
                
                df_fund_nav_filt = df_fund_nav[df_fund_nav['date'] >= common_start].copy()
                df_fund_nav_filt['indexed'] = df_fund_nav_filt['nav'] / fund_base * 100
                
                df_nifty_filt = df_nifty[df_nifty['date'] >= common_start].copy()
                df_nifty_filt['indexed'] = df_nifty_filt['close_value'] / bench_base * 100
            else:
                df_fund_nav_filt = pd.DataFrame(columns=['date', 'indexed'])
                df_nifty_filt = pd.DataFrame(columns=['date', 'indexed'])
                common_start = pd.Timestamp(min_date)
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_fund_nav_filt['date'], y=df_fund_nav_filt['indexed'],
                name=sel_fund_name[:40], line=dict(color='#e94560', width=2)
            ))
            fig2.add_trace(go.Scatter(
                x=df_nifty_filt['date'], y=df_nifty_filt['indexed'],
                name='NIFTY 100 Benchmark', line=dict(color='gray', dash='dash', width=1.5)
            ))
            fig2.update_layout(
                height=400,
                title=f"NAV vs NIFTY 100 — Indexed to 100 (Base: {common_start.date()})",
                yaxis_title="Indexed Value (Base = 100)",
                xaxis_title="Date",
                template="plotly_dark",
                legend=dict(x=0.01, y=0.99)
            )
            st.plotly_chart(fig2, use_container_width=True)
            
        # Interactive Fund Scorecard
        st.markdown('<div class="section-header">Fund Performance Scorecard</div>', unsafe_allow_html=True)
        if len(df_scorecard_filtered) > 0:
            df_scorecard_display = df_scorecard_filtered.copy()
            
            # Scorecard Table
            st.dataframe(
                df_scorecard_display[[
                    'score_rank', 'scheme_name', 'fund_house', 'category', 'plan',
                    'return_3yr_pct', 'sharpe_ratio', 'alpha', 'expense_ratio_pct',
                    'max_drawdown_pct', 'composite_score'
                ]].sort_values('score_rank'),
                column_config={
                    'score_rank'       : st.column_config.NumberColumn("Rank", width="small"),
                    'scheme_name'      : st.column_config.TextColumn("Fund Name", width="large"),
                    'fund_house'       : st.column_config.TextColumn("Fund House", width="medium"),
                    'return_3yr_pct'   : st.column_config.NumberColumn("3yr Return %", format="%.2f%%"),
                    'sharpe_ratio'     : st.column_config.NumberColumn("Sharpe", format="%.2f"),
                    'alpha'            : st.column_config.NumberColumn("Alpha", format="%.2f"),
                    'expense_ratio_pct': st.column_config.NumberColumn("Exp Ratio %", format="%.2f%%"),
                    'max_drawdown_pct' : st.column_config.NumberColumn("Max Drawdown %", format="%.2f%%"),
                    'composite_score'  : st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%.2f"),
                },
                use_container_width=True,
                hide_index=True,
                height=450
            )
            
            # Standout feature: Download scorecard Button
            csv_data = df_scorecard_display.to_csv(index=False)
            st.download_button(
                "⬇️ Download Scorecard CSV",
                data=csv_data,
                file_name="bluestock_fund_scorecard.csv",
                mime="text/csv"
            )
            
            st.caption(
                "**Scorecard Weighting**: 30% 3yr Return Rank, 25% Sharpe Rank, 20% Alpha Rank, "
                "15% Expense Ratio Rank (inverted), 10% Max Drawdown Rank (inverted). "
                "Calculated using standard AMFI-reference files."
            )
        else:
            st.warning("No scorecard data available for selected filters.")
            
    with tab_comparison:
        # Standout feature: Fund Comparison Tool
        st.markdown('<div class="section-header">Fund Performance Comparison Tool</div>', unsafe_allow_html=True)
        all_fund_names = data['master']['scheme_name'].tolist()
        
        sel_compare_funds = st.multiselect(
            "Select Funds to Compare (2 - 4 recommended)",
            options=all_fund_names,
            default=all_fund_names[:2]
        )
        
        if len(sel_compare_funds) > 0:
            fig_compare = go.Figure()
            
            # Fetch common start date across selected funds after applying Date Range
            start_dates = []
            for name in sel_compare_funds:
                code = data['master'][data['master']['scheme_name'] == name]['amfi_code'].values[0]
                df_fund_nav = data['nav'][data['nav']['amfi_code'] == code].sort_values('date')
                
                # Apply Date Range filter (slicer)
                if isinstance(sel_dates, (list, tuple)) and len(sel_dates) == 2:
                    start_dt, end_dt = pd.to_datetime(sel_dates[0]), pd.to_datetime(sel_dates[1])
                    df_fund_nav = df_fund_nav[(df_fund_nav['date'] >= start_dt) & (df_fund_nav['date'] <= end_dt)]
                
                if not df_fund_nav.empty:
                    start_dates.append(df_fund_nav['date'].min())
                    
            if start_dates:
                common_start = max(start_dates)
            else:
                common_start = pd.Timestamp(min_date)
            
            # Plot indexed NAV lines
            colors = px.colors.qualitative.Plotly
            for idx, name in enumerate(sel_compare_funds):
                code = data['master'][data['master']['scheme_name'] == name]['amfi_code'].values[0]
                df_fund_nav = data['nav'][data['nav']['amfi_code'] == code].sort_values('date')
                
                # Apply Date Range filter (slicer)
                if isinstance(sel_dates, (list, tuple)) and len(sel_dates) == 2:
                    start_dt, end_dt = pd.to_datetime(sel_dates[0]), pd.to_datetime(sel_dates[1])
                    df_fund_nav = df_fund_nav[(df_fund_nav['date'] >= start_dt) & (df_fund_nav['date'] <= end_dt)]
                
                # Filter to common start date
                df_fund_nav = df_fund_nav[df_fund_nav['date'] >= common_start].copy()
                if not df_fund_nav.empty:
                    base_nav = df_fund_nav.iloc[0]['nav']
                    df_fund_nav['indexed'] = df_fund_nav['nav'] / base_nav * 100
                    
                    fig_compare.add_trace(go.Scatter(
                        x=df_fund_nav['date'], y=df_fund_nav['indexed'],
                        name=name.split("Growth")[0].strip(),
                        line=dict(color=colors[idx % len(colors)], width=2)
                    ))
                    
            fig_compare.update_layout(
                height=500,
                title=f"Indexed NAV Growth Comparison (Base: {common_start.date()} = 100)",
                yaxis_title="Indexed Value (Base = 100)",
                xaxis_title="Date",
                template="plotly_dark",
                legend=dict(x=0.01, y=0.99, bgcolor="rgba(26,26,46,0.6)")
            )
            st.plotly_chart(fig_compare, use_container_width=True)
            
            # Show summary stats table for compared funds
            st.markdown("### Comparison Table")
            compare_codes = data['master'][data['master']['scheme_name'].isin(sel_compare_funds)]['amfi_code'].tolist()
            df_compare_stats = data['scorecard'][data['scorecard']['amfi_code'].isin(compare_codes)].copy()
            
            st.dataframe(
                df_compare_stats[[
                    'score_rank', 'scheme_name', 'return_3yr_pct', 'sharpe_ratio',
                    'alpha', 'expense_ratio_pct', 'max_drawdown_pct', 'composite_score'
                ]],
                column_config={
                    'score_rank'       : "Rank",
                    'scheme_name'      : "Fund Name",
                    'return_3yr_pct'   : st.column_config.NumberColumn("3yr Return %", format="%.2f%%"),
                    'sharpe_ratio'     : st.column_config.NumberColumn("Sharpe", format="%.2f"),
                    'alpha'            : st.column_config.NumberColumn("Alpha", format="%.2f"),
                    'expense_ratio_pct': st.column_config.NumberColumn("Expense Ratio", format="%.2f%%"),
                    'max_drawdown_pct' : st.column_config.NumberColumn("Max Drawdown", format="%.2f%%"),
                    'composite_score'  : st.column_config.NumberColumn("Composite Score", format="%.2f")
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Please select at least one mutual fund to compare.")

# PAGE 3 — INVESTOR ANALYTICS
elif page == "Investor Analytics":
    st.title("Investor Transaction Analytics")
    st.caption("Transactions Period: Jan 2024 – May 2025 | 32,778 transaction records | 5,000 investors")
    
    # KPI Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">Total Transactions</div>'
            '<div class="kpi-value">32,778</div>'
            '<div class="kpi-delta">5,000 Unique Retail Investors</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">Average SIP Amount</div>'
            '<div class="kpi-value">₹11,018</div>'
            '<div class="kpi-delta">Transaction Range: ₹400 – ₹5.97 Lakhs</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">KYC Verification %</div>'
            '<div class="kpi-value">92%</div>'
            '<div class="kpi-delta">8% Pending Verification</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
    st.markdown('<div class="section-header">Transaction Inflows & Demographics</div>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Chart 1: Transaction Amount by State (horizontal bar)
        df_tx = data['tx'].copy()
        
        # Apply State filter (slicer)
        if sel_state != 'All':
            df_tx = df_tx[df_tx['state'] == sel_state]
            
        state_data = df_tx.groupby('state')['amount_inr'].sum().reset_index()
        state_data['amount_crore'] = state_data['amount_inr'] / 1e7
        state_data = state_data.sort_values('amount_crore', ascending=True)
        
        fig1 = px.bar(
            state_data, x='amount_crore', y='state', orientation='h',
            color='amount_crore', color_continuous_scale='Blues',
            title="Total Transaction Inflow by Indian State (₹ Crore)",
            labels={'amount_crore': 'Amount (₹ Crore)', 'state': ''}
        )
        fig1.update_layout(
            height=420,
            template="plotly_dark",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_right:
        # Chart 2: SIP / Lumpsum / Redemption Donut
        type_data = df_tx.groupby('transaction_type').size().reset_index(name='count')
        
        fig2 = px.pie(
            type_data, values='count', names='transaction_type',
            hole=0.55,
            color_discrete_map={'SIP': '#0f3460', 'Lumpsum': '#e94560', 'Redemption': '#533483'},
            title="Transaction Type Volume Breakdown (Count)"
        )
        fig2.update_traces(textinfo='label+percent')
        fig2.update_layout(
            height=420,
            template="plotly_dark",
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
        
    col_left2, col_right2 = st.columns([2, 3])
    
    with col_left2:
        # Chart 3: Age Group vs Avg SIP Amount
        age_order = ['18-25', '26-35', '36-45', '46-55', '56+']
        sip_tx = df_tx[df_tx['transaction_type'] == 'SIP']
        age_data = sip_tx.groupby('age_group')['amount_inr'].mean().reset_index()
        age_data['age_group'] = pd.Categorical(age_data['age_group'], categories=age_order, ordered=True)
        age_data = age_data.sort_values('age_group')
        
        fig3 = px.bar(
            age_data, x='age_group', y='amount_inr',
            color='amount_inr', color_continuous_scale='Reds',
            title="Average Monthly SIP Contribution by Age Group (₹)",
            text=age_data['amount_inr'].apply(lambda x: f"₹{x:,.0f}"),
            labels={'amount_inr': 'Average SIP (₹)', 'age_group': 'Age Group'}
        )
        fig3.update_traces(textposition='outside')
        fig3.update_layout(
            height=380,
            template="plotly_dark",
            coloraxis_showscale=False,
            yaxis_range=[10000, 12200]
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("*SIP contributions are nearly uniform across ages — indicating consistent habits regardless of life stage.")
        
    with col_right2:
        # Chart 4: Monthly Transaction Volume by Type
        df_tx['month_ts'] = df_tx['transaction_date'].dt.to_period('M').dt.to_timestamp()
        monthly = df_tx.groupby(['month_ts', 'transaction_type']).size().reset_index(name='count')
        
        fig4 = px.line(
            monthly, x='month_ts', y='count', color='transaction_type',
            color_discrete_map={'SIP': '#0f3460', 'Lumpsum': '#e94560', 'Redemption': '#533483'},
            title="Monthly Transaction Volume Over Time (Count)",
            labels={'count': 'Transactions Count', 'month_ts': 'Month', 'transaction_type': 'Type'}
        )
        fig4.update_layout(
            height=380,
            template="plotly_dark",
            legend_title=''
        )
        st.plotly_chart(fig4, use_container_width=True)
        
    st.markdown('<div class="section-header">Segmentation Splits</div>', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        # T30 vs B30 SIP value split
        tier = df_tx[df_tx['transaction_type'] == 'SIP'].groupby('city_tier')['amount_inr'].sum().reset_index()
        fig_t = px.pie(
            tier, values='amount_inr', names='city_tier', hole=0.5,
            color_discrete_map={'T30': '#0f3460', 'B30': '#e94560'},
            title="T30 vs B30 — SIP Value Split"
        )
        fig_t.update_layout(height=280, template="plotly_dark")
        st.plotly_chart(fig_t, use_container_width=True)
        
    with col_b:
        # Gender split
        gender = df_tx[df_tx['transaction_type'] == 'SIP'].groupby('gender')['amount_inr'].sum().reset_index()
        fig_g = px.pie(
            gender, values='amount_inr', names='gender', hole=0.5,
            color_discrete_map={'Male': '#0f3460', 'Female': '#e94560'},
            title="Gender Split — SIP Value"
        )
        fig_g.update_layout(height=280, template="plotly_dark")
        st.plotly_chart(fig_g, use_container_width=True)
        
    with col_c:
        # Payment mode split
        payment = df_tx.groupby('payment_mode').size().reset_index(name='count')
        fig_p = px.pie(
            payment, values='count', names='payment_mode', hole=0.5,
            title="Payment Mode Distribution (Count)"
        )
        fig_p.update_layout(height=280, template="plotly_dark")
        st.plotly_chart(fig_p, use_container_width=True)

# PAGE 4 — SIP & MARKET TRENDS
elif page == "SIP & Market Trends":
    st.title("SIP Inflow Dynamics & Market Trends")
    st.caption("Historical Data: Jan 2022 – Dec 2025 | Sources: AMFI India & Benchmark Indices")
    
    # KPI Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">SIP Inflow Growth</div>'
            '<div class="kpi-value">2.69× Inflows</div>'
            '<div class="kpi-delta">₹11,517 Cr → ₹31,002 Cr</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">SIP Accounts Growth</div>'
            '<div class="kpi-value">+90.4% Accounts</div>'
            '<div class="kpi-delta">4.91 Crore → 9.35 Crore</div>'
            '</div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '<div class="metric-card">'
            '<div class="kpi-label">SIP AUM Dec 2025</div>'
            '<div class="kpi-value">₹15.90 Lakh Crore</div>'
            '<div class="kpi-delta">▲ +231% Growth since Jan 2022</div>'
            '</div>',
            unsafe_allow_html=True
        )
        
    # Chart 1: Dual Axis Monthly SIP Inflow vs Nifty50
    st.markdown('<div class="section-header">Monthly SIP Inflow vs Nifty50 Level</div>', unsafe_allow_html=True)
    df_sip = data['sip'].copy()
    df_sip['month_dt'] = pd.to_datetime(df_sip['month'] + '-01')
    
    df_nifty = data['bench'][data['bench']['index_name'] == 'Nifty50'].sort_values('date')
    df_nifty['month'] = df_nifty['date'].dt.to_period('M').dt.strftime('%Y-%m')
    nifty_monthly = df_nifty.groupby('month')['close_value'].last().reset_index()
    nifty_monthly['month_dt'] = pd.to_datetime(nifty_monthly['month'] + '-01')
    
    merged = df_sip.merge(nifty_monthly[['month_dt', 'close_value']], on='month_dt', how='left')
    
    fig1 = go.Figure()
    # Left Axis: Bars
    fig1.add_trace(go.Bar(
        x=merged['month_dt'], y=merged['sip_inflow_crore'],
        name='SIP Inflow (₹ Crore)', marker_color='#0f3460', opacity=0.85
    ))
    # Right Axis: Line
    fig1.add_trace(go.Scatter(
        x=merged['month_dt'], y=merged['close_value'],
        name='NIFTY 50 Level', yaxis='y2',
        line=dict(color='#e94560', width=2.5)
    ))
    
    # Annotate ATH Inflow
    fig1.add_annotation(
        x='2025-12-01', y=31002,
        text="ATH: ₹31,002 Cr",
        showarrow=True, arrowhead=2,
        font=dict(color='white'),
        bgcolor='#e94560', bordercolor='#e94560'
    )
    
    fig1.update_layout(
        title="Monthly SIP Inflow vs Nifty 50 Index — Jan 2022 to Dec 2025",
        yaxis=dict(title=dict(text='SIP Inflow (₹ Crore)', font=dict(color='#0f3460')), gridcolor='rgba(255,255,255,0.1)'),
        yaxis2=dict(title=dict(text='Nifty 50 Level', font=dict(color='#e94560')), overlaying='y', side='right'),
        template="plotly_dark",
        height=450,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(26,26,46,0.6)")
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Chart 2: Category Inflows Heatmap
    st.markdown('<div class="section-header">Category Net Inflow Heatmap (FY 2024-25)</div>', unsafe_allow_html=True)
    df_cat = data['cat'].copy()
    cat_pivot = df_cat.pivot(index='category', columns='month', values='net_inflow_crore').fillna(0)
    
    fig2 = px.imshow(
        cat_pivot,
        color_continuous_scale='RdYlGn',
        title="Net Category Inflows Heatmap — FY 2024-25 (₹ Crore)",
        labels=dict(color="Net Inflow (₹ Cr)"),
        aspect='auto'
    )
    fig2.update_layout(
        height=420,
        template="plotly_dark",
        xaxis_title="Reporting Month",
        yaxis_title="Category",
        coloraxis_colorbar=dict(title="₹ Crore")
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    col_left, col_right = st.columns([2, 3])
    
    with col_left:
        # Chart 3: Top Categories Inflow
        fy25 = data['cat'][data['cat']['month'] >= '2024-04']
        cat_total = fy25.groupby('category')['net_inflow_crore'].sum().sort_values(ascending=False).reset_index()
        
        fig3 = px.bar(
            cat_total.head(7), x='category', y='net_inflow_crore',
            color='net_inflow_crore', color_continuous_scale='Blues',
            title="Top Mutual Fund Categories by Net Inflow (₹ Crore)",
            text=cat_total.head(7)['net_inflow_crore'].apply(lambda x: f"₹{x:,.0f}"),
            labels={'net_inflow_crore': 'Net Inflow (₹ Cr)', 'category': ''}
        )
        fig3.update_traces(textposition='outside', textfont_size=9)
        fig3.update_layout(
            height=420,
            template="plotly_dark",
            coloraxis_showscale=False,
            xaxis_tickangle=25
        )
        st.plotly_chart(fig3, use_container_width=True)
        
    with col_right:
        # Chart 4: Active SIP Accounts Growth
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=df_sip['month_dt'], y=df_sip['active_sip_accounts_crore'],
            fill='tozeroy', fillcolor='rgba(233,69,96,0.15)',
            line=dict(color='#e94560', width=2),
            name='Active Accounts (Crore)'
        ))
        fig4.add_annotation(
            x=df_sip['month_dt'].iloc[0], y=4.91,
            text="4.91 Cr (Jan 22)", showarrow=True, arrowhead=2
        )
        fig4.add_annotation(
            x=df_sip['month_dt'].iloc[-1], y=9.35,
            text="9.35 Cr (Dec 25)", showarrow=True, arrowhead=2
        )
        fig4.update_layout(
            height=420,
            title="Active SIP Accounts Growth (Crore) — Jan 2022 to Dec 2025",
            xaxis_title="Month",
            yaxis_title="Accounts (Crore)",
            template="plotly_dark"
        )
        st.plotly_chart(fig4, use_container_width=True)

# PAGE 5 — FUND RECOMMENDER
elif page == "Fund Recommender":
    st.title("Fund Recommender")
    st.caption("Top 3 mutual fund recommendations optimized by Sharpe ratio for your risk appetite.")
    
    # Selection Mode
    mode = st.radio("Choose Input Mode", ["Risk Appetite Category", "Risk Score (0-10)"], horizontal=True)
    
    if mode == "Risk Appetite Category":
        appetite = st.selectbox("Select Risk Appetite Category", ["Low", "Moderate", "High"])
        score = None
    else:
        score = st.slider("Select Risk Score", 0, 10, 5, help="Low: 0-3 | Moderate: 4-6 | High: 7-10")
        appetite = None
        
    # Map Risk
    if score is not None:
        if score <= 3:
            target_appetite = 'Low'
        elif score <= 6:
            target_appetite = 'Moderate'
        else:
            target_appetite = 'High'
    else:
        target_appetite = appetite
        
    RISK_MAP = {
        'Low'      : ['Low'],
        'Moderate' : ['Moderate', 'Moderately High'],
        'High'     : ['High', 'Very High'],
    }
    
    target_grades = RISK_MAP[target_appetite]
    
    # Merge performance with var
    df_perf = data['perf']
    df_var = data['var_cvar']
    df_merged = df_perf.merge(df_var[['amfi_code', 'var_95_pct']], on='amfi_code', how='left')
    
    # Filter
    df_filtered = df_merged[df_merged['risk_grade'].isin(target_grades)].copy()
    
    # Top 3
    df_top = df_filtered.sort_values('sharpe_ratio', ascending=False).head(3).copy()
    
    if len(df_top) > 0:
        # Display recommendations
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for idx, (i, r) in enumerate(df_top.iterrows()):
            with cols[idx]:
                name_short = r['scheme_name'].split(' - ')[0]
                border_color = "#2ecc71" if target_appetite == "Low" else "#f39c12" if target_appetite == "Moderate" else "#e94560"
                st.markdown(
                    f'<div class="metric-card" style="border-left: 5px solid {border_color}; min-height: 250px; background-color: #16213e; padding: 15px; border-radius: 5px; margin-bottom: 20px;">'
                    f'<div class="kpi-label" style="color: #a8a8b3; font-weight: bold; font-size: 0.85em;">RANK {idx+1} ({r["risk_grade"]})</div>'
                    f'<div style="font-weight: bold; font-size: 1.1em; color: white; margin-top: 5px; margin-bottom: 10px; height: 50px; overflow: hidden;">{name_short}</div>'
                    f'<div style="font-size: 0.9em; margin-bottom: 5px; color: #ffffff;">Sharpe Ratio: <strong style="color: #4ecca3;">{r["sharpe_ratio"]:.2f}</strong></div>'
                    f'<div style="font-size: 0.9em; margin-bottom: 5px; color: #ffffff;">3Yr CAGR: <strong>{r["return_3yr_pct"]:.2f}%</strong></div>'
                    f'<div style="font-size: 0.9em; margin-bottom: 5px; color: #ffffff;">Expense Ratio: <strong>{r["expense_ratio_pct"]:.2f}%</strong></div>'
                    f'<div style="font-size: 0.9em; margin-bottom: 5px; color: #ffffff;">Daily VaR 95%: <strong>{r["var_95_pct"]:.4f}%</strong></div>'
                    f'<div class="kpi-label" style="font-size: 0.75em; margin-top: 10px; color: #a8a8b3;">{r["fund_house"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    else:
        st.warning("No recommendations found for the selected criteria.")
