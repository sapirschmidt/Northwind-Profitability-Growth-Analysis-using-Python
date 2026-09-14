# Northwind-Profitability-Growth-Analysis-using-Python

Project Overview

End-to-end data analytics project based on the Northwind database, focused on profitability, customer behavior, sales performance, and business growth.

The project transforms transactional data into analytical datasets and business insights using Python, Pandas, NumPy, and Streamlit.

Business Focus

The analysis examines:

Revenue and gross profit performance

Product and category profitability

Customer profitability and concentration

Customer behavior and RFM segmentation

Sales and operational performance

Trends and month-over-month changes

Key Research Questions

How do revenue, gross profit, and gross margin evolve over time?

Which customers generate the highest revenue and gross profit, and how concentrated is customer profitability?

Which products and categories contribute most to gross profit?

How do discounts affect revenue, gross profit, and profitability?

What customer behavior patterns can be identified through RFM and repeat-purchase analysis?

Analytical Process

Data Cleaning → EDA → KPI Development → Deep Analysis → Visualization → Business Insights → Recommendations

Data Preparation

Data loading and validation

Date conversion and time dimensions

Missing-value checks

Data type validation

Table relationships and joins

Creation of analytical variables

Exploratory Data Analysis

Revenue and profit distributions

Customer and product analysis

Trend analysis

Outlier identification

Basic statistical analysis

KPI & Metrics

Selected metrics include:

Revenue

Gross Profit

Gross Margin

Average Order Value (AOV)

Revenue per Customer

Profit per Customer

Repeat Purchase Rate

Customer Concentration

Monthly Active Customers

RFM: Recency, Frequency, Monetary

Month-over-Month (MoM) growth

Deep Analysis

The core of the project uses Python to investigate profitability and customer behavior from multiple perspectives.

Gross profit is calculated using the distinction between product purchase cost and order selling price:

Gross Profit = Sales Revenue − Product Cost

This allows the analysis to move beyond sales volume and evaluate economic contribution.

Technology Stack

Python: Pandas, NumPy, Matplotlib, Plotly

Streamlit

Jupyter Notebook

GitHub

Repository Structure

/
├── data/
│   └── dashboard_data/
├── analysis/
│   └── Jupyter notebooks
├── report/
│   └── Final report
├── app.py
└── README.md

Dashboard

The project includes an interactive Streamlit dashboard presenting KPIs, profitability analysis, customer analysis, product performance, and business insights.

The dashboard is designed to move from:

Data → Analysis → Insight → Business Decision

Expected Business Outcomes

The analysis aims to identify:

The main drivers of profitability

High-value and high-risk customer segments

Products and categories with strong or weak economic contribution

The relationship between discounts and profitability

Opportunities to improve customer retention and profitability

Author

Sapir Schmidt
