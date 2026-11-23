"""
AeroSense AI — Main Streamlit Entry Point
Intelligent Global Air Quality Monitoring, Analysis & Forecasting
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

from src.config import settings
from src.data.bootstrap import ensure_ready
from src.utils.logging_config import setup_logging

# Logging (do before any other import that might log)
setup_logging(level=settings.LOG_LEVEL, log_dir=settings.LOGS_DIR)

# Page config — MUST be the first Streamlit call
from src.visualization.theme import apply_theme

st.set_page_config(
    page_title=f"{settings.APP_NAME} — Air Quality Intelligence",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://docs.openaq.org/",
        "Report a bug": None,
        "About": f"**{settings.APP_NAME}** v{settings.APP_VERSION}\n\n{settings.APP_TAGLINE}",
    },
)

apply_theme()
ensure_ready()

# Sidebar branding
with st.sidebar:
    st.markdown(
        """
<div style="text-align:center; padding: 1rem 0 1.5rem 0;">
  <div style="font-size: 2.4rem; margin-bottom: 0.3rem;">🌬️</div>
  <div style="font-size: 1.3rem; font-weight: 700; color: #00D4FF; letter-spacing: -0.02em;">
    AeroSense AI
  </div>
  <div style="font-size: 0.65rem; color: #8B949E; margin-top: 0.3rem; letter-spacing: 0.05em;">
    AIR QUALITY INTELLIGENCE PLATFORM
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # API status pill
    if settings.api_key_configured():
        st.markdown('<span class="badge badge-ok">🔗 API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-warn">⚠️ API Key Not Set</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        f"""
<div style="font-size: 0.72rem; color: #8B949E; padding: 0.5rem 0;">
  v{settings.APP_VERSION} &nbsp;|&nbsp; Phase 1 India-first<br>
  <span style="color: #30363D;">Data: OpenAQ API v3</span>
</div>
""",
        unsafe_allow_html=True,
    )

# Home content (this page = app.py = "Home")
st.markdown(
    f"""
<div style="text-align:center; padding: 2rem 0 1rem 0;">
  <h1 style="font-size: 2.4rem; font-weight: 700; color: #00D4FF; margin:0;">
    🌬️ AeroSense AI
  </h1>
  <p style="font-size: 1rem; color: #8B949E; margin: 0.5rem 0 0 0;">
    {settings.APP_TAGLINE}
  </p>
</div>
""",
    unsafe_allow_html=True,
)

# Platform overview cards
c1, c2, c3, c4 = st.columns(4)
cards = [
    ("🌍", "Data Sources", "OpenAQ API v3", "Real-time & historical"),
    ("🤖", "ML Models", "6 algorithms", "Linear → XGBoost"),
    ("🧠", "DL Models", "4 architectures", "LSTM, GRU, TCN, Transformer"),
    ("📊", "AQI Standards", "2 standards", "CPCB (India) + US EPA"),
]
for col, (icon, label, val, sub) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(
            f"""
<div class="kpi-card">
  <div style="font-size:1.8rem">{icon}</div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value" style="font-size:1.2rem">{val}</div>
  <div style="font-size:0.72rem; color:#8B949E;">{sub}</div>
</div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# API configuration status
st.markdown('<div class="section-header">🔌 Platform Status</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([2, 1])

with col_a:
    if settings.api_key_configured():
        st.success(
            "**OpenAQ API v3** — API key configured. Navigate to **Global Data Explorer** to fetch data.",
            icon="✅",
        )
    else:
        st.warning(
            "**OpenAQ API key not configured.** Go to **🛠️ System Diagnostics** to add your key, "
            "or explore the pre-loaded reference benchmark datasets immediately.",
            icon="⚠️",
        )

    st.info(
        "**Navigation**: Use the sidebar pages to explore data, run analysis, train models, "
        "and generate forecasts. Each section is independently functional.",
        icon="ℹ️",
    )

with col_b:
    st.markdown(
        f"""
<div class="kpi-card" style="text-align:left; padding: 1rem;">
  <div style="font-size:0.72rem; color:#8B949E; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">
    Quick Status
  </div>
  <div style="font-size:0.85rem; margin-bottom:0.4rem;">
    API Key: {'<span class="badge badge-ok">SET</span>' if settings.api_key_configured() else '<span class="badge badge-warn">MISSING</span>'}
  </div>
  <div style="font-size:0.85rem; margin-bottom:0.4rem;">
    Env: <span class="badge badge-info">{settings.APP_ENV.upper()}</span>
  </div>
  <div style="font-size:0.85rem;">
    Default: <span style="color:#00D4FF;">🇮🇳 India / PM2.5</span>
  </div>
</div>""",
        unsafe_allow_html=True,
    )

# Getting Started
st.markdown('<div class="section-header">🚀 Getting Started</div>', unsafe_allow_html=True)
steps = [
    ("1", "🛠️ System Diagnostics", "Configure your OpenAQ API key, test connectivity, and inspect hardware."),
    ("2", "🌐 Data Explorer", "Select India (default) or any country, then fetch live or inspect stored data."),
    ("3", "📈 Analytics", "Explore temporal, spatial, and pollutant correlation patterns."),
    ("4", "🎯 AQI Intelligence", "Calculate CPCB and US EPA AQI from your collected data."),
    ("5", "🔮 Forecasting Studio", "Train ML/DL models and generate pollution forecasts."),
    ("6", "📊 Benchmarking", "Compare model performance with real metrics and test results."),
]
cols = st.columns(3)
for i, (num, page, desc) in enumerate(steps):
    with cols[i % 3]:
        st.markdown(
            f"""
<div class="kpi-card" style="text-align:left; margin-bottom:1rem; min-height:115px;">
  <div style="font-size:0.72rem; color:#8B949E;">{num}.</div>
  <div style="font-weight:600; color:#00D4FF; margin:0.3rem 0;">{page}</div>
  <div style="font-size:0.8rem; color:#8B949E;">{desc}</div>
</div>""",
            unsafe_allow_html=True,
        )

# Project Team & Faculty Supervision
st.markdown('<div class="section-header">👨‍🎓 Project Team & Faculty Supervision</div>', unsafe_allow_html=True)
st.caption(
    "**Assigned Project Title:** Air Pollution Pattern Analysis and AQI Forecasting  |  "
    "**Quantum University, Roorkee** (`CSE-DS`, Batch `2023 - 2027`, Sem `7`)  |  "
    "**Faculty Assigned:** Mr. Abhishek Kumar (QU0125261068)"
)
team_members = [
    ("Aryan Saini", "23030173", "2301315012", "Data Engineering, OpenAQ v3 & Parquet"),
    ("Ayaan Ali", "23030175", "2301315013", "Feature Synthesis, AQI Engine & Baselines"),
    ("Kawalpreet Kaur", "23030255", "2301315019", "ML & Deep Learning Benchmarking"),
    ("Mihir Kumar", "23030268", "2301315022", "Explainable AI, UI & Research Reports"),
]
tcols = st.columns(4)
for col, (name, sid, roll, role) in zip(tcols, team_members):
    with col:
        st.markdown(
            f"""
<div class="kpi-card" style="text-align:left; margin-bottom:0.8rem; min-height:122px;">
  <div style="font-weight:700; color:#00D4FF; font-size:0.95rem;">{name}</div>
  <div style="font-size:0.76rem; color:#E6EDF3; margin:0.25rem 0;">ID: <code>{sid}</code> | Roll: <code>{roll}</code></div>
  <div style="font-size:0.74rem; color:#8B949E;">2023 - 2027 · Sem 7 · CSE-DS</div>
  <div style="font-size:0.74rem; color:#8B949E; margin-top:0.2rem;">{role}</div>
</div>""",
            unsafe_allow_html=True,
        )
