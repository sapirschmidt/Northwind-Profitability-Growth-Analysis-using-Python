#app.py

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

#Page configuration

st.set_page_config(
    page_title="Northwind Profitability & Growth Analysis",
    page_icon="",
    layout="wide")


##Design Customizations##

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .bi-divider {
        height: 1px;
        background-color: #e1e4e8;
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)

#Data Loading

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "dashboard_data"

@st.cache_data
def load_data():
    names = [
        "profitability",
        "product_profitability",
        "category_profitability",
        "customer_profitability",
        "volume_margin",
        "employee_profitability",
        "country_profitability",
        "monthly_profitability",
        "discount_analysis",
        "monthly_active_customers",
        "rfm",
        "rfm_summary",
    ]
    data = {name: pd.read_csv(DATA_PATH / f"{name}.csv") for name in names}

    print(data["profitability"]["OrderDate"].head(10))

    data["profitability"]["OrderDate"] = pd.to_datetime(data["profitability"]["OrderDate"], errors='coerce')
    
    return data

data = load_data()
profitability = data["profitability"]
product_profitability = data["product_profitability"]
customer_profitability = data["customer_profitability"]
volume_margin = data["volume_margin"]
employee_profitability = data["employee_profitability"]
discount_analysis = data["discount_analysis"]
monthly_active_customers = data["monthly_active_customers"]
rfm = data["rfm"]
rfm_summary = data["rfm_summary"]
profitability["Year"] = profitability["OrderDate"].dt.year
profitability["Quarter"] = profitability["OrderDate"].dt.quarter
profitability["Month"] = profitability["OrderDate"].dt.month

# Header and caption

st.title("Northwind Profitability & Growth Analysis")
st.caption("Comprehensive Profitability, Customers, Products, Discounts & Employees")

# ============Sidebar filters============

st.sidebar.header("Filters")


profitability["OrderDate"] = pd.to_datetime(profitability["OrderDate"], errors='coerce')
years = sorted(profitability["Year"].dropna().unique())
selected_years = st.sidebar.multiselect("Year", years, default=years)

temp_filtered = profitability.copy()
if selected_years:
    temp_filtered = temp_filtered[temp_filtered["OrderDate"].dt.year.isin(selected_years)]

quarters = sorted([int(q) for q in temp_filtered["OrderDate"].dt.quarter.dropna().unique()])
selected_quarters = st.sidebar.multiselect("Quarter", quarters, default=quarters)

if selected_quarters:
    temp_filtered = temp_filtered[temp_filtered["OrderDate"].dt.quarter.isin(selected_quarters)]

months = sorted([int(m) for m in temp_filtered["OrderDate"].dt.month.dropna().unique()])
selected_months = st.sidebar.multiselect("Month", months, default=months)

if selected_months:
    temp_filtered = temp_filtered[temp_filtered["OrderDate"].dt.month.isin(selected_months)]

category_options = (
    sorted(profitability["CategoryName"].dropna().unique())
    if "CategoryName" in profitability.columns
    else []
)

selected_categories = st.sidebar.multiselect("Category", category_options, default=category_options)

if selected_categories:
    temp_filtered = temp_filtered[temp_filtered["CategoryName"].isin(selected_categories)]

customer_col = "CustomerID" if "CustomerID" in profitability.columns else "CompanyName"
customer_options = sorted(temp_filtered[customer_col].dropna().unique()) if customer_col in temp_filtered.columns else []
selected_customers = st.sidebar.multiselect("Customer", customer_options)

filtered = profitability.copy()

if selected_years:
    filtered = filtered[filtered["Year"].isin(selected_years)]
if selected_quarters:
    filtered = filtered[filtered["Quarter"].isin(selected_quarters)]
if selected_months:
    filtered = filtered[filtered["Month"].isin(selected_months)]
if selected_categories:
    filtered = filtered[filtered["CategoryName"].isin(selected_categories)]

customer_col = "CustomerID" if "CustomerID" in profitability.columns else "CompanyName"
customer_options = sorted(filtered[customer_col].dropna().unique())

if selected_customers:
    filtered = filtered[filtered[customer_col].isin(selected_customers)]

#==========dynamic filtering based on selections============
filtered = profitability.copy()
if selected_years:
    filtered = filtered[filtered["OrderDate"].dt.year.isin(selected_years)]
if selected_categories:
    filtered = filtered[filtered["CategoryName"].isin(selected_categories)]

# =====KPIs calculations=====

