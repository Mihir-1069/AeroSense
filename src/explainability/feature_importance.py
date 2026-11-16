"""
AeroSense AI — Explainability Module
Feature importance, permutation importance, SHAP explanations.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def get_feature_importance(model_dict: Dict, top_n: int = 20) -> Optional[pd.DataFrame]:
    """
    Extract feature importance from tree-based models.
    Returns a DataFrame with 'feature' and 'importance' columns.
    """
    model = model_dict.get("model")
    features = model_dict.get("features", [])

    # Handle sklearn Pipelines
    if hasattr(model, "steps"):
        for _, step in model.steps:
            if hasattr(step, "feature_importances_"):
                model = step
                break
            if hasattr(step, "coef_"):
                model = step
                break

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_)
    else:
        log.warning("Model does not expose feature importances.")
        return None

    if len(importances) != len(features):
        return None

    df = pd.DataFrame({"feature": features, "importance": importances})
    df = df.sort_values("importance", ascending=False).head(top_n).reset_index(drop=True)
    df["importance_pct"] = df["importance"] / df["importance"].sum() * 100
    return df


def permutation_importance(
    model_dict: Dict,
    X: np.ndarray,
    y: np.ndarray,
    n_repeats: int = 5,
) -> Optional[pd.DataFrame]:
    """Compute permutation importance."""
    try:
        from sklearn.inspection import permutation_importance as _pi
        model = model_dict["model"]
        features = model_dict.get("features", [f"f{i}" for i in range(X.shape[1])])
        result = _pi(model, X, y, n_repeats=n_repeats, random_state=42)
        df = pd.DataFrame({
            "feature": features,
            "importance_mean": result.importances_mean,
            "importance_std":  result.importances_std,
        })
        return df.sort_values("importance_mean", ascending=False).reset_index(drop=True)
    except Exception as exc:
        log.warning("Permutation importance failed: %s", exc)
        return None


def shap_values(
    model_dict: Dict,
    X: np.ndarray,
    max_samples: int = 200,
) -> Optional[tuple]:
    """
    Compute SHAP values for compatible models.
    Returns (shap_values_array, explainer) or None.
    """
    try:
        import shap
        model = model_dict["model"]
        X_sample = X[:max_samples]

        # Pipeline unwrap + preprocessing transform
        if hasattr(model, "steps") and len(model.steps) > 1:
            X_sample = model[:-1].transform(X_sample)
            est = model[-1]
        else:
            est = model

        est_name = type(est).__name__
        is_tree = (
            hasattr(est, "feature_importances_")
            or "Forest" in est_name
            or "Tree" in est_name
            or "Boost" in est_name
            or "XGB" in est_name
        )

        if is_tree:
            try:
                explainer = shap.TreeExplainer(est)
                sv = explainer.shap_values(X_sample)
            except Exception:
                explainer = shap.Explainer(est.predict, X_sample)
                sv = explainer(X_sample).values
        elif hasattr(est, "coef_"):
            explainer = shap.LinearExplainer(est, X_sample)
            sv = explainer.shap_values(X_sample)
        else:
            explainer = shap.Explainer(model.predict, X[:max_samples])
            sv = explainer(X[:max_samples]).values

        return sv, explainer
    except Exception as exc:
        log.warning("SHAP computation failed: %s", exc)
        return None


def residual_analysis(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    datetimes: Optional[List] = None,
) -> pd.DataFrame:
    """Return a DataFrame of residuals for plotting."""
    residuals = y_pred - y_true
    df = pd.DataFrame({
        "actual":    y_true,
        "predicted": y_pred,
        "residual":  residuals,
        "abs_error": np.abs(residuals),
    })
    if datetimes is not None and len(datetimes) == len(df):
        df["datetime"] = datetimes
    return df
