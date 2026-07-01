"""Standalone Charts Generator for Bluestock Mutual Fund Capstone.

This module re-runs the Exploratory Data Analysis (EDA) visualizations and
saves them as publication-quality PNG files to reports/charts/.
"""

import logging
import warnings
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("generate_eda_charts")

# --- Style Configuration ---
plt.rcParams["figure.dpi"] = 150
plt.rcParams["figure.figsize"] = (14, 6)
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
sns.set_palette("tab10")

# --- Constants & Directories ---
ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
CHARTS_DIR = ROOT_DIR / "reports" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Subtitle Source Annotation
SUBTITLE = "Source: AMFI India · mfapi.in · Bluestock Fintech Capstone 2026"


def load_data() -> dict:
    """Loads all cleaned datasets from data/processed/.

    Returns:
        Dict of loaded DataFrames.
    """
    logger.info("Loading cleaned CSV datasets...")
    dfs = {
        "master": pd.read_csv(PROCESSED_DIR / "clean_fund_master.csv"),
        "nav": pd.read_csv(PROCESSED_DIR / "clean_nav.csv", parse_dates=["date"]),
        "aum": pd.read_csv(PROCESSED_DIR / "clean_aum_by_fund_house.csv", parse_dates=["date"]),
        "sip": pd.read_csv(PROCESSED_DIR / "clean_sip_inflows.csv"),
        "cat": pd.read_csv(PROCESSED_DIR / "clean_category_inflows.csv"),
        "folio": pd.read_csv(PROCESSED_DIR / "clean_folio_count.csv"),
        "perf": pd.read_csv(PROCESSED_DIR / "clean_performance.csv"),
        "tx": pd.read_csv(PROCESSED_DIR / "clean_transactions.csv", parse_dates=["transaction_date"]),
        "port": pd.read_csv(PROCESSED_DIR / "clean_portfolio_holdings.csv"),
        "bench": pd.read_csv(PROCESSED_DIR / "clean_benchmark_indices.csv", parse_dates=["date"])
    }
    
    # Merge nav with master for scheme labels
    dfs["nav"] = dfs["nav"].merge(
        dfs["master"][["amfi_code", "scheme_name", "sub_category", "fund_house"]],
        on="amfi_code",
        how="left"
    )
    return dfs


