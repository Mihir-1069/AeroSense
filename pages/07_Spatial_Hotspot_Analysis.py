"""
AeroSense AI — Page: Spatial & Hotspot Analysis
Geospatial visualization, station clustering, and pollution hotspot identification.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.config import settings
from src.data.storage import load_processed, list_processed_files
from src.visualization.charts import map_scatter, PLOTLY_TEMPLATE, PALETTE

from src.visualization.theme import apply_theme

st.set_page_config(page_title="Spatial Analysis — AeroSense AI", page_icon="🗺️", layout="wide")

apply_theme()

st.title("🗺️ Spatial & Hotspot Analysis")
st.caption("Identify geographic pollution clusters, spatial dispersion, and regional severity across monitoring stations.")

# Sidebar dataset selector
with st.sidebar:
    st.markdown("### ⚙️ Spatial Controls")
    processed_files = list_processed_files()
    if processed_files:
        dataset_name = st.selectbox("Select Dataset", [f.stem for f in processed_files])
    else:
        dataset_name = None

    hotspot_threshold = st.slider("Hotspot Percentile Threshold", 75, 99, 90, help="Identifies stations exceeding this percentile")

# Check if data exists
df = None
if dataset_name:
    df = load_processed(dataset_name)

# Major Indian Reference Monitoring Stations for spatial benchmarking
INDIAN_STATIONS = pd.DataFrame([
    {"location_name": "Delhi (Anand Vihar)", "city": "Delhi", "latitude": 28.6469, "longitude": 77.3160, "region": "Indo-Gangetic Plain", "base_pm25": 145.0},
    {"location_name": "Delhi (RK Puram)", "city": "Delhi", "latitude": 28.5630, "longitude": 77.1860, "region": "Indo-Gangetic Plain", "base_pm25": 132.0},
    {"location_name": "Lucknow (Talkatora)", "city": "Lucknow", "latitude": 26.8330, "longitude": 80.9000, "region": "Indo-Gangetic Plain", "base_pm25": 118.0},
    {"location_name": "Patna (Muradpur)", "city": "Patna", "latitude": 25.6200, "longitude": 85.1600, "region": "Indo-Gangetic Plain", "base_pm25": 125.0},
    {"location_name": "Kolkata (Victoria)", "city": "Kolkata", "latitude": 22.5448, "longitude": 88.3426, "region": "Eastern / Coastal", "base_pm25": 88.0},
    {"location_name": "Mumbai (Bandra)", "city": "Mumbai", "latitude": 19.0596, "longitude": 72.8295, "region": "Western / Coastal", "base_pm25": 65.0},
    {"location_name": "Hyderabad (Sanathnagar)", "city": "Hyderabad", "latitude": 17.4570, "longitude": 78.4410, "region": "Deccan Plateau", "base_pm25": 54.0},
    {"location_name": "Bengaluru (BTM Layout)", "city": "Bengaluru", "latitude": 12.9166, "longitude": 77.6101, "region": "Southern Plateau", "base_pm25": 38.0},
    {"location_name": "Chennai (Alandur)", "city": "Chennai", "latitude": 13.0030, "longitude": 80.2010, "region": "Southern / Coastal", "base_pm25": 42.0},
])

# Spatial Dataset resolution
if df is not None and not df.empty and "latitude" in df.columns and "longitude" in df.columns and df["latitude"].notnull().any():
    spatial_df = df.dropna(subset=["latitude", "longitude", "value"]).copy()
    has_custom_geo = True
else:
    spatial_df = INDIAN_STATIONS.copy()
    spatial_df["value"] = spatial_df["base_pm25"]
    has_custom_geo = False
    st.info("Displaying Indian National Monitoring Grid benchmark stations. Ingest geo-tagged data via Data Explorer to map custom stations.", icon="📍")

# KPI Summary
st.markdown('<div class="section-header">📍 Spatial Distribution Overview</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

total_stations = spatial_df["location_name"].nunique() if "location_name" in spatial_df.columns else len(spatial_df)
mean_pm = spatial_df["value"].mean()
max_station_row = spatial_df.loc[spatial_df["value"].idxmax()]
p_threshold_val = np.percentile(spatial_df["value"], hotspot_threshold)
hotspots_count = int((spatial_df["value"] >= p_threshold_val).sum())

col1.metric("Monitoring Stations", f"{total_stations}")
col2.metric("Spatial Mean PM2.5", f"{mean_pm:.1f} µg/m³")
col3.metric("Peak Hotspot", f"{max_station_row.get('location_name', 'Unknown')[:18]}", f"{max_station_row['value']:.1f} µg/m³")
col4.metric(f"Hotspots (≥{hotspot_threshold}th %ile)", f"{hotspots_count}", f"Threshold: {p_threshold_val:.1f}")

# Main Interactive Map
st.markdown('<div class="section-header">🗺️ Interactive Geographic Station Map</div>', unsafe_allow_html=True)

fig_map = map_scatter(
    spatial_df,
    lat_col="latitude",
    lon_col="longitude",
    color_col="value",
    hover_col="location_name" if "location_name" in spatial_df.columns else "city",
    title="Continuous Ambient Monitoring Stations — PM2.5 Concentrations",
    height=550,
)
st.plotly_chart(fig_map, use_container_width=True)

# Hotspot Analysis and Regional Contrasts
tab1, tab2, tab3 = st.tabs(["🔥 Hotspot Identification", "🌐 Regional Contrasts", "📐 Spatial Distance Matrix"])

with tab1:
    st.markdown('<div class="section-header">Ranked Pollution Hotspots</div>', unsafe_allow_html=True)
    if "location_name" in spatial_df.columns:
        station_summary = spatial_df.groupby("location_name").agg(
            mean_pm25=("value", "mean"),
            max_pm25=("value", "max"),
            min_pm25=("value", "min"),
            std_pm25=("value", "std"),
            records=("value", "count")
        ).reset_index().sort_values("mean_pm25", ascending=False)
    else:
        station_summary = spatial_df[["city", "value"]].copy()

    # Colorize by severity
    st.dataframe(
        station_summary.round(2),
        use_container_width=True,
        hide_index=True,
    )

    fig_bar = px.bar(
        station_summary.head(10),
        x="location_name" if "location_name" in station_summary.columns else "city",
        y="mean_pm25" if "mean_pm25" in station_summary.columns else "value",
        color="mean_pm25" if "mean_pm25" in station_summary.columns else "value",
        color_continuous_scale="YlOrRd",
        title="Top 10 High-Concentration Monitoring Hotspots",
        template=PLOTLY_TEMPLATE,
        labels={"mean_pm25": "Mean PM2.5 (µg/m³)", "location_name": "Station Location"}
    )
    fig_bar.update_layout(paper_bgcolor="#0D1117", plot_bgcolor="#161B22", font=dict(color="#E6EDF3"))
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.markdown('<div class="section-header">Geographical & Regional Contrast Analysis</div>', unsafe_allow_html=True)
    if "region" in spatial_df.columns:
        region_df = spatial_df.groupby("region")["value"].agg(["mean", "median", "min", "max", "count"]).reset_index()
        st.dataframe(region_df.round(2), use_container_width=True, hide_index=True)

        fig_box = px.box(
            spatial_df,
            x="region",
            y="value",
            color="region",
            title="Pollutant Distribution by Indian Geographic Zone",
            template=PLOTLY_TEMPLATE,
            points="all",
        )
        fig_box.update_layout(paper_bgcolor="#0D1117", plot_bgcolor="#161B22", font=dict(color="#E6EDF3"), showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("Regional categorical tags are available for Indian reference grids.")

with tab3:
    st.markdown('<div class="section-header">Geodesic Proximity Matrix</div>', unsafe_allow_html=True)
    # Haversine distance calculator
    def haversine_np(lat1, lon1, lat2, lon2):
        r = 6371.0 # km
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        delta_phi = np.radians(lat2 - phi1)
        delta_lambda = np.radians(lon2 - lon1)
        a = np.sin(delta_phi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2)**2
        res = 2 * r * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
        return res

    sample_pts = spatial_df.drop_duplicates(subset=["latitude", "longitude"]).head(8)
    names = sample_pts["location_name" if "location_name" in sample_pts.columns else "city"].tolist()
    lats = sample_pts["latitude"].values
    lons = sample_pts["longitude"].values

    n = len(names)
    dist_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            dist_matrix[i, j] = haversine_np(lats[i], lons[i], lats[j], lons[j])

    dist_df = pd.DataFrame(dist_matrix.round(1), index=names, columns=names)
    st.write("Inter-Station Euclidean/Great-Circle Distances (Kilometers):")
    st.dataframe(dist_df, use_container_width=True)
