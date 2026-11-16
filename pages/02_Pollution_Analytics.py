"""
AeroSense AI — Page: Pollution Analytics
Statistical, temporal, spatial and correlation analysis.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.config import settings
from src.data.storage import load_processed, list_processed_files
from src.visualization.charts import (
    time_series_chart, bar_chart, box_plot,
    scatter_plot, correlation_heatmap, PLOTLY_TEMPLATE
)

from src.visualization.theme import apply_theme
from src.data.bootstrap import ensure_ready

st.set_page_config(page_title="Analytics — AeroSense AI", page_icon="📈", layout="wide")

apply_theme()
ensure_ready()

st.title("📈 Pollution Analytics")
st.caption("Statistical, temporal, spatial, and correlation analysis of collected data.")

# Load data
processed_files = list_processed_files()
df: pd.DataFrame = pd.DataFrame()

with st.sidebar:
    st.markdown("### 📂 Dataset")
    if processed_files:
        file_choice = st.selectbox(
            "Select processed dataset",
            [f.stem for f in processed_files],
            index=0,
        )
        df_loaded = load_processed(file_choice)
        if df_loaded is not None:
            df = df_loaded
        else:
            st.error("Could not load selected file.")
    else:
        st.info("No processed data yet. Use the **Data Explorer** to fetch data first.")

    if not df.empty:
        st.metric("Records", len(df))
        if "location_name" in df.columns:
            st.metric("Stations", df["location_name"].nunique())

# Ensure datetime is parsed
if not df.empty and "datetime_utc" in df.columns:
    df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["datetime_utc", "value"])
    df["hour"]        = df["datetime_utc"].dt.hour
    df["day"]         = df["datetime_utc"].dt.day_name()
    df["day_of_week"] = df["datetime_utc"].dt.dayofweek
    df["month"]       = df["datetime_utc"].dt.month_name()
    df["date"]        = df["datetime_utc"].dt.date

if df.empty:
    st.markdown("""
<div style="text-align:center; padding:4rem 0; color:#8B949E;">
  <div style="font-size:3rem">📈</div>
  <div style="font-size:1.1rem">No data loaded. Fetch data in <strong>Global Data Explorer</strong> first.</div>