def chart_01_nav_trends(dfs: dict) -> None:
    """Chart 01: NAV Trend Lines (2 subplots: Kotak Liquid vs Others)."""
    logger.info("Generating Chart 01: NAV Trends...")
    df_nav = dfs["nav"]
    
    # Set up subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # Subplot 1: Kotak Liquid (highest NAV)
    df_liquid = df_nav[df_nav["amfi_code"] == 120841]
    ax1.plot(df_liquid["date"], df_liquid["nav"], label="Kotak Liquid (AMFI 120841)", color="crimson", linewidth=1.5)
    ax1.set_title("Liquid Schemes (Kotak Liquid Fund)", fontsize=11, fontweight="bold")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"Rs. {x:,.0f}"))
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle=":", alpha=0.6)
    
    # Subplot 2: Other 39 schemes grouped by sub_category
    df_others = df_nav[df_nav["amfi_code"] != 120841]
    
    # Set color palette for subcategories
    subcats = df_others["sub_category"].dropna().unique()
    colors = plt.cm.tab20(np.linspace(0, 1, len(subcats)))
    color_map = dict(zip(subcats, colors))
    
    for subcat in subcats:
        df_sub = df_others[df_others["sub_category"] == subcat]
        for amfi in df_sub["amfi_code"].unique():
            df_fund = df_sub[df_sub["amfi_code"] == amfi]
            # Plot but only add label once per subcategory for clean legend
            label = subcat if amfi == df_sub["amfi_code"].unique()[0] else ""
            ax2.plot(df_fund["date"], df_fund["nav"], color=color_map[subcat], alpha=0.5, linewidth=0.8, label=label)
            
    ax2.set_title("Equity and Debt Schemes (Excluding Liquid)", fontsize=11, fontweight="bold")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"Rs. {x:,.0f}"))
    ax2.legend(loc="upper left", title="Sub-Categories", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    ax2.grid(True, linestyle=":", alpha=0.6)
    
    # Add vertical correction & rally lines to both axes
    milestones = [
        ("2022-06-16", "Jun 2022 Correction"),
        ("2024-01-15", "Jan 2024 Rally")
    ]
    for date_str, label in milestones:
        ts = pd.to_datetime(date_str)
        ax1.axvline(ts, color="gray", linestyle="--", alpha=0.7)
        ax2.axvline(ts, color="gray", linestyle="--", alpha=0.7)
        ax1.text(ts, ax1.get_ylim()[0] + (ax1.get_ylim()[1]-ax1.get_ylim()[0])*0.8, f" {label}", rotation=0, fontsize=8, color="black", alpha=0.8)
        
    plt.suptitle("NAV Movement — All 40 Funds (Jan 2022 – May 2026)\n" + SUBTITLE, fontsize=14, fontweight="bold")
    plt.xlabel("Date")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_01_nav_trends_all_funds.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 01 saved.")


def chart_02_aum_growth(dfs: dict) -> None:
    """Chart 02: AUM Growth by Fund House (Grouped Bar)."""
    logger.info("Generating Chart 02: AUM Growth...")
    df_aum = dfs["aum"].copy()
    
    # Format date to string for clean grouping on bar chart
    df_aum["Date String"] = df_aum["date"].dt.strftime("%Y-%m-%d")
    df_aum = df_aum.sort_values("date")
    
    plt.figure(figsize=(14, 7))
    ax = sns.barplot(data=df_aum, x="Date String", y="aum_lakh_crore", hue="fund_house")
    
    plt.title("AUM Growth by Fund House — 2022 to 2025\n" + SUBTITLE, fontsize=13, fontweight="bold")
    plt.xlabel("Reporting Date")
    plt.ylabel("AUM (₹ Lakh Crore)")
    plt.xticks(rotation=45)
    plt.grid(True, axis="y", linestyle=":", alpha=0.6)
    
    # Locate Dec 2025 bars to annotate
    # We find Dec 2025 values for SBI (12.50) and ICICI (10.74)
    # We can write direct annotations on the plot
    # Dec 2025 date string index is 7 or 8 depending on unique count
    unique_dates = df_aum["Date String"].unique()
    dec_2025_idx = list(unique_dates).index("2025-12-31")
    
    # Draw text annotations manually
    # SBI Dec 2025 AUM is 12.5
    plt.text(dec_2025_idx - 0.25, 12.7, "₹12.50L Cr\n(SBI)", ha="center", fontsize=8, color="blue", fontweight="bold")
    # ICICI Dec 2025 AUM is 10.74
    plt.text(dec_2025_idx + 0.15, 11.0, "₹10.74L Cr\n(ICICI)", ha="center", fontsize=8, color="darkorange", fontweight="bold")
    
    plt.legend(title="Fund Houses", bbox_to_anchor=(1.01, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_02_aum_growth_by_amc.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 02 saved.")


def chart_03_sip_inflows(dfs: dict) -> None:
    """Chart 03: SIP Inflow Time-Series with Milestones (Plotly Area)."""
    logger.info("Generating Chart 03: SIP Inflows...")
    df_sip = dfs["sip"].copy()
    df_sip["parsed_month"] = pd.to_datetime(df_sip["month"] + "-01")
    df_sip = df_sip.sort_values("parsed_month")
    
    # Convert dates to string format for Plotly JSON serialization
    x_dates = df_sip["parsed_month"].dt.strftime("%Y-%m-%d").tolist()
    min_date = df_sip["parsed_month"].min().strftime("%Y-%m-%d")
    max_date = df_sip["parsed_month"].max().strftime("%Y-%m-%d")
    
    fig = go.Figure()
    # Add fill area
    fig.add_trace(go.Scatter(
        x=x_dates,
        y=df_sip["sip_inflow_crore"],
        mode="lines+markers",
        name="SIP Inflow",
        line=dict(color="royalblue", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(31,119,180,0.12)"
    ))
    
    # Horizontal line ATH Dec 2025
    fig.add_shape(type="line", x0=min_date, x1=max_date,
                  y0=31002, y1=31002, line=dict(color="Red", width=1.5, dash="dash"))
    
    # Horizontal line Jan 2022 Start
    fig.add_shape(type="line", x0=min_date, x1=max_date,
                  y0=11517, y1=11517, line=dict(color="Gray", width=1.5, dash="dash"))
                  
    fig.add_annotation(x=df_sip["parsed_month"].iloc[-2].strftime("%Y-%m-%d"), y=31002, text="ATH: ₹31,002 Cr (Dec 2025)",
                       showarrow=True, arrowhead=1, ax=10, ay=-25, font=dict(color="red"))
    fig.add_annotation(x=df_sip["parsed_month"].iloc[2].strftime("%Y-%m-%d"), y=11517, text="Start: ₹11,517 Cr (Jan 2022)",
                       showarrow=True, arrowhead=1, ax=10, ay=25, font=dict(color="gray"))
                       
    fig.update_layout(
        title=dict(
            text=f"Monthly SIP Inflows — Jan 2022 to Dec 2025<br><sub>{SUBTITLE}</sub>",
            font=dict(size=16, family="DejaVu Sans")
        ),
        xaxis_title="Month",
        yaxis_title="SIP Inflow (₹ Crore)",
        template="plotly_white",
        width=1000,
        height=500
    )
    
    # Save Plotly static image
    fig.write_image(str(CHARTS_DIR / "chart_03_sip_inflow_trend.png"))
    print("Chart 03 saved.")


def chart_04_category_heatmap(dfs: dict) -> None:
    """Chart 04: Category-Wise Inflow Heatmap (Seaborn Heatmap)."""
    logger.info("Generating Chart 04: Category Heatmap...")
    df_cat = dfs["cat"]
    
    # Pivot category inflows
    df_pivot = df_cat.pivot(index="category", columns="month", values="net_inflow_crore")
    
    plt.figure(figsize=(18, 8))
    sns.heatmap(df_pivot, cmap="RdYlGn", annot=True, fmt=".0f", linewidths=0.5, annot_kws={"size": 8})
    
    plt.title("Net Fund Category Inflows Heatmap — FY 2024-25 (₹ Crore)\n" + SUBTITLE, fontsize=14, fontweight="bold")
    plt.ylabel("Fund Category")
    plt.xlabel("Month")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_04_category_inflow_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 04 saved.")


def chart_05_investor_demographics(dfs: dict) -> None:
    """Chart 05: Investor Age Group Distribution (Pie + Box, 2 panels)."""
    logger.info("Generating Chart 05: Investor Demographics...")
    df_tx = dfs["tx"]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Panel 1: Pie chart
    age_counts = df_tx["age_group"].value_counts()
    ax1.pie(age_counts, labels=age_counts.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))
    ax1.set_title("Investor Transaction Distribution\nby Age Group", fontsize=12, fontweight="bold")
    
    # Panel 2: Box plot (SIP amount)
    df_sip_only = df_tx[df_tx["transaction_type"] == "SIP"]
    sns.boxplot(
        data=df_sip_only,
        x="age_group",
        y="amount_inr",
        order=["18-25", "26-35", "36-45", "46-55", "56+"],
        showfliers=False,
        ax=ax2,
        palette="Set2"
    )
    ax2.set_title("SIP Amount Distribution\nby Age Group (Outliers Omitted)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Age Group")
    ax2.set_ylabel("SIP Amount (₹)")
    ax2.grid(True, axis="y", linestyle=":", alpha=0.5)
    
    # Add titles on each age group average
    # Mean values are: 18-25: ~10953, 26-35: ~10987, 36-45: ~10886, 46-55: ~11137, 56+: ~11575
    means = df_sip_only.groupby("age_group")["amount_inr"].mean()
    order_ages = ["18-25", "26-35", "36-45", "46-55", "56+"]
    for i, age in enumerate(order_ages):
        val = means.get(age, 0)
        ax2.text(i, val + 200, f"₹{val:,.0f}", ha="center", fontsize=8, color="darkred", fontweight="bold")
        
    plt.suptitle("Investor Demographics & SIP Commitments\n" + SUBTITLE, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_05_investor_demographics.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 05 saved.")


def chart_06_geographic_sip(dfs: dict) -> None:
    """Chart 06: Geographic Distribution of SIP Investments (Bar + Donut, 2 panels)."""
    logger.info("Generating Chart 06: Geographic SIP...")
    df_tx = dfs["tx"]
    df_sip = df_tx[df_tx["transaction_type"] == "SIP"]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Panel 1: Top 10 states by SIP amount
    state_inflows = df_sip.groupby("state")["amount_inr"].sum().reset_index()
    state_inflows = state_inflows.sort_values("amount_inr", ascending=False).head(10)
    
    # Highlight Maharashtra and Madhya Pradesh
    # Madhya Pradesh has largest transactions count/amount in transactions
    # Let's check which states are present and sort
    colors = ["#2980b9" if s not in ["Maharashtra", "Madhya Pradesh"] else "#e74c3c" for s in state_inflows["state"]]
    
    sns.barplot(data=state_inflows, x="amount_inr", y="state", palette=colors, ax=ax1)
    ax1.set_title("Top 10 States by Total SIP Investment", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Total Investment Amount")
    ax1.set_ylabel("State")
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"₹{x/1e7:.1f} Cr"))
    ax1.grid(True, axis="x", linestyle=":", alpha=0.5)
    
    # Panel 2: T30 vs B30 Donut chart
    tier_split = df_sip.groupby("city_tier")["amount_inr"].sum()
    ax2.pie(
        tier_split,
        labels=tier_split.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=["#34495e", "#f1c40f"],
        wedgeprops={"width": 0.5, "edgecolor": "white"}
    )
    ax2.set_title("T30 vs B30 City Tier\nSIP Investment Share", fontsize=12, fontweight="bold")
    
    plt.suptitle("Geographic and Tier Breakdown of SIP Accounts\n" + SUBTITLE, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_06_geographic_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 06 saved.")


def chart_07_folios_growth(dfs: dict) -> None:
    """Chart 07: Folio Count Growth (Plotly Stacked Area)."""
    logger.info("Generating Chart 07: Folio Count Growth...")
    df_folio = dfs["folio"].copy()
    df_folio["parsed_month"] = pd.to_datetime(df_folio["month"] + "-01")
    df_folio = df_folio.sort_values("parsed_month")
    
    # Convert dates to string format for Plotly JSON serialization
    x_dates = df_folio["parsed_month"].dt.strftime("%Y-%m-%d").tolist()
    
    fig = go.Figure()
    
    # Add stacked area traces
    fig.add_trace(go.Scatter(
        x=x_dates, y=df_folio["equity_folios_crore"],
        mode="lines", name="Equity Folios", stackgroup="one",
        line=dict(color="steelblue", width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=x_dates, y=df_folio["debt_folios_crore"],
        mode="lines", name="Debt Folios", stackgroup="one",
        line=dict(color="orange", width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=x_dates, y=df_folio["hybrid_folios_crore"],
        mode="lines", name="Hybrid Folios", stackgroup="one",
        line=dict(color="lightgreen", width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=x_dates, y=df_folio["others_folios_crore"],
        mode="lines", name="Others Folios", stackgroup="one",
        line=dict(color="purple", width=1.5)
    ))
    
    # Add annotations
    fig.add_annotation(x=df_folio["parsed_month"].iloc[0].strftime("%Y-%m-%d"), y=13.26, text="Start: 13.26 Cr",
                       showarrow=True, arrowhead=1, ax=-40, ay=-30, font=dict(color="blue"))
    fig.add_annotation(x=df_folio["parsed_month"].iloc[-1].strftime("%Y-%m-%d"), y=26.12, text="Total: 26.12 Cr Folios",
                       showarrow=True, arrowhead=1, ax=50, ay=-30, font=dict(color="darkgreen", size=11))
                       
    fig.update_layout(
        title=dict(
            text=f"Industry Folio Count Growth — Jan 2022 to Dec 2025 (Crore)<br><sub>{SUBTITLE}</sub>",
            font=dict(size=16, family="DejaVu Sans")
        ),
        xaxis_title="Month",
        yaxis_title="Folios (Crore)",
        template="plotly_white",
        width=1000,
        height=500
    )
    
    fig.write_image(str(CHARTS_DIR / "chart_07_folio_count_growth.png"))
    print("Chart 07 saved.")


def chart_08_risk_return(dfs: dict) -> None:
    """Chart 08: Return vs Risk Scatter Plot (Risk-Return Matrix)."""
    logger.info("Generating Chart 08: Risk-Return Scatter...")
    df_perf = dfs["perf"].copy()
    
    # Add composite size column for bubble size
    df_perf["bubble_size"] = df_perf["aum_crore"] / 1000.0 + 8
    
    fig = px.scatter(
        df_perf,
        x="std_dev_ann_pct",
        y="return_3yr_pct",
        size="bubble_size",
        color="category",
        hover_name="scheme_name",
        hover_data=["sharpe_ratio", "alpha", "beta", "aum_crore"],
        text="amfi_code"
    )
    
    # Horizontal line Nifty 100 benchmark average 3-year return (approx 11.49%)
    fig.add_shape(type="line", x0=0, x1=df_perf["std_dev_ann_pct"].max() + 2,
                  y0=11.49, y1=11.49, line=dict(color="Red", width=1.5, dash="dash"))
    
    fig.add_annotation(x=3, y=11.49, text="Avg Benchmark (Nifty 100: 3yr CAGR)",
                       showarrow=True, arrowhead=1, ax=120, ay=-15, font=dict(color="red", size=9))
                       
    # Add quadrant labels
    fig.add_annotation(x=4, y=22, text="High Return<br>Low Risk (Ideal)", showarrow=False, font=dict(color="green", size=10))
    fig.add_annotation(x=22, y=22, text="High Return<br>High Risk (Aggressive)", showarrow=False, font=dict(color="darkorange", size=10))
    fig.add_annotation(x=4, y=6, text="Low Return<br>Low Risk (Conservative)", showarrow=False, font=dict(color="blue", size=10))
    fig.add_annotation(x=22, y=6, text="Low Return<br>High Risk (Inefficient)", showarrow=False, font=dict(color="red", size=10))

    fig.update_layout(
        title=dict(
            text=f"Risk-Return Matrix — All 40 Funds (3-Year CAGR vs Annualised Std Dev)<br><sub>{SUBTITLE}</sub>",
            font=dict(size=16, family="DejaVu Sans")
        ),
        xaxis_title="Annualised Standard Deviation (%)",
        yaxis_title="3-Year Return CAGR (%)",
        template="plotly_white",
        width=1000,
        height=600
    )
    
    fig.write_image(str(CHARTS_DIR / "chart_08_risk_return_matrix.png"))
    print("Chart 08 saved.")


def chart_09_correlation(dfs: dict) -> None:
    """Chart 09: NAV Return Correlation Matrix (10 Selected Funds)."""
    logger.info("Generating Chart 09: Correlation Heatmap...")
    df_nav = dfs["nav"]
    
    selected_codes = {
        148569: "Mirae ELSS",
        120843: "Kotak Flexi",
        119120: "SBI Gilt",
        102885: "UTI Nifty Index",
        118635: "Nippon ETF",
        148568: "Mirae Large&Mid",
        119551: "SBI Bluechip",
        120507: "ICICI Liquid",
        100033: "HDFC MidCap",
        100025: "HDFC ShortDur"
    }
    
    # Filter nav to selected codes
    df_select = df_nav[df_nav["amfi_code"].isin(selected_codes.keys())].copy()
    
    # Calculate daily percent change returns
    df_select["daily_return"] = df_select.groupby("amfi_code")["nav"].pct_change()
    
    # Pivot returns
    df_pivot = df_select.pivot(index="date", columns="amfi_code", values="daily_return")
    
    # Calculate correlation
    corr = df_pivot.corr()
    
    # Rename index and columns using code names
    corr = corr.rename(index=selected_codes, columns=selected_codes)
    
    # Mask upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    plt.figure(figsize=(11, 9))
    sns.heatmap(
        corr,
        mask=mask,
        cmap="coolwarm",
        annot=True,
        fmt=".2f",
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        annot_kws={"size": 9}
    )
    
    plt.title("Daily Return Correlation Matrix — 10 Diversified Funds\n" + SUBTITLE, fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_09_nav_correlation_matrix.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 09 saved.")


def chart_10_sector_allocation(dfs: dict) -> None:
    """Chart 10: Top Holdings Sector Allocation (Donut Chart)."""
    logger.info("Generating Chart 10: Sector Allocation...")
    df_port = dfs["port"]
    
    # Group by sector and sum weight_pct
    sector_weight = df_port.groupby("sector")["weight_pct"].sum().reset_index()
    sector_weight = sector_weight.sort_values("weight_pct", ascending=False)
    
    # Take top 9 and group others into 'Others'
    top_9 = sector_weight.head(9)
    others_weight = sector_weight.iloc[9:]["weight_pct"].sum()
    others_row = pd.DataFrame([{"sector": "Others", "weight_pct": others_weight}])
    
    sector_chart_data = pd.concat([top_9, others_row])
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    wedges, texts, autotexts = ax.pie(
        sector_chart_data["weight_pct"],
        labels=sector_chart_data["sector"],
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("Set3", len(sector_chart_data)),
        wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 1.5}
    )
    
    # Center text
    ax.text(0, 0, "14\nSectors", ha="center", va="center", fontsize=16, fontweight="bold", color="darkgray")
    
    plt.title("Equity Portfolio Sector Allocation\nAggregated Across All Equity Funds\n" + SUBTITLE, fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_10_sector_allocation.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 10 saved.")


def chart_11_sip_accounts_dual(dfs: dict) -> None:
    """Chart 11: SIP Accounts Growth (Dual Y-Axis)."""
    logger.info("Generating Chart 11: SIP Accounts Growth...")
    df_sip = dfs["sip"].copy()
    df_sip["parsed_month"] = pd.to_datetime(df_sip["month"] + "-01")
    df_sip = df_sip.sort_values("parsed_month")
    
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    # Left axis: SIP Inflow Crore (Bar)
    ax1.bar(df_sip["parsed_month"], df_sip["sip_inflow_crore"], width=20, color="steelblue", alpha=0.7, label="SIP Inflow (₹ Cr)")
    ax1.set_xlabel("Reporting Month")
    ax1.set_ylabel("SIP Inflow (₹ Crore)", color="steelblue")
    ax1.tick_params(axis="y", labelcolor="steelblue")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"₹{x:,.0f} Cr"))
    
    # Right axis: Active SIP Accounts Crore (Line)
    ax2 = ax1.twinx()
    ax2.plot(df_sip["parsed_month"], df_sip["active_sip_accounts_crore"], color="darkorange", linewidth=2.5, marker="o", label="Active SIP Accounts (Cr)")
    ax2.set_ylabel("Active SIP Accounts (Crore)", color="darkorange")
    ax2.tick_params(axis="y", labelcolor="darkorange")
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"{x:.2f} Cr"))
    
    # Annotations
    dec_2025 = df_sip.iloc[-1]
    ax1.text(dec_2025["parsed_month"], dec_2025["sip_inflow_crore"] + 800, f"₹{dec_2025['sip_inflow_crore']:,} Cr", ha="center", fontsize=8, color="darkblue", fontweight="bold")
    ax2.text(dec_2025["parsed_month"], dec_2025["active_sip_accounts_crore"] + 0.1, f"{dec_2025['active_sip_accounts_crore']:.2f} Cr", ha="center", fontsize=8, color="darkorange", fontweight="bold")
    
    plt.title("SIP Inflow (Bars) vs Active SIP Accounts (Line) — 2022 to 2025\n" + SUBTITLE, fontsize=13, fontweight="bold")
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_11_sip_accounts_dual.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 11 saved.")


def chart_12_market_share(dfs: dict) -> None:
    """Chart 12: Fund House Market Share (Stacked Bar over Time)."""
    logger.info("Generating Chart 12: Market Share...")
    df_aum = dfs["aum"].copy()
    
    df_pivot = df_aum.pivot(index="date", columns="fund_house", values="aum_lakh_crore")
    
    # Calculate percentage market share per date row
    df_share = df_pivot.div(df_pivot.sum(axis=1), axis=0) * 100
    
    # Convert dates index to string for plotting
    df_share.index = df_share.index.strftime("%Y-%m-%d")
    
    ax = df_share.plot(kind="bar", stacked=True, figsize=(14, 7), colormap="tab20")
    
    plt.title("Fund House AUM Market Share (%) — 2022 to 2025\n" + SUBTITLE, fontsize=13, fontweight="bold")
    plt.xlabel("Reporting Date")
    plt.ylabel("Market Share (%)")
    plt.xticks(rotation=45)
    plt.legend(title="Fund House", bbox_to_anchor=(1.01, 1), loc="upper left")
    
    # Annotate Dec 2025 SBI market share
    # SBI is the last bar (index 8), we can annotate its section (which starts at 100 - SBI share)
    sbi_share = df_share.loc["2025-12-31", "SBI Mutual Fund"]
    plt.text(8, 100 - (sbi_share / 2.0), f"SBI: {sbi_share:.1f}%", ha="center", fontsize=9, color="white", fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_12_fund_house_market_share.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 12 saved.")


def chart_13_category_inflow_fy25(dfs: dict) -> None:
    """Chart 13: Category Inflow FY25 Bar Chart (Diverging Color)."""
    logger.info("Generating Chart 13: Category Inflow FY25...")
    df_cat = dfs["cat"]
    
    # Filter to FY25
    df_fy25 = df_cat[df_cat["month"] >= "2024-04"].copy()
    cat_inflows = df_fy25.groupby("category")["net_inflow_crore"].sum().reset_index()
    cat_inflows = cat_inflows.sort_values("net_inflow_crore", ascending=False)
    
    # Color top 5 green and bottom 5 red (middle categories get gray or standard colors)
    n_cats = len(cat_inflows)
    colors = []
    for i in range(n_cats):
        if i < 5:
            colors.append("#2ecc71") # Green
        elif i >= n_cats - 5:
            colors.append("#e74c3c") # Red
        else:
            colors.append("#bdc3c7") # Gray
            
    plt.figure(figsize=(14, 8))
    sns.barplot(data=cat_inflows, x="net_inflow_crore", y="category", palette=colors)
    
    # Add text labels on bars
    for idx, row in cat_inflows.iterrows():
        val = row["net_inflow_crore"]
        # Find index in sorting
        sorted_idx = list(cat_inflows["category"]).index(row["category"])
        plt.text(val + 5000, sorted_idx, f"₹{val:,.0f} Cr", va="center", fontsize=8, color="black", fontweight="bold")
        
    plt.title("FY 2024-25 Net Inflows by Fund Category (₹ Crore)\n" + SUBTITLE, fontsize=13, fontweight="bold")
    plt.xlabel("Net Inflow (₹ Crore)")
    plt.ylabel("Category")
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f"₹{x:,.0f} Cr"))
    plt.grid(True, axis="x", linestyle=":", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_13_category_inflow_fy25.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 13 saved.")


def chart_14_transaction_volume(dfs: dict) -> None:
    """Chart 14: Monthly Transaction Volume Over Time."""
    logger.info("Generating Chart 14: Transaction Volume...")
    df_tx = dfs["tx"].copy()
    
    # Create Year-Month period and format to timestamp
    df_tx["month"] = df_tx["transaction_date"].dt.to_period("M")
    tx_grouped = df_tx.groupby(["month", "transaction_type"]).size().reset_index(name="tx_count")
    tx_grouped["month_ts"] = tx_grouped["month"].dt.to_timestamp()
    
    fig, ax = plt.subplots(figsize=(16, 6))
    
    sns.lineplot(data=tx_grouped, x="month_ts", y="tx_count", hue="transaction_type", marker="o", linewidth=2.0, ax=ax)
    
    # Shaded band for overall SIP volume range
    sip_vol = tx_grouped[tx_grouped["transaction_type"] == "SIP"]
    ax.fill_between(sip_vol["month_ts"], sip_vol["tx_count"].min(), sip_vol["tx_count"].max(), color="blue", alpha=0.05, label="SIP Range Band")
    
    # Annotation on Peak month (Jan 2025)
    ax.annotate("Peak Vol (Jan 2025)", xy=(pd.to_datetime("2025-01-01"), 2020), xytext=(pd.to_datetime("2025-03-01"), 2035),
                arrowprops=dict(facecolor="black", shrink=0.08, width=1, headwidth=6))
                
    plt.title("Monthly Transaction Volume by Type — 2024 to 2025\n" + SUBTITLE, fontsize=13, fontweight="bold")
    plt.xlabel("Month")
    plt.ylabel("Number of Transactions")
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_14_monthly_tx_volume.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 14 saved.")


def chart_15_benchmark_performance(dfs: dict) -> None:
    """Chart 15: Benchmark Index Performance (Normalised to 100)."""
    logger.info("Generating Chart 15: Benchmark Index Performance...")
    df_bench = dfs["bench"].copy()
    
    selected_indices = ["Nifty50", "Nifty100", "Nifty_Midcap150", "Bse_Smallcap", "Nifty500"]
    df_bench = df_bench[df_bench["index_name"].isin(selected_indices)]
    
    # Normalise each index to 100 at the start date (Jan 2022)
    normalized_list = []
    for idx in selected_indices:
        df_idx = df_bench[df_bench["index_name"] == idx].sort_values("date").copy()
        if not df_idx.empty:
            base_value = df_idx.iloc[0]["close_value"]
            df_idx["indexed"] = (df_idx["close_value"] / base_value) * 100
            normalized_list.append(df_idx)
            
    df_normalized = pd.concat(normalized_list)
    
    plt.figure(figsize=(14, 7))
    
    # Plot each index
    for idx in selected_indices:
        df_plot = df_normalized[df_normalized["index_name"] == idx].sort_values("date")
        plt.plot(df_plot["date"], df_plot["indexed"], label=idx, linewidth=1.5)
        
        # Label each line at its final value on the right edge
        final_row = df_plot.iloc[-1]
        plt.text(final_row["date"] + pd.Timedelta(days=10), final_row["indexed"], f"{idx}: {final_row['indexed']:.1f}", va="center", fontsize=8, fontweight="bold")
        
    # Baseline line at y=100
    plt.axhline(100, color="black", linestyle="--", alpha=0.5)
    
    plt.title("Benchmark Index Performance — Indexed to 100 (Jan 2022 Base)\n" + SUBTITLE, fontsize=13, fontweight="bold")
    plt.xlabel("Date")
    plt.ylabel("Indexed Level (Base = 100 in Jan 2022)")
    plt.legend(loc="upper left")
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.xlim(right=df_normalized["date"].max() + pd.Timedelta(days=150)) # Extra space for text labels
    
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "chart_15_benchmark_performance_indexed.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Chart 15 saved.")


def main() -> None:
    """Runs all 15 chart generators and outputs status confirmations."""
    print("=" * 60)
    print("      STARTING DAY 3 AUTOMATED CHART GENERATOR")
    print("=" * 60)
    
    try:
        # Load processed datasets
        dfs = load_data()
        
        # Run each chart generator in sequence
        chart_01_nav_trends(dfs)
        chart_02_aum_growth(dfs)
        chart_03_sip_inflows(dfs)
        chart_04_category_heatmap(dfs)
        chart_05_investor_demographics(dfs)
        chart_06_geographic_sip(dfs)
        chart_07_folios_growth(dfs)
        chart_08_risk_return(dfs)
        chart_09_correlation(dfs)
        chart_10_sector_allocation(dfs)
        chart_11_sip_accounts_dual(dfs)
        chart_12_market_share(dfs)
        chart_13_category_inflow_fy25(dfs)
        chart_14_transaction_volume(dfs)
        chart_15_benchmark_performance(dfs)
        
        print("=" * 60)
        print("      ALL 15 CHARTS GENERATED AND SAVED")
        print("=" * 60)
    except Exception as e:
        logger.error(f"Error during chart generation: {e}")
        raise e


if __name__ == "__main__":
    main()
