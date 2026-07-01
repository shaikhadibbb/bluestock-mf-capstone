#!/usr/bin/env python3
"""Day 6 Recommender: Return top-3 fund picks based on investor risk appetite (Low/Moderate/High)."""
import pandas as pd
from pathlib import Path
import sys

def recommend_funds(risk_appetite: str = None, risk_score: int = None) -> pd.DataFrame:
    # TODO: add a check for direct vs regular plans in recommendations
    # FIXME: what happens if the input has trailing spaces? title() handles it, but check
    # print(f"DEBUG: risk_appetite={risk_appetite}, risk_score={risk_score}")
    ROOT = Path(__file__).resolve().parent.parent
    PROCESSED = ROOT / 'data' / 'processed'
    
    perf_path = PROCESSED / 'clean_performance.csv'
    var_path = PROCESSED / 'var_cvar_report.csv'
    
    if not perf_path.exists() or not var_path.exists():
        raise FileNotFoundError("Processed performance or VaR CSV files not found. Please run the analytics notebook first.")
        
    df_perf = pd.read_csv(perf_path)
    df_var = pd.read_csv(var_path)
    
    # Map risk appetite / risk score
    if risk_score is not None:
        try:
            score = int(risk_score)
        except ValueError:
            raise ValueError("Risk score must be an integer between 0 and 10.")
        if score < 0 or score > 10:
            raise ValueError("Risk score must be between 0 and 10.")
        if score <= 3:
            appetite = 'Low'
        elif score <= 6:
            appetite = 'Moderate'
        else:
            appetite = 'High'
    elif risk_appetite is not None:
        appetite = risk_appetite.strip().title()
        if appetite not in ['Low', 'Moderate', 'High']:
            raise ValueError("Risk appetite must be 'Low', 'Moderate', or 'High'.")
    else:
        raise ValueError("Either risk_appetite or risk_score must be provided.")
        
    RISK_MAP = {
        'Low'      : ['Low'],
        'Moderate' : ['Moderate', 'Moderately High'],
        'High'     : ['High', 'Very High'],
    }
    
    target_grades = RISK_MAP[appetite]
    
    # Merge performance and VaR metrics
    df_merged = df_perf.merge(df_var[['amfi_code', 'var_95_pct']], on='amfi_code', how='left')
    
    # Filter by risk grades
    df_filtered = df_merged[df_merged['risk_grade'].isin(target_grades)].copy()
    
    # Get top 3 by Sharpe ratio
    df_top = df_filtered.sort_values('sharpe_ratio', ascending=False).head(3).copy()
    
    # Select and format columns
    cols = ['scheme_name', 'fund_house', 'risk_grade', 'sharpe_ratio', 'return_3yr_pct', 'expense_ratio_pct', 'var_95_pct']
    df_top = df_top[cols]
    
    # Clean scheme name for display
    def clean_name(name):
        return name.split(' - ')[0]
        
    df_top['scheme_name'] = df_top['scheme_name'].apply(clean_name)
    df_top['return_3yr_pct'] = df_top['return_3yr_pct'].apply(lambda x: f"{x:.2f}%")
    df_top['expense_ratio_pct'] = df_top['expense_ratio_pct'].apply(lambda x: f"{x:.2f}%")
    df_top['var_95_pct'] = df_top['var_95_pct'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")
    df_top['sharpe_ratio'] = df_top['sharpe_ratio'].round(2)
    
    return df_top

if __name__ == '__main__':
    print("Bluestock Fund Recommender")
    print("--------------------------")
    print("Select Input Mode:")
    print("1. Enter Risk Appetite (Low / Moderate / High)")
    print("2. Enter Risk Score (0 - 10)")
    
    choice = input("Enter Choice [1 or 2]: ").strip()
    
    try:
        if choice == '1':
            appetite = input("Enter risk appetite [Low / Moderate / High]: ").strip()
            result = recommend_funds(risk_appetite=appetite)
            print("\nRecommended Funds:")
            print(result.to_string(index=False))
        elif choice == '2':
            score_str = input("Enter risk score [0 - 10]: ").strip()
            score = int(score_str)
            result = recommend_funds(risk_score=score)
            print("\nRecommended Funds:")
            print(result.to_string(index=False))
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)