"""
AeroSense AI — Page: Global Data Explorer
Fetch live OpenAQ API v3 data or inspect locally stored & benchmark datasets.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone

from src.config import settings
from src.api.openaq_client import OpenAQClient, OpenAQAuthError, OpenAQConnectionError
from src.data.ingestion import DataIngestion
from src.data.validation import validate_measurements
from src.data.cleaning import clean_measurements, normalise_units
from src.data.storage import save_processed, load_processed, list_processed_files, export_csv
from src.visualization.charts import time_series_chart, map_scatter

st.set_page_config(page_title="Data Explorer — AeroSense AI", page_icon="🌐", layout="wide")

# Inject shared CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.stApp { background: linear-gradient(135deg,#0D1117,#111827,#0D1117); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0D1117,#161B22); border-right:1px solid #21262D; }
.section-header { font-size:1.1rem; font-weight:600; color:#00D4FF; border-left:3px solid #00D4FF; padding-left:.75rem; margin:1.5rem 0 .75rem 0; }
.badge { display:inline-block; padding:.2rem .6rem; border-radius:20px; font-size:.72rem; font-weight:600; }
.badge-ok { background:rgba(0,228,0,.15); color:#00E400; border:1px solid #00E400; }
.badge-warn { background:rgba(255,165,0,.15); color:#FFA500; border:1px solid #FFA500; }
.badge-error { background:rgba(255,68,68,.15); color:#FF4444; border:1px solid #FF4444; }
</style>
""", unsafe_allow_html=True)

st.title("🌐 Global Data Explorer")
st.caption("Fetch real-time and historical measurements from OpenAQ API v3, or inspect stored datasets.")

