"""
AeroSense AI — Page: Explainable AI
Feature importance, permutation importance, SHAP explanations, and residual analysis.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from src.config import settings
from src.data.storage import load_processed, list_processed_files
from src.ml.train import load_model
from src.features.feature_engineering import build_feature_matrix, FEATURE_COLUMNS
from src.explainability.feature_importance import (
    get_feature_importance, permutation_importance, shap_values, residual_analysis
)
from src.visualization.charts import feature_importance_bar, residual_plot, PLOTLY_TEMPLATE

from src.visualization.theme import apply_theme

st.set_page_config(page_title="Explainable AI — AeroSense AI", page_icon="🧠", layout="wide")
apply_theme()

st.title("🧠 Explainable AI")
st.caption("Feature importance, SHAP explanations, and residual analysis for trained models.")

ml_dir = settings.ML_MODELS_DIR
ml_models = sorted([f.stem for f in ml_dir.glob("*.pkl")])
processed_files = list_processed_files()

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    if not ml_models:
        st.warning("No ML models found. Train models in Forecasting Studio first.")
    else:
        model_name = st.selectbox("Select Model", ml_models)

    if processed_files:
        dataset_name = st.selectbox("Dataset", [f.stem for f in processed_files])
    else:
        st.warning("No datasets found.")

if not ml_models or not processed_files:
    st.markdown("""
<div style="text-align:center; padding:4rem 0; color:#8B949E;">
  <div style="font-size:3rem">🧠</div>
  <div>Train ML models and fetch data first.</div>
</div>""", unsafe_allow_html=True)
    st.stop()

@st.cache_data(show_spinner=False)
def _load_df(dataset: str):
    return load_processed(dataset)

df = _load_df(dataset_name)
model_dict = load_model(model_name)

if df is None or model_dict is None:
    st.error("Could not load data or model.")
    st.stop()

df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], utc=True, errors="coerce")
df = df.dropna(subset=["datetime_utc", "value"]).sort_values("datetime_utc")

# Build feature matrix aligned with model features
feat_df = build_feature_matrix(df)
model_features = model_dict.get("features") or FEATURE_COLUMNS
avail_features = [c for c in model_features if c in feat_df.columns]
if not avail_features:
    st.error("No matching feature columns available. Check dataset and model compatibility.")
    st.stop()

X = feat_df[avail_features].values
y = feat_df["value"].values

# Test split
n_test = max(10, int(len(X) * 0.15))
X_test, y_test = X[-n_test:], y[-n_test:]
y_pred = model_dict["model"].predict(X_test)
model_dict_full = {"model": model_dict["model"], "features": avail_features}

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Feature Importance", "🔬 SHAP Analysis", "📐 Residuals"])

with tab1:
    st.markdown('<div class="section-header">Feature Importance</div>', unsafe_allow_html=True)
    imp_df = get_feature_importance(model_dict_full, top_n=20)
    if imp_df is not None:
        fig = feature_importance_bar(imp_df, title=f"Native Feature Importance — {model_name}")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(imp_df.round(4), use_container_width=True, hide_index=True)
    else:
        st.info(f"`{model_name}` does not expose native importances; computing Permutation Importance on the test split…")
        perm_df = permutation_importance(model_dict_full, X_test, y_test, n_repeats=5)
        if perm_df is not None:
            perm_plot_df = perm_df.rename(columns={"importance_mean": "importance"}).head(20)
            fig = feature_importance_bar(perm_plot_df, title=f"Permutation Importance — {model_name}")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(perm_df.round(4), use_container_width=True, hide_index=True)
        else:
            st.warning("Could not compute feature or permutation importance.")

with tab2:
    st.markdown('<div class="section-header">SHAP Explanations</div>', unsafe_allow_html=True)
    st.info("SHAP computation may take a few seconds depending on model complexity.", icon="ℹ️")
    if st.button("Compute SHAP Values"):
        with st.spinner("Computing SHAP…"):
            result = shap_values(model_dict_full, X_test, max_samples=min(100, len(X_test)))
        if result is not None:
            sv, _ = result
            if sv.ndim == 3:
                sv = sv[:, :, 0]
            shap_df = pd.DataFrame(
                np.abs(sv).mean(axis=0).reshape(1, -1),
                columns=avail_features[:sv.shape[1]],
            ).T.reset_index()
            shap_df.columns = ["feature", "mean_abs_shap"]
            shap_df = shap_df.sort_values("mean_abs_shap", ascending=False).head(15)

            fig_shap = px.bar(
                shap_df, x="mean_abs_shap", y="feature", orientation="h",
                title=f"Mean |SHAP| per Feature — {model_name}",
                template=PLOTLY_TEMPLATE,
                color="mean_abs_shap", color_continuous_scale="Viridis",
            )
            fig_shap.update_layout(
                paper_bgcolor="#0D1117", plot_bgcolor="#161B22",
                font=dict(color="#E6EDF3"), height=400,
            )
            fig_shap.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_shap, use_container_width=True)
            st.caption("⚠️ SHAP explanations describe feature influence on model predictions, not causal mechanisms.")
        else:
            st.warning("SHAP computation not supported for this model configuration.")

with tab3:
    st.markdown('<div class="section-header">Residual Analysis</div>', unsafe_allow_html=True)
    res_df = residual_analysis(y_test, y_pred)

    c1, c2, c3 = st.columns(3)
    c1.metric("MAE", f"{res_df['abs_error'].mean():.3f} µg/m³")
    c2.metric("Max Error", f"{res_df['abs_error'].max():.3f} µg/m³")
    c3.metric("Mean Residual", f"{res_df['residual'].mean():.3f} µg/m³")

    fig_res = residual_plot(res_df, title=f"Residuals — {model_name}")
    st.plotly_chart(fig_res, use_container_width=True)

    fig_hist = px.histogram(
        res_df, x="residual", nbins=30,
        title="Residual Distribution", template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#00D4FF"],
    )
    fig_hist.update_layout(
        paper_bgcolor="#0D1117", plot_bgcolor="#161B22",
        font=dict(color="#E6EDF3"), height=300,
    )
    st.plotly_chart(fig_hist, use_container_width=True)
