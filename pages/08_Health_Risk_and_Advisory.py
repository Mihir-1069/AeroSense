"""
AeroSense AI — Page: Health Risk & Advisory
Public health assessment, vulnerable population advisories, and international guideline audits.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.config import settings
from src.data.storage import load_processed, list_processed_files
from src.aqi.cpcb import calculate_cpcb_aqi
from src.aqi.us_epa import calculate_us_epa_aqi
from src.visualization.charts import PLOTLY_TEMPLATE, PALETTE

from src.visualization.theme import apply_theme

st.set_page_config(page_title="Health Advisory — AeroSense AI", page_icon="🏥", layout="wide")

apply_theme()

st.title("🏥 Public Health Risk & Advisory Engine")
st.caption("Epidemiological health exposure risk assessment, WHO 2021 compliance audits, and vulnerable group guidance.")

# Sidebar controls
with st.sidebar:
    st.markdown("### ⚙️ Exposure Profile")
    processed_files = list_processed_files()
    if processed_files:
        dataset_name = st.selectbox("Select Dataset", [f.stem for f in processed_files])
        df = load_processed(dataset_name)
    else:
        df = None

    st.markdown("---")
    st.markdown("### 🔬 Interactive Simulator")
    sim_mode = st.checkbox("Enable Simulation Mode", value=False)
    if sim_mode:
        sim_val = st.slider("Simulated PM2.5 (µg/m³)", 0, 500, 120)
    else:
        sim_val = None

# Determine current or target exposure value
if sim_mode and sim_val is not None:
    current_val = float(sim_val)
    pollutant_name = "pm25"
    data_source_label = f"Simulated Scenario ({current_val:.1f} µg/m³)"
elif df is not None and not df.empty and "value" in df.columns:
    current_val = float(df["value"].dropna().iloc[-1])
    pollutant_name = str(df["parameter"].iloc[0]).lower() if "parameter" in df.columns else "pm25"
    data_source_label = f"Latest observation from {dataset_name} ({current_val:.1f} µg/m³)"
else:
    current_val = 115.0  # Indian winter average reference
    pollutant_name = "pm25"
    data_source_label = f"Reference Indo-Gangetic Baseline ({current_val:.1f} µg/m³)"

# Compute AQI & Category
cpcb_res = calculate_cpcb_aqi(current_val, pollutant_name)
epa_res = calculate_us_epa_aqi(current_val, pollutant_name)

cpcb_aqi = cpcb_res.get("aqi", 0)
cpcb_cat = cpcb_res.get("category", "Unknown")

st.markdown(f'<div class="section-header">🩺 Immediate Health Status: {data_source_label}</div>', unsafe_allow_html=True)

# Status card
if cpcb_cat in ["Severe"]:
    alert_class = "alert-severe"
    badge_color = "#7E0023"
elif cpcb_cat in ["Very Poor"]:
    alert_class = "alert-very-poor"
    badge_color = "#FF0000"
elif cpcb_cat in ["Poor"]:
    alert_class = "alert-poor"
    badge_color = "#FF7E00"
elif cpcb_cat in ["Moderate"]:
    alert_class = "alert-moderate"
    badge_color = "#FFFF00"
else:
    alert_class = "alert-good"
    badge_color = "#00E400"

st.markdown(f"""
<div class="alert-box {alert_class}">
  <div style="font-size:1.3rem; font-weight:700; margin-bottom:0.4rem;">
    CPCB AQI: {cpcb_aqi} — Category: {cpcb_cat.upper()}
  </div>
  <div>
    <strong>Primary Health Implication:</strong> {cpcb_res.get('health_implication', 'Assess respiratory symptoms.')}
  </div>
</div>
""", unsafe_allow_html=True)

# 4 Key Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Concentration", f"{current_val:.1f} µg/m³")
c2.metric("CPCB AQI (India)", f"{cpcb_aqi}", cpcb_cat)
c3.metric("US EPA AQI", f"{epa_res.get('aqi', 'N/A')}", epa_res.get("category", ""))
who_diff = current_val - 15.0
c4.metric("WHO 24h Guideline Gap", f"{current_val / 15.0:.1f}x limit", f"+{who_diff:.1f} µg/m³", delta_color="inverse")

# Standards Audit Tab & Vulnerable Groups
tab1, tab2, tab3 = st.tabs(["🛡️ Vulnerable Cohorts & Protection", "⚖️ WHO vs NAAQS Standard Audit", "🏠 Indoor & Outdoor Mitigation"])

with tab1:
    st.markdown('<div class="section-header">Targeted Population Impact Matrix</div>', unsafe_allow_html=True)
    cohorts = [
        ("👶 Children & Infants", "Rapid breathing rate, alveolar growth in progress",
         "High risk of asthma exacerbation and reduced lung capacity development." if current_val > 60 else "Safe for limited outdoor play.",
         "Keep indoors; suspend outdoor school sports." if current_val > 90 else "Monitor for coughing."),
        ("🫀 Cardiovascular Patients", "Systemic inflammatory response triggered by PM2.5 translocation into bloodstream",
         "Elevated risk of ischemic heart disease, arrhythmia, and arterial vasoconstriction." if current_val > 60 else "Maintain regular medical checkups.",
         "Avoid morning exercise; ensure prescribed bronchodilators/statins are accessible."),
        ("🫁 Asthmatics & COPD Sufferers", "Direct irritation of bronchial tree and micro-airway hyper-reactivity",
         "Acute wheezing, dyspnea, and bronchospasm." if current_val > 30 else "Normal precautionary levels.",
         "Operate indoor air purifiers; wear certified N95/N99 respirators outdoors."),
        ("🏃 Outdoor Athletes & Workers", "Elevated ventilation volume multiplies total deposited particulate mass",
         "Heavy deposition in terminal bronchioles." if current_val > 45 else "Suitable for moderate physical activity.",
         "Shift outdoor training to indoor filtered facilities or mid-afternoon hours."),
    ]
    for title, vuln, impact, action in cohorts:
        with st.container():
            st.markdown(f"""
