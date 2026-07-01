"""ETL and Data Ingestion Pipeline for Bluestock Mutual Fund Capstone.

This module loads the 10 real-world CSV datasets, prints metadata audits,
flags anomalies, explores fund master dimensions, performs AMFI code cross-validation,
and outputs a Data Quality report to reports/data_quality_day1.txt.
"""

import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
import pandas as pd

# --- Section: Logging & Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("data_ingestion")

# Dict mapping dataset identifiers to actual filenames in the workspace
DATASETS = {
    "01_fund_master": "01_fund_master.csv",
    "02_nav_history": "02_nav_history.csv",
    "03_aum_by_fund_house": "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "05_category_inflows": "05_category_inflows.csv",
    "06_industry_folio_count": "06_industry_folio_count.csv",
    "07_scheme_performance": "07_scheme_performance.csv",
    "08_investor_transactions": "08_investor_transactions.csv",
    "09_portfolio_holdings": "09_portfolio_holdings.csv",
    "10_benchmark_indices": "10_benchmark_indices.csv"
}


def load_all_datasets(raw_dir: Path) -> Dict[str, pd.DataFrame]:
    # TODO: verify if any files are missing before starting load loop
    # FIXME: pd.read_csv can fail if CSV has encoding issues
    dfs = {}
    for key, filename in DATASETS.items():
        file_path = raw_dir / filename
        try:
            # print(f"DEBUG: Loading CSV file from {file_path}")
            dfs[key] = pd.read_csv(file_path)
            logger.info(f"Successfully loaded {filename} (Shape: {dfs[key].shape})")
        except Exception as e:
            logger.error(f"Error loading file {filename}: {e}")
            raise e
    return dfs


def print_dataset_audits(dfs: Dict[str, pd.DataFrame]) -> None:
    """Prints a structured metadata audit block for each DataFrame.

    Args:
        dfs: Dict of loaded DataFrames.
    """
    print("\n" + "=" * 60)
    print("                 DATASET QUALITY AUDIT LOGS")
    print("=" * 60)
    
    for key, df in dfs.items():
        filename = DATASETS[key]
        
        # Calculate null columns and formatting
        null_counts = df.isnull().sum()
        null_cols = null_counts[null_counts > 0]
        if null_cols.empty:
            nulls_str = "None"
        else:
            nulls_str = ", ".join([f"{col}: {cnt}" for col, cnt in null_cols.items()])
            
        print(f"\n============================================================")
        print(f" Dataset: {filename}")
        print(f" Shape  : {df.shape}")
        print(f" Nulls  : {nulls_str}")
        print(f"============================================================")
        print("Column Types:")
        for col, dtype in df.dtypes.items():
            print(f"  - {col}: {dtype}")
        print("\nFirst 3 Rows:")
        print(df.head(3).to_string())
        print("-" * 60)


def check_data_anomalies(dfs: Dict[str, pd.DataFrame]) -> None:
    """Checks and flags specific known anomalies in the key datasets.

    Checks:
    - 02_nav_history: NAV values <= 0
    - 08_investor_transactions: amount_inr <= 0
    - 01_fund_master: duplicate amfi_code values

    Args:
        dfs: Dict of loaded DataFrames.
    """
    print("\n" + "=" * 60)
    print("                 ANOMALY DETECTION REPORT")
    print("=" * 60)

    # 1. 02_nav_history.csv — check for any NAV values <= 0
    if "02_nav_history" in dfs:
        df_nav = dfs["02_nav_history"]
        invalid_nav = df_nav[df_nav["nav"] <= 0]
        if not invalid_nav.empty:
            logger.warning(f"Found {len(invalid_nav)} rows in 02_nav_history.csv with NAV <= 0!")
            print(invalid_nav.head(5).to_string())
        else:
            print("02_nav_history.csv: No NAV values <= 0 (all pricing is positive).")

    # 2. 08_investor_transactions.csv — check for any amount_inr <= 0
    if "08_investor_transactions" in dfs:
        df_tx = dfs["08_investor_transactions"]
        invalid_tx = df_tx[df_tx["amount_inr"] <= 0]
        if not invalid_tx.empty:
            logger.warning(f"Found {len(invalid_tx)} rows in 08_investor_transactions.csv with amount_inr <= 0!")
            print(invalid_tx.head(5).to_string())
        else:
            print("08_investor_transactions.csv: No transactions with amount_inr <= 0.")

    # 3. 01_fund_master.csv — check for duplicate amfi_code values
    if "01_fund_master" in dfs:
        df_master = dfs["01_fund_master"]
        duplicates = df_master[df_master.duplicated(subset=["amfi_code"], keep=False)]
        if not duplicates.empty:
            logger.warning(f"Found {len(duplicates)} duplicate amfi_code entries in 01_fund_master.csv!")
            print(duplicates.to_string())
        else:
            print("01_fund_master.csv: No duplicate amfi_code values found.")
            
    print("=" * 60)


