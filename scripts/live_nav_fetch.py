"""Live NAV Consumer and Analytics Fetcher for Bluestock Mutual Fund Capstone.

This module retrieves live NAV datasets from mfapi.in, parses date and numerical
formats, exports individual scheme data, creates a combined database, and calculates
historical returns for analysis.
"""

import logging
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple
import pandas as pd
import requests

# --- Section: Configuration & Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("live_nav_fetch")

API_TIMEOUT = 12
COOLDOWN_SLEEP = 1.0  # Respectful sleep delay between queries

# Mappings of the 5 additional key schemes
ADDITIONAL_SCHEMES = {
    119551: "sbi_bluechip",
    120503: "icici_bluechip",
    118632: "nippon_largecap",
    119092: "axis_bluechip",
    120841: "kotak_bluechip"
}


def fetch_scheme_dataframe(amfi_code: int) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    # TODO: Verify if mfapi.in has rate limits. Sometimes we get 429 errors when running this fast.
    # FIXME: Need to handle temporary DNS resolutions issues gracefully.
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    max_retries = 3
    backoff_base = 2.0
    
    for attempt in range(max_retries):
        try:
            # print(f"DEBUG: Attempting HTTP request for code {amfi_code}, attempt {attempt+1}")
            response = requests.get(url, timeout=API_TIMEOUT)
            response.raise_for_status()
            raw_json = response.json()
            
            # WIP: check if meta is actually returned. API can return empty dict
            if "meta" not in raw_json or "data" not in raw_json or not raw_json["data"]:
                logger.error(f"Empty or malformed payload returned for code: {amfi_code}")
                return None, None
                
            scheme_name = raw_json["meta"].get("scheme_name", "Unknown Scheme")
            df = pd.DataFrame(raw_json["data"])
            df = df.rename(columns={"date": "date", "nav": "nav"})
            df["nav"] = df["nav"].astype(float)
            
            # HACK: date parsing behaves weirdly across different OS locales, try both common patterns
            # works for now, will refactor later if we add custom formats
            try:
                df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
            except Exception:
                df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y")
                
            df["amfi_code"] = amfi_code
            df = df.sort_values("date").reset_index(drop=True)
            return df, scheme_name
            
        except requests.RequestException as re:
            # Check for 429 Too Many Requests
            if re.response is not None and re.response.status_code == 429:
                logger.warning(f"Rate limited (429) for code {amfi_code}. Retrying in {backoff_base ** attempt}s...")
            else:
                logger.warning(f"HTTP request failed for code {amfi_code} (attempt {attempt+1}): {re}")
            
            if attempt < max_retries - 1:
                time.sleep(backoff_base ** attempt)
            else:
                logger.error(f"Failed to fetch {amfi_code} after {max_retries} attempts.")
                return None, None
        except Exception as e:
            logger.error(f"Unexpected error processing AMFI code {amfi_code}: {e}")
            return None, None


def compute_quick_annual_return(df: pd.DataFrame) -> str:
    """Computes a 1-year historical return based on 252 trading days.

    Args:
        df: Scheme pricing DataFrame sorted ascending.

    Returns:
        String describing the percentage return or a fallback.
    """
    if len(df) >= 253:
        latest_nav = df["nav"].iloc[-1]
        prev_nav = df["nav"].iloc[-253]
        ret = (latest_nav - prev_nav) / prev_nav * 100.0
        return f"{ret:.2f}% (252-day basis)"
    elif len(df) > 1:
        latest_nav = df["nav"].iloc[-1]
        prev_nav = df["nav"].iloc[0]
        ret = (latest_nav - prev_nav) / prev_nav * 100.0
        return f"{ret:.2f}% (since inception / short series)"
    return "N/A"


def main() -> None:
    """Orchestrates live NAV fetching, saving, and returns analysis."""
    root_dir = Path(__file__).resolve().parents[1]
    raw_dir = root_dir / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("                 LIVE NAV RETRIEVAL AND ANALYSIS")
    print("=" * 60)

    # 1. Fetch HDFC Top 100 Direct (AMFI 125497)
    logger.info("Fetching HDFC Top 100 Direct NAV...")
    df_hdfc, hdfc_name = fetch_scheme_dataframe(125497)
    if df_hdfc is not None:
        out_path = raw_dir / "live_nav_hdfc_top100.csv"
        df_hdfc.to_csv(out_path, index=False)
        
        min_d = df_hdfc["date"].min().strftime("%Y-%m-%d")
        max_d = df_hdfc["date"].max().strftime("%Y-%m-%d")
        latest_val = df_hdfc["nav"].iloc[-1]
        
        print(f"HDFC Top 100: {len(df_hdfc)} rows | {min_d} → {max_d} | Latest NAV: Rs. {latest_val:.4f}")
        print(f"  Scheme Title : {hdfc_name}")
        print(f"  1-Year Return: {compute_quick_annual_return(df_hdfc)}")
    else:
        logger.error("Failed to retrieve HDFC Top 100 Direct NAV data.")

    # 2. Fetch the 5 additional key schemes
    logger.info("Fetching the 5 additional key schemes...")
    combined_dfs = []
    
    for code, short_name in ADDITIONAL_SCHEMES.items():
        # Polite API delay
        logger.info(f"Sleeping for {COOLDOWN_SLEEP} second...")
        time.sleep(COOLDOWN_SLEEP)
        
        df_scheme, scheme_title = fetch_scheme_dataframe(code)
        if df_scheme is not None:
            # Save individual CSV
            ind_path = raw_dir / f"live_nav_{short_name}.csv"
            df_scheme.to_csv(ind_path, index=False)
            
            min_d = df_scheme["date"].min().strftime("%Y-%m-%d")
            max_d = df_scheme["date"].max().strftime("%Y-%m-%d")
            latest_val = df_scheme["nav"].iloc[-1]
            
            print(f"{short_name}: {len(df_scheme)} rows | {min_d} → {max_d} | Latest NAV: Rs. {latest_val:.4f}")
            print(f"  Scheme Title : {scheme_title}")
            print(f"  1-Year Return: {compute_quick_annual_return(df_scheme)}")
            
            combined_dfs.append(df_scheme)
        else:
            logger.error(f"Failed to retrieve data for scheme: {short_name} ({code})")

    # 3. Stack and save the 5 combined key schemes
    if combined_dfs:
        df_all_combined = pd.concat(combined_dfs, ignore_index=True)
        comb_path = raw_dir / "live_nav_all5_combined.csv"
        df_all_combined.to_csv(comb_path, index=False)
        logger.info(f"Saved combined stacked dataset: {comb_path.name}")
        print(f"\nSuccessfully compiled all 5 schemes: {len(df_all_combined)} total rows.")
    else:
        logger.error("No additional schemes were successfully fetched. Combined dataset not saved.")
        
    print("=" * 60)


if __name__ == "__main__":
    main()
