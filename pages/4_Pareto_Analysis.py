import plotly.graph_objects as go
import streamlit as st

from nassau_utils import build_product_summary, load_and_prepare_data, render_global_sidebar

st.set_page_config(page_title="Pareto Analysis", layout="wide")
st.title("📈 Pareto Analysis")

df = load_and_prepare_data()
filtered_df, _ = render_global_sidebar(df)
product_summary = build_product_summary(filtered_df)

if product_summary.empty:
    st.info("No data matches the current filter settings.")
    st.stop()

revenue_pareto = product_summary.sort_values("Sales", ascending=False).reset_index(drop=True)
profit_pareto = product_summary.sort_values("Gross Profit", ascending=False).reset_index(drop=True)

revenue_pareto["Cumulative Revenue %"] = revenue_pareto["Sales"].cumsum() / revenue_pareto["Sales"].sum() * 100
profit_pareto["Cumulative Profit %"] = profit_pareto["Gross Profit"].cumsum() / profit_pareto["Gross Profit"].sum() * 100

revenue_80 = revenue_pareto[revenue_pareto["Cumulative Revenue %"] <= 80]
profit_80 = profit_pareto[profit_pareto["Cumulative Profit %"] <= 80]

cols = st.columns(4)
cols[0].metric("Products Driving 80% Revenue", f"{len(revenue_80):,}")
cols[1].metric("Products Driving 80% Profit", f"{len(profit_80):,}")
cols[2].metric("Revenue Dependency Risk", f"{len(revenue_80) / len(revenue_pareto) * 100:.1f}%")
cols[3].metric("Profit Dependency Risk", f"{len(profit_80) / len(profit_pareto) * 100:.1f}%")

left, right = st.columns(2)
with left:
    fig = go.Figure()
    fig.add_bar(x=revenue_pareto["Product Name"], y=revenue_pareto["Sales"], name="Revenue")
    fig.add_scatter(x=revenue_pareto["Product Name"], y=revenue_pareto["Cumulative Revenue %"], name="Cumulative Revenue %", yaxis="y2")
    fig.update_layout(title="80% Revenue Contribution Analysis", yaxis2=dict(overlaying="y", side="right", range=[0, 110]))
    st.plotly_chart(fig, use_container_width=True)

with right:
    fig = go.Figure()
    fig.add_bar(x=profit_pareto["Product Name"], y=profit_pareto["Gross Profit"], name="Profit")
    fig.add_scatter(x=profit_pareto["Product Name"], y=profit_pareto["Cumulative Profit %"], name="Cumulative Profit %", yaxis="y2")
    fig.update_layout(title="80% Profit Contribution Analysis", yaxis2=dict(overlaying="y", side="right", range=[0, 110]))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Dependency Risk Indicators")
st.write(f"Revenue concentration is driven by {len(revenue_80)} products, which account for the first 80% of revenue.")
st.write(f"Profit concentration is driven by {len(profit_80)} products, which account for the first 80% of profit.")

st.subheader("Pareto Tables")
left_table, right_table = st.columns(2)
with left_table:
    st.caption("Revenue Pareto")
    st.dataframe(revenue_pareto[["Product Name", "Sales", "Cumulative Revenue %", "Profit Contribution %"]], use_container_width=True, hide_index=True)
with right_table:
    st.caption("Profit Pareto")
    st.dataframe(profit_pareto[["Product Name", "Gross Profit", "Cumulative Profit %", "Revenue Contribution %"]], use_container_width=True, hide_index=True)