def print_summary_table(dfs: Dict[str, pd.DataFrame]) -> None:
    """Prints a summary table listing: dataset | rows | cols | null_cols.

    Args:
        dfs: Dict of loaded DataFrames.
    """
    print("\n" + "=" * 60)
    print("                 DATASETS SUMMARY TABLE")
    print("=" * 60)
    
    summary_data = []
    for key, df in dfs.items():
        filename = DATASETS[key]
        null_counts = df.isnull().sum()
        null_cols_count = len(null_counts[null_counts > 0])
        summary_data.append({
            "Dataset": filename,
            "Rows": df.shape[0],
            "Cols": df.shape[1],
            "Null Columns": null_cols_count
        })
        
    df_summary = pd.DataFrame(summary_data)
    print(df_summary.to_string(index=False))
    print("=" * 60)


def print_nav_insights(df_nav: pd.DataFrame, df_master: pd.DataFrame) -> None:
    """Prints mini insights regarding the NAV metrics in historical datasets.

    Args:
        df_nav: Historical NAV DataFrame.
        df_master: Fund master DataFrame to map amfi_codes to names.
    """
    print("\n" + "=" * 60)
    print("                 NAV ANALYTICAL INSIGHTS")
    print("=" * 60)
    
    # Identify highest and lowest historical NAV values
    max_idx = df_nav["nav"].idxmax()
    min_idx = df_nav["nav"].idxmin()
    
    max_nav_row = df_nav.loc[max_idx]
    min_nav_row = df_nav.loc[min_idx]
    
    # Map codes to names
    name_map = df_master.set_index("amfi_code")["scheme_name"].to_dict()
    
    max_name = name_map.get(max_nav_row["amfi_code"], f"AMFI {max_nav_row['amfi_code']}")
    min_name = name_map.get(min_nav_row["amfi_code"], f"AMFI {min_nav_row['amfi_code']}")
    
    print(f"Highest Historical NAV: Rs. {max_nav_row['nav']:.4f} ({max_name} on {max_nav_row['date']})")
    print(f"Lowest Historical NAV : Rs. {min_nav_row['nav']:.4f} ({min_name} on {min_nav_row['date']})")
    print(f"Overall NAV Range     : Rs. {df_nav['nav'].min():.4f} to Rs. {df_nav['nav'].max():.4f}")
    print("=" * 60)


