"""Shared dark theme CSS for AeroSense AI Streamlit pages."""
import streamlit as st

DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #E6EDF3; }
.stApp { background: linear-gradient(135deg, #0D1117 0%, #111827 50%, #0D1117 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0D1117 0%, #161B22 100%); border-right: 1px solid #21262D; }
.kpi-card, .aqi-card { background: linear-gradient(135deg, #161B22, #21262D); border: 1px solid #30363D; border-radius: 12px; padding: 1.2rem 1rem; text-align: center; transition: border-color 0.2s, box-shadow 0.2s; }
.kpi-card:hover { border-color: #00D4FF; box-shadow: 0 0 20px rgba(0,212,255,0.15); }
.kpi-value { font-size: 2rem; font-weight: 700; color: #00D4FF; margin: 0.3rem 0; }
.kpi-label { font-size: 0.75rem; color: #8B949E; text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-delta { font-size: 0.8rem; }
.kpi-delta.up { color: #FF4444; }
.kpi-delta.down { color: #00E400; }
.info-box { background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.3); border-radius: 8px; padding: 0.75rem 1rem; margin: 0.5rem 0; font-size: 0.85rem; }
.warn-box { background: rgba(255,165,0,0.08); border: 1px solid rgba(255,165,0,0.3); border-radius: 8px; padding: 0.75rem 1rem; margin: 0.5rem 0; font-size: 0.85rem; }
.section-header { font-size: 1.1rem; font-weight: 600; color: #00D4FF; border-left: 3px solid #00D4FF; padding-left: 0.75rem; margin: 1.5rem 0 0.75rem 0; }
.badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.badge-ok { background: rgba(0,228,0,0.15); color: #00E400; border: 1px solid #00E400; }
.badge-warn { background: rgba(255,165,0,0.15); color: #FFA500; border: 1px solid #FFA500; }
.badge-error { background: rgba(255,68,68,0.15); color: #FF4444; border: 1px solid #FF4444; }
.badge-info { background: rgba(0,212,255,0.15); color: #00D4FF; border: 1px solid #00D4FF; }
.health-card { background: linear-gradient(135deg, #161B22, #21262D); border: 1px solid #30363D; border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; }
.alert-box { border-radius: 8px; padding: 1rem; margin: 0.8rem 0; font-size: 0.95rem; }
.alert-severe { background: rgba(126,0,35,0.2); border: 1px solid #7E0023; color: #FF809B; }
.alert-very-poor { background: rgba(255,0,0,0.15); border: 1px solid #FF0000; color: #FFA4A4; }
.alert-poor { background: rgba(255,126,0,0.15); border: 1px solid #FF7E00; color: #FFD199; }
.alert-moderate { background: rgba(255,255,0,0.12); border: 1px solid #CCCC00; color: #FFFF99; }
.alert-good { background: rgba(0,228,0,0.12); border: 1px solid #00E400; color: #85FF85; }
.stButton > button { border-radius: 8px !important; font-weight: 500 !important; transition: all 0.2s !important; }
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 15px rgba(0,212,255,0.3) !important; }
[data-testid="stMetricValue"] { font-size: 1.55rem !important; line-height: 1.25 !important; }
.js-plotly-plot .plotly .bg { fill: #161B22 !important; }
</style>
"""

def apply_theme() -> None:
    """Inject the dark AeroSense theme stylesheet."""
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
