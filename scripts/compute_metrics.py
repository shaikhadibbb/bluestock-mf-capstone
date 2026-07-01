"""Day 4 Metrics: Compute CAGR, Sharpe, Sortino, Alpha, Beta, VaR and fund scorecard."""

# ============================================================
# Bluestock MF Capstone — Day 4: Standalone Metrics Ingestion & Analysis
# ============================================================
import os
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Constants
RF_ANNUAL   = 0.065          # RBI repo rate proxy (risk-free rate)
RF_DAILY    = RF_ANNUAL / 252
TRADING_DAYS = 252
SUBTITLE = "Source: AMFI India · NAV History 2022–2026 · Bluestock Fintech Capstone"

# Setup plot style
plt.rcParams['figure.dpi'] = 120
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
sns.set_palette('tab10')

# Paths setup
ROOT       = Path(__file__).resolve().parent.parent
PROCESSED  = ROOT / 'data' / 'processed'
REPORTS    = ROOT / 'reports'
CHARTS     = REPORTS / 'charts'
CHARTS.mkdir(parents=True, exist_ok=True)


def compute_returns(df_nav: pd.DataFrame, df_master: pd.DataFrame) -> pd.DataFrame:
    # TODO: make sure date sorting doesn't mess up indexing
    # FIXME: head of returns will be NaN, handles properly?
    print("Computing CAGR and daily returns...")
    
    # Calculate daily returns if not already present
    df_nav = df_nav.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()
    
    results = []
    for amfi in df_nav['amfi_code'].unique():
        df_fund = df_nav[df_nav['amfi_code'] == amfi].sort_values('date')
        nav_series = df_fund['nav']
        daily_ret = df_fund['daily_return'].dropna()
        
        # Full period CAGR (N=1149 trading intervals)
        n_days = len(daily_ret)
        ann_return = (1 + daily_ret).prod() ** (TRADING_DAYS / n_days) - 1
        
        # 1yr CAGR (last 252 trading days)
        # tail(253) has 253 rows, giving 252 daily return intervals
        nav_end = nav_series.iloc[-1]
        nav_start_1yr = nav_series.iloc[-253]
        cagr_1yr = (nav_end / nav_start_1yr) ** (252 / 252) - 1
        
        # 3yr CAGR (last 756 trading days)
        # tail(757) has 757 rows, giving 756 daily return intervals
        nav_start_3yr = nav_series.iloc[-757]
        cagr_3yr = (nav_end / nav_start_3yr) ** (252 / 756) - 1
        
        # Get master info
        m_row = df_master[df_master['amfi_code'] == amfi].iloc[0]
        
        results.append({
            'amfi_code': amfi,
            'scheme_name': m_row['scheme_name'],
            'fund_house': m_row['fund_house'],
            'category': m_row['category'],
            'sub_category': m_row['sub_category'],
            'plan': m_row['plan'],
            'ann_return_pct': ann_return * 100,
            'cagr_1yr_pct': cagr_1yr * 100,
            'cagr_3yr_pct': cagr_3yr * 100
        })
        
    df_returns = pd.DataFrame(results)
    output_path = PROCESSED / 'returns_computed.csv'
    df_returns.to_csv(output_path, index=False)
    print(f"Saved returns_computed.csv: {len(df_returns)} rows")
    return df_returns


def compute_cagr_report(df_returns: pd.DataFrame, df_ref: pd.DataFrame, df_master: pd.DataFrame) -> pd.DataFrame:
    """Task 2: Compare computed CAGR with reference CAGR values."""
    print("Generating CAGR comparison report...")
    
    # Merge computed results with reference return columns
    df_merge = pd.merge(
        df_returns[['amfi_code', 'scheme_name', 'fund_house', 'category', 'plan', 'cagr_1yr_pct', 'cagr_3yr_pct']],
        df_ref[['amfi_code', 'return_3yr_pct', 'return_5yr_pct']],
        on='amfi_code',
        how='left'
    )
    
    df_merge = df_merge.rename(columns={
        'cagr_1yr_pct': 'cagr_1yr_computed',
        'cagr_3yr_pct': 'cagr_3yr_computed',
        'return_3yr_pct': 'cagr_3yr_ref',
        'return_5yr_pct': 'cagr_5yr_ref'
    })
    
    df_merge['diff_3yr_pct'] = df_merge['cagr_3yr_computed'] - df_merge['cagr_3yr_ref']
    
    output_path = PROCESSED / 'cagr_report.csv'
    df_merge.to_csv(output_path, index=False)
    print(f"Saved cagr_report.csv: {len(df_merge)} rows")
    return df_merge