total_revenue = filtered["Revenue"].sum()
monthly_revenue = (filtered.groupby(filtered["OrderDate"].dt.month)["Revenue"].sum().sort_index())
revenue_mom = monthly_revenue.pct_change().iloc[-1]
total_cogs = filtered["COGS"].sum()
cogs_mom = (filtered.groupby(filtered["OrderDate"].dt.month)["COGS"].sum().sort_index().pct_change().iloc[-1])
total_profit = filtered["GrossProfit"].sum()
profit_mom = (filtered.groupby(filtered["OrderDate"].dt.month)["GrossProfit"].sum().sort_index().pct_change().iloc[-1])
gross_margin = (total_profit / total_revenue) if total_revenue else 0
gross_margin_mom_percent = (filtered.groupby(filtered["OrderDate"].dt.month).apply(lambda x: x["GrossProfit"].sum() / x["Revenue"].sum() if x["Revenue"].sum() else 0).sort_index().pct_change().iloc[-1])  
orders = filtered["OrderID"].nunique()
orders_mom = (filtered.groupby(filtered["OrderDate"].dt.month)["OrderID"].nunique().sort_index().pct_change().iloc[-1])
customers = filtered["CustomerID"].nunique()
customers_mom = (filtered.groupby(filtered["OrderDate"].dt.month)["CustomerID"].nunique().sort_index().pct_change().iloc[-1])
aov = total_revenue / orders if orders else 0
aov_mom = (filtered.groupby(filtered["OrderDate"].dt.month).apply(lambda x: x["Revenue"].sum() / x["OrderID"].nunique() if x["OrderID"].nunique() else 0).sort_index().pct_change().iloc[-1])
profit_per_customer = total_profit / customers if customers else 0
profit_mom_per_customer = (filtered.groupby(filtered["OrderDate"].dt.month).apply(lambda x: x["GrossProfit"].sum() / x["CustomerID"].nunique() if x["CustomerID"].nunique() else 0).sort_index().pct_change().iloc[-1])

#===== Display KPIs========

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Revenue", f"${total_revenue:,.0f}", f"{revenue_mom:.1%}" " MoM")
kpi2.metric("COGS", f"${total_cogs:,.0f}", f"{cogs_mom:.1%}" " MoM")
kpi3.metric("Gross Profit", f"${total_profit:,.0f}", f"{profit_mom:.1%}" " MoM")
kpi4.metric("Gross Margin", f"{gross_margin:.1%}", f"{gross_margin_mom_percent:.1%}" " MoM")

kpi5, kpi6, kpi7, kpi8 = st.columns(4)
kpi5.metric("Orders", f"{orders:,}", f"{orders_mom:.1%}" " MoM")
kpi6.metric("Customers", f"{customers:,}", f"{customers_mom:.1%}" " MoM")
kpi7.metric("Average Order Value", f"${aov:,.0f}", f"{aov_mom:.1%}" " MoM")
kpi8.metric("Profit Per Customer", f"${profit_per_customer:,.0f}", f"{profit_mom_per_customer:.1%}" " MoM")

st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# ================= (Time Analysis) =================

st.subheader("1. Time Analysis & Growth Over Time")

monthly = (
    filtered.dropna(subset=["OrderDate"])
    .assign(MonthPeriod=lambda x: x["OrderDate"].dt.to_period("M").dt.to_timestamp())
    .groupby("MonthPeriod", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        GrossProfit=("GrossProfit", "sum"),
        COGS=("COGS", "sum"),
    )
    .sort_values("MonthPeriod"))

col1, col2 = st.columns(2)
with col1:
    if not monthly.empty:
        fig1 = px.line(monthly, x="MonthPeriod", y=["Revenue", "GrossProfit"], markers=True ,title="Revenue & Gross Profit Over Time", template="plotly_white")
        fig1.update_layout(xaxis_title="", yaxis_title="USD ($)", margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="#FFF5F5",paper_bgcolor="#FFF5F5")
      
        
        fig1.update_xaxes(showgrid=False,zeroline=False)

        fig1.update_yaxes(showgrid=False,zeroline=False)

st.plotly_chart(fig1, use_container_width=True)

