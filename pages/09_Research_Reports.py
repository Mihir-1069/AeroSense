"""
AeroSense AI — Page: Research Reports & Export Engine
Generate publication-ready academic reports, PDF documentation, and reproducibility bundles.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from src.config import settings
from src.data.storage import load_processed, list_processed_files
from src.reporting.report_generator import (
    generate_markdown_report,
    generate_html_report,
    generate_pdf_report,
    create_export_archive,
    compute_dataset_summary,
)

st.set_page_config(page_title="Research Reports — AeroSense AI", page_icon="📑", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.stApp { background: linear-gradient(135deg,#0D1117,#111827,#0D1117); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0D1117,#161B22); border-right:1px solid #21262D; }
.section-header { font-size:1.1rem; font-weight:600; color:#00D4FF; border-left:3px solid #00D4FF; padding-left:.75rem; margin:1.5rem 0 .75rem 0; }
.kpi-card { background:linear-gradient(135deg,#161B22,#21262D); border:1px solid #30363D; border-radius:12px; padding:1.2rem; }
</style>""", unsafe_allow_html=True)

st.title("📑 Academic Research & Technical Reports")
st.caption("Generate formal B.Tech research reports, data provenance ledgers, and verifiable reproducibility archives.")

# Sidebar dataset selector
with st.sidebar:
    st.markdown("### ⚙️ Report Settings")
    processed_files = list_processed_files()
    if not processed_files:
        st.warning("No datasets found. Ingest data in Data Explorer first.")
        st.stop()

    dataset_name = st.selectbox("Select Target Dataset", [f.stem for f in processed_files])
    location_label = st.text_input("Station / Location Label", value=dataset_name.replace("_", " ").title())
    include_benchmarks = st.checkbox("Include Model Benchmarks", value=True)

# Load data
df = load_processed(dataset_name)
if df is None or df.empty:
    st.error("Could not load the selected dataset.")
    st.stop()

# Retrieve model metrics from session state or persisted disk artifacts
metrics_df = st.session_state.get("train_results")
if metrics_df is None or metrics_df.empty:
    bench_csv = settings.PROJECT_ROOT / "experiments" / "results" / "ml_benchmark_results.csv"
    if bench_csv.exists():
        try:
            metrics_df = pd.read_csv(bench_csv)
        except Exception:
            metrics_df = None
    if metrics_df is None and settings.ML_MODELS_DIR.exists():
        ml_rows = []
        import joblib
        for p in sorted(settings.ML_MODELS_DIR.glob("*.pkl")):
            try:
                d = joblib.load(p)
                tm = d.get("test_metrics")
                if tm:
                    ml_rows.append({
                        "model": p.stem,
                        "test_MAE": tm.get("MAE"),
                        "test_RMSE": tm.get("RMSE"),
                        "test_R2": tm.get("R2"),
                        "train_time_s": d.get("train_time_s", 0.0),
                    })
            except Exception:
                pass
        if ml_rows:
            metrics_df = pd.DataFrame(ml_rows)

dl_results = st.session_state.get("dl_result")
if not dl_results and settings.DL_MODELS_DIR.exists():
    dl_rows = []
    for p in sorted(settings.DL_MODELS_DIR.glob("*.pt")):
        try:
            import torch
            ckpt = torch.load(p, map_location="cpu", weights_only=False)
            if ckpt.get("metrics"):
                dl_rows.append({
                    "model_name": ckpt.get("model_name", p.stem),
                    "lookback": ckpt.get("lookback", 24),
                    "horizon": ckpt.get("horizon", 24),
                    "metrics": ckpt["metrics"],
                    "device": "cpu",
                })
        except Exception:
            pass
    if dl_rows:
        dl_results = dl_rows

# Summary metrics
stats = compute_dataset_summary(df)