# ---------------------------------------------------------------------------
# Sidebar — controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌍 Live API Extraction")

    country_iso   = st.text_input("Country ISO Code", value=settings.DEFAULT_COUNTRY, help="e.g. IN, US, DE, GB, CN")
    pollutant     = st.selectbox("Pollutant", settings.SUPPORTED_POLLUTANTS,
                                  index=0, format_func=str.upper)
    days_back     = st.slider("Days of history", 1, 90, settings.DEFAULT_DATE_RANGE_DAYS)
    max_locations = st.slider("Max locations to query", 1, 20, 3)
    impute_strategy = st.selectbox("Missing-value strategy",
                                    ["interpolate", "forward_fill", "station_median", "none"])
    fetch_btn = st.button("🚀 Fetch Live OpenAQ Data", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("### 📂 Local / Benchmark Store")
    stored_files = list_processed_files()
    if stored_files:
        selected_stored = st.selectbox("Stored Datasets", [f.stem for f in stored_files])
        load_stored_btn = st.button("📥 Load Stored Dataset", use_container_width=True)
    else:
        selected_stored = None
        load_stored_btn = False
        st.caption("No locally saved Parquet datasets yet.")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "clean_df" not in st.session_state:
    st.session_state.clean_df = None
if "locations_df" not in st.session_state:
    st.session_state.locations_df = None
if "data_origin" not in st.session_state:
    st.session_state.data_origin = None

# ---------------------------------------------------------------------------
# API key notice
# ---------------------------------------------------------------------------
if not settings.api_key_configured():
    st.warning(
        "⚠️ OpenAQ API key is not configured. Go to **🛠️ System Diagnostics** (sidebar) to enter your key for live queries, "
        "or load a stored benchmark dataset from the sidebar.",
        icon="⚠️",
    )

# ---------------------------------------------------------------------------
# Load stored dataset
# ---------------------------------------------------------------------------
if load_stored_btn and selected_stored:
    loaded = load_processed(selected_stored)
    if loaded is not None and not loaded.empty:
        st.session_state.clean_df = loaded
        st.session_state.raw_df = loaded
        st.session_state.data_origin = f"Stored Dataset: {selected_stored}"
        if {"location_id", "latitude", "longitude"}.issubset(loaded.columns):
            loc_cols = [c for c in ["location_id", "location_name", "city", "country", "latitude", "longitude"] if c in loaded.columns]
            st.session_state.locations_df = loaded[loc_cols].drop_duplicates(subset=["location_id"])
        else:
            st.session_state.locations_df = None
        st.success(f"✅ Loaded **{len(loaded):,}** records from `{selected_stored}`.")
    else:
        st.error(f"Could not load dataset `{selected_stored}`.")

# ---------------------------------------------------------------------------
# Fetch Live Data
# ---------------------------------------------------------------------------
if fetch_btn:
    if not settings.api_key_configured():
        st.error("Cannot fetch live data: OpenAQ API key not configured. Add it in System Diagnostics or `.env`.")
    else:
        ingestion = DataIngestion()
        date_to   = datetime.now(timezone.utc)
        date_from = date_to - timedelta(days=days_back)
        df_from   = date_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        df_to     = date_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        with st.spinner(f"Discovering {pollutant.upper()} monitoring stations in {country_iso}…"):
            try:
                locs_df = ingestion.fetch_locations(country_iso, limit=200, parameter=pollutant)
                st.session_state.locations_df = locs_df
            except OpenAQAuthError as e:
                st.error(f"Authentication failed: {e}")
                st.stop()
            except OpenAQConnectionError as e:
                st.error(f"Connection error: {e}")
                st.stop()
            except Exception as e:
                st.error(f"Error fetching locations: {e}")
                st.stop()

        if locs_df.empty:
            st.warning(f"No locations found for country code '{country_iso}' measuring {pollutant.upper()}.")
            st.stop()

        active_mask = locs_df["is_active"] if "is_active" in locs_df.columns else pd.Series([True] * len(locs_df))
        active_locs = locs_df[active_mask].head(max_locations)
        if active_locs.empty:
            active_locs = locs_df.head(max_locations)

        prog = st.progress(0, text="Fetching sensor measurements…")
        all_frames = []
        loc_rows = active_locs.to_dict("records")
        for i, row in enumerate(loc_rows):
            loc_id = int(row["location_id"])
            prog.progress((i + 1) / len(loc_rows), text=f"Station {i+1}/{len(loc_rows)}: {row.get('location_name', loc_id)}")
            try:
                s_map = json.loads(row.get("sensors_map", "{}")) if isinstance(row.get("sensors_map"), str) else {}
                sensor_id = s_map.get(pollutant.lower())
                loc_meta = {
                    "location_name": row.get("location_name", ""),
                    "city": row.get("city", ""),
                    "country": row.get("country", country_iso),
                    "latitude": row.get("latitude"),
                    "longitude": row.get("longitude"),
                }
                df = ingestion.fetch_measurements(
                    loc_id, pollutant, df_from, df_to,
                    sensor_id=sensor_id, location_meta=loc_meta,
                )
                if not df.empty:
                    all_frames.append(df)
            except Exception as exc:
                st.warning(f"Skipped station {loc_id}: {exc}")

        prog.empty()

        if not all_frames:
            st.warning("No measurements returned for the selected date window. Try expanding days of history or choosing another station/country.")
            st.stop()

        raw_df = pd.concat(all_frames, ignore_index=True)
        st.session_state.raw_df = raw_df

        # Validate + clean
        clean_df, report = validate_measurements(raw_df.copy())
        clean_df = normalise_units(clean_df)
        clean_df = clean_measurements(clean_df, impute=impute_strategy)
        st.session_state.clean_df = clean_df
        st.session_state.data_origin = f"Live OpenAQ API v3 ({country_iso} / {pollutant.upper()})"

        # Save processed
        save_processed(clean_df, f"{country_iso}_{pollutant}_processed")
        st.success(f"✅ Fetched **{len(raw_df):,}** raw → **{len(clean_df):,}** clean records from {len(all_frames)} active station(s).")

# Auto-load first stored dataset if session state has nothing yet so the user sees data right away
if st.session_state.clean_df is None and stored_files:
    default_name = stored_files[0].stem
    default_df = load_processed(default_name)
    if default_df is not None and not default_df.empty:
        st.session_state.clean_df = default_df
        st.session_state.raw_df = default_df
        st.session_state.data_origin = f"Pre-loaded Reference Benchmark ({default_name})"
        if {"location_id", "latitude", "longitude"}.issubset(default_df.columns):
            loc_cols = [c for c in ["location_id", "location_name", "city", "country", "latitude", "longitude"] if c in default_df.columns]
            st.session_state.locations_df = default_df[loc_cols].drop_duplicates(subset=["location_id"])

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
clean_df = st.session_state.clean_df
locs_df  = st.session_state.locations_df

if clean_df is not None and not clean_df.empty:
    if st.session_state.data_origin:
        st.info(f"**Active Data Source:** {st.session_state.data_origin}", icon="📡")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Table", "📈 Time Series", "🗺️ Map", "📋 Quality Report"])

    with tab1:
        st.markdown('<div class="section-header">Validated Measurements</div>', unsafe_allow_html=True)
        display_cols = [c for c in ["datetime_utc", "location_name", "city", "country",
                                     "parameter", "value", "unit", "is_imputed", "data_source"] if c in clean_df.columns]
        st.dataframe(clean_df[display_cols].sort_values("datetime_utc", ascending=False), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            csv_path = export_csv(clean_df, f"aerosense_{country_iso}_{pollutant}")
            with open(csv_path, "rb") as f:
                st.download_button("⬇️ Download CSV", f, file_name=csv_path.name, mime="text/csv")
        with col2:
            st.metric("Records", f"{len(clean_df):,}")

    with tab2:
        st.markdown('<div class="section-header">Time Series</div>', unsafe_allow_html=True)
        color_col = "location_name" if "location_name" in clean_df.columns and clean_df["location_name"].nunique() > 1 else None
        active_param = str(clean_df["parameter"].iloc[0]).upper() if "parameter" in clean_df.columns else pollutant.upper()
        fig = time_series_chart(
            clean_df.sort_values("datetime_utc"),
            y_col="value",
            title=f"{active_param} Concentration over Time",
            y_label=f"{active_param} (µg/m³)",
            color_col=color_col,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown('<div class="section-header">Station Map</div>', unsafe_allow_html=True)
        if locs_df is not None and not locs_df.empty:
            map_data = locs_df.dropna(subset=["latitude", "longitude"]).copy()
            if map_data.empty:
                st.info("No coordinate data available for map display.")
            else:
                if "location_id" in clean_df.columns:
                    avg = clean_df.groupby("location_id")["value"].mean().reset_index()
                    avg.columns = ["location_id", "value"]
                    map_data = map_data.merge(avg, on="location_id", how="left")
                    map_data["value"] = map_data["value"].fillna(0)
                fig = map_scatter(map_data, title="Monitoring Stations")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Location metadata not available.")

    with tab4:
        st.markdown('<div class="section-header">Data Quality Report</div>', unsafe_allow_html=True)
        raw_df = st.session_state.raw_df
        if raw_df is not None:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Raw Records", f"{len(raw_df):,}")
            m2.metric("Clean Records", f"{len(clean_df):,}")
            m3.metric("Stations", clean_df["location_id"].nunique() if "location_id" in clean_df.columns else "N/A")
            m4.metric("Imputed", int(clean_df["is_imputed"].sum()) if "is_imputed" in clean_df.columns else 0)

            if "value" in clean_df.columns:
                st.markdown("**Value Statistics**")
                st.dataframe(clean_df["value"].describe().to_frame().T, use_container_width=True)

            missing_pct = clean_df.isnull().mean() * 100
            st.markdown("**Missing Value %**")
            miss_df = missing_pct[missing_pct > 0].to_frame("missing_%").round(2)
            if miss_df.empty:
                st.success("Zero missing values in validated columns.")
            else:
                st.dataframe(miss_df, use_container_width=True)
else:
    st.markdown(
        """
<div style="text-align:center; padding: 4rem 0; color: #8B949E;">
  <div style="font-size:3rem; margin-bottom:1rem;">🌐</div>
  <div style="font-size:1.1rem;">Configure filters and click <strong>Fetch Live OpenAQ Data</strong> to begin.</div>
  <div style="font-size:0.85rem; margin-top:.5rem;">Default: India (IN) | PM2.5 | Last 30 days</div>
</div>""",
        unsafe_allow_html=True,
    )
