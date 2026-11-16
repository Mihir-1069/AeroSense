"""
AeroSense AI — Page: AQI Intelligence
CPCB (India) and US EPA AQI calculation with sub-indices and health info.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.aqi.cpcb import calculate_cpcb_aqi
from src.aqi.us_epa import calculate_epa_aqi
from src.data.storage import load_processed, list_processed_files
from src.visualization.charts import aqi_gauge, PLOTLY_TEMPLATE, AQI_COLORS

from src.visualization.theme import apply_theme

st.set_page_config(page_title="AQI Intelligence — AeroSense AI", page_icon="🎯", layout="wide")

apply_theme()

st.title("🎯 AQI Intelligence")
st.caption("Calculate CPCB (India) and US EPA Air Quality Index from measured pollutant concentrations.")

# Manual input or from loaded data
st.markdown('<div class="section-header">📥 Pollutant Input</div>', unsafe_allow_html=True)

input_mode = st.radio("Input mode", ["Manual entry", "From loaded dataset"], horizontal=True)

measurements: dict = {}

if input_mode == "Manual entry":
    st.markdown("Enter average concentrations. Leave at 0 to exclude a pollutant.")
    col1, col2, col3 = st.columns(3)
    with col1:
        pm25 = st.number_input("PM2.5 (µg/m³, 24h avg)", 0.0, 1000.0, 0.0, step=0.5)
        pm10 = st.number_input("PM10 (µg/m³, 24h avg)", 0.0, 2000.0, 0.0, step=1.0)
    with col2:
        no2  = st.number_input("NO2 (µg/m³, 24h avg)", 0.0, 2000.0, 0.0, step=0.5)
        so2  = st.number_input("SO2 (µg/m³, 24h avg)", 0.0, 2000.0, 0.0, step=0.5)
    with col3:
        co   = st.number_input("CO (mg/m³, 8h avg)", 0.0, 50.0, 0.0, step=0.1)
        o3   = st.number_input("O3 (µg/m³, 8h avg)", 0.0, 1000.0, 0.0, step=0.5)

    if pm25 > 0: measurements["pm25"] = pm25
    if pm10 > 0: measurements["pm10"] = pm10
    if no2  > 0: measurements["no2"]  = no2
    if so2  > 0: measurements["so2"]  = so2
    if co   > 0: measurements["co"]   = co
    if o3   > 0: measurements["o3"]   = o3

else:
    processed_files = list_processed_files()
    if processed_files:
        file_choice = st.selectbox("Select dataset", [f.stem for f in processed_files])
        df = load_processed(file_choice)
        if df is not None and not df.empty and "value" in df.columns and "parameter" in df.columns:
            # Use latest 24h average per parameter
            df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], utc=True, errors="coerce")
            df = df.dropna(subset=["datetime_utc", "value"])
            cutoff = df["datetime_utc"].max() - pd.Timedelta(hours=24)
            recent = df[df["datetime_utc"] >= cutoff]
            if recent.empty:
                recent = df
            avg_per_param = recent.groupby("parameter")["value"].mean()
            measurements = avg_per_param.to_dict()
            st.success(f"Loaded {len(measurements)} pollutant(s) from dataset: {', '.join(measurements.keys())}")
    else:
        st.info("No processed data found. Use **Data Explorer** first, or switch to Manual entry.")

# Calculate
if st.button("🔬 Calculate AQI", type="primary") or measurements:
    if not measurements:
        st.warning("Enter at least one pollutant concentration.")
        st.stop()

    tab_cpcb, tab_epa, tab_method = st.tabs(["🇮🇳 CPCB (India)", "🇺🇸 US EPA", "📖 Methodology"])

    # CPCB
    with tab_cpcb:
        result = calculate_cpcb_aqi(measurements)
        col1, col2 = st.columns([1, 2])
        with col1:
            fig = aqi_gauge(result.aqi, "CPCB")
            st.plotly_chart(fig, use_container_width=True)

            cat_color = AQI_COLORS.get(result.category, "#888")
            st.markdown(
                f"""
