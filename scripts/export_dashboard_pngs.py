"""Day 5 Export: Render static 1920x1080 PNG snapshots of all 4 dashboard pages."""

# ============================================================
# Bluestock MF Capstone — Day 5: Static Dashboard Export Script
# ============================================================
import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid blocking
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Style Constants for Dark Theme Dashboard
BG_COLOR    = '#1a1a2e'
CARD_COLOR  = '#16213e'
ACCENT_RED  = '#e94560'
ACCENT_BLUE = '#0f3460'
TEXT_COLOR  = '#ffffff'
SUB_TEXT    = '#a8a8b3'
GREEN_COLOR = '#4ecca3'
GRID_COLOR  = '#222240'

# Configure Matplotlib styles
plt.rcParams['figure.facecolor'] = BG_COLOR
plt.rcParams['axes.facecolor']   = BG_COLOR
plt.rcParams['text.color']       = TEXT_COLOR
plt.rcParams['axes.labelcolor']  = TEXT_COLOR
plt.rcParams['xtick.color']      = TEXT_COLOR
plt.rcParams['ytick.color']      = TEXT_COLOR
plt.rcParams['grid.color']       = GRID_COLOR
plt.rcParams['font.family']      = 'DejaVu Sans'
plt.rcParams['figure.dpi']       = 100

# Paths
ROOT       = Path(__file__).resolve().parent.parent
PROCESSED  = ROOT / 'data' / 'processed'
REPORTS    = ROOT / 'reports'
CHARTS     = REPORTS / 'charts'
CHARTS.mkdir(parents=True, exist_ok=True)


def draw_kpi_card(ax, label, value, delta):
    """Helper to draw a styled metric card in matplotlib."""
    ax.set_facecolor(CARD_COLOR)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color(ACCENT_RED)
    ax.spines['left'].set_linewidth(5)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Text Positioning
    ax.text(0.08, 0.72, label, fontsize=10, fontweight='bold', color=SUB_TEXT, transform=ax.transAxes, va='center')
    ax.text(0.08, 0.42, value, fontsize=20, fontweight='bold', color=ACCENT_RED, transform=ax.transAxes, va='center')
    ax.text(0.08, 0.18, delta, fontsize=9, fontweight='bold', color=GREEN_COLOR, transform=ax.transAxes, va='center')


def draw_page_header(fig, title, caption):
    """Draws page header at the top of the figure."""
    fig.text(0.05, 0.95, title, fontsize=20, fontweight='bold', color=TEXT_COLOR)
    fig.text(0.05, 0.92, caption, fontsize=10, color=SUB_TEXT)
    fig.text(0.95, 0.95, "BLUESTOCK FINTECH", fontsize=10, fontweight='bold', color=ACCENT_RED, ha='right')
    fig.text(0.95, 0.92, "Mutual Fund Analytics Portfolio 2026", fontsize=8, color=SUB_TEXT, ha='right')


