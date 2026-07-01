"""Database Loading and Validation Pipeline for Bluestock Mutual Fund Capstone.

This module initializes the SQLite database, creates the star schema,
programmatically populates the date dimension table, loads all processed
datasets, and performs referential integrity validation.
"""

import logging
import sqlite3
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("load_database")

# --- Constants & Directories ---
ROOT_DIR = Path(__file__).resolve().parents[1]
DB_DIR = ROOT_DIR / "data" / "db"
DB_PATH = DB_DIR / "bluestock_mf.db"
SCHEMA_PATH = ROOT_DIR / "sql" / "schema.sql"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

# Mapping from processed CSV file to SQLite table name
CSV_TO_TABLE_MAP = {
    "clean_fund_master.csv": "dim_fund",
    "clean_nav.csv": "fact_nav",  # note: date needs rename to nav_date
    "clean_transactions.csv": "fact_transactions",
    "clean_performance.csv": "fact_performance",
    "clean_portfolio_holdings.csv": "fact_portfolio",
    "clean_aum_by_fund_house.csv": "fact_aum",
    "clean_sip_inflows.csv": "fact_sip_industry"
}


def populate_dim_date(engine) -> int:
    """Programmatically populates the dim_date table for the range 2022-01-01 to 2026-12-31.

    Args:
        engine: SQLAlchemy database engine.

    Returns:
        The number of rows loaded.
    """
    logger.info("Generating dim_date data...")
    date_range = pd.date_range(start="2022-01-01", end="2026-12-31")
    df_date = pd.DataFrame()
    df_date["date_id"] = range(1, len(date_range) + 1)
    df_date["date"] = date_range.strftime("%Y-%m-%d")
    df_date["year"] = date_range.year
    df_date["month"] = date_range.month
    df_date["quarter"] = date_range.quarter
    df_date["month_name"] = date_range.strftime("%B")
    df_date["is_weekday"] = date_range.dayofweek.map(lambda x: 1 if x < 5 else 0)

    # Insert into dim_date using append mode to preserve custom schema
    df_date.to_sql("dim_date", engine, if_exists="append", index=False)
    return len(df_date)


def run_schema_sql(engine, schema_path: Path) -> None:
    """Executes the schema.sql script to define tables and indexes.

    Args:
        engine: SQLAlchemy engine.
        schema_path: Path to the SQL file.
    """
    logger.info(f"Applying schema script: {schema_path.name}")
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # Execute multiple SQL statements using the raw sqlite3 connection
        with engine.connect() as conn:
            raw_conn = conn.connection
            cursor = raw_conn.cursor()
            cursor.executescript(sql_script)
            raw_conn.commit()
        logger.info("Schema and indexes applied successfully.")
    except Exception as e:
        logger.error(f"Failed to apply database schema: {e}")
        raise e


def verify_referential_integrity(engine) -> bool:
    """Validates that all amfi_codes in fact tables exist in the dim_fund dimension.

    Args:
        engine: SQLAlchemy database engine.

    Returns:
        True if 100% clean referential integrity, False otherwise.
    """
    logger.info("Running referential integrity validation on amfi_code...")
    
    fact_tables = {
        "fact_nav": "nav_date",
        "fact_transactions": "transaction_date",
        "fact_performance": "return_3yr_pct",
        "fact_portfolio": "stock_symbol"
    }
    
    with engine.connect() as conn:
        # Get dim_fund codes
        dim_codes_res = conn.execute(text("SELECT amfi_code FROM dim_fund")).fetchall()
        dim_codes = {row[0] for row in dim_codes_res}
        
        all_valid = True
        for table, col in fact_tables.items():
            query = text(f"SELECT DISTINCT amfi_code FROM {table}")
            res = conn.execute(query).fetchall()
            fact_codes = {row[0] for row in res}
            
            missing_codes = fact_codes - dim_codes
            if missing_codes:
                all_valid = False
                logger.error(f"❌ Broken FK codes found in {table}: {missing_codes}")
            else:
                logger.info(f"{table} resolved successfully.")
                
        if all_valid:
            print("-" * 60)
            print("Referential integrity: 100% (all FK codes resolved)")
            print("-" * 60)
            return True
        else:
            print("-" * 60)
            print("❌ Referential integrity violations detected!")
            print("-" * 60)
            return False


def main() -> None:
    """Main function to recreate and load the SQLite database."""
    print("=" * 60)
    print("      STARTING SQLITE DATABASE BUILD & LOAD PROCESS")
    print("=" * 60)

    # 1. Clean build - recreate db file
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
            logger.info(f"Deleted existing SQLite DB at: {DB_PATH.name}")
        except Exception as e:
            logger.error(f"Could not delete database file: {e}")
            raise e

    # Create SQLAlchemy Engine
    engine = create_engine(f"sqlite:///{DB_PATH}")

    # 2. Run schema creation script
    run_schema_sql(engine, SCHEMA_PATH)

    # 3. Load datasets
    load_counts = {}

    # Programmatic Date Load
    date_rows = populate_dim_date(engine)
    load_counts["dim_date"] = date_rows
    print(f"Loaded dim_date          →  {date_rows} rows")

    # Clean CSV file loads
    for csv_file, table_name in CSV_TO_TABLE_MAP.items():
        csv_path = PROCESSED_DIR / csv_file
        if not csv_path.exists():
            logger.error(f"Processed file not found: {csv_path}")
            raise FileNotFoundError(f"File {csv_path} does not exist.")

        df = pd.read_csv(csv_path)

        # Special column rename check for fact_nav
        if table_name == "fact_nav":
            df = df.rename(columns={"date": "nav_date"})
        elif table_name == "fact_performance":
            # TODO: drop redundant text fields to comply with 3NF database schema
            # FIXME: we should probably ensure the CSV actually has these columns before dropping
            df = df.drop(columns=["scheme_name", "fund_house", "category", "plan"], errors="ignore")

        # Load to SQL using append to keep SQLite constraints defined in schema.sql
        df.to_sql(table_name, engine, if_exists="append", index=False)
        load_counts[table_name] = len(df)
        print(f"Loaded {table_name:<17}  →  {len(df)} rows")

    print("=" * 60)
    print("                 DATABASE SUMMARY STATISTICS")
    print("=" * 60)
    for tbl, count in load_counts.items():
        print(f"  Table: {tbl:<18} | Loaded Rows: {count}")
    print("=" * 60)

    # 4. Perform referential checks
    verify_referential_integrity(engine)

    print("=" * 60)
    print("      SQLITE DATABASE LOADING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