</div>""", unsafe_allow_html=True)
    st.stop()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⏱️ Temporal", "📊 Statistical", "🏙️ Spatial", "🔗 Correlation", "📋 Summary"
])

PARAM_LABEL = f"{df['parameter'].iloc[0].upper()} (µg/m³)" if "parameter" in df.columns else "Value (µg/m³)"

# Temporal
with tab1:
    st.markdown('<div class="section-header">Temporal Patterns</div>', unsafe_allow_html=True)
    sub_t1, sub_t2, sub_t3 = st.tabs(["Daily Trend", "Hourly Pattern", "Day-of-Week"])

    with sub_t1:
        daily = df.groupby("date")["value"].mean().reset_index()
        daily.columns = ["date", "mean_value"]
        daily["date"] = pd.to_datetime(daily["date"])
        fig = time_series_chart(daily, x_col="date", y_col="mean_value",
                                title="Daily Average Concentration", y_label=PARAM_LABEL)
        st.plotly_chart(fig, use_container_width=True)

    with sub_t2:
        hourly = df.groupby("hour")["value"].agg(["mean", "std"]).reset_index()
        import plotly.graph_objects as go
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=hourly["hour"], y=hourly["mean"],
            mode="lines+markers", name="Mean",
            line=dict(color="#00D4FF", width=2),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.1)",
        ))
        fig2.update_layout(
            title="Average Concentration by Hour of Day",
            xaxis_title="Hour (0–23)", yaxis_title=PARAM_LABEL,
            template=PLOTLY_TEMPLATE, paper_bgcolor="#0D1117",
            plot_bgcolor="#161B22", font=dict(color="#E6EDF3"), height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

    with sub_t3:
        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = df.groupby("day")["value"].mean().reindex(dow_order).reset_index()
        dow.columns = ["day", "mean_value"]
        fig3 = bar_chart(dow, x_col="day", y_col="mean_value",
                         title="Average by Day of Week", y_label=PARAM_LABEL)
        st.plotly_chart(fig3, use_container_width=True)

# Statistical
with tab2:
    st.markdown('<div class="section-header">Statistical Analysis</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        stats = df["value"].describe(percentiles=[.25, .5, .75, .90, .95])
        st.dataframe(stats.to_frame("Statistics").round(3), use_container_width=True)
        st.metric("Skewness", round(float(df["value"].skew()), 3))
        st.metric("Kurtosis", round(float(df["value"].kurt()), 3))

    with col2:
        fig_hist = px.histogram(
            df, x="value", nbins=50,
            title="Value Distribution",
            labels={"value": PARAM_LABEL},
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=["#00D4FF"],
        )
        fig_hist.update_layout(paper_bgcolor="#0D1117", plot_bgcolor="#161B22",
                                font=dict(color="#E6EDF3"), height=350)
        st.plotly_chart(fig_hist, use_container_width=True)

    # Monthly box plot
    if "month" in df.columns:
        fig_box = box_plot(df, x_col="month", y_col="value",
                           title="Monthly Distribution", y_label=PARAM_LABEL)
        st.plotly_chart(fig_box, use_container_width=True)

# Spatial
with tab3:
    st.markdown('<div class="section-header">Spatial Comparison</div>', unsafe_allow_html=True)
    has_city = "city" in df.columns and (df["city"].fillna("").astype(str).str.strip() != "").any()
    has_loc  = "location_name" in df.columns and (df["location_name"].fillna("").astype(str).str.strip() != "").any()

    if has_city or has_loc:
        group_col   = "city" if has_city else "location_name"
        entity_lbl  = "City" if has_city else "Station"
        chart_title = f"Top {entity_lbl}s by Average Concentration"
        spatial_df  = df[df[group_col].fillna("").astype(str).str.strip() != ""]
        spatial_avg = spatial_df.groupby(group_col)["value"].agg(["mean", "median", "std", "count"]).reset_index()
        spatial_avg.columns = [entity_lbl, "Mean", "Median", "Std", "Count"]
        spatial_avg = spatial_avg.sort_values("Mean", ascending=False)
        st.dataframe(spatial_avg.round(2), use_container_width=True, hide_index=True)

        fig_spatial = bar_chart(
            spatial_avg.head(20), x_col=entity_lbl, y_col="Mean",
            title=chart_title, y_label=PARAM_LABEL,
        )
        st.plotly_chart(fig_spatial, use_container_width=True)
    else:
        st.info("No city/location data available for spatial comparison.")

# Correlation
with tab4:
    st.markdown('<div class="section-header">Feature Correlation</div>', unsafe_allow_html=True)
    num_cols = ["value", "hour", "day_of_week"] if "day_of_week" in df.columns \
               else ["value", "hour"]
    num_cols = [c for c in num_cols if c in df.columns]

    if len(num_cols) >= 2:
        corr = df[num_cols].corr()
        fig_corr = correlation_heatmap(corr, title="Correlation Matrix")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Insufficient numeric columns for correlation analysis.")

# Summary
with tab5:
    st.markdown('<div class="section-header">Data Summary</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Records", f"{len(df):,}")
    s2.metric("Mean " + (df["parameter"].iloc[0].upper() if "parameter" in df.columns else "Value"),
              f"{df['value'].mean():.1f} µg/m³")
    s3.metric("Max Value", f"{df['value'].max():.1f} µg/m³")
    s4.metric("Date Range",
              f"{df['datetime_utc'].min().date()} → {df['datetime_utc'].max().date()}"
              if "datetime_utc" in df.columns else "N/A")
