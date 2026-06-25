from __future__ import annotations

import plotly.express as px
import streamlit as st

from nassau_utils import (
    build_division_summary,
    build_executive_insights,
    build_monthly_trend,
    build_product_summary,
    format_currency,
    format_percent,
    load_and_prepare_data,
    render_global_sidebar,
)

st.set_page_config(page_title="Nassau Candy Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    .main { background: linear-gradient(180deg, #fffdf7 0%, #ffffff 100%); }
    .block-container { padding-top: 1.5rem; }
    .hero-banner {
        padding: 1.5rem 1.75rem;
        border-radius: 1.25rem;
        background: linear-gradient(135deg, #183b66 0%, #2c6e91 55%, #e9a93b 100%);
        color: white;
        box-shadow: 0 12px 35px rgba(24, 59, 102, 0.18);
        margin-bottom: 1rem;
    }
    .hero-banner h1 { margin: 0; font-size: 2rem; }
    .hero-banner p { margin: 0.4rem 0 0 0; opacity: 0.92; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def get_data():
    return load_and_prepare_data()


df = get_data()
filtered_df, filter_state = render_global_sidebar(df)

product_summary = build_product_summary(filtered_df)
division_summary = build_division_summary(filtered_df)
monthly_trend = build_monthly_trend(filtered_df)
insights = build_executive_insights(filtered_df, product_summary, division_summary, monthly_trend)

st.markdown(
    "<div class='hero-banner'><h1>Product Line Profitability & Margin Performance Analysis</h1><p>Executive view of sales, profit, margin, risk, and factory performance for Nassau Candy Distributor.</p></div>",
    unsafe_allow_html=True,
)

st.subheader("Executive Summary")
metric_cols = st.columns(4)
metric_cols[0].metric("Total Sales", format_currency(filtered_df["Sales"].sum()))
metric_cols[1].metric("Total Profit", format_currency(filtered_df["Gross Profit"].sum()))
metric_cols[2].metric("Gross Margin", format_percent((filtered_df["Gross Profit"].sum() / filtered_df["Sales"].sum() * 100) if filtered_df["Sales"].sum() else float("nan")))
metric_cols[3].metric("Products", f"{filtered_df['Product Name'].nunique():,}")

summary_cols = st.columns(3)
summary_cols[0].metric("Top Product by Profit", insights["top_product"]["Product Name"] if insights["top_product"] is not None else "-")
summary_cols[1].metric("Best Division", insights["best_division"]["Division"] if insights["best_division"] is not None else "-")
summary_cols[2].metric("Margin Volatility", format_percent(insights["margin_volatility"] if insights["margin_volatility"] is not None else float("nan")))

st.divider()

left, right = st.columns(2)
with left:
    st.markdown("### Monthly Profit Trend")
    if monthly_trend.empty:
        st.info("No data matches the current filters.")
    else:
        fig = px.line(monthly_trend, x="Order Month", y="Gross Profit", markers=True, title="Monthly Profit Trend")
        fig.update_layout(showlegend=False, xaxis_title="Month", yaxis_title="Gross Profit")
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### Monthly Margin Trend")
    if monthly_trend.empty:
        st.info("No data matches the current filters.")
    else:
        fig = px.line(monthly_trend, x="Order Month", y="Gross Margin %", markers=True, title="Monthly Margin Trend")
        fig.update_layout(showlegend=False, xaxis_title="Month", yaxis_title="Margin %")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

left, right = st.columns(2)
with left:
    st.markdown("### Revenue vs Profit by Division")
    if division_summary.empty:
        st.info("No data matches the current filters.")
    else:
        chart_df = division_summary.melt(id_vars="Division", value_vars=["Sales", "Gross Profit"], var_name="Measure", value_name="Amount")
        fig = px.bar(chart_df, x="Division", y="Amount", color="Measure", barmode="group", title="Revenue vs Profit")
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### Profit Contribution by Division")
    if division_summary.empty:
        st.info("No data matches the current filters.")
    else:
        fig = px.pie(division_summary, names="Division", values="Gross Profit", title="Profit Contribution")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

st.markdown("### Business Recommendations")
recommendations = []
if not filtered_df.empty and insights["best_division"] is not None and insights["worst_division"] is not None:
    recommendations.append(f"Protect the {insights['best_division']['Division']} division, which is leading profit contribution.")
    recommendations.append(f"Review the {insights['worst_division']['Division']} division for pricing, cost, or product mix improvements.")
if not product_summary.empty:
    top_product = product_summary.iloc[0]
    recommendations.append(f"Prioritize inventory and promotion for {top_product['Product Name']}, the highest profit product in the current filter set.")
if monthly_trend["Gross Margin %"].std(skipna=True) > 0:
    recommendations.append("Monitor monthly margin volatility closely and investigate large swings in cost or promotion cadence.")

if recommendations:
    for item in recommendations:
        st.write(f"- {item}")
else:
    st.info("No recommendations available for the current filter combination.")

st.caption(
    f"Current filters: {filter_state['date_range'][0]} to {filter_state['date_range'][1]} | Divisions: {', '.join(filter_state['divisions']) if filter_state['divisions'] else 'All'}"
)