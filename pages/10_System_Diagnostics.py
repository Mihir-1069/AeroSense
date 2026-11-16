"""
AeroSense AI — Page: System Diagnostics & Settings
API key configuration, OpenAQ v3 connectivity audit, hardware profiling, storage inspection, and log monitoring.
"""
import os
import sys
import platform
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd

from src.config import settings
from src.api.openaq_client import OpenAQClient

from src.visualization.theme import apply_theme

st.set_page_config(page_title="System Diagnostics — AeroSense AI", page_icon="🛠️", layout="wide")

apply_theme()

st.title("🛠️ System Diagnostics & Settings")
st.caption("Configure OpenAQ v3 API credentials, verify live connectivity, inspect hardware, and monitor runtime telemetry.")

# API Key Configuration (.env Management)
st.markdown('<div class="section-header">🔑 OpenAQ v3 API Key & Configuration</div>', unsafe_allow_html=True)

col_key1, col_key2 = st.columns([2, 1])

with col_key1:
    api_key_input = st.text_input(
        "OpenAQ API Key",
        value="",
        type="password",
        placeholder=f"Current: {settings.masked_api_key()}",
        help="Register for a free OpenAQ API v3 key at https://explore.openaq.org/register",
    )
    if st.button("💾 Save & Activate API Key", type="primary"):
        cleaned_key = api_key_input.strip()
        if not cleaned_key:
            st.warning("Please paste a valid API key before saving.")
        else:
            env_path = settings.PROJECT_ROOT / ".env"
            lines = []
            if env_path.exists():
                lines = env_path.read_text(encoding="utf-8").splitlines()
            elif (settings.PROJECT_ROOT / ".env.example").exists():
                lines = (settings.PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()

            updated = False
            new_lines = []
            for line in lines:
                if line.strip().startswith("OPENAQ_API_KEY="):
                    new_lines.append(f"OPENAQ_API_KEY={cleaned_key}")
                    updated = True
                else:
                    new_lines.append(line)
            if not updated:
                new_lines.append(f"OPENAQ_API_KEY={cleaned_key}")

            env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            os.environ["OPENAQ_API_KEY"] = cleaned_key
            settings.OPENAQ_API_KEY = cleaned_key
            st.success("✅ OpenAQ API key saved to `.env` and activated in this session!")

with col_key2:
    st.markdown(f"""
<div class="kpi-card">
  <div style="font-size:0.75rem; color:#8B949E; text-transform:uppercase;">Active Configuration</div>
  <div style="margin-top:0.5rem; font-size:0.9rem;">
    <strong>API Key:</strong> <code>{settings.masked_api_key()}</code><br>
    <strong>Default Country:</strong> <code>{settings.DEFAULT_COUNTRY}</code><br>
    <strong>Default Pollutant:</strong> <code>{settings.DEFAULT_POLLUTANT.upper()}</code><br>
    <strong>Train/Val/Test:</strong> <code>{int(settings.TRAIN_RATIO*100)}/{int(settings.VAL_RATIO*100)}/{int((1-settings.TRAIN_RATIO-settings.VAL_RATIO)*100)}%</code>
  </div>
</div>
""", unsafe_allow_html=True)

# API Connectivity Section
st.markdown('<div class="section-header">🌐 OpenAQ v3 API Connectivity Audit</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 2])

has_key = settings.api_key_configured()
c1.metric("API Key Status", "Configured" if has_key else "Missing", "X-API-Key Header" if has_key else "Required")
c2.metric("Target Endpoint", "api.openaq.org/v3", "HTTPS / TLS 1.3")

with c3:
    if st.button("🔄 Test Live OpenAQ v3 Connection"):
        with st.spinner("Pinging OpenAQ v3 API..."):
            t0 = time.time()
            client = OpenAQClient()
            res = client.test_connection()
            lat_ms = (time.time() - t0) * 1000
            if res.get("ok"):
                st.success(
                    f"✅ {res['message']} Latency: {lat_ms:.1f} ms | "
                    f"Countries indexed: {res.get('total_countries', 'unknown')}"
                )
            else:
                st.error(f"❌ Connection failed: {res.get('message', 'Unknown error')}")

# Hardware & Acceleration
st.markdown('<div class="section-header">⚡ Compute Hardware & Deep Learning Acceleration</div>', unsafe_allow_html=True)

try:
    import torch
    cuda_avail = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_avail else "CPU Engine (PyTorch 2.x)"
    torch_version = torch.__version__
except ImportError:
    cuda_avail = False
    device_name = "PyTorch not found"
    torch_version = "None"

hw1, hw2, hw3, hw4 = st.columns(4)
hw1.metric("OS & Architecture", f"{platform.system()} ({platform.machine()})")
hw2.metric("Python Runtime", platform.python_version())
hw3.metric("PyTorch Engine", torch_version)
hw4.metric("Acceleration Device", "CUDA GPU" if cuda_avail else "CPU Engine", device_name[:22])

# Storage & Disk Footprint
st.markdown('<div class="section-header">💾 Persistent Storage & Artifact Inventory</div>', unsafe_allow_html=True)

def get_dir_stats(path: Path):
    if not path.exists():
        return 0, 0.0
    files = [f for f in path.rglob("*") if f.is_file()]
    total_size = sum(f.stat().st_size for f in files)
    return len(files), total_size / (1024 * 1024)

dirs_to_check = [
    ("Raw Ingestion Data", settings.RAW_DIR),
    ("Processed Parquet Datasets", settings.PROCESSED_DIR),
    ("Engineered Feature Sets", settings.FEATURES_DIR),
    ("Traditional ML Models", settings.ML_MODELS_DIR),
    ("Deep Learning Checkpoints", settings.DL_MODELS_DIR),
    ("Exported Archives & Reports", settings.EXPORTS_DIR),
    ("Runtime Application Logs", settings.LOGS_DIR),
]

storage_data = []
for label, p in dirs_to_check:
    fc, mb = get_dir_stats(p)
    try:
        rel_path = str(p.relative_to(settings.PROJECT_ROOT))
    except ValueError:
        rel_path = str(p)
    storage_data.append({
        "Component Directory": label,
        "Path": rel_path,
        "File Count": fc,
        "Footprint (MB)": round(mb, 2),
    })

st.dataframe(pd.DataFrame(storage_data), use_container_width=True, hide_index=True)

# Cache & Memory Management
st.markdown('<div class="section-header">🧹 Cache & Memory Governance</div>', unsafe_allow_html=True)
cm1, cm2 = st.columns(2)

with cm1:
    if st.button("🗑️ Clear Streamlit Cache", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Application memory cache cleared successfully.")

with cm2:
    if st.button("🧹 Purge Temporary Exports", use_container_width=True):
        export_dir = settings.EXPORTS_DIR
        if export_dir.exists():
            count = 0
            for f in export_dir.glob("*"):
                if f.is_file():
                    f.unlink()
                    count += 1
            st.success(f"Cleaned {count} temporary export file(s).")

# Live Log Streamer
st.markdown('<div class="section-header">📜 Runtime Logs (Tail 30 Entries)</div>', unsafe_allow_html=True)

log_files = sorted(settings.LOGS_DIR.glob("*.log")) if settings.LOGS_DIR.exists() else []
if log_files:
    log_file = log_files[-1]
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        recent_lines = lines[-30:] if len(lines) >= 30 else lines
        log_text = "".join(recent_lines)
        st.caption(f"Showing tail of `{log_file.name}`")
        st.code(log_text if log_text.strip() else "Log file is currently empty.", language="text")
    except Exception as e:
        st.warning(f"Could not read log file: {e}")
else:
    st.info(f"Log files will appear inside `{settings.LOGS_DIR}` as actions execute.")