def compute_sharpe(df_nav: pd.DataFrame, df_master: pd.DataFrame, df_ref: pd.DataFrame) -> pd.DataFrame:
    # TODO: Sharpe standard deviation should use excess returns std dev, even if RF_DAILY is constant
    # FIXME: check if we should annualise using daily risk-free or annual risk-free
    print("Computing Sharpe Ratios...")
    
    results = []
    for amfi in df_nav['amfi_code'].unique():
        df_fund = df_nav[df_nav['amfi_code'] == amfi].sort_values('date')
        daily_ret = df_fund['daily_return'].dropna()
        
        # Sharpe full period
        excess_ret_full = daily_ret - RF_DAILY
        sharpe_full = excess_ret_full.mean() / excess_ret_full.std() * np.sqrt(TRADING_DAYS)
        
        # Sharpe 1yr (last 252 returns)
        daily_ret_1yr = daily_ret.tail(252)
        excess_ret_1yr = daily_ret_1yr - RF_DAILY
        sharpe_1yr = excess_ret_1yr.mean() / excess_ret_1yr.std() * np.sqrt(TRADING_DAYS)
        
        m_row = df_master[df_master['amfi_code'] == amfi].iloc[0]
        ref_sharpe = df_ref[df_ref['amfi_code'] == amfi]['sharpe_ratio'].values[0]
        
        results.append({
            'amfi_code': amfi,
            'scheme_name': m_row['scheme_name'],
            'category': m_row['category'],
            'plan': m_row['plan'],
            'sharpe_full': sharpe_full,
            'sharpe_1yr': sharpe_1yr,
            'ref_sharpe': ref_sharpe
        })
        
    df_sharpe = pd.DataFrame(results)
    output_path = PROCESSED / 'sharpe_values.csv'
    df_sharpe.to_csv(output_path, index=False)
    print(f"Saved sharpe_values.csv: {len(df_sharpe)} rows")
    return df_sharpe


def compute_sortino(df_nav: pd.DataFrame, df_master: pd.DataFrame, df_ref: pd.DataFrame) -> pd.DataFrame:
    # TODO: check if standard downside target should be MAR (Minimum Acceptable Return) or 0
    # FIXME: downside calculation is sensitive to choice of risk-free rate proxy
    print("Computing Sortino Ratios...")
    
    results = []
    for amfi in df_nav['amfi_code'].unique():
        df_fund = df_nav[df_nav['amfi_code'] == amfi].sort_values('date')
        daily_ret = df_fund['daily_return'].dropna()
        
        # WIP: Double-check if we need to divide by total N (including positive return days)
        # Yes, downside risk requires dividing by total N. So we take minimum of excess returns and 0.
        excess_returns = daily_ret - RF_DAILY
        downside_returns = np.minimum(excess_returns, 0)
        downside_std = np.sqrt((downside_returns ** 2).mean()) * np.sqrt(TRADING_DAYS)
        
        # HACK: prevent division by zero for cash/liquid funds with zero downside deviation
        if downside_std == 0:
            sortino_full = 0.0  # works for now, will refactor later
        else:
            sortino_full = excess_returns.mean() * TRADING_DAYS / downside_std
            
        # print(f"Debug Sortino for {amfi}: Mean excess = {excess_returns.mean():.6f}, downside std = {downside_std:.6f}")
        
        m_row = df_master[df_master['amfi_code'] == amfi].iloc[0]
        ref_sortino = df_ref[df_ref['amfi_code'] == amfi]['sortino_ratio'].values[0]
        
        results.append({
            'amfi_code': amfi,
            'scheme_name': m_row['scheme_name'],
            'category': m_row['category'],
            'plan': m_row['plan'],
            'sortino_full': sortino_full,
            'ref_sortino': ref_sortino
        })
        
    df_sortino = pd.DataFrame(results)
    output_path = PROCESSED / 'sortino_values.csv'
    df_sortino.to_csv(output_path, index=False)
    print(f"Saved sortino_values.csv: {len(df_sortino)} rows")
    return df_sortino


