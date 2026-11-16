"""
AeroSense AI — ML Training Pipeline
Trains traditional ML models with strict chronological splitting.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    ExtraTreesRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import settings
from src.features.feature_engineering import FEATURE_COLUMNS, build_feature_matrix

log = logging.getLogger(__name__)

try:
    from xgboost import XGBRegressor
    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False
    log.warning("XGBoost not available. Skipping XGBRegressor.")


def _get_models() -> Dict[str, Any]:
    models: Dict[str, Any] = {
        "LinearRegression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LinearRegression()),
        ]),
        "Ridge": Pipeline([
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=1.0)),
        ]),
        "RandomForest": RandomForestRegressor(
            n_estimators=100, random_state=settings.ML_RANDOM_STATE, n_jobs=-1
        ),
        "ExtraTrees": ExtraTreesRegressor(
            n_estimators=100, random_state=settings.ML_RANDOM_STATE, n_jobs=-1
        ),
        "HistGradientBoosting": HistGradientBoostingRegressor(
            random_state=settings.ML_RANDOM_STATE, max_iter=200, early_stopping=True
        ),
    }
    if _HAS_XGB:
        models["XGBoost"] = XGBRegressor(
            n_estimators=200, learning_rate=0.05, max_depth=6,
            random_state=settings.ML_RANDOM_STATE, n_jobs=-1,
            verbosity=0, eval_metric="rmse",
        )
    return models


def chronological_split_df(
    df: pd.DataFrame,
    train_ratio: float = settings.TRAIN_RATIO,
    val_ratio: float = settings.VAL_RATIO,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Strictly time-ordered train/val/test split."""
    n = len(df)
    n_train = int(n * train_ratio)
    n_val   = int(n * val_ratio)
    train = df.iloc[:n_train]
    val   = df.iloc[n_train : n_train + n_val]
    test  = df.iloc[n_train + n_val :]
    log.info("Split: train=%d, val=%d, test=%d", len(train), len(val), len(test))
    return train, val, test


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    mae  = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    # MAPE (avoid division by zero)
    nonzero = y_true != 0
    mape = float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100) \
           if nonzero.any() else float("nan")
    return {"MAE": round(mae, 3), "RMSE": round(rmse, 3),
            "R2": round(r2, 3), "MAPE": round(mape, 2)}


def train_models(
    df: pd.DataFrame,
    target_col: str = "value",
    dt_col: str = "datetime_utc",
    model_names: Optional[List[str]] = None,
    save_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Build feature matrix, split chronologically, train all models,
    evaluate on val and test, save artifacts, return results DataFrame.
    """
    save_dir = save_dir or settings.ML_MODELS_DIR

    # Feature engineering
    feat_df = build_feature_matrix(df, target_col=target_col, dt_col=dt_col)

    avail_features = [c for c in FEATURE_COLUMNS if c in feat_df.columns]
    if not avail_features or len(feat_df) < 50:
        raise ValueError(
            f"Insufficient data for ML training: {len(feat_df)} rows, "
            f"{len(avail_features)} features."
        )

    X = feat_df[avail_features].values
    y = feat_df[target_col].values

    n = len(X)
    n_train = int(n * settings.TRAIN_RATIO)
    n_val   = int(n * settings.VAL_RATIO)

    X_train, y_train = X[:n_train], y[:n_train]
    X_val,   y_val   = X[n_train : n_train + n_val], y[n_train : n_train + n_val]
    X_test,  y_test  = X[n_train + n_val :], y[n_train + n_val :]

    all_models = _get_models()
    if model_names:
        all_models = {k: v for k, v in all_models.items() if k in model_names}

    results = []
    for name, model in all_models.items():
        log.info("Training %s…", name)
        t0 = time.time()
        try:
            model.fit(X_train, y_train)
            train_time = round(time.time() - t0, 2)

            t1 = time.time()
            val_pred  = model.predict(X_val)
            test_pred = model.predict(X_test)
            pred_time = round(time.time() - t1, 2)

            val_metrics  = compute_metrics(y_val,  val_pred)
            test_metrics = compute_metrics(y_test, test_pred)

            # Save artifact with embedded evaluation metadata
            path = save_dir / f"{name}.pkl"
            joblib.dump(
                {
                    "model": model,
                    "features": avail_features,
                    "val_metrics": val_metrics,
                    "test_metrics": test_metrics,
                    "train_time_s": train_time,
                    "pred_time_s": pred_time,
                    "n_features": len(avail_features),
                    "train_rows": len(X_train),
                },
                path,
            )
            log.info("%s → val_MAE=%.3f | test_MAE=%.3f", name, val_metrics["MAE"], test_metrics["MAE"])

            results.append({
                "model": name,
                "val_MAE":  val_metrics["MAE"],
                "val_RMSE": val_metrics["RMSE"],
                "val_R2":   val_metrics["R2"],
                "test_MAE":  test_metrics["MAE"],
                "test_RMSE": test_metrics["RMSE"],
                "test_R2":   test_metrics["R2"],
                "train_time_s": train_time,
                "pred_time_s":  pred_time,
                "n_features": len(avail_features),
                "train_rows": len(X_train),
                "artifact": str(path),
            })

        except Exception as exc:
            log.error("Failed to train %s: %s", name, exc)
            results.append({"model": name, "error": str(exc)})

    res_df = pd.DataFrame(results)
    if save_dir == settings.ML_MODELS_DIR:
        try:
            bench_dir = settings.PROJECT_ROOT / "experiments" / "results"
            bench_dir.mkdir(parents=True, exist_ok=True)
            res_df.to_csv(bench_dir / "ml_benchmark_results.csv", index=False)
        except Exception as exc:
            log.warning("Could not save benchmark CSV: %s", exc)
    return res_df


def load_model(name: str, model_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    d = model_dir or settings.ML_MODELS_DIR
    path = d / f"{name}.pkl"
    if not path.exists():
        return None
    return joblib.load(path)


def predict(
    model_dict: Dict[str, Any],
    df: pd.DataFrame,
    target_col: str = "value",
    dt_col: str = "datetime_utc",
) -> np.ndarray:
    model  = model_dict["model"]
    feats  = model_dict["features"]
    feat_df = build_feature_matrix(df, target_col=target_col, dt_col=dt_col, drop_na=False)
    X = feat_df[feats].fillna(0).values
    return model.predict(X)
