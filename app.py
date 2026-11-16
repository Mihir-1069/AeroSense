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
from src.utils.logging_config import setup_logging

# ---------------------------------------------------------------------------
# Logging (do before any other import that might log)
# ---------------------------------------------------------------------------
setup_logging(level=settings.LOG_LEVEL, log_dir=settings.LOGS_DIR)

# ---------------------------------------------------------------------------
# Page config — MUST be the first Streamlit call
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Global CSS — premium dark theme
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
/* ---- Base ---- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #E6EDF3;
}
.stApp {
    background: linear-gradient(135deg, #0D1117 0%, #111827 50%, #0D1117 100%);
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1117 0%, #161B22 100%);
    border-right: 1px solid #21262D;
}
[data-testid="stSidebar"] .css-1d391kg { background: transparent; }

/* ---- KPI Cards ---- */
.kpi-card {
    background: linear-gradient(135deg, #161B22, #21262D);
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    border-color: #00D4FF;
    box-shadow: 0 0 20px rgba(0,212,255,0.15);
}
.kpi-value { font-size: 2rem; font-weight: 700; color: #00D4FF; margin: 0.3rem 0; }
.kpi-label { font-size: 0.75rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-delta { font-size: 0.8rem; }
.kpi-delta.up   { color: #FF4444; }
.kpi-delta.down { color: #00E400; }

/* ---- Section headers ---- */
.section-header {
    font-size: 1.1rem; font-weight: 600; color: #00D4FF;
    border-left: 3px solid #00D4FF; padding-left: 0.75rem;
    margin: 1.5rem 0 0.75rem 0;
}

/* ---- Status badges ---- */
.badge { display: inline-block; padding: 0.2rem 0.6rem;
         border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.badge-ok     { background: rgba(0,228,0,0.15);   color: #00E400; border: 1px solid #00E400; }
.badge-warn   { background: rgba(255,165,0,0.15); color: #FFA500; border: 1px solid #FFA500; }
.badge-error  { background: rgba(255,68,68,0.15); color: #FF4444; border: 1px solid #FF4444; }
.badge-info   { background: rgba(0,212,255,0.15); color: #00D4FF; border: 1px solid #00D4FF; }

/* ---- AQI chips ---- */
.aqi-chip {
    display: inline-block; padding: 0.5rem 1.2rem;
    border-radius: 24px; font-weight: 700; font-size: 1rem;
}

/* ---- Buttons ---- */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 15px rgba(0,212,255,0.3) !important; }

/* ---- Tables ---- */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* ---- Tabs ---- */
[data-testid="stTab"] { border-radius: 8px 8px 0 0 !important; }

/* ---- Plotly charts dark bg ---- */
.js-plotly-plot .plotly .bg { fill: #161B22 !important; }

/* ---- Warning / Info boxes ---- */
.info-box {
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 8px; padding: 0.75rem 1rem; margin: 0.5rem 0;
    font-size: 0.85rem;
}
.warn-box {
    background: rgba(255,165,0,0.08);
    border: 1px solid rgba(255,165,0,0.3);
    border-radius: 8px; padding: 0.75rem 1rem; margin: 0.5rem 0;
    font-size: 0.85rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar branding
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Home content (this page = app.py = "Home")
# ---------------------------------------------------------------------------
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
    ("🤖", "ML Models", "5 algorithms", "Linear → XGBoost"),
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
<div class="kpi-card" style="text-align:left; margin-bottom:1rem;">
  <div style="font-size:0.72rem; color:#8B949E;">{num}.</div>
  <div style="font-weight:600; color:#00D4FF; margin:0.3rem 0;">{page}</div>
  <div style="font-size:0.8rem; color:#8B949E;">{desc}</div>
</div>""",
            unsafe_allow_html=True,
        )
