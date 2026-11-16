"""
AeroSense AI — Page: Model Benchmarking
Compare all trained ML and DL models with real held-out evaluation metrics.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.config import settings

from src.visualization.theme import apply_theme

st.set_page_config(page_title="Benchmarking — AeroSense AI", page_icon="📊", layout="wide")
apply_theme()

st.title("📊 Model Benchmarking")
st.caption("Compare trained ML and DL models using held-out test split evaluation metrics.")

PLOTLY_TEMPLATE = "plotly_dark"

ml_dir = settings.ML_MODELS_DIR
dl_dir = settings.DL_MODELS_DIR

ml_artifacts = sorted(ml_dir.glob("*.pkl"))
dl_artifacts = sorted(dl_dir.glob("*.pt"))

if not ml_artifacts and not dl_artifacts:
    st.markdown("""
<div style="text-align:center; padding:4rem 0; color:#8B949E;">
  <div style="font-size:3rem">📊</div>
  <div style="font-size:1.1rem">No trained models yet.</div>
  <div style="font-size:.85rem; margin-top:.5rem;">Go to <strong>Forecasting Studio</strong> to train models first.</div>
</div>""", unsafe_allow_html=True)
    st.stop()

# Collect ML metrics (session state first, else persisted .pkl / CSV metadata)
ml_rows = []
session_res = st.session_state.get("train_results")
if session_res is not None and not session_res.empty:
    ml_bench_df = session_res.copy()
    ml_bench_df["Family"] = "ML"
else:
    for path in ml_artifacts:
        try:
            import joblib
            d = joblib.load(path)
            tm = d.get("test_metrics", {})
            vm = d.get("val_metrics", {})
            ml_rows.append({
                "model": path.stem,
                "Family": "ML",
                "val_MAE": vm.get("MAE"),
                "val_RMSE": vm.get("RMSE"),
                "val_R2": vm.get("R2"),
                "test_MAE": tm.get("MAE"),
                "test_RMSE": tm.get("RMSE"),
                "test_R2": tm.get("R2"),
                "train_time_s": d.get("train_time_s"),
                "Artifact": path.name,
            })
        except Exception:
            pass
    ml_bench_df = pd.DataFrame(ml_rows)

# Collect DL metrics from checkpoints
dl_rows = []
for path in dl_artifacts:
    try:
        import torch
        ckpt = torch.load(path, map_location="cpu", weights_only=False)
        m = ckpt.get("metrics", {})
        dl_rows.append({
            "model": ckpt.get("model_name", path.stem),
            "Family": "DL",
            "Lookback": ckpt.get("lookback"),
            "Horizon": ckpt.get("horizon"),
            "test_MAE": m.get("MAE"),
            "test_RMSE": m.get("RMSE"),
            "test_R2": m.get("R2"),
            "Artifact": path.name,
        })
    except Exception:
        pass
dl_bench_df = pd.DataFrame(dl_rows)

# Unified leaderboard
combined_cols = ["model", "Family", "test_MAE", "test_RMSE", "test_R2"]
frames = []
if not ml_bench_df.empty and "test_MAE" in ml_bench_df.columns and ml_bench_df["test_MAE"].notna().any():
    frames.append(ml_bench_df[[c for c in ["model", "Family", "val_MAE", "test_MAE", "test_RMSE", "test_R2", "train_time_s"] if c in ml_bench_df.columns]])
if not dl_bench_df.empty and "test_MAE" in dl_bench_df.columns and dl_bench_df["test_MAE"].notna().any():
    frames.append(dl_bench_df[[c for c in ["model", "Family", "test_MAE", "test_RMSE", "test_R2", "Lookback", "Horizon"] if c in dl_bench_df.columns]])

st.markdown('<div class="section-header">🏆 Unified Model Leaderboard</div>', unsafe_allow_html=True)

if frames:
    unified = pd.concat(frames, ignore_index=True)
    unified = unified.sort_values("test_MAE", ascending=True).reset_index(drop=True)
    unified.insert(0, "Rank", range(1, len(unified) + 1))

    # Top KPI summary
    best = unified.iloc[0]
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Top Performing Model", f"{best['model']} ({best['Family']})")
    k2.metric("Best Test MAE", f"{best['test_MAE']:.3f} µg/m³")
    k3.metric("Best Test RMSE", f"{best['test_RMSE']:.3f} µg/m³")
    k4.metric("Best Test R²", f"{best['test_R2']:.3f}")

    st.dataframe(unified.round(3), use_container_width=True, hide_index=True)

    # Bar comparison chart
    metric = st.selectbox("Compare Models By", ["test_MAE", "test_RMSE", "test_R2"])
    color_scale = "Viridis" if metric == "test_R2" else "Viridis_r"
    fig = px.bar(
        unified,
        x="model",
        y=metric,
        color="Family",
        text_auto=".3f",
        title=f"Held-Out Test Comparison — {metric}",
        template=PLOTLY_TEMPLATE,
        color_discrete_map={"ML": "#00D4FF", "DL": "#7B61FF"},
    )
    fig.update_layout(
        paper_bgcolor="#0D1117",
        plot_bgcolor="#161B22",
        font=dict(color="#E6EDF3"),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Saved model artifacts found, but evaluation metrics are missing. Re-train in **Forecasting Studio** to record metrics.")
    if not ml_bench_df.empty:
        st.dataframe(ml_bench_df, use_container_width=True, hide_index=True)
    if not dl_bench_df.empty:
        st.dataframe(dl_bench_df, use_container_width=True, hide_index=True)

st.markdown('<div class="section-header">📖 Evaluation Methodology</div>', unsafe_allow_html=True)
st.markdown("""
- All models use **strict chronological splitting** (no future data leakage).
- **Train / Val / Test** = 70% / 15% / 15% strictly in temporal sequence.
- **MAE** = Mean Absolute Error | **RMSE** = Root Mean Squared Error | **R²** = Coefficient of Determination.
- Lower MAE/RMSE is better; higher R² (max 1.0) is better.
- Metrics are computed exclusively on the **held-out test split**.
""")
