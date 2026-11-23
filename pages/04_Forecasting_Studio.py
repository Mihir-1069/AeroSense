"""
AeroSense AI — Page: Forecasting Studio
Train ML and DL models and generate pollution forecasts.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

from src.config import settings
from src.data.storage import load_processed, list_processed_files
from src.ml.train import train_models, load_model, predict as ml_predict
from src.ml.baselines import evaluate_baselines
from src.visualization.charts import forecast_chart, loss_curves

from src.visualization.theme import apply_theme
from src.data.bootstrap import ensure_ready

st.set_page_config(page_title="Forecasting Studio — AeroSense AI", page_icon="🔮", layout="wide")

apply_theme()
ensure_ready()

st.title("🔮 Forecasting Studio")
st.caption("Train traditional ML and deep learning models on collected air quality data.")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Training Configuration")
    processed_files = list_processed_files()
    if not processed_files:
        st.warning("No data available. Fetch data in the Data Explorer first.")
        st.stop()

    dataset_name = st.selectbox("Dataset", [f.stem for f in processed_files])
    model_family = st.radio("Model Family", ["Machine Learning", "Deep Learning"])

    if model_family == "Machine Learning":
        available_ml = ["LinearRegression", "Ridge", "RandomForest",
                        "ExtraTrees", "HistGradientBoosting", "XGBoost"]
        selected_models = st.multiselect("Models", available_ml,
                                          default=["RandomForest", "HistGradientBoosting"])
    else:
        available_dl = ["LSTM", "GRU", "TCN", "Transformer"]
        selected_models = st.multiselect("Architectures", available_dl, default=["LSTM"])
        lookback = st.slider("Lookback window (hours)", 6, 72, 24)
        horizon  = st.slider("Forecast horizon (hours)", 1, 48, 24)
        epochs   = st.slider("Max epochs", 10, 200, 50)

    train_btn = st.button("🚀 Train Models", type="primary", use_container_width=True)

# Load data
df = load_processed(dataset_name)
if df is None or df.empty:
    st.error("Could not load selected dataset.")
    st.stop()

df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], utc=True, errors="coerce")
df = df.dropna(subset=["datetime_utc", "value"]).sort_values("datetime_utc")

st.markdown('<div class="section-header">📊 Dataset Overview</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
d_min, d_max = df["datetime_utc"].min(), df["datetime_utc"].max()
c1.metric("Records", f"{len(df):,}", f"{max(1, (d_max - d_min).days)} days span")
c2.metric("Date Span", f"{d_min.strftime('%d %b')} → {d_max.strftime('%d %b %Y')}", "Hourly UTC")
c3.metric("Mean Value", f"{df['value'].mean():.2f} µg/m³")
c4.metric("Stations", df["location_id"].nunique() if "location_id" in df.columns else 1)

# Data suitability check
if len(df) < 50:
    st.error(
        f"⚠️ Only {len(df)} records available. Training requires at least 50 records "
        "for ML and 100+ for deep learning. Fetch more historical data."
    )
    st.stop()

# Training
if "train_results" not in st.session_state:
    st.session_state.train_results = None
if "dl_result" not in st.session_state:
    st.session_state.dl_result = None

if train_btn:
    if model_family == "Machine Learning":
        with st.spinner(f"Training {len(selected_models)} ML model(s)…"):
            try:
                results_df = train_models(df, model_names=selected_models if selected_models else None)
                st.session_state.train_results = results_df
                st.session_state.dl_result = None
                st.success(f"✅ Trained {len(results_df)} model(s) successfully.")
            except ValueError as e:
                st.error(f"Training error: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
    else:
        # DL training
        try:
            from src.dl.trainer import train_dl_model
        except ImportError:
            st.error("PyTorch not installed. Run: pip install torch")
            st.stop()

        series = df.set_index("datetime_utc")["value"].sort_index()
        series = series.resample("h").mean().dropna()
        values = series.values.astype(np.float32)

        if len(values) < 100:
            st.error(
                f"⚠️ Only {len(values)} hourly observations after resampling. "
                "Deep learning needs 100+ observations. Collect more data."
            )
            st.stop()

        all_dl_results = []
        prog = st.progress(0, "Training DL models…")
        for i, arch in enumerate(selected_models):
            with st.spinner(f"Training {arch}…"):
                try:
                    result = train_dl_model(
                        values, model_name=arch,
                        lookback=lookback, horizon=horizon, epochs=epochs,
                    )
                    result["model_name"] = arch
                    all_dl_results.append(result)
                    st.success(f"✅ {arch}: MAE={result['metrics']['MAE']:.3f}, "
                               f"RMSE={result['metrics']['RMSE']:.3f}, "
                               f"R²={result['metrics']['R2']:.3f}")
                except Exception as exc:
                    st.warning(f"⚠️ {arch} failed: {exc}")
            prog.progress((i + 1) / len(selected_models))

        prog.empty()
        st.session_state.dl_result = all_dl_results
        st.session_state.train_results = None

def _load_persisted_ml_results() -> pd.DataFrame | None:
    """Build ML benchmark table from persisted .pkl model artifacts."""
    rows = []
    for path in sorted(settings.ML_MODELS_DIR.glob("*.pkl")):
        d = load_model(path.stem)
        if not d:
            continue
        tm = d.get("test_metrics", {})
        vm = d.get("val_metrics", {})
        if not tm:
            continue
        rows.append({
            "model": path.stem,
            "val_MAE": vm.get("MAE"),
            "val_RMSE": vm.get("RMSE"),
            "val_R2": vm.get("R2"),
            "test_MAE": tm.get("MAE"),
            "test_RMSE": tm.get("RMSE"),
            "test_R2": tm.get("R2"),
            "train_time_s": d.get("train_time_s"),
        })
    return pd.DataFrame(rows) if rows else None


def _render_ml_results(res: pd.DataFrame, df_target: pd.DataFrame, is_persisted: bool = False) -> None:
    """Display ML evaluation table, forecast preview chart, and baseline table."""
    st.markdown('<div class="section-header">📊 ML Results</div>', unsafe_allow_html=True)
    if is_persisted:
        st.info(
            "Displaying forecasts from persisted ML models. Click **Train Models** in the sidebar "
            "to re-train on this dataset or launch Deep Learning.",
            icon="ℹ️",
        )

    display_cols = [c for c in [
        "model", "val_MAE", "val_RMSE", "val_R2",
        "test_MAE", "test_RMSE", "test_R2", "train_time_s"
    ] if c in res.columns]
    st.dataframe(res[display_cols].round(3), use_container_width=True, hide_index=True)

    # Best model forecast preview
    if "test_MAE" in res.columns and res["test_MAE"].notna().any():
        best_model_name = res.loc[res["test_MAE"].idxmin(), "model"]
        st.markdown(f"**Best model by test MAE: `{best_model_name}`**")
        model_dict = load_model(best_model_name)
        if model_dict:
            pred = ml_predict(model_dict, df_target)
            n_test = max(10, int(len(df_target) * 0.15))
            hist_df = df_target.iloc[:-n_test][["datetime_utc", "value"]]
            test_df = df_target.iloc[-n_test:][["datetime_utc", "value"]]
            fc_df = test_df.copy()
            fc_df["forecast"] = pred[-n_test:]
            fig = forecast_chart(
                hist_df, fc_df, test_df,
                title=f"{best_model_name} — Test Period Forecast vs Actual",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Baselines
    with st.expander("📐 Baseline Comparison", expanded=is_persisted):
        series_arr = df_target["value"].values
        n = len(series_arr)
        train_arr = series_arr[:int(n * settings.TRAIN_RATIO)]
        test_arr  = series_arr[int(n * settings.TRAIN_RATIO):]
        baseline_df = evaluate_baselines(train_arr, test_arr)
        st.dataframe(baseline_df, use_container_width=True, hide_index=True)


# Results display
if st.session_state.train_results is not None:
    _render_ml_results(st.session_state.train_results, df, is_persisted=False)

elif st.session_state.dl_result:
    st.markdown('<div class="section-header">🧠 DL Results</div>', unsafe_allow_html=True)
    for res in st.session_state.dl_result:
        with st.expander(f"🔬 {res['model_name']} (Device: {res['device']})", expanded=True):
            m = res["metrics"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("MAE",  f"{m['MAE']:.3f}")
            c2.metric("RMSE", f"{m['RMSE']:.3f}")
            c3.metric("R²",   f"{m['R2']:.3f}")
            c4.metric("Train Time", f"{res['train_time_s']:.1f}s")

            fig_loss = loss_curves(res["history"], title=f"{res['model_name']} Training Loss")
            st.plotly_chart(fig_loss, use_container_width=True)
else:
    persisted_res = _load_persisted_ml_results()
    if persisted_res is not None and not persisted_res.empty:
        _render_ml_results(persisted_res, df, is_persisted=True)
    else:
        st.markdown(
            """
<div style="text-align:center; padding:3rem 0; color:#8B949E;">
  <div style="font-size:3rem">🔮</div>
  <div style="font-size:1.1rem">Configure training in the sidebar and click <strong>Train Models</strong>.</div>
  <div style="font-size:.85rem; margin-top:.5rem;">Training runs with real data only — no fabricated metrics.</div>
</div>""",
            unsafe_allow_html=True,
        )
