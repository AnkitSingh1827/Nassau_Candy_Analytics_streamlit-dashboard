from __future__ import annotations

import plotly.express as px
import streamlit as st

from nassau_utils import build_division_summary, format_currency, format_percent, load_and_prepare_data, render_global_sidebar

st.set_page_config(page_title="Division Analysis", layout="wide")
st.title("🏭 Division Performance Dashboard")

df = load_and_prepare_data()
filtered_df, _ = render_global_sidebar(df)
division_summary = build_division_summary(filtered_df)

if division_summary.empty:
    st.info("No data matches the current filter settings.")
    st.stop()

best_division = division_summary.iloc[0]
worst_division = division_summary.iloc[-1]

cols = st.columns(4)
cols[0].metric("Best Performing Division", best_division["Division"])
cols[1].metric("Best Division Profit", format_currency(best_division["Gross Profit"]))
cols[2].metric("Worst Performing Division", worst_division["Division"])
cols[3].metric("Worst Division Margin", format_percent(worst_division["Gross Margin %"]))

left, right = st.columns(2)
with left:
    chart_df = division_summary.melt(id_vars="Division", value_vars=["Sales", "Gross Profit"], var_name="Measure", value_name="Amount")
    fig = px.bar(chart_df, x="Division", y="Amount", color="Measure", barmode="group", title="Revenue vs Profit Comparison")
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = px.bar(division_summary, x="Division", y="Gross Margin %", title="Average Margin by Division", color="Gross Margin %", color_continuous_scale="YlGnBu")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Division Ranking Table")
ranking = division_summary.copy()
ranking["Rank"] = range(1, len(ranking) + 1)
st.dataframe(
    ranking[["Rank", "Division", "Sales", "Gross Profit", "Gross Margin %", "Revenue Contribution %", "Profit Contribution %", "Orders", "Products"]],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Division Summary")
st.dataframe(
    division_summary[["Division", "Sales", "Gross Profit", "Cost", "Gross Margin %", "Profit Per Unit", "Revenue Contribution %", "Profit Contribution %"]],
    use_container_width=True,
    hide_index=True,
)