def compute_alpha_beta(df_nav: pd.DataFrame, df_bench: pd.DataFrame, df_master: pd.DataFrame, df_ref: pd.DataFrame) -> pd.DataFrame:
    """Task 5: Compute Alpha and Beta vs Benchmark using OLS Regression."""
    print("Computing Alpha and Beta vs Benchmark...")
    
    BENCH_MAP = {
        'NIFTY 100 TRI'               : 'NIFTY100',
        'NIFTY 50 TRI'                : 'NIFTY50',
        'Nifty 50 TRI'                : 'NIFTY50',
        'BSE 250 SmallCap TRI'        : 'BSE_SMALLCAP',
        'BSE 250 Small Cap TRI'       : 'BSE_SMALLCAP',
        'CRISIL Dynamic Gilt Index'   : 'CRISIL_GILT',
        'NIFTY Midcap 150 TRI'        : 'NIFTY_MIDCAP150',
        'CRISIL Liquid Fund Index'    : 'CRISIL_LIQUID',
        'CRISIL Short Term Bond Index': 'CRISIL_LIQUID',
        'Nifty Large Midcap 250 TRI'  : 'NIFTY500',
        'Nifty 500 TRI'               : 'NIFTY500',
        'BSE Sensex TRI'              : 'NIFTY50',
    }

    INDEX_RESOLVER = {
        'NIFTY100': 'Nifty100',
        'NIFTY50': 'Nifty50',
        'BSE_SMALLCAP': 'Bse_Smallcap',
        'CRISIL_GILT': 'Crisil_Gilt',
        'NIFTY_MIDCAP150': 'Nifty_Midcap150',
        'CRISIL_LIQUID': 'Crisil_Liquid',
        'NIFTY500': 'Nifty500'
    }

    BENCH_MAP_NORM = {}
    for k, v in BENCH_MAP.items():
        norm_k = ' '.join(k.upper().split())
        BENCH_MAP_NORM[norm_k] = v
    BENCH_MAP_NORM['CRISIL LIQUID FUND AI INDEX'] = 'CRISIL_LIQUID'
    BENCH_MAP_NORM['NIFTY MIDCAP 50 TRI'] = 'NIFTY_MIDCAP150'
    BENCH_MAP_NORM['NIFTY 500 TRI'] = 'NIFTY500'
    BENCH_MAP_NORM['NIFTY LARGE MIDCAP 250 TRI'] = 'NIFTY500'

    # Compute daily return for all indices if not already present
    df_bench = df_bench.sort_values(['index_name', 'date']).reset_index(drop=True)
    if 'daily_return' not in df_bench.columns:
        df_bench['daily_return'] = df_bench.groupby('index_name')['close_value'].pct_change()
    
    results = []
    for amfi in df_nav['amfi_code'].unique():
        df_fund = df_nav[df_nav['amfi_code'] == amfi].sort_values('date')
        fund_ret = df_fund[['date', 'daily_return']].dropna()
        
        m_row = df_master[df_master['amfi_code'] == amfi].iloc[0]
        bench_name = m_row['benchmark']
        norm_b = ' '.join(bench_name.upper().split())
        
        raw_mapped = BENCH_MAP_NORM.get(norm_b)
        mapped_index = INDEX_RESOLVER.get(raw_mapped)
        
        if not mapped_index:
            raise ValueError(f"No benchmark index resolved for: {bench_name}")
            
        bench_ret = df_bench[df_bench['index_name'] == mapped_index][['date', 'daily_return']].dropna()
        
        # Merge on date to align returns
        merged = pd.merge(fund_ret, bench_ret, on='date', suffixes=('_fund', '_bench'))
        
        # OLS regression on excess returns under CAPM
        merged['excess_fund'] = merged['daily_return_fund'] - RF_DAILY
        merged['excess_bench'] = merged['daily_return_bench'] - RF_DAILY
        
        # TODO: double check if OLS regression should include a weight parameter (usually not in simple CAPM)
        # FIXME: check if benchmark mapping is 100% correct for all debt funds
        slope, intercept, r_value, p_value, std_err = stats.linregress(merged['excess_bench'], merged['excess_fund'])
        
        ref_row = df_ref[df_ref['amfi_code'] == amfi].iloc[0]
        
        results.append({
            'amfi_code': amfi,
            'scheme_name': m_row['scheme_name'],
            'category': m_row['category'],
            'benchmark_used': mapped_index,
            'beta_ols': slope,
            'alpha_ann_pct_ols': intercept * TRADING_DAYS * 100,
            'r_squared': r_value**2,
            'ref_alpha': ref_row['alpha'],
            'ref_beta': ref_row['beta']
        })
        
    df_alpha_beta = pd.DataFrame(results)
    output_path = PROCESSED / 'alpha_beta.csv'
    df_alpha_beta.to_csv(output_path, index=False)
    print(f"Saved alpha_beta.csv: {len(df_alpha_beta)} rows")
    return df_alpha_beta