<div class="aqi-card">
  <div style="font-size:2rem; font-weight:700; color:{cat_color};">{result.aqi}</div>
  <div style="font-size:1.1rem; font-weight:600; color:{cat_color};">{result.category}</div>
  <div style="font-size:0.8rem; color:#8B949E; margin-top:.5rem;">Dominant: <b>{result.dominant_pollutant.upper()}</b></div>
</div>""",
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(f"**Health Message:** {result.health_message}")
            if not result.is_complete:
                st.warning(
                    f"⚠️ Partial AQI: only {', '.join(result.calculated_pollutants)} available. "
                    f"Missing: {', '.join(result.missing_pollutants)}. This is an indicative value.",
                    icon="⚠️",
                )
            # Sub-indices table
            if result.sub_indices:
                sub_df = pd.DataFrame([
                    {"Pollutant": s.pollutant.upper(),
                     "Concentration": f"{s.concentration:.2f} {s.unit}",
                     "Sub-Index": s.sub_index}
                    for s in result.sub_indices
                ])
                st.dataframe(sub_df, use_container_width=True, hide_index=True)

    # EPA
    with tab_epa:
        epa_result = calculate_epa_aqi(measurements)
        col1, col2 = st.columns([1, 2])
        with col1:
            fig_e = aqi_gauge(epa_result.aqi, "EPA")
            st.plotly_chart(fig_e, use_container_width=True)
            cat_color_e = AQI_COLORS.get(epa_result.category, "#888")
            st.markdown(
                f"""
<div class="aqi-card">
  <div style="font-size:2rem; font-weight:700; color:{cat_color_e};">{epa_result.aqi}</div>
  <div style="font-size:1.1rem; font-weight:600; color:{cat_color_e};">{epa_result.category}</div>
  <div style="font-size:0.8rem; color:#8B949E; margin-top:.5rem;">Dominant: <b>{epa_result.dominant_pollutant.upper()}</b></div>
</div>""",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(f"**Health Message:** {epa_result.health_message}")
            if not epa_result.is_complete:
                st.warning(
                    f"⚠️ Partial AQI: computed from {', '.join(epa_result.calculated_pollutants)} only.",
                    icon="⚠️",
                )
            if epa_result.sub_indices:
                sub_df_e = pd.DataFrame([
                    {"Pollutant": s.pollutant.upper(),
                     "Concentration": f"{s.concentration:.2f} {s.unit}",
                     "Sub-Index": s.sub_index}
                    for s in epa_result.sub_indices
                ])
                st.dataframe(sub_df_e, use_container_width=True, hide_index=True)

    # Methodology
    with tab_method:
        st.markdown("""
### CPCB (India) AQI Methodology
- **Standard**: National Air Quality Index, CPCB 2014
- **Pollutants**: PM2.5, PM10, NO2, SO2, CO, O3, NH3
- **Averaging periods**: PM — 24h; NO2/SO2 — 24h; CO — 8h; O3 — 8h
- **Formula**: Sub-index = ((Ihi−Ilo)/(BPhi−BPlo)) × (C−BPlo) + Ilo
- **Final AQI** = maximum of all computed sub-indices (dominant pollutant)

### US EPA AQI Methodology
- **Standard**: EPA AQI Technical Assistance Document 2018
- **Pollutants**: PM2.5 (24h), PM10 (24h), O3 (8h, ppm), NO2 (1h, ppb), SO2 (1h, ppb), CO (8h, ppm)
- **Same interpolation formula** as CPCB with EPA-specific breakpoints
- **Final AQI** = maximum of all computed sub-indices

> ⚠️ **Important**: AQI values computed here use the available data only.
> An incomplete set of pollutants results in an indicative AQI, not an official value.
        """)