st.markdown('<div class="section-header">📊 Report Dataset Scope</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Validated Observations", f"{stats.get('count', 0):,}")
c2.metric("Mean Concentration", f"{stats.get('mean', 0.0):.2f} µg/m³")
c3.metric("Observation Span", f"{stats.get('duration_days', 0)} days")
c4.metric("WHO Exceedance Rate", f"{stats.get('who_exceedance_pct', 0.0):.1f}%")

# Generate contents
md_report = generate_markdown_report(
    dataset_name=dataset_name,
    df=df,
    metrics_df=metrics_df if include_benchmarks else None,
    dl_results=dl_results if include_benchmarks else None,
    location_name=location_label,
)

html_report = generate_html_report(
    dataset_name=dataset_name,
    df=df,
    metrics_df=metrics_df if include_benchmarks else None,
    dl_results=dl_results if include_benchmarks else None,
    location_name=location_label,
)

# Export buttons
st.markdown('<div class="section-header">📥 Export Documentation & Data Bundles</div>', unsafe_allow_html=True)
b1, b2, b3, b4 = st.columns(4)

with b1:
    st.download_button(
        label="📄 Download Markdown (.md)",
        data=md_report,
        file_name=f"AeroSense_Report_{dataset_name}.md",
        mime="text/markdown",
        use_container_width=True,
    )

with b2:
    st.download_button(
        label="🌐 Download HTML Report (.html)",
        data=html_report,
        file_name=f"AeroSense_Report_{dataset_name}.html",
        mime="text/html",
        use_container_width=True,
    )

with b3:
    # PDF generation
    pdf_path = settings.DATA_DIR / "exports" / f"AeroSense_Report_{dataset_name}.pdf"
    if st.button("📑 Generate PDF Report", use_container_width=True):
        with st.spinner("Compiling PDF with ReportLab..."):
            try:
                generate_pdf_report(
                    dataset_name=dataset_name,
                    df=df,
                    output_path=pdf_path,
                    metrics_df=metrics_df if include_benchmarks else None,
                    dl_results=dl_results if include_benchmarks else None,
                    location_name=location_label,
                )
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label="⬇️ Save PDF Document",
                    data=pdf_bytes,
                    file_name=f"AeroSense_Report_{dataset_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.success("PDF successfully compiled!")
            except Exception as e:
                st.error(f"PDF compilation failed: {e}")

with b4:
    # Archive bundle
    if st.button("📦 Create ZIP Bundle", use_container_width=True):
        with st.spinner("Packaging archive..."):
            zip_path = create_export_archive(
                dataset_name=dataset_name,
                df=df,
                metrics_df=metrics_df if include_benchmarks else None,
            )
            with open(zip_path, "rb") as f:
                zip_bytes = f.read()
            st.download_button(
                label="⬇️ Download Full ZIP",
                data=zip_bytes,
                file_name=zip_path.name,
                mime="application/zip",
                use_container_width=True,
            )
            st.success("Bundle packaged!")

# Interactive Report Preview
st.markdown('<div class="section-header">👁️ Live Report Preview</div>', unsafe_allow_html=True)
with st.expander("Expand to Read Complete Technical Report", expanded=True):
    st.markdown(md_report)

# Citation generator
st.markdown('<div class="section-header">📚 Citation & Provenance Ledger</div>', unsafe_allow_html=True)
col_cite, col_prov = st.columns(2)

with col_cite:
    st.markdown("""
<div class="kpi-card">
  <div style="font-weight:600; color:#00D4FF; margin-bottom:0.4rem;">IEEE Academic Citation Format</div>
  <code style="font-size:0.78rem; display:block; padding:0.6rem; background:#0D1117; border-radius:6px; color:#E6EDF3;">
    [1] AeroSense AI Research Group, "Global Air Pollution Pattern Analysis and AQI Forecasting Using Machine Learning and Deep Learning," B.Tech Thesis Technical Report, 2026. Data sourced from OpenAQ Community API v3.
  </code>
</div>
""", unsafe_allow_html=True)

with col_prov:
    st.markdown(f"""
<div class="kpi-card">
  <div style="font-weight:600; color:#00D4FF; margin-bottom:0.4rem;">Data Provenance Metadata</div>
  <div style="font-size:0.82rem; color:#8B949E; line-height:1.6;">
    • <strong>Ingestion Source:</strong> OpenAQ API v3 Continuous Ambient Monitoring<br>
    • <strong>Dataset Identifier:</strong> <code>{dataset_name}</code><br>
    • <strong>Storage Format:</strong> Apache Parquet (Snappy compression)<br>
    • <strong>Validation Status:</strong> Schema & MAD Outlier Filter Passed
  </div>
</div>
""", unsafe_allow_html=True)
