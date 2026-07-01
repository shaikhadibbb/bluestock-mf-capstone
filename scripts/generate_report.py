#!/usr/bin/env python3
"""
Report Generator — Bluestock MF Capstone
Uses reportlab to generate the final PDF report.

Usage: python scripts/generate_report.py
"""
import os
import pandas as pd
from pathlib import Path
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, Preformatted
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Paths
ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / 'data' / 'processed'
REPORTS = ROOT / 'reports'
CHARTS = REPORTS / 'charts'
REPORTS.mkdir(parents=True, exist_ok=True)

# Document Setup
PDF_PATH = REPORTS / 'Final_Report.pdf'
doc = SimpleDocTemplate(
    str(PDF_PATH),
    pagesize=A4,
    rightMargin=1.8*cm, leftMargin=1.8*cm,
    topMargin=2*cm, bottomMargin=2*cm
)

# Colors
BRAND_DARK = colors.HexColor('#1a1a2e')
BRAND_RED = colors.HexColor('#e94560')
BRAND_BLUE = colors.HexColor('#0f3460')
TEXT_DARK = colors.HexColor('#333333')
GREY_LIGHT = colors.HexColor('#f7f9fa')
LINE_COLOR = colors.HexColor('#e1e4e6')

# Styles
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'CoverTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=28,
    leading=34,
    textColor=BRAND_DARK,
    alignment=TA_LEFT,
    spaceAfter=15
)

subtitle_style = ParagraphStyle(
    'CoverSubtitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=14,
    leading=18,
    textColor=BRAND_BLUE,
    alignment=TA_LEFT,
    spaceAfter=30
)

h1_style = ParagraphStyle(
    'SectionHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=BRAND_DARK,
    spaceBefore=15,
    spaceAfter=10,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'SubSectionHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=16,
    textColor=BRAND_BLUE,
    spaceBefore=10,
    spaceAfter=6,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'BodyTextCustom',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14.5,
    textColor=TEXT_DARK,
    alignment=TA_LEFT,
    spaceAfter=10
)

body_justify = ParagraphStyle(
    'BodyTextJustify',
    parent=body_style,
    alignment=TA_JUSTIFY
)

caption_style = ParagraphStyle(
    'ImageCaption',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor('#555555'),
    alignment=TA_CENTER,
    spaceAfter=15
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=9,
    leading=11,
    textColor=colors.white,
    alignment=TA_LEFT
)

table_body_style = ParagraphStyle(
    'TableBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=11,
    textColor=TEXT_DARK,
    alignment=TA_LEFT
)

# Helper for images
PAGE_W = A4[0] - 3.6*cm  # 17.4 cm usable width

def make_image(path, width_ratio=0.75):
    """Helper to draw a styled image at the given width ratio."""
    if not path.exists():
        # Fallback empty space/box if chart not generated yet
        print(f"Warning: Chart not found at {path}")
        return Paragraph(f"[Chart missing: {path.name}]", body_style)
    
    with PILImage.open(path) as img_file:
        img_w, img_h = img_file.size
        
    draw_w = PAGE_W * width_ratio
    draw_h = draw_w * (img_h / img_w)
    return Image(str(path), width=draw_w, height=draw_h)

def clean_scheme_name(name):
    if "SBI Small Cap Fund - Direct" in name: return "SBI Small Cap Direct"
    if "Axis Small Cap Fund - Regular" in name: return "Axis Small Cap Regular"
    if "ABSL Small Cap Fund - Regular" in name: return "ABSL Small Cap Regular"
    if "Nippon India Small Cap Fund - Regular" in name: return "Nippon India Small Cap Reg"
    if "SBI Small Cap Fund - Regular Plan" in name: return "SBI Small Cap Regular"
    if "ICICI Pru Liquid Fund - Regular" in name: return "ICICI Pru Liquid Regular"
    if "ABSL Liquid Fund - Regular" in name: return "ABSL Liquid Regular"
    if "Kotak Liquid Fund - Regular" in name: return "Kotak Liquid Regular"
    if "HDFC Short Term Debt Fund - Regular" in name: return "HDFC Short Term Debt Regular"
    if "Nippon India Gilt Securities Fund - Regular" in name: return "Nippon India Gilt Regular"
    return name.split(' - ')[0]

