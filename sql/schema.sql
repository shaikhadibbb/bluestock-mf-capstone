-- ============================================================
-- Bluestock MF Capstone — Star Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code       INTEGER PRIMARY KEY,
    fund_house      TEXT    NOT NULL,
    scheme_name     TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    sub_category    TEXT,
    plan            TEXT,
    launch_date     DATE,
    benchmark       TEXT,
    expense_ratio_pct REAL,
    exit_load_pct   REAL,
    min_sip_amount  INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager    TEXT,
    risk_category   TEXT,
    sebi_category_code TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    date        DATE    NOT NULL UNIQUE,
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    month_name  TEXT,
    is_weekday  INTEGER  -- 1 = weekday, 0 = weekend
);

CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code       INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    nav_date        DATE    NOT NULL,
    nav             REAL    NOT NULL CHECK (nav > 0),
    daily_return_pct REAL,
    PRIMARY KEY (amfi_code, nav_date)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT    NOT NULL,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    transaction_date    DATE    NOT NULL,
    transaction_type    TEXT    NOT NULL CHECK (transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount_inr          INTEGER NOT NULL CHECK (amount_inr > 0),
    state               TEXT,
    city                TEXT,
    city_tier           TEXT    CHECK (city_tier IN ('T30','B30')),
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT    CHECK (kyc_status IN ('Verified','Pending'))
);

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           REAL,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    PRIMARY KEY (amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_portfolio (
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    stock_symbol        TEXT    NOT NULL,
    stock_name          TEXT,
    sector              TEXT,
    weight_pct          REAL,
    market_value_cr     REAL,
    current_price_inr   REAL,
    portfolio_date      DATE,
    PRIMARY KEY (amfi_code, stock_symbol, portfolio_date)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    date            DATE    NOT NULL,
    fund_house      TEXT    NOT NULL,
    aum_lakh_crore  REAL,
    aum_crore       REAL,
    num_schemes     INTEGER,
    PRIMARY KEY (date, fund_house)
);

CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month                       TEXT    PRIMARY KEY,
    sip_inflow_crore            REAL,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);

-- ============================================================
-- Indexes for performance tuning
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_nav_date       ON fact_nav(nav_date);
CREATE INDEX IF NOT EXISTS idx_nav_code       ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_tx_date        ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_tx_investor    ON fact_transactions(investor_id);
CREATE INDEX IF NOT EXISTS idx_tx_code        ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_tx_state       ON fact_transactions(state);
