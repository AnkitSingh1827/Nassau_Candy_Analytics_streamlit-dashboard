from __future__ import annotations

import plotly.express as px
import streamlit as st

from nassau_utils import build_product_summary, format_currency, format_percent, load_and_prepare_data, render_global_sidebar

st.set_page_config(page_title="Product Analysis", layout="wide")
st.title("📦 Product Profitability Dashboard")

df = load_and_prepare_data()
filtered_df, _ = render_global_sidebar(df)
product_summary = build_product_summary(filtered_df)

if product_summary.empty:
    st.info("No data matches the current filter settings.")
    st.stop()

top_cols = st.columns(4)
top_cols[0].metric("Top Product Profit", format_currency(product_summary.iloc[0]["Gross Profit"]))
top_cols[1].metric("Top Product Margin", format_percent(product_summary.sort_values("Gross Margin %", ascending=False).iloc[0]["Gross Margin %"]))
top_cols[2].metric("Average Product Margin", format_percent(product_summary["Gross Margin %"].mean()))
top_cols[3].metric("Products Analyzed", f"{len(product_summary):,}")

left, right = st.columns(2)
with left:
    top_profit = product_summary.nlargest(10, "Gross Profit")
    fig = px.bar(top_profit, x="Gross Profit", y="Product Name", orientation="h", title="Top 10 Products by Profit")
    st.plotly_chart(fig, use_container_width=True)

with right:
    top_margin = product_summary.nlargest(10, "Gross Margin %")
    fig = px.bar(top_margin, x="Gross Margin %", y="Product Name", orientation="h", title="Top 10 Products by Margin")
    st.plotly_chart(fig, use_container_width=True)

segment_cols = st.columns(3)
segment_cols[0].subheader("High-Profit High-Margin")
high_profit_high_margin = product_summary[(product_summary["Gross Profit"] >= product_summary["Gross Profit"].median()) & (product_summary["Gross Margin %"] >= product_summary["Gross Margin %"].median())]
segment_cols[0].dataframe(high_profit_high_margin[["Product Name", "Division", "Sales", "Gross Profit", "Gross Margin %"]], use_container_width=True, hide_index=True)

segment_cols[1].subheader("High-Sales Low-Margin")
high_sales_low_margin = product_summary[(product_summary["Sales"] >= product_summary["Sales"].median()) & (product_summary["Gross Margin %"] <= product_summary["Gross Margin %"].median())]
segment_cols[1].dataframe(high_sales_low_margin[["Product Name", "Division", "Sales", "Gross Profit", "Gross Margin %"]], use_container_width=True, hide_index=True)

segment_cols[2].subheader("Low-Sales Low-Profit")
low_sales_low_profit = product_summary[(product_summary["Sales"] <= product_summary["Sales"].quantile(0.25)) & (product_summary["Gross Profit"] <= product_summary["Gross Profit"].quantile(0.25))]
segment_cols[2].dataframe(low_sales_low_profit[["Product Name", "Division", "Sales", "Gross Profit", "Gross Margin %"]], use_container_width=True, hide_index=True)

st.subheader("Profit Contribution Visualization")
contribution = product_summary.nlargest(20, "Gross Profit")
fig = px.treemap(contribution, path=["Division", "Product Name"], values="Gross Profit", color="Gross Margin %", title="Profit Contribution by Product")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Product Detail Table")
st.dataframe(
    product_summary[["Product Name", "Division", "Sales", "Gross Profit", "Gross Margin %", "Profit Per Unit", "Revenue Contribution %", "Profit Contribution %"]],
    use_container_width=True,
    hide_index=True,
)