def export_page1(data):
    """Page 1: Industry Overview dashboard export."""
    print("Exporting Page 1: Industry Overview...")
    fig = plt.figure(figsize=(19.2, 10.8))
    draw_page_header(fig, "INDIAN MUTUAL FUND INDUSTRY OVERVIEW", "As of December 2025 | Sources: AMFI India & Industry Reports")
    
    # 3x2 main layout GridSpec, reserving top for KPIs
    gs = fig.add_gridspec(3, 4, height_ratios=[1, 4, 4], hspace=0.4, wspace=0.3, left=0.05, right=0.95, top=0.88, bottom=0.08)
    
    # Row 0: 4 KPI Cards
    ax_kpi1 = fig.add_subplot(gs[0, 0])
    draw_kpi_card(ax_kpi1, "TOTAL INDUSTRY AUM", "₹81.00 Lakh Crore", "▲ +14.5% vs Dec 2024")
    
    ax_kpi2 = fig.add_subplot(gs[0, 1])
    draw_kpi_card(ax_kpi2, "MONTHLY SIP INFLOW", "₹31,002 Crore", "▲ +17.2% YoY (Dec 2025)")
    
    ax_kpi3 = fig.add_subplot(gs[0, 2])
    draw_kpi_card(ax_kpi3, "TOTAL FOLIOS", "26.12 Crore", "▲ +18.4% YoY (Dec 2025)")
    
    ax_kpi4 = fig.add_subplot(gs[0, 3])
    draw_kpi_card(ax_kpi4, "ACTIVE SIP ACCOUNTS", "9.35 Crore", "▲ +90.4% vs Jan 2022")
    
    # Row 1, Col 0-1: Industry AUM Growth Line
    ax_aum = fig.add_subplot(gs[1, 0:2])
    df_aum = data['aum'].copy()
    df_aum_sum = df_aum.groupby('date')['aum_lakh_crore'].sum().reset_index()
    ax_aum.plot(df_aum_sum['date'], df_aum_sum['aum_lakh_crore'], marker='o', color=ACCENT_RED, linewidth=2)
    ax_aum.fill_between(df_aum_sum['date'], df_aum_sum['aum_lakh_crore'], color=ACCENT_RED, alpha=0.1)
    ax_aum.set_title("Top-10 AMC Industry AUM — Mar 2022 to Dec 2025 (₹ Lakh Crore)", fontsize=11, fontweight='bold', pad=10)
    ax_aum.set_ylabel("AUM (₹ Lakh Crore)")
    ax_aum.grid(True, linestyle=':', alpha=0.5)
    # Add label at the end
    ax_aum.text(df_aum_sum['date'].iloc[-1], df_aum_sum['aum_lakh_crore'].iloc[-1] + 1.5, f"₹{df_aum_sum['aum_lakh_crore'].iloc[-1]:.2f}L Cr", color=ACCENT_RED, fontweight='bold', ha='right')
    
    # Row 1, Col 2-3: Folio Count Growth
    ax_folio = fig.add_subplot(gs[1, 2:4])
    df_folio = data['folio'].copy()
    df_folio['month_dt'] = pd.to_datetime(df_folio['month'] + '-01')
    ax_folio.plot(df_folio['month_dt'], df_folio['total_folios_crore'], color='#0f3460', linewidth=2, label='Total Folios')
    ax_folio.fill_between(df_folio['month_dt'], df_folio['total_folios_crore'], color='#0f3460', alpha=0.1)
    ax_folio.plot(df_folio['month_dt'], df_folio['equity_folios_crore'], color=ACCENT_RED, linewidth=2, label='Equity Folios')
    ax_folio.set_title("Industry Folio Count Growth (Crore) — 2022 to 2025", fontsize=11, fontweight='bold', pad=10)
    ax_folio.set_ylabel("Folios (Crore)")
    ax_folio.legend(frameon=False, loc='upper left')
    ax_folio.grid(True, linestyle=':', alpha=0.5)
    
    # Row 2, Col 0-4 (Spans whole bottom row): AUM by Fund House Bar Chart
    ax_amc = fig.add_subplot(gs[2, :])
    df_aum_latest = df_aum[df_aum['date'] == df_aum['date'].max()].sort_values('aum_lakh_crore', ascending=True)
    bar_colors = [ACCENT_RED if fh == 'SBI Mutual Fund' else ACCENT_BLUE for fh in df_aum_latest['fund_house']]
    bars = ax_amc.barh(df_aum_latest['fund_house'], df_aum_latest['aum_lakh_crore'], color=bar_colors, height=0.6, alpha=0.85)
    ax_amc.set_title("AUM by Fund House — December 2025 (₹ Lakh Crore)", fontsize=11, fontweight='bold', pad=10)
    ax_amc.set_xlabel("AUM (₹ Lakh Crore)")
    ax_amc.grid(True, axis='x', linestyle=':', alpha=0.5)
    # Add values on bars
    for bar in bars:
        width = bar.get_width()
        ax_amc.text(width + 0.1, bar.get_y() + bar.get_height()/2, f"₹{width:.2f}L Cr", va='center', ha='left', fontsize=8, color=TEXT_COLOR)
        
    plt.savefig(CHARTS / 'dashboard_page1_industry_overview.png', dpi=100, bbox_inches='tight', facecolor=BG_COLOR)
    plt.close()
    print("Saved dashboard_page1_industry_overview.png")