def compute_max_drawdown(df_nav: pd.DataFrame, df_master: pd.DataFrame, df_ref: pd.DataFrame) -> pd.DataFrame:
    # TODO: Verify if drawdown recovery duration calculation should ignore non-business days
    # FIXME: Drawdown dates can be identical if NAV is flat
    print("Computing Maximum Drawdown...")
    
    results = []
    for amfi in df_nav['amfi_code'].unique():
        df_fund = df_nav[df_nav['amfi_code'] == amfi].sort_values('date').copy()
        nav_series = df_fund.set_index('date')['nav']
        
        rolling_max = nav_series.cummax()
        drawdown = (nav_series / rolling_max) - 1.0
        max_dd = drawdown.min()
        dd_start = drawdown.idxmin()
        
        # Last time NAV was at rolling max before the trough date
        peak_date = nav_series.loc[:dd_start].idxmax()
        duration_days = (dd_start - peak_date).days
        
        m_row = df_master[df_master['amfi_code'] == amfi].iloc[0]
        ref_row = df_ref[df_ref['amfi_code'] == amfi].iloc[0]
        
        results.append({
            'amfi_code': amfi,
            'scheme_name': m_row['scheme_name'],
            'category': m_row['category'],
            'max_drawdown_pct': max_dd * 100,
            'peak_date': peak_date.strftime('%Y-%m-%d'),
            'trough_date': dd_start.strftime('%Y-%m-%d'),
            'drawdown_duration_days': duration_days,
            'ref_max_drawdown_pct': ref_row['max_drawdown_pct']
        })
        
    df_drawdown = pd.DataFrame(results)
    output_path = PROCESSED / 'max_drawdown.csv'
    df_drawdown.to_csv(output_path, index=False)
    print(f"Saved max_drawdown.csv: {len(df_drawdown)} rows")
    return df_drawdown


def compute_var_cvar(df_nav: pd.DataFrame, df_master: pd.DataFrame) -> pd.DataFrame:
    """Task 6b (Standout): Compute Historical VaR 95% and CVaR 95%."""
    print("Computing VaR and CVaR...")
    
    results = []
    for amfi in df_nav['amfi_code'].unique():
        df_fund = df_nav[df_nav['amfi_code'] == amfi]
        returns = df_fund['daily_return'].dropna()
        
        # 5th percentile of daily returns
        var_95 = np.percentile(returns, 5)
        # CVaR (Expected Shortfall): mean of returns below VaR threshold
        cvar_95 = returns[returns <= var_95].mean()
        
        m_row = df_master[df_master['amfi_code'] == amfi].iloc[0]
        
        results.append({
            'amfi_code': amfi,
            'scheme_name': m_row['scheme_name'],
            'category': m_row['category'],
            'plan': m_row['plan'],
            'var_95_pct': var_95 * 100,
            'cvar_95_pct': cvar_95 * 100
        })
        
    df_var_cvar = pd.DataFrame(results)
    output_path = PROCESSED / 'var_cvar_report.csv'
    df_var_cvar.to_csv(output_path, index=False)
    print(f"Saved var_cvar_report.csv: {len(df_var_cvar)} rows")
    return df_var_cvar


def build_scorecard(df_ref: pd.DataFrame, df_master: pd.DataFrame) -> pd.DataFrame:
    """Task 7: Build Fund Scorecard using reference metrics."""
    print("Building Fund Scorecard...")
    
    df_score = df_ref.copy()
    n = len(df_score)
    
    df_score['score_return']  = df_score['return_3yr_pct'].rank(ascending=True)  / n * 100
    df_score['score_sharpe']  = df_score['sharpe_ratio'].rank(ascending=True)     / n * 100
    df_score['score_alpha']   = df_score['alpha'].rank(ascending=True)            / n * 100
    df_score['score_expense'] = df_score['expense_ratio_pct'].rank(ascending=False) / n * 100  # lower cost = better rank
    df_score['score_maxdd']   = df_score['max_drawdown_pct'].rank(ascending=False)  / n * 100  # less negative = better rank

    df_score['composite_score'] = (
        0.30 * df_score['score_return'] +
        0.25 * df_score['score_sharpe'] +
        0.20 * df_score['score_alpha'] +
        0.15 * df_score['score_expense'] +
        0.10 * df_score['score_maxdd']
    ).round(2)
    
    df_score['score_rank'] = df_score['composite_score'].rank(ascending=False).astype(int)
    
    # Select columns
    output_cols = [
        'amfi_code', 'scheme_name', 'fund_house', 'category', 'plan',
        'return_3yr_pct', 'sharpe_ratio', 'alpha', 'expense_ratio_pct',
        'max_drawdown_pct', 'composite_score', 'score_rank',
        'score_return', 'score_sharpe', 'score_alpha', 'score_expense', 'score_maxdd'
    ]
    df_scorecard = df_score[output_cols].sort_values('score_rank').reset_index(drop=True)
    
    output_path = PROCESSED / 'fund_scorecard.csv'
    df_scorecard.to_csv(output_path, index=False)
    print(f"Saved fund_scorecard.csv: {len(df_scorecard)} rows")
    return df_scorecard


