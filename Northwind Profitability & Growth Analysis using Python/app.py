from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Northwind Profitability & Growth Analysis",
    page_icon="",
    layout="wide"
)
## Design Customizations ##
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 8px;
        min-height: 40px;
    }
    .bi-divider {
        height: 1px;
        background-color: #e1e4e8;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)
# Data Loading
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

# ============ Sidebar filters ============
st.sidebar.header("Filters")
years = sorted(profitability["Year"].dropna().unique())
selected_years = st.sidebar.multiselect("Year", years, default=[])

temp_filtered = profitability.copy()
if selected_years:
    temp_filtered = temp_filtered[temp_filtered["Year"].isin(selected_years)]

quarters = sorted([int(q) for q in temp_filtered["Quarter"].dropna().unique()])
selected_quarters = st.sidebar.multiselect("Quarter", quarters, default=[])

if selected_quarters:
    temp_filtered = temp_filtered[temp_filtered["Quarter"].isin(selected_quarters)]

months = sorted([int(m) for m in temp_filtered["Month"].dropna().unique()])
selected_months = st.sidebar.multiselect("Month", months, default=[])

if selected_months:
    temp_filtered = temp_filtered[temp_filtered["Month"].isin(selected_months)]

category_options = (
    sorted(profitability["CategoryName"].dropna().unique())
    if "CategoryName" in profitability.columns
    else []
)
selected_categories = st.sidebar.multiselect("Category", category_options, default=[])

if selected_categories:
    temp_filtered = temp_filtered[temp_filtered["CategoryName"].isin(selected_categories)]

customer_col = "CustomerID" if "CustomerID" in profitability.columns else "CompanyName"
customer_options = sorted(temp_filtered[customer_col].dropna().unique()) if customer_col in temp_filtered.columns else []
selected_customers = st.sidebar.multiselect("Customer", customer_options, default=[])

# Apply filters
filtered = profitability.copy()
if selected_years:
    filtered = filtered[filtered["Year"].isin(selected_years)]
if selected_quarters:
    filtered = filtered[filtered["Quarter"].isin(selected_quarters)]
if selected_months:
    filtered = filtered[filtered["Month"].isin(selected_months)]
if selected_categories:
    filtered = filtered[filtered["CategoryName"].isin(selected_categories)]
if selected_customers:
    filtered = filtered[filtered[customer_col].isin(selected_customers)]

# ===== Correct Chronological MoM KPI Calculations =====
monthly_agg = (
    filtered.dropna(subset=["OrderDate"])
    .assign(MonthPeriod=lambda x: x["OrderDate"].dt.to_period("M").dt.to_timestamp())
    .groupby("MonthPeriod", as_index=False)
    .agg(
        Revenue=("Revenue", "sum"),
        COGS=("COGS", "sum"),
        GrossProfit=("GrossProfit", "sum"),
        Orders=("OrderID", "nunique"),
        Customers=("CustomerID", "nunique"),
    )
    .sort_values("MonthPeriod")
)
monthly_agg["GrossMargin"] = np.where(monthly_agg["Revenue"] != 0, monthly_agg["GrossProfit"] / monthly_agg["Revenue"], np.nan)
monthly_agg["AOV"] = np.where(monthly_agg["Orders"] != 0, monthly_agg["Revenue"] / monthly_agg["Orders"], np.nan)
monthly_agg["ProfitPerCustomer"] = np.where(monthly_agg["Customers"] != 0, monthly_agg["GrossProfit"] / monthly_agg["Customers"], np.nan)
total_revenue = filtered["Revenue"].sum()
total_cogs = filtered["COGS"].sum()
total_profit = filtered["GrossProfit"].sum()
gross_margin = (total_profit / total_revenue) if total_revenue else 0
orders = filtered["OrderID"].nunique()
customers = filtered[customer_col].nunique()
aov = total_revenue / orders if orders else 0
profit_per_customer = total_profit / customers if customers else 0

# Safe MoM percentage change from last full chronological month
valid_monthly = monthly_agg[monthly_agg["Revenue"] > 0].sort_values("MonthPeriod")

if len(valid_monthly) >= 2:
    prev_rev, curr_rev = valid_monthly["Revenue"].iloc[-2], valid_monthly["Revenue"].iloc[-1]
    revenue_mom = (curr_rev - prev_rev) / prev_rev

    prev_cogs, curr_cogs = valid_monthly["COGS"].iloc[-2], valid_monthly["COGS"].iloc[-1]
    cogs_mom = (curr_cogs - prev_cogs) / prev_cogs

    prev_gp, curr_gp = valid_monthly["GrossProfit"].iloc[-2], valid_monthly["GrossProfit"].iloc[-1]
    profit_mom = (curr_gp - prev_gp) / prev_gp

    prev_gm, curr_gm = valid_monthly["GrossMargin"].iloc[-2], valid_monthly["GrossMargin"].iloc[-1]
    gross_margin_mom_percent = (curr_gm - prev_gm) / prev_gm if prev_gm != 0 else 0

    prev_ord, curr_ord = valid_monthly["Orders"].iloc[-2], valid_monthly["Orders"].iloc[-1]
    orders_mom = (curr_ord - prev_ord) / prev_ord

    prev_cust, curr_cust = valid_monthly["Customers"].iloc[-2], valid_monthly["NumCustomers"].iloc[-1] if "NumCustomers" in valid_monthly else valid_monthly["Customers"].iloc[-1]
    customers_mom = (curr_cust - prev_cust) / prev_cust

    prev_aov, curr_aov = valid_monthly["AOV"].iloc[-2], valid_monthly["AOV"].iloc[-1]
    aov_mom = (curr_aov - prev_aov) / prev_aov

    prev_ppc, curr_ppc = valid_monthly["ProfitPerCustomer"].iloc[-2], valid_monthly["ProfitPerCustomer"].iloc[-1]
    profit_mom_per_customer = (curr_ppc - prev_ppc) / prev_ppc
else:
    revenue_mom = cogs_mom = profit_mom = gross_margin_mom_percent = orders_mom = customers_mom = aov_mom = profit_mom_per_customer = 0

# ===== Display KPIs ========
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Revenue", f"${total_revenue:,.0f}", f"{revenue_mom:.1%} MoM")
kpi2.metric("COGS", f"${total_cogs:,.0f}", f"{cogs_mom:.1%} MoM")
kpi3.metric("Gross Profit", f"${total_profit:,.0f}", f"{profit_mom:.1%} MoM")
kpi4.metric("Gross Margin", f"{gross_margin:.1%}", f"{gross_margin_mom_percent:.1%} MoM")
kpi5, kpi6, kpi7, kpi8 = st.columns(4)
kpi5.metric("Orders", f"{orders:,}", f"{orders_mom:.1%} MoM")
kpi6.metric("Customers", f"{customers:,}", f"{customers_mom:.1%} MoM")
kpi7.metric("Average Order Value", f"${aov:,.0f}", f"{aov_mom:.1%} MoM")
kpi8.metric("Profit Per Customer", f"${profit_per_customer:,.0f}", f"{profit_mom_per_customer:.1%} MoM")

st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# ================= (1. Time Analysis) =================
st.subheader("1. Time Analysis & Growth Over Time")

col1, col2 = st.columns(2)
with col1:
    if not monthly_agg.empty:
        fig1 = px.line(monthly_agg, x="MonthPeriod", y=["Revenue", "GrossProfit"], markers=True, title="Revenue & Gross Profit Over Time", template="plotly_white")
        fig1.update_traces(line=dict(color="#8B9A6E"))
        fig1.update_layout(xaxis_title="", yaxis_title="USD ($)", margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    if not monthly_agg.empty:
        fig2 = px.line(monthly_agg, x="MonthPeriod", y="GrossMargin", markers=True, title="Gross Margin Over Time", template="plotly_white")
        fig2.update_traces(line=dict(color="#8B9A6E"))
        fig2.update_yaxes(tickformat=".0%")
        fig2.update_layout(xaxis_title="", yaxis_title="Margin", margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig2, use_container_width=True)

st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# ================= (2. Products & Volume/Margin Matrix) =================
st.subheader("2. Product Profitability & Volume/Margin Matrix")

segment_colors = {
    "High Volume / High Margin": "#8B9A6E",
    "High Volume / Low Margin": "#C97A6B",
    "Low Volume / High Margin": "#7A8FA6",
    "Low Volume / Low Margin": "#B8B8B8"
}

col1, col2 = st.columns(2)
with col1:
    top_products = product_profitability.nlargest(10, "GrossProfit").sort_values("GrossProfit")
    fig3 = px.bar(top_products, x="GrossProfit", y="ProductName", orientation="h", title="Top 10 Products by Gross Profit", template="plotly_white")
    fig3.update_traces(marker_color="#8B9A6E")
    fig3.update_layout(xaxis_title="Gross Profit ($)", yaxis_title="", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    color_col = "Segment" if "Segment" in volume_margin.columns else None
    fig4 = px.scatter(
        volume_margin, x="Revenue", y="GrossMargin",
        color=color_col, color_discrete_map=segment_colors,
        size="UnitsSold", hover_name="ProductName",
        title="Product Volume vs Margin Matrix", template="plotly_white"
    )
    fig4.update_yaxes(tickformat=".0%")
    fig4.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig4, use_container_width=True)

st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# ================= (3. Customers & Pareto Analysis) =================
st.subheader("3. Customer Profitability & Concentration")

col1, col2 = st.columns(2)
with col1:
    top_customers = customer_profitability.nlargest(10, "Revenue").sort_values("Revenue")
    fig5 = px.bar(top_customers, x="Revenue", y="CustomerID", orientation="h", title="Top 10 Customers by Revenue", template="plotly_white")
    fig5.update_traces(marker_color="#8B9A6E")
    fig5.update_layout(xaxis_title="Revenue ($)", yaxis_title="", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig5, use_container_width=True)

with col2:
  prod_sorted = product_profitability.sort_values(
      "GrossProfit", ascending=True
  ).copy()
  prod_sorted["CumulativeProfitShare"] = (
      prod_sorted["GrossProfit"] / prod_sorted["GrossProfit"].sum()
  ).cumsum()
  total_products = len(prod_sorted)
  prod_sorted["ProductRank"] = range(1, total_products + 1)

  display_df = (
      prod_sorted.sort_values("ProductRank", ascending=False)[
          [
              "ProductRank",
              "ProductName",
              "GrossProfit",
              "CumulativeProfitShare",
          ]
      ]
      .copy()
  )
  display_df["GrossProfit"] = display_df["GrossProfit"].map("${:,.2f}".format)
  display_df["CumulativeProfitShare"] = display_df[
      "CumulativeProfitShare"
  ].map("{:.1%}".format)

  fig6 = px.line(
      prod_sorted,
      x="ProductRank",
      y="CumulativeProfitShare",
      hover_name="ProductName",
      hover_data=["GrossProfit", "CumulativeProfitShare"],
      title="Pareto Analysis: Cumulative Profit Share",
      template="plotly_white",
  )
  fig6.update_traces(line=dict(color="#8B9A6E"))
  fig6.update_yaxes(tickformat=".0%")
  fig6.add_hline(
      y=0.8, line_dash="dash", line_color="gray", annotation_text="80% Profit"
  )
  fig6.update_layout(
      xaxis_title="Product Rank",
      yaxis_title="Cumulative Share",
      margin=dict(l=0, r=0, t=40, b=0),
  )
  st.plotly_chart(fig6, use_container_width=True)

st.markdown("### Product Profitability Ranking Table")
st.dataframe(display_df, use_container_width=True, height=300)

# ================= (4. RFM Analysis) =================
st.subheader("4. RFM Customer Segmentation Analysis")

correct_rfm_order = [
    "Lost / Low Value",
    "At Risk",
    "Potential Loyalists",
    "Loyal Customers",
    "Champions"
]

col1, col2 = st.columns(2)

with col1:
    fig_rfm1 = px.bar(
        rfm_summary, x="RFM_Segment", y="Customers",
        title="Customer Distribution by RFM Segment", template="plotly_white"
    )
    fig_rfm1.update_traces(marker_color="#8B9A6E")
    fig_rfm1.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=correct_rfm_order),
        xaxis_title="RFM Segment", yaxis_title="Customer Count", margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig_rfm1, use_container_width=True)

