"""SQL Queries Runner for Bluestock Mutual Fund Capstone.

This module reads queries from sql/queries.sql, executes them against the
SQLite database, and saves the formatted tabular results to
reports/sql_query_results_day2.txt while displaying them in the console.
"""

import logging
import re
import sqlite3
from pathlib import Path
import pandas as pd

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("run_queries")

# --- Constants & Directories ---
ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "data" / "db" / "bluestock_mf.db"
QUERIES_PATH = ROOT_DIR / "sql" / "queries.sql"
REPORTS_DIR = ROOT_DIR / "reports"
OUTPUT_PATH = REPORTS_DIR / "sql_query_results_day2.txt"


def load_queries(queries_path: Path) -> list:
    """Parses sql/queries.sql into individual queries.

    Args:
        queries_path: Path to the SQL file.

    Returns:
        List of tuples: (query_title, query_sql)
    """
    with open(queries_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match comments starting with -- Q followed by number, and the query ending with semicolon
    raw_queries = re.findall(r"(-- Q\d+[\s\S]*?)(?=(?:-- Q\d+|$))", content)
    
    parsed_queries = []
    for rq in raw_queries:
        lines = rq.strip().split("\n")
        title = lines[0].strip()
        sql = "\n".join(lines[1:]).strip()
        if sql:
            parsed_queries.append((title, sql))
            
    return parsed_queries


def execute_queries(db_path: Path, queries: list) -> str:
    """Executes the parsed queries and returns a formatted string report.

    Args:
        db_path: Path to the SQLite DB.
        queries: List of (title, sql) tuples.

    Returns:
        Formatted string containing all query results.
    """
    report_parts = [
        "=" * 80,
        "              BLUESTOCK MUTUAL FUND CAPSTONE — SQL QUERY RESULTS",
        "=" * 80,
        ""
    ]

    try:
        conn = sqlite3.connect(db_path)
        for title, sql in queries:
            report_parts.append("-" * 80)
            report_parts.append(f" QUERY: {title}")
            report_parts.append("-" * 80)
            report_parts.append(f"SQL Code:\n{sql}\n")
            
            try:
                # Load query into pandas DataFrame
                df = pd.read_sql_query(sql, conn)
                report_parts.append("Results:")
                if df.empty:
                    report_parts.append("  (No rows returned)")
                else:
                    report_parts.append(df.to_string(index=False))
            except Exception as q_err:
                report_parts.append(f"ERROR executing query: {q_err}")
                logger.error(f"Error executing query {title}: {q_err}")
                
            report_parts.append("\n")
            
        conn.close()
    except Exception as db_err:
        report_parts.append(f"Database connection error: {db_err}")
        logger.error(f"Failed to connect to database: {db_err}")
        
    report_parts.append("=" * 80)
    return "\n".join(report_parts)


def main() -> None:
    """Orchestrates query loading, execution, and report generation."""
    logger.info("Initializing SQL queries runner...")
    
    if not DB_PATH.exists():
        logger.error(f"Database does not exist at {DB_PATH}. Run load_database.py first!")
        return

    if not QUERIES_PATH.exists():
        logger.error(f"Queries file does not exist at {QUERIES_PATH}!")
        return

    # Load and parse queries
    queries = load_queries(QUERIES_PATH)
    logger.info(f"Loaded {len(queries)} queries from {QUERIES_PATH.name}")

    # Execute queries
    report_content = execute_queries(DB_PATH, queries)

    # Write report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info(f"Saved query results to: {OUTPUT_PATH.name}")
    except Exception as e:
        logger.error(f"Failed to save query results: {e}")

    # Also display to the user
    print(report_content)


if __name__ == "__main__":
    main()
