from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "Nassau Candy Distributor.csv"

FACTORY_COORDS: Dict[str, Tuple[float, float]] = {
    "Lot's O' Nuts": (32.881893, -111.768036),
    "Wicked Choccy's": (32.076176, -81.088371),
    "Sugar Shack": (48.11914, -96.18115),
    "Secret Factory": (41.446333, -90.565487),
    "The Other Factory": (35.1175, -89.971107),
    "Unmapped / Other": (39.8283, -98.5795),
}


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def normalize_product_name(value: object) -> str:
    text = normalize_text(value)
    if not text:
        return text
    text = re.sub(r"\s*-\s*", " - ", text)
    return text


def standardize_division(value: object) -> str:
    text = normalize_text(value).lower()
    if not text:
        return "Unknown"
    if "chocolate" in text:
        return "Chocolate"
    if "sugar" in text:
        return "Sugar"
    if "other" in text:
        return "Other"
    return text.title()


PRODUCT_FACTORY_SOURCE = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar - Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack",
    "SweeTARTS": "Sugar Shack",
    "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory",
    "Hair Toffee": "The Other Factory",
    "Fizzy Lifting Drinks": "Sugar Shack",
    "Lickable Wallpaper": "Secret Factory",
    "Wonka Gum": "Secret Factory",
    "Kazookles": "The Other Factory",
}

PRODUCT_TO_FACTORY = {
    normalize_product_name(name): factory for name, factory in PRODUCT_FACTORY_SOURCE.items()
}


@st.cache_data(show_spinner=False)
def load_and_prepare_data(data_path: str | Path = DATA_FILE) -> pd.DataFrame:
    raw = pd.read_csv(data_path)
    return clean_data(raw)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [normalize_text(column) for column in cleaned.columns]

    text_columns = [
        "Order ID",
        "Ship Mode",
        "Country/Region",
        "City",
        "State/Province",
        "Division",
        "Region",
        "Product ID",
        "Product Name",
    ]
    for column in text_columns:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].map(normalize_text)

    if "Division" in cleaned.columns:
        cleaned["Division"] = cleaned["Division"].map(standardize_division)

    if "Product Name" in cleaned.columns:
        cleaned["Product Name"] = cleaned["Product Name"].map(normalize_product_name)

    for column in ["Sales", "Units", "Gross Profit", "Cost", "Postal Code", "Customer ID", "Row ID"]:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    if "Order Date" in cleaned.columns:
        cleaned["Order Date"] = pd.to_datetime(cleaned["Order Date"], errors="coerce", dayfirst=True)
    if "Ship Date" in cleaned.columns:
        cleaned["Ship Date"] = pd.to_datetime(cleaned["Ship Date"], errors="coerce", dayfirst=True)

    if "Units" in cleaned.columns:
        missing_units = cleaned["Units"].isna()
        if missing_units.any():
            units_by_product = cleaned.groupby("Product Name")["Units"].transform("median")
            units_by_division = cleaned.groupby("Division")["Units"].transform("median")
            overall_units = cleaned["Units"].median()
            cleaned["Units"] = cleaned["Units"].fillna(units_by_product)
            cleaned["Units"] = cleaned["Units"].fillna(units_by_division)
            cleaned["Units"] = cleaned["Units"].fillna(overall_units)
        cleaned["Units"] = cleaned["Units"].round().clip(lower=1)

    cleaned = cleaned[
        cleaned["Sales"].notna()
        & cleaned["Gross Profit"].notna()
        & cleaned["Cost"].notna()
        & cleaned["Units"].notna()
        & cleaned["Order Date"].notna()
    ].copy()
    cleaned = cleaned[
        (cleaned["Sales"] > 0)
        & (cleaned["Cost"] >= 0)
        & (cleaned["Units"] > 0)
    ].copy()

    cleaned["Gross Margin %"] = np.where(
        cleaned["Sales"] != 0,
        cleaned["Gross Profit"] / cleaned["Sales"] * 100,
        np.nan,
    )
    cleaned["Profit Per Unit"] = np.where(
        cleaned["Units"] != 0,
        cleaned["Gross Profit"] / cleaned["Units"],
        np.nan,
    )
    cleaned["Cost Rate %"] = np.where(
        cleaned["Sales"] != 0,
        cleaned["Cost"] / cleaned["Sales"] * 100,
        np.nan,
    )
    cleaned["Order Month"] = cleaned["Order Date"].dt.to_period("M").dt.to_timestamp()
    cleaned["Factory"] = cleaned["Product Name"].map(
        lambda product: PRODUCT_TO_FACTORY.get(normalize_product_name(product), "Unmapped / Other")
    )

    return cleaned.reset_index(drop=True)