def export_page2(data):
    """Page 2: Fund Performance dashboard export."""
    print("Exporting Page 2: Fund Performance...")
    fig = plt.figure(figsize=(19.2, 10.8))
    draw_page_header(fig, "FUND PERFORMANCE ANALYTICS", "Risk-Return Matrix, Index Overlay, and Composite Ranks")
    
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 4.5, 4.5], hspace=0.4, wspace=0.25, left=0.05, right=0.95, top=0.88, bottom=0.08)
    
    # Row 0: Filters Indicator Card (Spans both)
    ax_filt = fig.add_subplot(gs[0, :])
    ax_filt.set_facecolor(CARD_COLOR)
    ax_filt.spines['top'].set_visible(False)
    ax_filt.spines['right'].set_visible(False)
    ax_filt.spines['left'].set_visible(True)
    ax_filt.spines['left'].set_color(ACCENT_RED)
    ax_filt.spines['left'].set_linewidth(5)
    ax_filt.spines['bottom'].set_visible(False)
    ax_filt.set_xticks([])
    ax_filt.set_yticks([])
    ax_filt.text(0.02, 0.5, "FILTERS ACTIVE: Fund House=All | Category=All | Plan Type=All | Universe=40 Schemes", fontsize=11, fontweight='bold', color=TEXT_COLOR, transform=ax_filt.transAxes, va='center')
    
    # Row 1, Col 0: Risk-Return Scatter Plot
    ax_scatter = fig.add_subplot(gs[1, 0])
    df_perf = data['perf'].copy()
    categories = df_perf['category'].unique()
    colors = plt.cm.Set2(np.linspace(0, 1, len(categories)))
    cat_color_map = dict(zip(categories, colors))
    
    for cat in categories:
        df_cat = df_perf[df_perf['category'] == cat]
        sizes = df_cat['aum_crore'] / 30.0 + 15
        ax_scatter.scatter(df_cat['std_dev_ann_pct'], df_cat['return_3yr_pct'], s=sizes, color=cat_color_map[cat], label=cat, alpha=0.7)
    
    ax_scatter.axhline(11.49, color='gray', linestyle='--', linewidth=1.5, label='Nifty 100 3yr (11.49%)')
    ax_scatter.set_title("Risk-Return Matrix — 3yr CAGR vs Annualised Std Dev (Bubble = AUM)", fontsize=11, fontweight='bold', pad=10)
    ax_scatter.set_xlabel("Risk — Annualised Standard Deviation (%)")
    ax_scatter.set_ylabel("Return — 3yr CAGR (%)")
    ax_scatter.legend(frameon=False, loc='upper left', fontsize=8)
    ax_scatter.grid(True, linestyle=':', alpha=0.5)
    
    # Row 1, Col 1: Fund Comparison Tool Line Chart (Overlay SBI Small Cap, Kotak Flexicap vs Nifty100)
    ax_nav = fig.add_subplot(gs[1, 1])
    common_start = pd.to_datetime('2022-01-03')
    
    # SBI Small Cap
    df_sbi = data['nav'][data['nav']['amfi_code'] == 119598].sort_values('date')
    base_sbi = df_sbi[df_sbi['date'] >= common_start].iloc[0]['nav']
    ax_nav.plot(df_sbi['date'], df_sbi['nav'] / base_sbi * 100, color='#e94560', linewidth=1.5, label='SBI Small Cap Reg')
    
    # Kotak Flexicap
    df_kotak = data['nav'][data['nav']['amfi_code'] == 120843].sort_values('date')
    base_kot = df_kotak[df_kotak['date'] >= common_start].iloc[0]['nav']
    ax_nav.plot(df_kotak['date'], df_kotak['nav'] / base_kot * 100, color='#0f3460', linewidth=1.5, label='Kotak Flexicap Reg')
    
    # Nifty100
    df_nifty = data['bench'][data['bench']['index_name'] == 'Nifty100'].sort_values('date')
    base_nifty = df_nifty[df_nifty['date'] >= common_start].iloc[0]['close_value']
    ax_nav.plot(df_nifty['date'], df_nifty['close_value'] / base_nifty * 100, color='gray', linestyle='--', linewidth=1.5, label='Nifty 100 Index')
    
    ax_nav.set_title("Fund Comparison Tool — Indexed NAV (Base: Jan 2022 = 100)", fontsize=11, fontweight='bold', pad=10)
    ax_nav.set_ylabel("Indexed Value")
    ax_nav.legend(frameon=False, loc='upper left', fontsize=8)
    ax_nav.grid(True, linestyle=':', alpha=0.5)
    
    # Row 2: Table of Top 10 Scorecard Funds
    ax_table = fig.add_subplot(gs[2, :])
    ax_table.axis('off')
    df_sc = data['scorecard'].copy().head(10)
    
    # Render table beautifully
    table_data = []
    # Add header
    headers = ["Rank", "Mutual Fund Scheme Name", "Fund House", "Category", "Plan", "3yr CAGR", "Sharpe", "Alpha", "Exp Ratio", "Max DD", "Score"]
    table_data.append(headers)
    for idx, r in df_sc.iterrows():
        table_data.append([
            str(r['score_rank']),
            r['scheme_name'][:45],
            r['fund_house'][:20],
            r['category'],
            r['plan'],
            f"{r['return_3yr_pct']:.2f}%",
            f"{r['sharpe_ratio']:.2f}",
            f"{r['alpha']:.2f}",
            f"{r['expense_ratio_pct']:.2f}%",
            f"{r['max_drawdown_pct']:.2f}%",
            f"{r['composite_score']:.2f}"
        ])
        
    table = ax_table.table(
        cellText=table_data,
        loc='center',
        cellLoc='center',
        colWidths=[0.05, 0.35, 0.15, 0.08, 0.06, 0.07, 0.05, 0.05, 0.06, 0.06, 0.06]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    
    # Style table colors
    for (row_idx, col_idx), cell in table.get_celld().items():
        cell.set_edgecolor('#222240')
        if row_idx == 0:
            cell.set_facecolor('#0f3460')
            cell.get_text().set_weight('bold')
            cell.get_text().set_color('white')
        else:
            cell.set_facecolor(CARD_COLOR if row_idx % 2 == 0 else BG_COLOR)
            cell.get_text().set_color('white')
            # Color rank and score columns
            if col_idx == 0:
                cell.get_text().set_color(ACCENT_RED)
                cell.get_text().set_weight('bold')
            if col_idx == 10:
                cell.get_text().set_color(GREEN_COLOR)
                cell.get_text().set_weight('bold')
                
    ax_table.set_title("Top 10 Mutual Funds overall — Scorecard Table", fontsize=11, fontweight='bold', pad=10)
    
    plt.savefig(CHARTS / 'dashboard_page2_fund_performance.png', dpi=100, bbox_inches='tight', facecolor=BG_COLOR)
    plt.close()
    print("Saved dashboard_page2_fund_performance.png")


def export_page3(data):
    """Page 3: Investor Analytics dashboard export."""
    print("Exporting Page 3: Investor Analytics...")
    fig = plt.figure(figsize=(19.2, 10.8))
    draw_page_header(fig, "INVESTOR TRANSACTION ANALYTICS", "Retail Flows, Segmentation, Payment Modes, and Age-Group Dynamics")
    
    gs = fig.add_gridspec(4, 6, height_ratios=[1, 3.8, 3.8, 2.8], hspace=0.45, wspace=0.35, left=0.05, right=0.95, top=0.88, bottom=0.05)
    
    # Row 0: 3 KPI Cards (taking 2 columns each)
    ax_kpi1 = fig.add_subplot(gs[0, 0:2])
    draw_kpi_card(ax_kpi1, "TOTAL TRANSACTIONS", "32,778", "5,000 Unique Retail Investors")
    
    ax_kpi2 = fig.add_subplot(gs[0, 2:4])
    draw_kpi_card(ax_kpi2, "AVERAGE SIP AMOUNT", "₹11,018", "Range: ₹400 – ₹5,97,498")
    
    ax_kpi3 = fig.add_subplot(gs[0, 4:6])
    draw_kpi_card(ax_kpi3, "KYC VERIFICATION RATE", "92.00%", "8.00% Pending KYC Check")
    
    # Row 1, Col 0-3: State Inflow Bar
    ax_state = fig.add_subplot(gs[1, 0:4])
    df_tx = data['tx'].copy()
    state_data = df_tx.groupby('state')['amount_inr'].sum().reset_index()
    state_data['amount_crore'] = state_data['amount_inr'] / 1e7
    state_data = state_data.sort_values('amount_crore', ascending=True)
    
    bars = ax_state.barh(state_data['state'], state_data['amount_crore'], color=plt.cm.Blues(np.linspace(0.4, 0.9, len(state_data))), height=0.6)
    ax_state.set_title("Total Transaction Inflow by Indian State (₹ Crore)", fontsize=11, fontweight='bold', pad=10)
    ax_state.set_xlabel("Amount (₹ Crore)")
    ax_state.grid(True, axis='x', linestyle=':', alpha=0.5)
    for bar in bars:
        width = bar.get_width()
        ax_state.text(width + 0.05, bar.get_y() + bar.get_height()/2, f"₹{width:.2f}Cr", va='center', ha='left', fontsize=8, color=TEXT_COLOR)
        
    # Row 1, Col 4-5: Transaction Type Split Pie
    ax_type = fig.add_subplot(gs[1, 4:6])
    type_data = df_tx.groupby('transaction_type').size().reset_index(name='count')
    ax_type.pie(
        type_data['count'], labels=type_data['transaction_type'],
        autopct='%1.1f%%', startangle=90,
        colors=['#0f3460', '#e94560', '#533483'],
        wedgeprops={'width': 0.55, 'edgecolor': BG_COLOR, 'linewidth': 2}
    )
    ax_type.set_title("Transaction Type Split (Count)", fontsize=11, fontweight='bold', pad=10)
    
    # Row 2, Col 0-2: Age Group SIP
    ax_age = fig.add_subplot(gs[2, 0:2])
    age_order = ['18-25', '26-35', '36-45', '46-55', '56+']
    sip_tx = df_tx[df_tx['transaction_type'] == 'SIP']
    age_data = sip_tx.groupby('age_group')['amount_inr'].mean().reset_index()
    age_data['age_group'] = pd.Categorical(age_data['age_group'], categories=age_order, ordered=True)
    age_data = age_data.sort_values('age_group')
    
    bars_age = ax_age.bar(age_data['age_group'], age_data['amount_inr'], color=plt.cm.Reds(np.linspace(0.4, 0.8, len(age_data))), width=0.5)
    ax_age.set_title("Average Monthly SIP Contribution by Age Group (₹)", fontsize=11, fontweight='bold', pad=10)
    ax_age.set_ylabel("Average SIP (₹)")
    ax_age.set_ylim(10000, 12200)
    for bar in bars_age:
        yval = bar.get_height()
        ax_age.text(bar.get_x() + bar.get_width()/2, yval + 50, f"₹{yval:,.0f}", ha='center', va='bottom', fontsize=8, color=TEXT_COLOR)
        
    # Row 2, Col 2-5: Monthly Transaction Volume Line
    ax_monthly = fig.add_subplot(gs[2, 2:6])
    df_tx['month_ts'] = df_tx['transaction_date'].dt.to_period('M').dt.to_timestamp()
    monthly = df_tx.groupby(['month_ts', 'transaction_type']).size().reset_index(name='count')
    
    type_color_map = {'SIP': '#0f3460', 'Lumpsum': '#e94560', 'Redemption': '#533483'}
    for t_type in monthly['transaction_type'].unique():
        df_t = monthly[monthly['transaction_type'] == t_type]
        ax_monthly.plot(df_t['month_ts'], df_t['count'], color=type_color_map[t_type], label=t_type, linewidth=1.5, marker='o', markersize=4)
        
    ax_monthly.set_title("Monthly Transaction Volume Over Time (Count)", fontsize=11, fontweight='bold', pad=10)
    ax_monthly.legend(frameon=False, loc='upper left')
    ax_monthly.grid(True, linestyle=':', alpha=0.5)
    
    # Row 3, Col 0-1: T30 vs B30 Split Donut
    ax_tier = fig.add_subplot(gs[3, 0:2])
    tier = df_tx[df_tx['transaction_type'] == 'SIP'].groupby('city_tier')['amount_inr'].sum().reset_index()
    ax_tier.pie(
        tier['amount_inr'], labels=tier['city_tier'], autopct='%1.1f%%', startangle=90,
        colors=['#0f3460', '#e94560'], wedgeprops={'width': 0.5, 'edgecolor': BG_COLOR, 'linewidth': 2}
    )
    ax_tier.set_title("T30 vs B30 — SIP Value Split", fontsize=10, fontweight='bold')
    
    # Row 3, Col 2-3: Gender Split Donut
    ax_gender = fig.add_subplot(gs[3, 2:4])
    gender = df_tx[df_tx['transaction_type'] == 'SIP'].groupby('gender')['amount_inr'].sum().reset_index()
    ax_gender.pie(
        gender['amount_inr'], labels=gender['gender'], autopct='%1.1f%%', startangle=90,
        colors=['#0f3460', '#e94560'], wedgeprops={'width': 0.5, 'edgecolor': BG_COLOR, 'linewidth': 2}
    )
    ax_gender.set_title("Gender Split — SIP Value", fontsize=10, fontweight='bold')
    
    # Row 3, Col 4-5: Payment Mode Split Donut
    ax_pay = fig.add_subplot(gs[3, 4:6])
    payment = df_tx.groupby('payment_mode').size().reset_index(name='count')
    ax_pay.pie(
        payment['count'], labels=payment['payment_mode'], autopct='%1.1f%%', startangle=90,
        colors=plt.cm.Set3(np.linspace(0, 1, len(payment))), wedgeprops={'width': 0.5, 'edgecolor': BG_COLOR, 'linewidth': 2}
    )
    ax_pay.set_title("Payment Mode Distribution", fontsize=10, fontweight='bold')
    
    plt.savefig(CHARTS / 'dashboard_page3_investor_analytics.png', dpi=100, bbox_inches='tight', facecolor=BG_COLOR)
    plt.close()
    print("Saved dashboard_page3_investor_analytics.png")


def export_page4(data):
    """Page 4: SIP and Market Trends dashboard export."""
    print("Exporting Page 4: SIP & Market Trends...")
    fig = plt.figure(figsize=(19.2, 10.8))
    draw_page_header(fig, "SIP FLOW DYNAMICS & MARKET TRENDS", "Monthly SIP Inflows, Active Accounts, Index Overlay, and Category heatmaps")
    
    gs = fig.add_gridspec(3, 4, height_ratios=[1, 4.2, 4.2], hspace=0.45, wspace=0.3, left=0.05, right=0.95, top=0.88, bottom=0.08)
    
    # Row 0: 3 KPI Cards (Columns 0-2, Column 3 is a helper box)
    ax_kpi1 = fig.add_subplot(gs[0, 0])
    draw_kpi_card(ax_kpi1, "SIP INFLOW GROWTH", "2.69× Inflows", "₹11,517 Cr → ₹31,002 Cr")
    
    ax_kpi2 = fig.add_subplot(gs[0, 1])
    draw_kpi_card(ax_kpi2, "SIP ACCOUNTS GROWTH", "+90.40% Accounts", "4.91 Crore → 9.35 Crore")
    
    ax_kpi3 = fig.add_subplot(gs[0, 2])
    draw_kpi_card(ax_kpi3, "SIP AUM (DEC 2025)", "₹15.90 Lakh Crore", "▲ +231% since Jan 2022")
    
    # Helper box (Row 0, Col 3)
    ax_hb = fig.add_subplot(gs[0, 3])
    ax_hb.set_facecolor(CARD_COLOR)
    ax_hb.spines['top'].set_visible(False)
    ax_hb.spines['right'].set_visible(False)
    ax_hb.spines['bottom'].set_visible(False)
    ax_hb.spines['left'].set_visible(True)
    ax_hb.spines['left'].set_color(ACCENT_BLUE)
    ax_hb.spines['left'].set_linewidth(5)
    ax_hb.set_xticks([])
    ax_hb.set_yticks([])
    ax_hb.text(0.08, 0.5, "SIP accounts peaked at\n9.35 Cr active accounts\nin December 2025.", fontsize=9, fontweight='bold', color=TEXT_COLOR, transform=ax_hb.transAxes, va='center')
    
    # Row 1: Dual Axis Monthly SIP vs Nifty50
    ax_dual = fig.add_subplot(gs[1, :])
    df_sip = data['sip'].copy()
    df_sip['month_dt'] = pd.to_datetime(df_sip['month'] + '-01')
    
    df_nifty = data['bench'][data['bench']['index_name'] == 'Nifty50'].sort_values('date')
    df_nifty['month'] = df_nifty['date'].dt.to_period('M').dt.strftime('%Y-%m')
    nifty_monthly = df_nifty.groupby('month')['close_value'].last().reset_index()
    nifty_monthly['month_dt'] = pd.to_datetime(nifty_monthly['month'] + '-01')
    merged = df_sip.merge(nifty_monthly[['month_dt', 'close_value']], on='month_dt', how='left')
    
    # Plot left: SIP Inflows (bar)
    ax_dual.bar(merged['month_dt'], merged['sip_inflow_crore'], color=ACCENT_BLUE, width=15, alpha=0.85, label='SIP Inflow (Left Y)')
    ax_dual.set_ylabel("SIP Inflow (₹ Crore)", color=SUB_TEXT)
    ax_dual.tick_params(axis='y', labelcolor=SUB_TEXT)
    
    # Plot right: Nifty50 (line)
    ax_nifty = ax_dual.twinx()
    ax_nifty.plot(merged['month_dt'], merged['close_value'], color=ACCENT_RED, linewidth=2, label='Nifty 50 Level')
    ax_nifty.set_ylabel("Nifty 50 level", color=ACCENT_RED)
    ax_nifty.tick_params(axis='y', labelcolor=ACCENT_RED)
    
    ax_dual.set_title("Monthly SIP Inflow vs Nifty 50 index — Jan 2022 to Dec 2025", fontsize=11, fontweight='bold', pad=10)
    ax_dual.grid(True, linestyle=':', alpha=0.3)
    
    # Annotate ATH
    ax_dual.text(pd.to_datetime('2025-12-01'), 31002 + 800, "ATH: ₹31,002 Cr", color=ACCENT_RED, fontsize=8, fontweight='bold', ha='center')
    
    # Row 2, Col 0-1: Category heatmap
    ax_hm = fig.add_subplot(gs[2, 0:2])
    df_cat = data['cat'].copy()
    cat_pivot = df_cat.pivot(index='category', columns='month', values='net_inflow_crore').fillna(0)
    sns.heatmap(cat_pivot, cmap='RdYlGn', annot=False, ax=ax_hm, cbar_kws={'label': '₹ Cr'})
    ax_hm.set_title("Net Category Inflows Heatmap — FY 2024-25 (₹ Crore)", fontsize=11, fontweight='bold', pad=10)
    ax_hm.set_xticklabels(ax_hm.get_xticklabels(), rotation=45, ha='right', fontsize=7)
    ax_hm.set_yticklabels(ax_hm.get_yticklabels(), fontsize=7)
    
    # Row 2, Col 2: Top categories
    ax_catbar = fig.add_subplot(gs[2, 2])
    fy25 = data['cat'][data['cat']['month'] >= '2024-04']
    cat_total = fy25.groupby('category')['net_inflow_crore'].sum().sort_values(ascending=False).reset_index()
    bars_cat = ax_catbar.bar(cat_total['category'].head(5), cat_total['net_inflow_crore'].head(5), color=ACCENT_BLUE, width=0.4)
    ax_catbar.set_title("Top 5 Categories — Net Inflow FY25 (₹ Cr)", fontsize=11, fontweight='bold', pad=10)
    ax_catbar.set_xticklabels([c[:15] for c in cat_total['category'].head(5)], rotation=20, ha='right', fontsize=7)
    ax_catbar.grid(True, axis='y', linestyle=':', alpha=0.5)
    for bar in bars_cat:
        yval = bar.get_height()
        ax_catbar.text(bar.get_x() + bar.get_width()/2, yval + 10000, f"₹{yval/1e3:.0f}K Cr", ha='center', va='bottom', fontsize=7, color=TEXT_COLOR)
        
    # Row 2, Col 3: Active SIP Accounts Growth
    ax_act = fig.add_subplot(gs[2, 3])
    ax_act.plot(df_sip['month_dt'], df_sip['active_sip_accounts_crore'], color=ACCENT_RED, linewidth=1.5)
    ax_act.fill_between(df_sip['month_dt'], df_sip['active_sip_accounts_crore'], color=ACCENT_RED, alpha=0.15)
    ax_act.set_title("Active SIP Accounts Growth (Crore)", fontsize=11, fontweight='bold', pad=10)
    ax_act.set_ylabel("Accounts (Crore)")
    ax_act.grid(True, linestyle=':', alpha=0.5)
    ax_act.text(df_sip['month_dt'].iloc[0], df_sip['active_sip_accounts_crore'].iloc[0] + 0.3, "4.91 Cr", ha='center', fontsize=8, color=TEXT_COLOR)
    ax_act.text(df_sip['month_dt'].iloc[-1], df_sip['active_sip_accounts_crore'].iloc[-1] + 0.3, "9.35 Cr", ha='center', fontsize=8, color=TEXT_COLOR)
    
    plt.savefig(CHARTS / 'dashboard_page4_sip_trends.png', dpi=100, bbox_inches='tight', facecolor=BG_COLOR)
    plt.close()
    print("Saved dashboard_page4_sip_trends.png")


def main():
    print("Loading processed datasets...")
    datasets = {
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
    }
    
    # Sort nav
    datasets['nav'] = datasets['nav'].sort_values(['amfi_code', 'date']).reset_index(drop=True)
    datasets['nav']['daily_return'] = datasets['nav'].groupby('amfi_code')['nav'].pct_change()
    
    export_page1(datasets)
    export_page2(datasets)
    export_page3(datasets)
    export_page4(datasets)
    print("\nAll 4 dashboard static PNG panels successfully exported to reports/charts/")


if __name__ == '__main__':
    main()