def generate_charts(df_nav: pd.DataFrame, df_bench: pd.DataFrame, df_master: pd.DataFrame, df_returns: pd.DataFrame, df_scorecard: pd.DataFrame) -> None:
    """Generate Charts 16, 17, and 18."""
    print("Generating premium charts...")
    
    # ----------------- CHART 16: 2-Panel Benchmark Comparison -----------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Panel 1: NAV Indexed to 100 (top 5 funds vs benchmarks)
    top_5_funds = df_returns.sort_values('ann_return_pct', ascending=False).head(5)['amfi_code'].tolist()
    
    # Fetch start date base for NAV
    df_nav_indexed = df_nav.copy()
    
    # Plot top 5 funds
    for amfi in top_5_funds:
        df_fund = df_nav_indexed[df_nav_indexed['amfi_code'] == amfi].sort_values('date')
        base_nav = df_fund['nav'].iloc[0]
        indexed_nav = (df_fund['nav'] / base_nav) * 100
        scheme_label = df_master[df_master['amfi_code'] == amfi]['scheme_name'].iloc[0].split("Fund")[0].strip()
        
        ax1.plot(df_fund['date'], indexed_nav, label=scheme_label, linewidth=1.5)
        # Annotate right edge
        ax1.text(df_fund['date'].iloc[-1] + pd.Timedelta(days=15), indexed_nav.iloc[-1], f"{indexed_nav.iloc[-1]:.1f}", va='center', fontsize=9)
        
    # Plot benchmarks Nifty50 and Nifty100
    df_bench = df_bench.sort_values(['index_name', 'date']).reset_index(drop=True)
    if 'daily_return' not in df_bench.columns:
        df_bench['daily_return'] = df_bench.groupby('index_name')['close_value'].pct_change()
        
    for index_name, color in [('Nifty50', 'black'), ('Nifty100', 'dimgray')]:
        df_b = df_bench[df_bench['index_name'] == index_name].sort_values('date')
        base_val = df_b['close_value'].iloc[0]
        indexed_bench = (df_b['close_value'] / base_val) * 100
        
        ax1.plot(df_b['date'], indexed_bench, label=index_name, color=color, linestyle='--', linewidth=2.0)
        # Annotate right edge
        ax1.text(df_b['date'].iloc[-1] + pd.Timedelta(days=15), indexed_bench.iloc[-1], f"{indexed_bench.iloc[-1]:.1f}", va='center', fontsize=9)
        
    ax1.set_title("NAV Indexed to 100 (Top 5 Funds vs Indices)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Date", fontsize=10)
    ax1.set_ylabel("Indexed Value (Base = 100)", fontsize=10)
    ax1.legend(loc='upper left', frameon=False)
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.set_xlim(right=df_nav_indexed['date'].max() + pd.Timedelta(days=180))
    
    # Panel 2: Tracking Error Horizontal Bar Chart
    # Compute Tracking Error for all 40 funds vs their mapped benchmark
    BENCH_MAP = {
        'NIFTY 100 TRI'               : 'NIFTY100',
        'NIFTY 50 TRI'                : 'NIFTY50',
        'Nifty 50 TRI'                : 'NIFTY50',
        'BSE 250 SmallCap TRI'        : 'BSE_SMALLCAP',
        'BSE 250 Small Cap TRI'       : 'BSE_SMALLCAP',
        'CRISIL Dynamic Gilt Index'   : 'CRISIL_GILT',
        'NIFTY Midcap 150 TRI'        : 'NIFTY_MIDCAP150',
        'CRISIL Liquid Fund Index'    : 'CRISIL_LIQUID',
        'CRISIL Short Term Bond Index': 'CRISIL_LIQUID',
        'Nifty Large Midcap 250 TRI'  : 'NIFTY500',
        'Nifty 500 TRI'               : 'NIFTY500',
        'BSE Sensex TRI'              : 'NIFTY50',
    }

    INDEX_RESOLVER = {
        'NIFTY100': 'Nifty100',
        'NIFTY50': 'Nifty50',
        'BSE_SMALLCAP': 'Bse_Smallcap',
        'CRISIL_GILT': 'Crisil_Gilt',
        'NIFTY_MIDCAP150': 'Nifty_Midcap150',
        'CRISIL_LIQUID': 'Crisil_Liquid',
        'NIFTY500': 'Nifty500'
    }

    BENCH_MAP_NORM = {}
    for k, v in BENCH_MAP.items():
        norm_k = ' '.join(k.upper().split())
        BENCH_MAP_NORM[norm_k] = v
    BENCH_MAP_NORM['CRISIL LIQUID FUND AI INDEX'] = 'CRISIL_LIQUID'
    BENCH_MAP_NORM['NIFTY MIDCAP 50 TRI'] = 'NIFTY_MIDCAP150'
    BENCH_MAP_NORM['NIFTY 500 TRI'] = 'NIFTY500'
    BENCH_MAP_NORM['NIFTY LARGE MIDCAP 250 TRI'] = 'NIFTY500'
    
    te_results = []
    for amfi in df_nav_indexed['amfi_code'].unique():
        df_fund = df_nav_indexed[df_nav_indexed['amfi_code'] == amfi].sort_values('date')
        fund_ret = df_fund[['date', 'daily_return']].dropna()
        
        m_row = df_master[df_master['amfi_code'] == amfi].iloc[0]
        bench_name = m_row['benchmark']
        norm_b = ' '.join(bench_name.upper().split())
        mapped_index = INDEX_RESOLVER.get(BENCH_MAP_NORM.get(norm_b))
        
        bench_ret = df_bench[df_bench['index_name'] == mapped_index][['date', 'daily_return']].dropna()
        
        merged = pd.merge(fund_ret, bench_ret, on='date', suffixes=('_fund', '_bench'))
        diff_ret = merged['daily_return_fund'] - merged['daily_return_bench']
        te = diff_ret.std() * np.sqrt(TRADING_DAYS) * 100
        
        te_results.append({
            'amfi_code': amfi,
            'scheme_name': m_row['scheme_name'],
            'sub_category': m_row['sub_category'],
            'tracking_error': te
        })
        
    df_te = pd.DataFrame(te_results).sort_values('tracking_error')
    
    # Create horizontal bar chart colored by sub_category
    unique_subcats = df_te['sub_category'].dropna().unique()
    colors_palette = sns.color_palette("Set2", len(unique_subcats))
    subcat_color_map = dict(zip(unique_subcats, colors_palette))
    bar_colors = [subcat_color_map.get(sc, 'gray') for sc in df_te['sub_category']]
    
    y_pos = np.arange(len(df_te))
    # Simplify labels for display
    short_labels = [name.split("Fund")[0].strip() for name in df_te['scheme_name']]
    
    ax2.barh(y_pos, df_te['tracking_error'], color=bar_colors, height=0.75, alpha=0.8)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(short_labels, fontsize=7)
    ax2.set_xlabel("Annualised Tracking Error (%)", fontsize=10)
    ax2.set_title("Annualised Tracking Error vs Mapped Benchmark", fontsize=12, fontweight='bold')
    ax2.axvline(5.0, color='crimson', linestyle=':', linewidth=1.5, label='TE=5% Threshold')
    
    # Create custom legend for subcategories
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, label=sc) for sc, color in subcat_color_map.items()]
    legend_elements.append(plt.Line2D([0], [0], color='crimson', linestyle=':', label='5% TE Threshold'))
    ax2.legend(handles=legend_elements, loc='lower right', frameon=False, fontsize=8)
    ax2.grid(True, axis='x', linestyle=':', alpha=0.5)
    
    plt.suptitle("Benchmark Performance Comparison & Volatility Tracking\n" + SUBTITLE, fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig(CHARTS / 'chart_16_benchmark_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved chart_16_benchmark_comparison.png")
    
    # ----------------- CHART 17: Rolling 90-Day Sharpe Chart -----------------
    plt.figure(figsize=(14, 7))
    rep_funds = {
        119551: 'SBI Bluechip Reg (Large Cap)',
        119598: 'SBI Small Cap Reg (Small Cap)',
        125497: 'HDFC Top 100 Direct (Large Cap Direct)',
        100016: 'HDFC Top 100 Reg (Large Cap Regular)',
        120507: 'ICICI Pru Liquid Reg (Liquid / Debt)'
    }
    
    for amfi, label in rep_funds.items():
        df_fund = df_nav_indexed[df_nav_indexed['amfi_code'] == amfi].sort_values('date')
        # Compute rolling 90-day Sharpe
        rolling_sharpe = df_fund['daily_return'].rolling(90).apply(
            lambda x: (x.mean() - RF_DAILY) / x.std() * np.sqrt(TRADING_DAYS) if x.std() > 0 else np.nan
        )
        
        plt.plot(df_fund['date'], rolling_sharpe, label=label, linewidth=1.5)
        
    plt.axhline(1.0, color='green', linestyle='--', alpha=0.6, label='Good Sharpe (1.0)')
    plt.axhline(0.0, color='red', linestyle='-.', alpha=0.6, label='Break-even (0.0)')
    plt.title("Rolling 90-Day Sharpe Ratio Over Time\n" + SUBTITLE, fontsize=13, fontweight='bold')
    plt.xlabel("Date", fontsize=10)
    plt.ylabel("Rolling Sharpe Ratio (Annualised)", fontsize=10)
    plt.legend(loc='upper right', frameon=False)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(CHARTS / 'chart_17_rolling_sharpe.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved chart_17_rolling_sharpe.png")
    
    # ----------------- CHART 18: Scorecard Heatmap -----------------
    plt.figure(figsize=(12, 8))
    # Take top 15 funds in scorecard
    df_heatmap = df_scorecard.head(15).copy()
    df_heatmap = df_heatmap.set_index('scheme_name')
    
    # Heatmap metric scores to plot
    score_cols = ['score_return', 'score_sharpe', 'score_alpha', 'score_expense', 'score_maxdd', 'composite_score']
    df_heatmap_plot = df_heatmap[score_cols]
    
    # Clean index names
    df_heatmap_plot.index = [name.split("Fund")[0].strip() for name in df_heatmap_plot.index]
    
    # Plot heatmap
    ax = sns.heatmap(
        df_heatmap_plot, 
        annot=True, 
        cmap='RdYlGn', 
        fmt='.2f', 
        linewidths=0.5, 
        cbar_kws={'label': 'Score Rank Percentile / Composite Score'}
    )
    
    # Format labels
    ax.set_xticklabels(['3yr CAGR Score', 'Sharpe Score', 'Alpha Score', 'Expense Score', 'Max DD Score', 'Composite Score'], rotation=15, ha='right')
    plt.title("Fund Scorecard Breakdown — Top 15 Mutual Funds\n" + SUBTITLE, fontsize=13, fontweight='bold')
    plt.ylabel("Mutual Fund Scheme", fontsize=10)
    plt.tight_layout()
    plt.savefig(CHARTS / 'chart_18_scorecard_heatmap.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved chart_18_scorecard_heatmap.png")


def main():
    print("Loading processed datasets...")
    df_master = pd.read_csv(PROCESSED / 'clean_fund_master.csv')
    df_nav    = pd.read_csv(PROCESSED / 'clean_nav.csv', parse_dates=['date'])
    df_ref    = pd.read_csv(PROCESSED / 'clean_performance.csv')
    df_bench  = pd.read_csv(PROCESSED / 'clean_benchmark_indices.csv', parse_dates=['date'])
    
    # Sort nav
    df_nav = df_nav.sort_values(['amfi_code', 'date']).reset_index(drop=True)
    df_nav['daily_return'] = df_nav.groupby('amfi_code')['nav'].pct_change()
    
    # Task 1: CAGR and daily returns
    df_returns = compute_returns(df_nav, df_master)
    
    # Task 2: CAGR comparison report
    df_cagr_rep = compute_cagr_report(df_returns, df_ref, df_master)
    
    # Task 3: Sharpe Ratios
    df_sharpe = compute_sharpe(df_nav, df_master, df_ref)
    
    # Task 4: Sortino Ratios
    df_sortino = compute_sortino(df_nav, df_master, df_ref)
    
    # Task 5: Alpha and Beta OLS vs Benchmark
    df_alpha_beta = compute_alpha_beta(df_nav, df_bench, df_master, df_ref)
    
    # Task 6: Maximum Drawdown
    df_drawdown = compute_max_drawdown(df_nav, df_master, df_ref)
    
    # Task 6b: VaR and CVaR
    df_var_cvar = compute_var_cvar(df_nav, df_master)
    
    # Task 7: Scorecard Ranking
    df_scorecard = build_scorecard(df_ref, df_master)
    
    # Task 8, 9, 9b: Premium Visualizations
    generate_charts(df_nav, df_bench, df_master, df_returns, df_scorecard)
    
    # Get Safest Fund (Lowest Tracking Error vs mapped benchmark)
    # Let's compute that to print it in the validation summary
    te_list = []
    BENCH_MAP = {
        'NIFTY 100 TRI'               : 'NIFTY100',
        'NIFTY 50 TRI'                : 'NIFTY50',
        'Nifty 50 TRI'                : 'NIFTY50',
        'BSE 250 SmallCap TRI'        : 'BSE_SMALLCAP',
        'BSE 250 Small Cap TRI'       : 'BSE_SMALLCAP',
        'CRISIL Dynamic Gilt Index'   : 'CRISIL_GILT',
        'NIFTY Midcap 150 TRI'        : 'NIFTY_MIDCAP150',
        'CRISIL Liquid Fund Index'    : 'CRISIL_LIQUID',
        'CRISIL Short Term Bond Index': 'CRISIL_LIQUID',
        'Nifty Large Midcap 250 TRI'  : 'NIFTY500',
        'Nifty 500 TRI'               : 'NIFTY500',
        'BSE Sensex TRI'              : 'NIFTY50',
    }

    INDEX_RESOLVER = {
        'NIFTY100': 'Nifty100',
        'NIFTY50': 'Nifty50',
        'BSE_SMALLCAP': 'Bse_Smallcap',
        'CRISIL_GILT': 'Crisil_Gilt',
        'NIFTY_MIDCAP150': 'Nifty_Midcap150',
        'CRISIL_LIQUID': 'Crisil_Liquid',
        'NIFTY500': 'Nifty500'
    }

    BENCH_MAP_NORM = {}
    for k, v in BENCH_MAP.items():
        norm_k = ' '.join(k.upper().split())
        BENCH_MAP_NORM[norm_k] = v
    BENCH_MAP_NORM['CRISIL LIQUID FUND AI INDEX'] = 'CRISIL_LIQUID'
    BENCH_MAP_NORM['NIFTY MIDCAP 50 TRI'] = 'NIFTY_MIDCAP150'
    BENCH_MAP_NORM['NIFTY 500 TRI'] = 'NIFTY500'
    BENCH_MAP_NORM['NIFTY LARGE MIDCAP 250 TRI'] = 'NIFTY500'
    
    # Compute daily return for indices
    df_bench['daily_return'] = df_bench.groupby('index_name')['close_value'].pct_change()
    
    for amfi in df_nav['amfi_code'].unique():
        df_fund = df_nav[df_nav['amfi_code'] == amfi].sort_values('date')
        fund_ret = df_fund[['date', 'daily_return']].dropna()
        m_row = df_master[df_master['amfi_code'] == amfi].iloc[0]
        bench_name = m_row['benchmark']
        norm_b = ' '.join(bench_name.upper().split())
        mapped_index = INDEX_RESOLVER.get(BENCH_MAP_NORM.get(norm_b))
        bench_ret = df_bench[df_bench['index_name'] == mapped_index][['date', 'daily_return']].dropna()
        merged = pd.merge(fund_ret, bench_ret, on='date', suffixes=('_fund', '_bench'))
        diff_ret = merged['daily_return_fund'] - merged['daily_return_bench']
        te = diff_ret.std() * np.sqrt(TRADING_DAYS) * 100
        te_list.append((m_row['scheme_name'], te))
        
    te_list.sort(key=lambda x: x[1])
    safest_fund, min_te = te_list[0]
    
    # Print summary block
    print("\n" + "="*60)
    print("PERFORMANCE ANALYTICS — DAY 4 SUMMARY")
    print("="*60)
    print(f"Funds analysed          : {len(df_returns)}")
    print("Metrics computed        : CAGR (1yr, 3yr, full), Sharpe, Sortino,")
    print("                          Alpha (OLS), Beta (OLS), Max Drawdown,")
    print("                          VaR 95%, CVaR 95%, Tracking Error")
    print("Risk-free rate used     : 6.50% p.a. (RBI repo rate proxy)")
    print("Trading days convention : 252 per year")
    print(f"NAV data period         : {df_nav['date'].min().date()} → {df_nav['date'].max().date()} ({len(df_nav.groupby('amfi_code').size().unique())} groups, {df_nav.groupby('amfi_code').size().unique()[0]} days)")
    print("\nTop fund overall (composite score):")
    print(f"  #1  {df_scorecard.iloc[0]['scheme_name']} -> Score: {df_scorecard.iloc[0]['composite_score']}")
    print(f"  #2  {df_scorecard.iloc[1]['scheme_name']} -> Score: {df_scorecard.iloc[1]['composite_score']}")
    print(f"  #3  {df_scorecard.iloc[2]['scheme_name']} -> Score: {df_scorecard.iloc[2]['composite_score']}")
    print(f"\nHighest 3yr return (ref): {df_ref.sort_values('return_3yr_pct', ascending=False).iloc[0]['scheme_name']} -> {df_ref['return_3yr_pct'].max()}%")
    print(f"Highest Sharpe (ref):     {df_ref.sort_values('sharpe_ratio', ascending=False).iloc[0]['scheme_name']} -> {df_ref['sharpe_ratio'].max()}")
    print(f"Worst Max Drawdown:       {df_drawdown.sort_values('max_drawdown_pct').iloc[0]['scheme_name']} -> {df_drawdown['max_drawdown_pct'].min():.2f}%")
    print(f"Safest fund (lowest TE):  {safest_fund} -> {min_te:.2f}%")
    print("\nOutput files:")
    print(f"  returns_computed.csv    ({len(df_returns)} rows)")
    print(f"  cagr_report.csv         ({len(df_cagr_rep)} rows)")
    print(f"  sharpe_values.csv       ({len(df_sharpe)} rows)")
    print(f"  sortino_values.csv      ({len(df_sortino)} rows)")
    print(f"  alpha_beta.csv          ({len(df_alpha_beta)} rows)")
    print(f"  max_drawdown.csv        ({len(df_drawdown)} rows)")
    print(f"  fund_scorecard.csv      ({len(df_scorecard)} rows)")
    print(f"  var_cvar_report.csv     ({len(df_var_cvar)} rows)")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