with col2:
    fig_rfm2 = px.bar(
        rfm_summary, x="RFM_Segment", y=["Revenue", "GrossProfit"],
        barmode="group", title="Revenue & Gross Profit by RFM Segment", template="plotly_white"
    )
    fig_rfm2.update_traces(selector=dict(name="Revenue"), marker_color="#8B9A6E")
    fig_rfm2.update_traces(selector=dict(name="GrossProfit"), marker_color="#C97A6B")
    
    fig_rfm2.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=correct_rfm_order),
        xaxis_title="RFM Segment", yaxis_title="USD ($)", margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig_rfm2, use_container_width=True)

# ================= (5. Discount Impact Analysis) =================
st.subheader("5. Discount Impact Analysis")
correct_discount_order = ["0%", "0-5%", "5-10%", "10-20%", "20%+"]

col1, col2 = st.columns(2)
with col1:
    fig7 = px.bar(
        discount_analysis, x="DiscountBand", y="Revenue",
        title="Revenue by Discount Band", template="plotly_white"
    )
    fig7.update_traces(marker_color="#8B9A6E")
    fig7.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=correct_discount_order),
        xaxis_title="Discount Band", yaxis_title="Revenue ($)", margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig7, use_container_width=True)

with col2:
    fig8 = px.bar(
        discount_analysis, x="DiscountBand", y="GrossMargin",
        title="Gross Margin by Discount Band", template="plotly_white"
    )
    fig8.update_traces(marker_color="#8B9A6E")
    fig8.update_yaxes(tickformat=".0%")
    fig8.update_layout(
        xaxis=dict(categoryorder="array", categoryarray=correct_discount_order),
        xaxis_title="Discount Band", yaxis_title="Gross Margin", margin=dict(l=0, r=0, t=40, b=0)
    )
    st.plotly_chart(fig8, use_container_width=True)

st.markdown('<div class="bi-divider"></div>', unsafe_allow_html=True)

# ================= (6. Employee Performance & Active Customers) =================
st.subheader("6. Employee Performance & Monthly Active Customers")

col1, col2 = st.columns(2)
with col1:
    fig9 = px.bar(employee_profitability, x="LastName", y="GrossProfit", title="Gross Profit by Employee", template="plotly_white")
    fig9.update_traces(marker_color="#8B9A6E")
    fig9.update_layout(xaxis_title="Employee", yaxis_title="Gross Profit ($)", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig9, use_container_width=True)

with col2:
    fig10 = px.line(monthly_active_customers, x="Month", y="Monthly Active Customers", markers=True, title="Monthly Active Customers", template="plotly_white")
    fig10.update_traces(line=dict(color="#8B9A6E"))
    fig10.update_layout(xaxis_title="", yaxis_title="Active Customers", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig10, use_container_width=True)

st.caption("Analytical dashboard built with Python, Pandas, Plotly and Streamlit - Northwind Project.")