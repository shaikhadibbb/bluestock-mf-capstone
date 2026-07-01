-- Q1: Top 5 funds by AUM (scheme level)
SELECT f.scheme_name, f.fund_house, p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- Q2: Average NAV per month across all funds (2025 only)
SELECT
    strftime('%Y-%m', nav_date) AS month,
    ROUND(AVG(nav), 4) AS avg_nav
FROM fact_nav
WHERE nav_date >= '2025-01-01' AND nav_date <= '2025-12-31'
GROUP BY month
ORDER BY month;

-- Q3: SIP inflow Year-over-Year growth
SELECT
    substr(month, 1, 4) AS year,
    ROUND(SUM(sip_inflow_crore), 0) AS total_sip_inflow_crore,
    ROUND(AVG(yoy_growth_pct), 2) AS avg_yoy_growth_pct
FROM fact_sip_industry
GROUP BY year
ORDER BY year;

-- Q4: Total transaction volume by state (top 5)
SELECT state, COUNT(*) AS tx_count, ROUND(SUM(amount_inr)/1e7, 2) AS total_amount_crore
FROM fact_transactions
GROUP BY state
ORDER BY tx_count DESC
LIMIT 5;

-- Q5: Funds with expense ratio below 1%
SELECT f.scheme_name, f.fund_house, f.plan, f.expense_ratio_pct
FROM dim_fund f
WHERE f.expense_ratio_pct < 1.0
ORDER BY f.expense_ratio_pct ASC;

-- Q6: Top 5 funds by 3-year CAGR return
SELECT f.scheme_name, f.fund_house, f.category, p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 5;

-- Q7: SIP vs Lumpsum vs Redemption split (count and total value)
SELECT
    transaction_type,
    COUNT(*)                            AS tx_count,
    ROUND(SUM(amount_inr)/1e7, 2)      AS total_crore,
    ROUND(AVG(amount_inr), 0)          AS avg_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY tx_count DESC;

-- Q8: AUM growth for SBI Mutual Fund over time
SELECT date, fund_house, aum_lakh_crore, aum_crore
FROM fact_aum
WHERE fund_house = 'SBI Mutual Fund'
ORDER BY date;

-- Q9: Average SIP amount by age group
SELECT
    t.age_group,
    COUNT(*)                          AS sip_count,
    ROUND(AVG(t.amount_inr), 0)       AS avg_sip_amount
FROM fact_transactions t
WHERE t.transaction_type = 'SIP'
GROUP BY t.age_group
ORDER BY t.age_group;

-- Q10: Funds with Sharpe ratio above 1.5 (strong risk-adjusted performers)
SELECT f.scheme_name, f.fund_house, f.category, p.sharpe_ratio, p.return_3yr_pct, p.risk_grade
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
WHERE p.sharpe_ratio > 1.5
ORDER BY p.sharpe_ratio DESC;

-- Q11 (BONUS): Fund Health Scorecard — Return, Risk, Cost in one view
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.return_3yr_pct,
    p.sharpe_ratio,
    p.max_drawdown_pct,
    p.expense_ratio_pct,
    ROUND(
        (p.return_3yr_pct * 0.3) +
        (p.sharpe_ratio * 5 * 0.25) +
        ((100 + p.max_drawdown_pct) * 0.2) +
        ((2.5 - p.expense_ratio_pct) * 10 * 0.15),
    2) AS composite_score
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY composite_score DESC
LIMIT 10;