# Layout callbacks
def draw_cover(canvas, doc):
    canvas.saveState()
    # Top accent line
    canvas.setFillColor(BRAND_RED)
    canvas.rect(0, A4[1]-1*cm, A4[0], 1*cm, stroke=0, fill=1)
    
    # Bottom confidentiality bar
    canvas.setFillColor(BRAND_DARK)
    canvas.rect(0, 0, A4[0], 2.5*cm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawCentredString(A4[0]/2.0, 1.1*cm, "Confidential | For Internal Use Only")
    canvas.restoreState()

def add_header_footer(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#a8a8b3'))
    canvas.drawString(1.8*cm, A4[1]-1.2*cm, "Bluestock Fintech | Mutual Fund Analytics Capstone Report")
    canvas.setStrokeColor(LINE_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(1.8*cm, A4[1]-1.4*cm, A4[0]-1.8*cm, A4[1]-1.4*cm)
    
    # Footer page number
    canvas.drawRightString(A4[0]-1.8*cm, 1*cm, f"Page {doc.page}")
    canvas.restoreState()

def main():
    print("Generating Final_Report.pdf...")
    story = []
    
    # -------------------------------------------------------------------------
    # PAGE 1: COVER PAGE
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 3.5*cm))
    story.append(Paragraph("BLUESTOCK FINTECH", ParagraphStyle('Logo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=BRAND_RED, spaceAfter=20)))
    story.append(Paragraph("MUTUAL FUND ANALYTICS PLATFORM", title_style))
    story.append(Paragraph("End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard", subtitle_style))
    
    story.append(Spacer(1, 4.0*cm))
    
    info_data = [
        [Paragraph("<b>Prepared by:</b>", body_style), Paragraph("Adib Shaikh", body_style)],
        [Paragraph("<b>Role:</b>", body_style), Paragraph("Data Analyst Intern", body_style)],
        [Paragraph("<b>Company:</b>", body_style), Paragraph("Bluestock Fintech Pvt. Ltd.", body_style)],
        [Paragraph("<b>Date:</b>", body_style), Paragraph("June 2026", body_style)]
    ]
    info_table = Table(info_data, colWidths=[3*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(info_table)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 2: TABLE OF CONTENTS & DATA STORY
    # -------------------------------------------------------------------------
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    toc_data = [
        [Paragraph("1. Executive Summary", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("3", body_style)],
        [Paragraph("2. Problem Statement", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("4", body_style)],
        [Paragraph("3. Data Sources & Architecture", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("5", body_style)],
        [Paragraph("4. ETL Pipeline & Database Design", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("6", body_style)],
        [Paragraph("5. Exploratory Data Analysis (EDA)", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("7", body_style)],
        [Paragraph("6. Fund Performance Analytics", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("9", body_style)],
        [Paragraph("7. Advanced Analytics & Risk Metrics", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("11", body_style)],
        [Paragraph("8. Interactive Dashboard", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("12", body_style)],
        [Paragraph("9. Key Findings & Recommendations", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("13", body_style)],
        [Paragraph("10. Limitations & Future Work", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("14", body_style)],
        [Paragraph("11. Appendix: Tech Stack & File Index", body_style), Paragraph(". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", body_style), Paragraph("15", body_style)]
    ]
    toc_table = Table(toc_data, colWidths=[6.0*cm, 10.4*cm, 1.0*cm])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(toc_table)
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Project Data Story", h2_style))
    
    # Standout Feature 1: Data Story Visual Infographic
    story_boxes = [
        [Paragraph("<b>Step 1: Ingestion</b>", body_style), Paragraph("Ingest 10 raw CSVs from AMFI India, mfapi.in & indices.", body_style)],
        [Paragraph("<b>Step 2: Cleaning</b>", body_style), Paragraph("Date parsing, forward-fill NAVs, backfill null YoY growths.", body_style)],
        [Paragraph("<b>Step 3: Database Load</b>", body_style), Paragraph("Construct 8-table star schema database with 6 performance indexes.", body_style)],
        [Paragraph("<b>Step 4: Exploratory Analysis</b>", body_style), Paragraph("Identify AUM growth, demographics splits, and category heatmaps.", body_style)],
        [Paragraph("<b>Step 5: Scorecard Metrics</b>", body_style), Paragraph("Compute CAGR, Sharpe, OLS alpha/beta, drawdown & historical VaR.", body_style)],
        [Paragraph("<b>Step 6: Dashboard & Report</b>", body_style), Paragraph("Deploy interactive Streamlit dashboard and compile report.", body_style)]
    ]
    story_table = Table(story_boxes, colWidths=[4.5*cm, 12.9*cm])
    story_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GREY_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e1e4e6')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e1e4e6')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(story_table)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 3: EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    p1 = ("The Indian mutual fund industry has undergone a structural transformation over the past four years. "
          "As of December 2025, industry AUM stands at <b>Rs. 81 lakh crore</b> managed across 1,908 schemes and 26.12 crore investor "
          "folios — double the 13.26 crore folios recorded in January 2022. Monthly SIP inflows reached an all-time high of "
          "<b>Rs. 31,002 crore</b> in December 2025, a 2.69x increase from Rs. 11,517 crore in January 2022, reflecting India's deepening "
          "equity savings culture.")
    story.append(Paragraph(p1, body_justify))
    story.append(Spacer(1, 8))
    
    p2 = ("This capstone project built a full-stack Mutual Fund Analytics Platform for Bluestock Fintech. "
          "The platform ingests 10 real-world datasets from AMFI India, mfapi.in, and NSE/BSE, processes them through a "
          "Python ETL pipeline, stores them in a normalised SQLite star schema, and delivers insights via a 5-page "
          "interactive Streamlit dashboard. The project covers 40 real mutual fund schemes from India's top 10 AMCs, "
          "with 87,543 source rows spanning 4.5 years of market data.")
    story.append(Paragraph(p2, body_justify))
    story.append(Spacer(1, 8))
    
    p3 = ("Fund performance analysis revealed significant return dispersion across sub-categories. Small Cap funds "
          "delivered 3yr CAGRs of 20-23% with high volatility (VaR95 up to -2.69% daily), while Liquid funds delivered stable "
          "5-7% returns with near-zero risk (VaR95 as low as -0.02% daily). The composite fund scorecard — combining 3yr return, "
          "Sharpe ratio, alpha, expense ratio, and max drawdown — ranked SBI Small Cap Direct as the top all-round fund with "
          "a score of 72.75/100.")
    story.append(Paragraph(p3, body_justify))
    story.append(Spacer(1, 8))
    
    p4 = ("Investor analytics across 32,778 transactions from 5,000 investors in 12 states revealed that the 26-35 age cohort "
          "dominates transaction volume (41%), average SIP amounts are remarkably flat across age groups (Rs. 10,886-Rs. 11,575), and "
          "T30 cities account for 65.9% of SIP value. A fund recommender system provides top-3 personalised picks by risk "
          "appetite, integrated directly into the Streamlit dashboard.")
    story.append(Paragraph(p4, body_justify))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 4: PROBLEM STATEMENT
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Problem Statement", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    prob_data = [
        [Paragraph("<b>Identified Problem</b>", table_header_style), Paragraph("<b>Implemented Solution</b>", table_header_style)],
        [Paragraph("<b>P1: Data Fragmentation</b><br/>Mutual fund data is split across AMFI (AUM/folios), mfapi.in API (NAVs), and transaction tables, preventing cohesive reporting.", table_body_style),
         Paragraph("<b>Unified ETL Pipeline</b><br/>Built a programmatic Python pipeline that merges live APIs and CSV files, standardizing columns and normalising text.", table_body_style)],
        [Paragraph("<b>P2: Performance Evaluation</b><br/>Comparing funds based solely on raw CAGR returns neglects cost structure and downside risk exposures.", table_body_style),
         Paragraph("<b>Multi-Dimensional Scorecard</b><br/>Built a weighted scorecard (30% CAGR, 25% Sharpe, 20% Alpha, 15% Expense, 10% Drawdown) to rank all 40 schemes.", table_body_style)],
        [Paragraph("<b>P3: Index Tracking Gaps</b><br/>No standard benchmark comparisons to verify active manager outperformance or evaluate tracking error volatility.", table_body_style),
         Paragraph("<b>Benchmark Matching Engine</b><br/>Mapped all funds to relevant indices (NIFTY50, NIFTY100, BSE SmallCap) to run OLS alpha, beta, and tracking error metrics.", table_body_style)],
        [Paragraph("<b>P4: Investor Behaviour Blind Spot</b><br/>AMCs lack insight into retail investor churn, average payment schedules, and geographic concentrations.", table_body_style),
         Paragraph("<b>Cohort & Continuity Modeling</b><br/>Developed cohort analysis by signup year and transaction gap modeling to flag irregular, at-risk SIP accounts.", table_body_style)],
        [Paragraph("<b>P5: Sluggish Reporting Cadence</b><br/>Traditional static reporting processes make it slow for advisors to recommend funds dynamically based on risk profiles.", table_body_style),
         Paragraph("<b>Interactive Streamlit Dashboard</b><br/>Developed a local interactive portal with dynamic filters and an active risk-profile fund recommender.", table_body_style)]
    ]
    prob_table = Table(prob_data, colWidths=[8.7*cm, 8.7*cm])
    prob_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, GREY_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(prob_table)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 5: DATA SOURCES & ARCHITECTURE
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Data Sources & Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    story.append(Paragraph("Data Sources catalog", h2_style))
    src_data = [
        [Paragraph("<b>Source</b>", table_header_style), Paragraph("<b>Data Type</b>", table_header_style), Paragraph("<b>Scale</b>", table_header_style), Paragraph("<b>Update Frequency</b>", table_header_style)],
        [Paragraph("AMFI India", table_body_style), Paragraph("AUM, folios, industry SIP inflows, scheme master metadata", table_body_style), Paragraph("90 AUM rows, 48 SIP rows", table_body_style), Paragraph("Monthly", table_body_style)],
        [Paragraph("mfapi.in API", table_body_style), Paragraph("Historical NAV prices for 40 schemes", table_body_style), Paragraph("46,000+ daily NAV records", table_body_style), Paragraph("Daily", table_body_style)],
        [Paragraph("NSE & BSE India", table_body_style), Paragraph("Benchmark index closing prices (Nifty50, Nifty100, BSE SmallCap)", table_body_style), Paragraph("8,050 index price records", table_body_style), Paragraph("Daily", table_body_style)],
        [Paragraph("Retail Transactions", table_body_style), Paragraph("Simulated investor transactions (SIP, Lumpsum, Redemption)", table_body_style), Paragraph("32,778 rows (5,000 investors)", table_body_style), Paragraph("Historical (Simulated)", table_body_style)]
    ]
    src_table = Table(src_data, colWidths=[3.5*cm, 6.4*cm, 4.5*cm, 3.0*cm])
    src_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, GREY_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(src_table)
    
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("System Architecture Flow", h2_style))
    
    arch_data = [
        [Paragraph("<b>Raw Ingestion</b>", table_header_style), Paragraph("<b>ETL Pipeline</b>", table_header_style), Paragraph("<b>Database Schema</b>", table_header_style), Paragraph("<b>Analytics</b>", table_header_style), Paragraph("<b>Dashboard UI</b>", table_header_style)],
        [Paragraph("AMFI CSVs<br/>API Responses<br/>Index Prices", table_body_style),
         Paragraph("Pandas parsing<br/>Forward-fill NAVs<br/>Clean anomalies", table_body_style),
         Paragraph("SQLite 3<br/>Star Schema<br/>6 Indexes", table_body_style),
         Paragraph("CAGR, Sharpe<br/>OLS alpha/beta<br/>Daily VaR/CVaR", table_body_style),
         Paragraph("Streamlit app<br/>5 pages<br/>Plotly charts", table_body_style)]
    ]
    arch_table = Table(arch_data, colWidths=[3.48*cm]*5)
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_BLUE),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('BACKGROUND', (0,1), (-1,-1), GREY_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(arch_table)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 6: ETL PIPELINE & DATABASE DESIGN
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. ETL Pipeline & Database Design", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    story.append(Paragraph("ETL Processing Steps", h2_style))
    etl_steps = (
        "1. <b>Extract:</b> Loaded 10 raw datasets from processed folders, supplemented by API request "
        "calls for live scheme indices.<br/>"
        "2. <b>Transform:</b> Cleaned data anomalies. Converted all date string attributes into timestamp columns. "
        "Forward-filled missing daily NAV gaps (e.g. weekends/holidays) to ensure complete daily time-series. "
        "Standardized fund house and category names into normalized text categories.<br/>"
        "3. <b>Load:</b> Structured and inserted cleaned data into a normalized SQLite star schema comprising "
        "2 dimensions and 6 fact tables.<br/>"
        "4. <b>Indexing:</b> Added 6 database indexes on keys (`amfi_code`, `date`, `investor_id`, `state`) "
        "to optimize query response times under Streamlit dashboard loads."
    )
    story.append(Paragraph(etl_steps, body_style))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Database Star Schema Summary", h2_style))
    
    db_data = [
        [Paragraph("<b>Table Name</b>", table_header_style), Paragraph("<b>Type</b>", table_header_style), Paragraph("<b>Key Columns</b>", table_header_style), Paragraph("<b>Row Count</b>", table_header_style)],
        [Paragraph("dim_fund", table_body_style), Paragraph("Dimension", table_body_style), Paragraph("amfi_code (PK), fund_house, category, plan", table_body_style), Paragraph("40", table_body_style)],
        [Paragraph("dim_date", table_body_style), Paragraph("Dimension", table_body_style), Paragraph("date (PK), year, month, quarter, day_of_week", table_body_style), Paragraph("1,826", table_body_style)],
        [Paragraph("fact_nav", table_body_style), Paragraph("Fact", table_body_style), Paragraph("amfi_code (FK), date (FK), nav", table_body_style), Paragraph("46,000", table_body_style)],
        [Paragraph("fact_transactions", table_body_style), Paragraph("Fact", table_body_style), Paragraph("tx_id (PK), investor_id, amfi_code (FK), amount_inr", table_body_style), Paragraph("32,778", table_body_style)],
        [Paragraph("fact_performance", table_body_style), Paragraph("Fact", table_body_style), Paragraph("amfi_code (FK), return_3yr, sharpe, alpha, beta", table_body_style), Paragraph("40", table_body_style)],
        [Paragraph("fact_portfolio", table_body_style), Paragraph("Fact", table_body_style), Paragraph("amfi_code (FK), stock_symbol, weight_pct", table_body_style), Paragraph("322", table_body_style)],
        [Paragraph("fact_aum", table_body_style), Paragraph("Fact", table_body_style), Paragraph("date (FK), fund_house, aum_lakh_crore", table_body_style), Paragraph("90", table_body_style)],
        [Paragraph("fact_sip_industry", table_body_style), Paragraph("Fact", table_body_style), Paragraph("month, sip_inflow_crore, active_accounts", table_body_style), Paragraph("48", table_body_style)]
    ]
    db_table = Table(db_data, colWidths=[4.0*cm, 2.5*cm, 8.5*cm, 2.4*cm])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, GREY_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(db_table)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 7: EXPLORATORY DATA ANALYSIS (EDA) — PART 1
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Exploratory Data Analysis — Industry Trends", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    p5 = ("Exploratory Data Analysis revealed strong expansion metrics across the Indian mutual fund industry. "
          "By visualizing historical NAV patterns and aggregate assets under management (AUM) growth, we observe "
          "significant industry consolidation and a structural shift in retail savings behavior towards capital markets.")
    story.append(Paragraph(p5, body_style))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("NAV Price Movements across 40 Schemes", h2_style))
    story.append(make_image(CHARTS / 'chart_01_nav_trends_all_funds.png', width_ratio=0.75))
    story.append(Paragraph("Figure 1: NAV movement across all 40 funds (Jan 2022 – May 2026). Liquid schemes display near-linear upward growth.", caption_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Assets Under Management (AUM) Growth by Fund House", h2_style))
    story.append(make_image(CHARTS / 'chart_02_aum_growth_by_amc.png', width_ratio=0.75))
    story.append(Paragraph("Figure 2: AUM growth of the top 10 AMC houses. SBI Mutual Fund leads the industry with Rs. 12.50 lakh crore in Dec 2025.", caption_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 8: EXPLORATORY DATA ANALYSIS (EDA) — PART 2
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Exploratory Data Analysis — SIP & Folios", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    p6 = ("Systematic Investment Plan (SIP) transaction volume shows exponential growth over the 2022-2025 period. "
          "Furthermore, comparing retail folio expansion confirms that the industry's growth is heavily supported "
          "by massive retail investor participation in equity-based schemes.")
    story.append(Paragraph(p6, body_style))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("Monthly SIP Inflows Over Time", h2_style))
    story.append(make_image(CHARTS / 'chart_03_sip_inflow_trend.png', width_ratio=0.75))
    story.append(Paragraph("Figure 3: Monthly SIP inflows. Peaked at an all-time high of Rs. 31,002 crore in December 2025 (2.69x growth).", caption_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Mutual Fund Folio Growth Trends", h2_style))
    story.append(make_image(CHARTS / 'chart_07_folio_count_growth.png', width_ratio=0.75))
    story.append(Paragraph("Figure 4: Total and equity-specific folios. Folios doubled from 13.26 to 26.12 crore, driven by equity.", caption_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 9: FUND PERFORMANCE ANALYTICS — RISK-RETURN & BENCHMARKS
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Fund Performance Analytics — Risk & Return", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    p7 = ("To analyze return efficiency, we mapped risk and returns on a scatter quadrant. Additionally, "
          "we indexed historical NAV returns against NIFTY50 and NIFTY100 indices to track tracking error "
          "and active manager outperformance.")
    story.append(Paragraph(p7, body_style))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("Risk-Return Matrix Scatter Quadrants", h2_style))
    story.append(make_image(CHARTS / 'chart_08_risk_return_matrix.png', width_ratio=0.75))
    story.append(Paragraph("Figure 5: Risk-Return Scatter (Bubble size represents AUM). Small Cap schemes cluster in high-return/high-risk.", caption_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Indexed Fund NAV Performance vs Benchmark Indices", h2_style))
    story.append(make_image(CHARTS / 'chart_16_benchmark_comparison.png', width_ratio=0.75))
    story.append(Paragraph("Figure 6: Top 5 equity funds vs benchmarks (indexed from 100). The right panel shows tracking error.", caption_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 10: FUND PERFORMANCE ANALYTICS — SCORECARD
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Fund Performance Analytics — Scorecard", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    p8 = ("We constructed a composite scorecard using reference metrics to evaluate overall fund quality. "
          "The scorecard applies the formula: 30% Return + 25% Sharpe + 20% Alpha + 15% Expense + 10% Drawdown.")
    story.append(Paragraph(p8, body_style))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("Composite Fund Scorecard Heatmap", h2_style))
    story.append(make_image(CHARTS / 'chart_18_scorecard_heatmap.png', width_ratio=0.68))
    story.append(Paragraph("Figure 7: Scorecard component heat map. Details percentile ranks for the top 15 schemes.", caption_style))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("Top 10 Scorecard Funds Table", h2_style))
    
    # Load scorecard data
    try:
        df_sc = pd.read_csv(PROCESSED / 'fund_scorecard.csv').head(10)
        sc_rows = [[Paragraph("<b>Rank</b>", table_header_style), Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Sharpe</b>", table_header_style), Paragraph("<b>Composite Score</b>", table_header_style)]]
        for _, r in df_sc.iterrows():
            sc_rows.append([
                Paragraph(str(int(r['score_rank'])), table_body_style),
                Paragraph(clean_scheme_name(r['scheme_name']), table_body_style),
                Paragraph(r['category'], table_body_style),
                Paragraph(f"{r['sharpe_ratio']:.2f}", table_body_style),
                Paragraph(f"{r['composite_score']:.2f}", table_body_style)
            ])
    except Exception as e:
        print(f"Error reading scorecard: {e}")
        sc_rows = [[Paragraph("Data loading error", body_style)]]
        
    sc_table = Table(sc_rows, colWidths=[1.5*cm, 7.4*cm, 3.0*cm, 2.5*cm, 3.0*cm])
    sc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, GREY_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sc_table)
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 11: ADVANCED RISK ANALYTICS
    # -------------------------------------------------------------------------
    story.append(Paragraph("7. Advanced Analytics & Risk Metrics", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    p9 = ("To quantify tail risk, we computed daily Historical Value at Risk (VaR) and Conditional VaR (CVaR). "
          "Additionally, sector concentration was evaluated using the Herfindahl-Hirschman Index (HHI) for equity portfolios.")
    story.append(Paragraph(p9, body_style))
    
    story.append(Spacer(1, 2))
    story.append(Paragraph("Historical Daily VaR 95% Distribution", h2_style))
    story.append(make_image(CHARTS / 'chart_19_var_distribution.png', width_ratio=0.6))
    story.append(Paragraph("Figure 8: Daily VaR (95%) distribution across all schemes. Equity threshold sits at -1%.", caption_style))
    
    story.append(Spacer(1, 2))
    story.append(Paragraph("Sector Concentration Index (HHI) for Equity Funds", h2_style))
    story.append(make_image(CHARTS / 'chart_22_sector_hhi.png', width_ratio=0.6))
    story.append(Paragraph("Figure 9: Sector HHI concentration. Axis Bluechip has highest concentration (HHI: 2,064). All stay below SEBI 2,500 limit.", caption_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 12: INTERACTIVE DASHBOARD
    # -------------------------------------------------------------------------
    story.append(Paragraph("8. Interactive Dashboard Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    p10 = ("The analytics platform is exposed via a production-quality, responsive 5-page Streamlit web application. "
           "It utilizes sidebar filtering, clean table visualization templates, and incorporates an active fund recommender page.")
    story.append(Paragraph(p10, body_style))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("Dashboard Panel: Industry Overview Page", h2_style))
    story.append(make_image(CHARTS / 'dashboard_page1_industry_overview.png', width_ratio=0.72))
    story.append(Paragraph("Figure 10: Industry Overview panel showing industry folios, total AUM, and monthly SIP milestones.", caption_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Dashboard Panel: Fund Performance Matrix Page", h2_style))
    story.append(make_image(CHARTS / 'dashboard_page2_fund_performance.png', width_ratio=0.72))
    story.append(Paragraph("Figure 11: Fund Performance analytics panel containing the interactive bubble risk scatter and comparison line tool.", caption_style))
    
    story.append(Spacer(1, 10))
    dash_text = (
        "<b>Dashboard CLI:</b> <code>streamlit run dashboard/app.py</code> (local)<br/>"
        "<b>Subpages:</b> Industry Overview | Fund Performance | Investor Analytics | SIP Trends | Fund Recommender<br/>"
        "<b>Aesthetic System:</b> Modern dark layout, harmonious grid paddings, dynamic cards, download scorecards."
    )
    story.append(Paragraph(dash_text, body_style))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 13: KEY FINDINGS & RECOMMENDATIONS
    # -------------------------------------------------------------------------
    story.append(Paragraph("9. Key Findings & Recommendations", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    story.append(Paragraph("Top 10 Analytical Findings", h2_style))
    findings = [
        "1. SIP inflows grew 2.69x (from Rs. 11,517 Cr to Rs. 31,002 Cr) showing a massive structural shift in savings behavior.",
        "2. Retail folios doubled (from 13.26 to 26.12 crore) driven entirely by equity mutual fund participation.",
        "3. Small Cap schemes deliver the highest returns (23.39% 3yr CAGR) but carry 120x more daily risk than Liquid funds.",
        "4. SBI Mutual Fund dominates the asset market at Rs. 12.50 lakh crore, representing a 19.8% share of top-10 AMCs.",
        "5. Liquid mutual funds dominated net category inflows in FY25 (Rs. 4,51,275 crore) as institutions parked corporate cash.",
        "6. The 26-35 age group represents the largest investor demographic segment, contributing 41% of all transaction volume.",
        "7. Average SIP contributions are flat across all age cohorts, ranging narrowly between Rs. 10,886 and Rs. 11,575.",
        "8. T30 cities account for 65.9% of total SIP value, while B30 represents 34.1%, showing massive room for retail growth.",
        "9. Axis Bluechip has the highest sector concentration (HHI: 2,064) but remains safely under the SEBI limit of 2,500.",
        "10. 97.8% of SIP accounts with 6+ historic transactions are at-risk, exhibiting average transaction gaps exceeding 35 days."
    ]
    for f in findings:
        story.append(Paragraph(f, body_style))
        story.append(Spacer(1, 3))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("Core Strategic Recommendations", h2_style))
    recs = [
        "• <b>Automate Payment Alerts:</b> AMCs must implement automated, interactive SIP payment reminders as the high at-risk rate (97.8%) highlights frequent retail funding lapses.",
        "• <b>Optimized Risk Profiling:</b> Advisors should direct risk-averse retail capital into top-performing moderate assets like HDFC Top 100 Regular (Sharpe: 1.06) or high-risk assets like Kotak Emerging Equity Regular (Sharpe: 0.96) according to composite scorecard rankings.",
        "• <b>Target B30 Growth:</b> Bluestock Fintech should target its digital platform acquisition towards B30 districts, as local retail savings remain heavily concentrated in T30 cities (65.9% total value)."
    ]
    for r in recs:
        story.append(Paragraph(r, body_style))
        story.append(Spacer(1, 4))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 14: CHALLENGES, LESSONS & LIMITATIONS
    # -------------------------------------------------------------------------
    story.append(Paragraph("10. Challenges, Lessons & Limitations", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    # TODO: Verify ReportLab flow templates. If section overflows, it pushes Appendix to Page 16.
    # FIXME: Visually balancing charts to fit took days of trial-and-error.
    story.append(Paragraph("Challenges Faced during Capstone", h2_style))
    challenges = [
        "• <b>API Rate Limits & Timeouts:</b> Fetching live daily NAV records from mfapi.in frequently failed due to timeouts. I had to implement an exponential backoff retry loop with rate-limiting handlers in Python to ensure robust data loading.",
        "• <b>Holiday and Weekend NAV Gaps:</b> The raw NAV values did not contain records for weekends and holidays. Resampling to business days (`resample('B')`) and forward-filling was tricky and initially threw index matching errors before I aligned datetime structures.",
        "• <b>CAPM Jensen's Alpha & Sortino Formulas:</b> Computing Sortino ratios using downside risk and Alpha values via OLS regressions took three tries to write correctly. Standard Python math examples often regress raw returns rather than excess returns, introducing substantial errors.",
        "• <b>ReportLab Document Layout Flow:</b> ReportLab's template layout was extremely painful to manage, especially with table margins and image scaling. Visually balancing charts to fit on specific pages took days of trial-and-error."
    ]
    for c in challenges:
        story.append(Paragraph(c, body_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("Lessons Learned & What Didn't Work", h2_style))
    lessons = [
        "• <b>Normalization vs Performance:</b> Denormalizing the database table `fact_performance` by including fund name strings initially seemed easier, but it violated 3NF and led to data inconsistencies. I removed the text fields and refactored the SQL queries to JOIN `dim_fund` on `amfi_code` which is much cleaner.",
        "• <b>Attempted & Removed Feature:</b> I originally attempted to build a dynamic PDF table generator that queries the live mfapi.in endpoint during the report compilation. This was removed because API delays and rate-limiting during ReportLab's document build frequently caused compile crashes. Keeping the pipeline separate is much more stable."
    ]
    for les in lessons:
        story.append(Paragraph(les, body_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Project Limitations & Future Scope", h2_style))
    lims = [
        "• <b>Time Horizon:</b> Mapped NAV history covers Jan 2022 to May 2026. True 5-year CAGR/metrics rely on pre-computed reference file data.",
        "• <b>Synthetic Transaction Data:</b> Retail transactions (32,778 rows) are simulated, meaning real retail transaction habits may exhibit additional variables.",
        "• <b>Modern Portfolio Optimization:</b> Future roadmap includes a Markowitz Efficient Frontier module to allow users to build and optimize custom asset allocations.",
        "• <b>Cloud Host Deployment:</b> Deploy the Streamlit application and database to Streamlit Community Cloud and AWS RDS for general public access."
    ]
    for l in lims:
        story.append(Paragraph(l, body_style))
        story.append(Spacer(1, 4))
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # PAGE 15: APPENDIX & FILE INDEX
    # -------------------------------------------------------------------------
    story.append(Paragraph("11. Appendix: Tech Stack & File Index", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_DARK, spaceBefore=5, spaceAfter=15))
    
    story.append(Paragraph("Technology Stack", h2_style))
    tech_data = [
        [Paragraph("<b>Component</b>", table_header_style), Paragraph("<b>Tool / Library</b>", table_header_style), Paragraph("<b>Role in Project</b>", table_header_style)],
        [Paragraph("Programming Language", table_body_style), Paragraph("Python 3.11", table_body_style), Paragraph("All scripts, ETL pipeline, and notebook execution", table_body_style)],
        [Paragraph("Data Processing", table_body_style), Paragraph("Pandas 2.0+ / NumPy 1.24+", table_body_style), Paragraph("ETL, transaction cleaning, and metrics computation", table_body_style)],
        [Paragraph("Statistical Analysis", table_body_style), Paragraph("SciPy 1.10+", table_body_style), Paragraph("OLS regression slope/intercept for beta and alpha", table_body_style)],
        [Paragraph("Static Visuals", table_body_style), Paragraph("Matplotlib 3.7+ / Seaborn 0.12+", table_body_style), Paragraph("23 analytical charts and Infographics", table_body_style)],
        [Paragraph("Interactive Dashboard", table_body_style), Paragraph("Streamlit 1.35+ / Plotly 5.x", table_body_style), Paragraph("Web UI page layouts, filters, and dynamic comparisons", table_body_style)],
        [Paragraph("Database Engine", table_body_style), Paragraph("SQLite3 / SQLAlchemy 2.0", table_body_style), Paragraph("Normalised Star Schema database & performance indexing", table_body_style)],
        [Paragraph("Document Compilation", table_body_style), Paragraph("ReportLab 4.x / Python-PPTX", table_body_style), Paragraph("Programmatic PDF generation and PPTX presentation", table_body_style)]
    ]
    tech_table = Table(tech_data, colWidths=[4.5*cm, 4.5*cm, 8.4*cm])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BRAND_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, LINE_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, GREY_LIGHT]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(tech_table)
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Workspace File Index", h2_style))
    
    idx_code = (
        "bluestock_mf_capstone/\n"
        "  |-- scripts/\n"
        "  |   |-- data_ingestion.py        (Day 1: raw ingestion)\n"
        "  |   |-- live_nav_fetch.py        (Day 1: mfapi.in API fetch)\n"
        "  |   |-- clean_data.py            (Day 2: data cleaning)\n"
        "  |   |-- load_database.py         (Day 2: Star Schema DB loader)\n"
        "  |   |-- generate_eda_charts.py   (Day 3: 15 publication charts)\n"
        "  |   |-- compute_metrics.py       (Day 4: cagr, Sharpe, alpha)\n"
        "  |   |-- recommender.py           (Day 6: fund recommender CLI)\n"
        "  |   |-- generate_report.py       (Day 7: PDF compile script)\n"
        "  |   +-- generate_presentation.py  (Day 7: slide compile script)\n"
        "  |-- notebooks/\n"
        "  |   |-- 03_eda_analysis.ipynb            (Day 3 EDA notebook)\n"
        "  |   |-- 04_performance_analytics.ipynb   (Day 4 performance notebook)\n"
        "  |   +-- 05_advanced_analytics.ipynb      (Day 6 advanced risk notebook)\n"
        "  |-- dashboard/app.py              (Day 5 interactive streamlit app)\n"
        "  |-- sql/schema.sql                (Day 2 database Star Schema)\n"
        "  |-- sql/queries.sql               (Day 2 11 analytical query scripts)\n"
        "  |-- data/processed/               (10 cleaned CSVs + 7 metric reports)\n"
        "  |-- reports/charts/               (23 charts + 4 dashboard static PNGs)\n"
        "  +-- reports/Final_Report.pdf      (This PDF Report)"
    )
    story.append(Preformatted(idx_code, ParagraphStyle('CodeStyle', fontName='Courier', fontSize=7.0, leading=9.0, textColor=BRAND_DARK)))
    
    # Build Document
    doc.build(story, onFirstPage=draw_cover, onLaterPages=add_header_footer)
    print("Saved Final_Report.pdf")

if __name__ == '__main__':
    main()