@st.cache_data(show_spinner=False)
def get_date_bounds(df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    return df["Order Date"].min(), df["Order Date"].max()


def render_global_sidebar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    min_date, max_date = get_date_bounds(df)
    min_date_value = min_date.date()
    max_date_value = max_date.date()
    all_divisions = sorted(df["Division"].dropna().unique().tolist())

    st.sidebar.header("Global Filters")
    st.sidebar.caption("These filters apply to every analysis page.")

    if "filter_date_range" not in st.session_state:
        st.session_state["filter_date_range"] = (min_date_value, max_date_value)
    if "filter_divisions" not in st.session_state:
        st.session_state["filter_divisions"] = all_divisions
    if "filter_product_search" not in st.session_state:
        st.session_state["filter_product_search"] = ""
    if "filter_margin_threshold" not in st.session_state:
        st.session_state["filter_margin_threshold"] = 20.0

    st.sidebar.date_input(
        "Date Range",
        min_value=min_date_value,
        max_value=max_date_value,
        value=st.session_state["filter_date_range"],
        key="filter_date_range",
    )
    st.sidebar.multiselect(
        "Division Filter",
        options=all_divisions,
        default=st.session_state["filter_divisions"],
        key="filter_divisions",
    )
    st.sidebar.text_input(
        "Product Search Box",
        placeholder="Search by product name",
        key="filter_product_search",
    )
    st.sidebar.slider(
        "Margin Threshold (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state["filter_margin_threshold"]),
        step=1.0,
        key="filter_margin_threshold",
    )

    filtered = apply_filters(
        df,
        date_range=st.session_state["filter_date_range"],
        divisions=st.session_state["filter_divisions"],
        product_search=st.session_state["filter_product_search"],
        margin_threshold=st.session_state["filter_margin_threshold"],
    )

    st.sidebar.caption(f"Showing {len(filtered):,} of {len(df):,} rows")

    return filtered, {
        "date_range": st.session_state["filter_date_range"],
        "divisions": st.session_state["filter_divisions"],
        "product_search": st.session_state["filter_product_search"],
        "margin_threshold": st.session_state["filter_margin_threshold"],
    }


def apply_filters(
    df: pd.DataFrame,
    date_range: tuple,
    divisions: Iterable[str],
    product_search: str,
    margin_threshold: float,
) -> pd.DataFrame:
    filtered = df.copy()

    start_date, end_date = date_range
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    filtered = filtered[(filtered["Order Date"] >= start_ts) & (filtered["Order Date"] <= end_ts)]

    selected_divisions = list(divisions) if divisions else []
    if selected_divisions and set(selected_divisions) != set(sorted(df["Division"].dropna().unique().tolist())):
        filtered = filtered[filtered["Division"].isin(selected_divisions)]

    search_text = normalize_text(product_search)
    if search_text:
        filtered = filtered[filtered["Product Name"].str.contains(search_text, case=False, regex=False, na=False)]

    if margin_threshold is not None:
        filtered = filtered[filtered["Gross Margin %"] >= float(margin_threshold)]

    return filtered.reset_index(drop=True)


def _mode(series: pd.Series) -> str:
    modes = series.mode(dropna=True)
    if not modes.empty:
        return str(modes.iat[0])
    non_null = series.dropna()
    return str(non_null.iat[0]) if not non_null.empty else "Unknown"


def build_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Product Name", dropna=False)
        .agg(
            Division=("Division", _mode),
            Orders=("Order ID", "nunique"),
            Sales=("Sales", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Cost=("Cost", "sum"),
            Units=("Units", "sum"),
            FirstOrder=("Order Date", "min"),
            LastOrder=("Order Date", "max"),
        )
        .reset_index()
    )
    summary = summary.rename(columns={"GrossProfit": "Gross Profit", "FirstOrder": "First Order", "LastOrder": "Last Order"})
    summary["Gross Margin %"] = np.where(summary["Sales"] != 0, summary["Gross Profit"] / summary["Sales"] * 100, np.nan)
    summary["Profit Per Unit"] = np.where(summary["Units"] != 0, summary["Gross Profit"] / summary["Units"], np.nan)
    summary["Cost Rate %"] = np.where(summary["Sales"] != 0, summary["Cost"] / summary["Sales"] * 100, np.nan)

    total_sales = summary["Sales"].sum()
    total_profit = summary["Gross Profit"].sum()
    summary["Revenue Contribution %"] = np.where(total_sales != 0, summary["Sales"] / total_sales * 100, np.nan)
    summary["Profit Contribution %"] = np.where(total_profit != 0, summary["Gross Profit"] / total_profit * 100, np.nan)

    return summary.sort_values("Gross Profit", ascending=False).reset_index(drop=True)


def build_division_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Division", dropna=False)
        .agg(
            Orders=("Order ID", "nunique"),
            Products=("Product Name", "nunique"),
            Sales=("Sales", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Cost=("Cost", "sum"),
            Units=("Units", "sum"),
            AverageMarginPct=("Gross Margin %", "mean"),
        )
        .reset_index()
    )
    summary = summary.rename(columns={"GrossProfit": "Gross Profit", "AverageMarginPct": "Average Margin %"})
    summary["Gross Margin %"] = np.where(summary["Sales"] != 0, summary["Gross Profit"] / summary["Sales"] * 100, np.nan)
    summary["Profit Per Unit"] = np.where(summary["Units"] != 0, summary["Gross Profit"] / summary["Units"], np.nan)

    total_sales = summary["Sales"].sum()
    total_profit = summary["Gross Profit"].sum()
    summary["Revenue Contribution %"] = np.where(total_sales != 0, summary["Sales"] / total_sales * 100, np.nan)
    summary["Profit Contribution %"] = np.where(total_profit != 0, summary["Gross Profit"] / total_profit * 100, np.nan)

    return summary.sort_values("Gross Profit", ascending=False).reset_index(drop=True)


def build_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("Order Month", dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
        .sort_values("Order Month")
        .reset_index(drop=True)
    )
    monthly = monthly.rename(columns={"GrossProfit": "Gross Profit"})
    monthly["Gross Margin %"] = np.where(monthly["Sales"] != 0, monthly["Gross Profit"] / monthly["Sales"] * 100, np.nan)
    monthly["Margin Volatility 3M"] = monthly["Gross Margin %"].rolling(window=3, min_periods=2).std()
    return monthly


def build_regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Region", dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
    )
    summary = summary.rename(columns={"GrossProfit": "Gross Profit"})
    summary["Gross Margin %"] = np.where(summary["Sales"] != 0, summary["Gross Profit"] / summary["Sales"] * 100, np.nan)
    return summary.sort_values("Gross Profit", ascending=False).reset_index(drop=True)


