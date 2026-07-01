#!/usr/bin/env python3
"""
email_summary.py — Weekly Performance Email Generator (Bonus Challenge B5)
Queries the SQLite database and compiles a publication-quality HTML email report.
"""
import sqlite3
import pandas as pd
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'data' / 'db' / 'bluestock_mf.db'
OUTPUT_HTML = ROOT / 'reports' / 'weekly_summary_email.html'

def get_performance_summary():
    """Query the SQLite database for top funds and industry metrics."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run scripts/run_pipeline.py first.")
        
    conn = sqlite3.connect(DB_PATH)
    
    # Query Top 5 Funds by Sharpe Ratio
    query_top_funds = """
    SELECT f.scheme_name, f.category, p.sharpe_ratio, p.sortino_ratio, p.aum_crore
    FROM fact_performance p
    JOIN dim_fund f ON p.amfi_code = f.amfi_code
    ORDER BY p.sharpe_ratio DESC
    LIMIT 5
    """
    df_top = pd.read_sql_query(query_top_funds, conn)
    
    # Query Latest Industry SIP Inflows
    query_sip = """
    SELECT month, sip_inflow_crore, active_sip_accounts_crore
    FROM fact_sip_industry
    ORDER BY month DESC
    LIMIT 1
    """
    df_sip = pd.read_sql_query(query_sip, conn)
    sip_data = df_sip.iloc[0] if not df_sip.empty else {"month": "N/A", "sip_inflow_crore": 0, "active_sip_accounts_crore": 0}
    
    conn.close()
    return df_top, sip_data

def generate_html_email(df_top, sip_data):
    """Compile the HTML template with dynamic data."""
    # Top Funds rows construction
    table_rows = ""
    for idx, row in df_top.iterrows():
        table_rows += f"""
        <tr style="border-bottom: 1px solid #dddddd;">
            <td style="padding: 12px 15px; text-align: left; font-size: 14px; color: #333333;">{row['scheme_name']}</td>
            <td style="padding: 12px 15px; text-align: left; font-size: 14px; color: #666666;">{row['category']}</td>
            <td style="padding: 12px 15px; text-align: right; font-weight: bold; color: #0f172a;">{row['sharpe_ratio']:.2f}</td>
            <td style="padding: 12px 15px; text-align: right; color: #0f172a;">{row['sortino_ratio']:.2f}</td>
            <td style="padding: 12px 15px; text-align: right; color: #0f172a;">₹{row['aum_crore']:,.1f} Cr</td>
        </tr>
        """
        
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bluestock Mutual Fund Weekly Summary</title>
</head>
<body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; -webkit-font-smoothing: antialiased;">
    <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); overflow: hidden; border: 1px solid #e2e8f0;">
        <!-- Header -->
        <tr>
            <td bgcolor="#0f172a" style="padding: 30px 20px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: bold; letter-spacing: 1px;">BLUESTOCK FINTECH</h1>
                <p style="color: #ef4444; margin: 5px 0 0 0; font-size: 12px; font-weight: bold; letter-spacing: 2px; text-transform: uppercase;">Mutual Fund Weekly Performance Report</p>
            </td>
        </tr>
        
        <!-- Summary Banner -->
        <tr>
            <td style="padding: 30px 30px 15px 30px;">
                <h2 style="color: #0f172a; margin: 0 0 10px 0; font-size: 18px; border-bottom: 2px solid #ef4444; padding-bottom: 8px;">Market & Industry Pulse</h2>
                <table width="100%" cellpadding="10" cellspacing="0" style="margin-top: 15px; background-color: #f1f5f9; border-radius: 6px;">
                    <tr>
                        <td width="50%" style="text-align: center; border-right: 1px solid #e2e8f0;">
                            <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold;">SIP Inflows ({sip_data['month']})</span><br/>
                            <span style="font-size: 20px; font-weight: bold; color: #ef4444;">₹{sip_data['sip_inflow_crore']:,.0f} Cr</span>
                        </td>
                        <td width="50%" style="text-align: center;">
                            <span style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold;">Active SIP Accounts</span><br/>
                            <span style="font-size: 20px; font-weight: bold; color: #0f172a;">{sip_data['active_sip_accounts_crore']:.2f} Crore</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- Top Performing Funds -->
        <tr>
            <td style="padding: 15px 30px 30px 30px;">
                <h2 style="color: #0f172a; margin: 0 0 15px 0; font-size: 18px; border-bottom: 2px solid #ef4444; padding-bottom: 8px;">Top 5 Schemes (By Sharpe Ratio)</h2>
                <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; margin-top: 10px;">
                    <thead>
                        <tr style="background-color: #0f172a; color: #ffffff;">
                            <th style="padding: 12px 15px; text-align: left; font-size: 12px; text-transform: uppercase;">Scheme</th>
                            <th style="padding: 12px 15px; text-align: left; font-size: 12px; text-transform: uppercase;">Category</th>
                            <th style="padding: 12px 15px; text-align: right; font-size: 12px; text-transform: uppercase;">Sharpe</th>
                            <th style="padding: 12px 15px; text-align: right; font-size: 12px; text-transform: uppercase;">Sortino</th>
                            <th style="padding: 12px 15px; text-align: right; font-size: 12px; text-transform: uppercase;">AUM</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td bgcolor="#f8fafc" style="padding: 20px 30px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 11px; color: #64748b;">
                <p style="margin: 0 0 5px 0; font-weight: bold;">Bluestock Fintech Mutual Fund Capstone Project Log</p>
                <p style="margin: 0;">This email summary is automatically generated from the normalized star-schema SQLite database. Confidential - Internal Use Only.</p>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return html_content

def main():
    print("Generating Weekly Performance HTML Email Summary...")
    df_top, sip_data = get_performance_summary()
    html_email = generate_html_email(df_top, sip_data)
    
    # Save to file
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_email)
        
    print(f"Weekly HTML email report saved successfully to: {OUTPUT_HTML}")

if __name__ == '__main__':
    main()