<div class="health-card">
  <div style="font-size:1.1rem; font-weight:600; color:#00D4FF; margin-bottom:0.3rem;">{title}</div>
  <div style="font-size:0.85rem; color:#8B949E; margin-bottom:0.5rem;"><strong>Vulnerability Mechanism:</strong> {vuln}</div>
  <div style="font-size:0.9rem; margin-bottom:0.4rem;"><strong>Health Impact:</strong> {impact}</div>
  <div style="font-size:0.9rem; color:#FFA500;"><strong>Recommended Action:</strong> {action}</div>
</div>
""", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-header">Regulatory Standard Benchmark Comparison</div>', unsafe_allow_html=True)
    standards_data = [
        {"Standard": "WHO Global Air Quality Guidelines (2021)", "Period": "24-Hour Mean", "Target (µg/m³)": 15.0, "Current Value": current_val, "Status": "Exceeded" if current_val > 15 else "Compliant"},
        {"Standard": "WHO Annual Guideline (2021)", "Period": "Annual Mean", "Target (µg/m³)": 5.0, "Current Value": current_val, "Status": "Exceeded" if current_val > 5 else "Compliant"},
        {"Standard": "Indian NAAQS (CPCB 2009)", "Period": "24-Hour Mean", "Target (µg/m³)": 60.0, "Current Value": current_val, "Status": "Exceeded" if current_val > 60 else "Compliant"},
        {"Standard": "Indian NAAQS (CPCB 2009)", "Period": "Annual Mean", "Target (µg/m³)": 40.0, "Current Value": current_val, "Status": "Exceeded" if current_val > 40 else "Compliant"},
        {"Standard": "US EPA NAAQS (2024 revised)", "Period": "Annual Mean", "Target (µg/m³)": 9.0, "Current Value": current_val, "Status": "Exceeded" if current_val > 9 else "Compliant"},
    ]
    st_df = pd.DataFrame(standards_data)
    st.dataframe(st_df, use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Limit Threshold",
        x=st_df["Standard"] + " (" + st_df["Period"] + ")",
        y=st_df["Target (µg/m³)"],
        marker_color="#00D4FF"
    ))
    fig.add_trace(go.Bar(
        name="Observed Concentration",
        x=st_df["Standard"] + " (" + st_df["Period"] + ")",
        y=st_df["Current Value"],
        marker_color="#FF4444" if current_val > 60 else "#FFA500"
    ))
    fig.update_layout(
        title="Ambient PM2.5 vs International Environmental Standards",
        barmode="group",
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="#0D1117",
        plot_bgcolor="#161B22",
        font=dict(color="#E6EDF3"),
        yaxis_title="PM2.5 (µg/m³)"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('<div class="section-header">Actionable Mitigation Directives</div>', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""
<div class="health-card">
  <div style="font-size:1.1rem; font-weight:600; color:#00D4FF;">😷 Personal Respiratory Protection</div>
  <ul style="font-size:0.88rem; line-height:1.6; margin-top:0.6rem;">
    <li><strong>Surgical / Cloth Masks:</strong> Ineffective against PM2.5 particles (filtration efficiency &lt; 20%).</li>
    <li><strong>N95 / FFP2 Respirators:</strong> Certified to capture ≥ 95% of 0.3 µm particles. Recommended during moderate-to-poor episodes.</li>
    <li><strong>N99 / FFP3 Respirators:</strong> Capture ≥ 99% of particulate mass. Essential for severe/hazardous air quality episodes.</li>
    <li><strong>Fit-Testing:</strong> Ensure airtight seal around nose bridge and chin without facial hair gaps.</li>
  </ul>
</div>
""", unsafe_allow_html=True)
    with m2:
        st.markdown("""
<div class="health-card">
  <div style="font-size:1.1rem; font-weight:600; color:#00D4FF;">🏡 Indoor Air Quality Management</div>
  <ul style="font-size:0.88rem; line-height:1.6; margin-top:0.6rem;">
    <li><strong>HEPA Filtration:</strong> Deploy True-HEPA air purifiers rated for room CADR (Clean Air Delivery Rate).</li>
    <li><strong>Ventilation Windows:</strong> Seal windows during morning (06:00 - 10:00) and evening inversion peaks.</li>
    <li><strong>Ventilation Slots:</strong> Air out rooms briefly around mid-afternoon (13:00 - 15:00) when planetary boundary layer expands.</li>
    <li><strong>Indoor Source Avoidance:</strong> Avoid incense sticks, scented candles, and unventilated biomass/frying.</li>
  </ul>
</div>
""", unsafe_allow_html=True)