def build_state_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("State/Province", dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
    )
    summary = summary.rename(columns={"GrossProfit": "Gross Profit"})
    summary["Gross Margin %"] = np.where(summary["Sales"] != 0, summary["Gross Profit"] / summary["Sales"] * 100, np.nan)
    return summary.sort_values("Sales", ascending=False).reset_index(drop=True)


def build_factory_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("Factory", dropna=False)
        .agg(
            Sales=("Sales", "sum"),
            GrossProfit=("Gross Profit", "sum"),
            Cost=("Cost", "sum"),
            Units=("Units", "sum"),
            Products=("Product Name", "nunique"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
    )
    summary = summary.rename(columns={"GrossProfit": "Gross Profit"})
    summary["Gross Margin %"] = np.where(summary["Sales"] != 0, summary["Gross Profit"] / summary["Sales"] * 100, np.nan)
    total_sales = summary["Sales"].sum()
    total_profit = summary["Gross Profit"].sum()
    summary["Revenue Contribution %"] = np.where(total_sales != 0, summary["Sales"] / total_sales * 100, np.nan)
    summary["Profit Contribution %"] = np.where(total_profit != 0, summary["Gross Profit"] / total_profit * 100, np.nan)
    return summary.sort_values("Gross Profit", ascending=False).reset_index(drop=True)


def build_executive_insights(
    filtered_df: pd.DataFrame,
    product_summary: pd.DataFrame,
    division_summary: pd.DataFrame,
    monthly_trend: pd.DataFrame,
) -> dict:
    insights: dict[str, object] = {}

    if not filtered_df.empty:
        insights["top_product"] = product_summary.iloc[0] if not product_summary.empty else None
        insights["best_division"] = division_summary.iloc[0] if not division_summary.empty else None
        insights["worst_division"] = division_summary.iloc[-1] if not division_summary.empty else None
        insights["top_profit_5_share"] = product_summary.head(5)["Profit Contribution %"].sum() if not product_summary.empty else np.nan
        insights["top_revenue_5_share"] = product_summary.head(5)["Revenue Contribution %"].sum() if not product_summary.empty else np.nan
        insights["margin_volatility"] = monthly_trend["Gross Margin %"].std() if not monthly_trend.empty else np.nan
        insights["monthly_peak"] = monthly_trend.sort_values("Gross Profit", ascending=False).iloc[0] if not monthly_trend.empty else None
    else:
        insights["top_product"] = None
        insights["best_division"] = None
        insights["worst_division"] = None
        insights["top_profit_5_share"] = np.nan
        insights["top_revenue_5_share"] = np.nan
        insights["margin_volatility"] = np.nan
        insights["monthly_peak"] = None

    return insights


def format_currency(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"${value:,.0f}"


def format_percent(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:,.2f}%"