def explore_fund_master(df: pd.DataFrame) -> None:
    """Explores fund houses, categories, plan splits, and expense ratios.

    Args:
        df: Fund master DataFrame.
    """
    print("\n" + "=" * 60)
    print("                 FUND MASTER EXPLORATION")
    print("=" * 60)
    
    # 1. Unique fund houses and their count of schemes
    print("\n--- Scheme Counts by Fund House ---")
    print(df["fund_house"].value_counts().to_string())
    
    # 2. Unique categories and sub-categories (cross-tab)
    print("\n--- Category vs Sub-Category Cross-Tabulation ---")
    crosstab = pd.crosstab(df["category"], df["sub_category"])
    print(crosstab.to_string())
    
    # 3. Risk category distribution
    print("\n--- Risk Category Distribution ---")
    print(df["risk_category"].value_counts().to_string())
    
    # 4. Plan split (Regular vs Direct)
    print("\n--- Plan Split ---")
    print(df["plan"].value_counts().to_string())
    
    # 5. Expense ratio range: min, max, mean by category
    print("\n--- Expense Ratio Stats by Category ---")
    expense_stats = df.groupby("category")["expense_ratio_pct"].agg(["min", "max", "mean"])
    print(expense_stats.to_string())
    
    # 6. Unique SEBI category codes mapping
    print("\n--- SEBI Category Code Mapping (Inferred) ---")
    # Group by code and get unique sub-category values
    sebi_groups = df.groupby("sebi_category_code")["sub_category"].unique().to_dict()
    for code, subs in sebi_groups.items():
        print(f"  - {code}: {', '.join(subs)}")
        
    # Print human-readable summary paragraph
    num_houses = df["fund_house"].nunique()
    num_cats = df["category"].nunique()
    num_subs = df["sub_category"].nunique()
    
    risk_counts = df["risk_category"].value_counts().to_dict()
    low_cnt = risk_counts.get("Low", 0)
    mod_cnt = risk_counts.get("Moderate", 0) + risk_counts.get("Moderately High", 0)
    high_cnt = risk_counts.get("High", 0)
    vhigh_cnt = risk_counts.get("Very High", 0)
    
    min_exp = df["expense_ratio_pct"].min()
    max_exp = df["expense_ratio_pct"].max()
    mean_exp = df["expense_ratio_pct"].mean()
    
    print("\n--- FUND MASTER SUMMARY ---")
    print(
        f"The dataset covers {num_houses} fund houses across {num_cats} categories and "
        f"{num_subs} sub-categories.\n"
        f"Risk breakdown: Low: {low_cnt}, Moderate/Moderately High: {mod_cnt}, "
        f"High: {high_cnt}, Very High: {vhigh_cnt}\n"
        f"Expense ratios range from {min_exp:.2f}% to {max_exp:.2f}% (mean: {mean_exp:.2f}%)."
    )
    print("=" * 60)


