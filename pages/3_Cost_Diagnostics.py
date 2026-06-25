from __future__ import annotations

import numpy as np
import plotly.express as px
import streamlit as st

from nassau_utils import build_product_summary, format_currency, format_percent, load_and_prepare_data, render_global_sidebar

st.set_page_config(page_title="Cost Diagnostics", layout="wide")
st.title("💰 Cost vs Margin Diagnostics")

df = load_and_prepare_data()
filtered_df, filter_state = render_global_sidebar(df)
product_summary = build_product_summary(filtered_df)

if product_summary.empty:
    st.info("No data matches the current filter settings.")
    st.stop()

left, right = st.columns(2)
with left:
    fig = px.scatter(
        product_summary,
        x="Cost",
        y="Sales",
        size="Gross Profit",
        color="Gross Margin %",
        hover_name="Product Name",
        title="Cost vs Sales Scatter Plot",
        color_continuous_scale="Turbo",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.scatter(
        product_summary,
        x="Cost",
        y="Gross Profit",
        size="Sales",
        color="Gross Margin %",
        hover_name="Product Name",
        title="Cost vs Profit Scatter Plot",
        color_continuous_scale="Bluered",
    )
    st.plotly_chart(fig, use_container_width=True)

margin_threshold = float(filter_state["margin_threshold"])
margin_risk = product_summary[product_summary["Gross Margin %"] < margin_threshold].copy()
margin_risk["Pricing Gap"] = np.maximum(0, product_summary["Sales"] * margin_threshold / 100 - product_summary["Gross Profit"])

st.subheader("Margin Risk Products")
st.dataframe(
    margin_risk[["Product Name", "Division", "Sales", "Cost", "Gross Profit", "Gross Margin %", "Profit Per Unit"]],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Pricing Inefficiency Detection")
inefficient = product_summary[
    (product_summary["Gross Margin %"] < margin_threshold)
    & (product_summary["Sales"] >= product_summary["Sales"].median())
].copy()
inefficient["Recommended Margin %"] = margin_threshold
inefficient["Suggested Gross Profit"] = inefficient["Sales"] * margin_threshold / 100
inefficient["Profit Lift"] = inefficient["Suggested Gross Profit"] - inefficient["Gross Profit"]
st.dataframe(
    inefficient[["Product Name", "Division", "Sales", "Gross Profit", "Gross Margin %", "Recommended Margin %", "Profit Lift"]],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Products Recommended for Repricing")
repricing = inefficient.nlargest(10, "Profit Lift")
st.dataframe(
    repricing[["Product Name", "Division", "Sales", "Gross Profit", "Gross Margin %", "Profit Lift"]],
    use_container_width=True,
    hide_index=True,
)