with col2:
    monthly["GrossMargin"] = np.where(monthly["Revenue"] != 0, monthly["GrossProfit"] / monthly["Revenue"], np.nan)
    fig2 = px.line(monthly, x="MonthPeriod", y="GrossMargin", markers=True ,title="Gross Margin Over Time", template="plotly_white")
    fig2.update_yaxes(tickformat=".0%")
    fig2.update_layout(xaxis_title="", yaxis_title="Margin", margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5")
    

    fig2.update_xaxes(showgrid=False,zeroline=False)

    fig2.update_yaxes(showgrid=False,zeroline=False)

st.plotly_chart(fig2, width="stretch")

st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# ================= (Products & Volume/Margin Matrix) =================
st.subheader("2. Product Profitability & Volume/Margin Matrix")

col1, col2 = st.columns(2)
with col1:
    top_products = product_profitability.nlargest(10, "GrossProfit").sort_values("GrossProfit")
    fig3 = px.bar(top_products, x="GrossProfit", y="ProductName", orientation="h", title="Top 10 Products by Gross Profit", template="plotly_white")
    fig3.update_layout(xaxis_title="Gross Profit ($)", yaxis_title="" ,margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5  ")
    st.plotly_chart(fig3, width="stretch")

with col2:
    fig4 = px.scatter(volume_margin, x="Revenue", y="GrossMargin", size="UnitsSold", hover_name="ProductName", title="Product Volume vs Margin Matrix", template="plotly_white")
    fig4.update_yaxes(tickformat=".0%")
    fig4.update_layout(margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5")
    st.plotly_chart(fig4, width="stretch")

st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# ================= (Customers & Pareto Analysis) =================
st.subheader("3. Customer Profitability & Concentration")

col1, col2 = st.columns(2)
with col1:
    top_customers = customer_profitability.nlargest(10, "Revenue").sort_values("Revenue")
    fig5 = px.bar(top_customers, x="Revenue", y="CustomerID", orientation="h", title="Top 10 Customers by Revenue", template="plotly_white")
    fig5.update_layout(xaxis_title="Revenue ($)", yaxis_title="" ,margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5")
    st.plotly_chart(fig5, width="stretch")

with col2:
    prod_sorted = product_profitability.sort_values(
    "GrossProfit", ascending=True
    ).copy()
    prod_sorted["CumulativeProfitShare"] = (
    prod_sorted["GrossProfit"] / prod_sorted["GrossProfit"].sum()
    ).cumsum()
    prod_sorted["ProductRank"] = range(1, len(prod_sorted) + 1)

col_chart, col_table = st.columns([1.2, 1])

with col_chart:
    fig6 = px.line(
        prod_sorted,
        x="ProductRank",
        y="CumulativeProfitShare",
        hover_name="ProductName",
        hover_data=["GrossProfit", "CumulativeProfitShare"],
        title="Pareto Analysis: Cumulative Profit Share by Products",
        template="plotly_white",
    )
    fig6.update_yaxes(tickformat=".0%")
    fig6.add_hline(
        y=0.8, line_dash="dash", line_color="8B9A6E", annotation_text="80% Profit"
    )
    fig6.update_layout(
        xaxis_title="Product Rank",
        yaxis_title="Cumulative Profit Share",
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5"     
    )
    st.plotly_chart(fig6, use_container_width=True)

with col_table:
    st.markdown("### Product Profitability Ranking")
    display_df = prod_sorted[
        [
            "ProductRank",
            "ProductName",
            "GrossProfit",
            "CumulativeProfitShare",
        ]
    ].copy()
    display_df["GrossProfit"] = display_df["GrossProfit"].map("${:,.2f}".format)
    display_df["CumulativeProfitShare"] = display_df[
        "CumulativeProfitShare"
    ].map("{:.1%}".format)

    st.dataframe(
        display_df, width='stretch', height=400
    ) 
st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# =================(Discount Analysis) =================
st.subheader("4. Discount Impact Analysis")
correct_discount_order = ["0%", "0-5%", "5-10%", "10-20%", "20%+"]

col1, col2 = st.columns(2)
with col1:
    fig7 = px.bar(
    discount_analysis,
    x="DiscountBand",
    y="Revenue",
    title="Revenue by Discount Band",
    template="plotly_white",
)
    fig7.update_layout(
    xaxis=dict(
        categoryorder="array", categoryarray=correct_discount_order
    ), 
    xaxis_title="Discount Band",
    yaxis_title="Revenue ($)",
    margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5"
)
st.plotly_chart(fig7, use_container_width=True)

with col2:
    fig8 = px.bar(
    discount_analysis,
    x="DiscountBand",
    y="GrossMargin",
    title="Gross Margin by Discount Band",
    template="plotly_white",
)
    fig8.update_yaxes(tickformat=".0%")
    fig8.update_layout(
    xaxis=dict(
        categoryorder="array", categoryarray=correct_discount_order
    ), 
    xaxis_title="Discount Band",
    yaxis_title="Gross Margin",
    margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5"     
)

st.plotly_chart(fig8, width="stretch")

st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# ================(Employee Performance & Active Customers) =================
st.subheader("5. Employee Performance & Monthly Active Customers")

col1, col2 = st.columns(2)
with col1:
    fig9 = px.bar(employee_profitability, x="LastName", y="GrossProfit", title="Gross Profit by Employee", template="plotly_white")
    fig9.update_layout(xaxis_title="Employee", yaxis_title="Gross Profit ($)" ,margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5")
    st.plotly_chart(fig9, width="stretch")

with col2:
    fig10 = px.line(monthly_active_customers, x="Month", y="Monthly Active Customers", markers=True, title="Monthly Active Customers (Cohort / Activity)", template="plotly_white")
    fig10.update_layout(xaxis_title="", yaxis_title="Active Customers" ,margin=dict(l=0, r=0, t=40, b=0),
    plot_bgcolor="#FFF5F5", paper_bgcolor="#FFF5F5")
    st.plotly_chart(fig10, width="stretch")

st.caption("Analytical dashboard built with Python, Pandas, Plotly and Streamlit - Northwind Project.")