def validate_amfi_codes(
    df_master: pd.DataFrame,
    df_nav: pd.DataFrame,
    reports_dir: Path
) -> Tuple[Dict, str]:
    """Validates the referential integrity of AMFI codes between master and history.

    Args:
        df_master: Fund master DataFrame.
        df_nav: NAV history DataFrame.
        reports_dir: Directory to save the final report.

    Returns:
        A tuple of (validation_summary_dict, report_string).
    """
    logger.info("Starting AMFI code validation...")
    
    # Retrieve code sets
    master_codes = set(df_master["amfi_code"].dropna().unique())
    nav_codes = set(df_nav["amfi_code"].dropna().unique())
    
    missing_nav_codes = master_codes.difference(nav_codes)
    orphan_nav_codes = nav_codes.difference(master_codes)
    
    # Compile coverage metrics for each scheme
    coverage_rows = []
    name_map = df_master.set_index("amfi_code")["scheme_name"].to_dict()
    
    for code in sorted(master_codes):
        df_scheme_nav = df_nav[df_nav["amfi_code"] == code]
        row_count = len(df_scheme_nav)
        if row_count > 0:
            min_date = df_scheme_nav["date"].min()
            max_date = df_scheme_nav["date"].max()
        else:
            min_date, max_date = "N/A", "N/A"
            
        coverage_rows.append({
            "amfi_code": code,
            "scheme_name": name_map.get(code, "Unknown"),
            "nav_rows": row_count,
            "date_min": min_date,
            "date_max": max_date
        })
        
    # Determine Data Readiness Score (0-100)
    # Completeness (40/40 codes present) = 40 pts
    # API / Pricing coverage (No missing NAVs) = 30 pts
    # Anomaly absence (No NAV <= 0, no duplicate amfi_code) = 30 pts
    completeness_score = 40.0 * (len(master_codes - missing_nav_codes) / len(master_codes))
    pricing_score = 30.0 if not missing_nav_codes else 15.0
    
    has_pos_nav = (df_nav["nav"] > 0).all()
    has_no_master_dups = not df_master.duplicated(subset=["amfi_code"]).any()
    anomaly_score = 30.0
    if not has_pos_nav:
        anomaly_score -= 15.0
    if not has_no_master_dups:
        anomaly_score -= 15.0
        
    readiness_score = int(completeness_score + pricing_score + anomaly_score)

    # Format the report string
    report_lines = [
        "DATA QUALITY REPORT — AMFI CODE VALIDATION",
        "============================================",
        f"Total codes in fund_master    : {len(master_codes)}",
        f"Total codes in nav_history    : {len(nav_codes)}",
        f"Codes in master, missing NAV  : {len(missing_nav_codes)} {list(missing_nav_codes) if missing_nav_codes else ''}",
        f"Orphan NAV codes (no master)  : {len(orphan_nav_codes)} {list(orphan_nav_codes) if orphan_nav_codes else ''}"
    ]
    
    if not missing_nav_codes and not orphan_nav_codes:
        report_lines.append(f"All {len(master_codes)} codes validated ")
    else:
        report_lines.append("Validation complete with mismatch warnings.")
        
    report_lines.append("\nNAV coverage per fund:")
    report_lines.append(f"{'amfi_code':<10} | {'scheme_name':<55} | {'nav_rows':<8} | {'date_min':<10} | {'date_max':<10}")
    report_lines.append("-" * 105)
    
    for row in coverage_rows:
        short_name = row['scheme_name']
        if len(short_name) > 55:
            short_name = short_name[:52] + "..."
        report_lines.append(
            f"{row['amfi_code']:<10} | {short_name:<55} | {row['nav_rows']:<8} | {row['date_min']:<10} | {row['date_max']:<10}"
        )
        
    report_lines.append("\n" + "=" * 45)
    report_lines.append(f"DATA READINESS SCORE: {readiness_score}/100")
    report_lines.append("=" * 45)
    
    report_str = "\n".join(report_lines)
    
    # Save the report to reports/data_quality_day1.txt
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "data_quality_day1.txt"
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_str)
        logger.info(f"Saved validation report to: {report_path.name}")
    except Exception as e:
        logger.error(f"Error saving quality report: {e}")
        
    return {
        "master_codes_count": len(master_codes),
        "nav_codes_count": len(nav_codes),
        "missing_nav_count": len(missing_nav_codes),
        "orphan_count": len(orphan_nav_codes),
        "readiness_score": readiness_score
    }, report_str


def main() -> None:
    """Orchestrates the Day 1 Capstone data ingestion and audit process."""
    # Define directory paths relative to root using pathlib
    root_dir = Path(__file__).resolve().parents[1]
    raw_dir = root_dir / "data" / "raw"
    reports_dir = root_dir / "reports"

    logger.info(f"Ingesting datasets from: {raw_dir}")
    
    # Load all 10 datasets
    dfs = load_all_datasets(raw_dir)
    
    # Print dataset quality audits
    print_dataset_audits(dfs)
    
    # Print dataset summary table
    print_summary_table(dfs)
    
    # Flag known anomalies
    check_data_anomalies(dfs)
    
    # Explore fund master metrics
    if "01_fund_master" in dfs:
        explore_fund_master(dfs["01_fund_master"])
        
    # Print NAV range insights
    if "02_nav_history" in dfs and "01_fund_master" in dfs:
        print_nav_insights(dfs["02_nav_history"], dfs["01_fund_master"])
        
    # Perform referential code validation
    if "01_fund_master" in dfs and "02_nav_history" in dfs:
        _, report_text = validate_amfi_codes(dfs["01_fund_master"], dfs["02_nav_history"], reports_dir)
        print("\n" + "=" * 60)
        print(report_text)
        print("=" * 60)


if __name__ == "__main__":
    main()
