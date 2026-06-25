from __future__ import annotations

import folium
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from nassau_utils import FACTORY_COORDS, build_factory_summary, load_and_prepare_data, render_global_sidebar

st.set_page_config(page_title="Factory Analysis", layout="wide")
st.title("🏭 Factory Analysis")

df = load_and_prepare_data()
filtered_df, _ = render_global_sidebar(df)
factory_summary = build_factory_summary(filtered_df)

if factory_summary.empty:
    st.info("No data matches the current filter settings.")
    st.stop()

left, right = st.columns(2)
with left:
    factory_chart = px.bar(factory_summary, x="Factory", y="Gross Profit", title="Profit by Factory", color="Gross Margin %", color_continuous_scale="RdYlGn")
    st.plotly_chart(factory_chart, use_container_width=True)

with right:
    sales_chart = px.bar(factory_summary, x="Factory", y="Sales", title="Sales by Factory", color="Gross Margin %", color_continuous_scale="Blues")
    st.plotly_chart(sales_chart, use_container_width=True)

st.subheader("Factory Margin Performance")
margin_chart = px.bar(factory_summary, x="Factory", y="Gross Margin %", title="Margin by Factory", color="Gross Margin %", color_continuous_scale="Viridis")
st.plotly_chart(margin_chart, use_container_width=True)

st.subheader("Factory Map Visualization")
map_center = [39.5, -95.0]
factory_map = folium.Map(location=map_center, zoom_start=4, tiles="cartodbpositron")

for _, row in factory_summary.iterrows():
    location = FACTORY_COORDS.get(row["Factory"], FACTORY_COORDS["Unmapped / Other"])
    folium.CircleMarker(
        location=location,
        radius=max(6, min(24, row["Sales"] / factory_summary["Sales"].max() * 24)),
        color="#1f77b4",
        fill=True,
        fill_opacity=0.75,
        popup=folium.Popup(
            f"<b>{row['Factory']}</b><br>Sales: ${row['Sales']:,.0f}<br>Profit: ${row['Gross Profit']:,.0f}<br>Margin: {row['Gross Margin %']:.2f}%",
            max_width=300,
        ),
        tooltip=row["Factory"],
    ).add_to(factory_map)

st_folium(factory_map, use_container_width=True, height=520)

st.subheader("Factory Summary Table")
st.dataframe(
    factory_summary[["Factory", "Sales", "Gross Profit", "Gross Margin %", "Revenue Contribution %", "Profit Contribution %", "Products", "Orders"]],
    use_container_width=True,
    hide_index=True,
)