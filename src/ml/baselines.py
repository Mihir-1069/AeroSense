"""
AeroSense AI — ML Baselines
Persistence, historical-mean, and seasonal-naive forecasts.
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

class PersistenceBaseline:
    """Forecasts = last observed value."""
    name = "Persistence"

    def predict(self, series: np.ndarray, horizon: int = 1) -> np.ndarray:
        last = series[-1]
        return np.full(horizon, last, dtype=np.float32)

class HistoricalMeanBaseline:
    """Forecasts = mean of training window."""
    name = "Historical Mean"

    def predict(self, series: np.ndarray, horizon: int = 1) -> np.ndarray:
        mean = float(np.mean(series))
        return np.full(horizon, mean, dtype=np.float32)

class SeasonalNaiveBaseline:
    """Forecasts = value from one season (period) ago."""
    name = "Seasonal Naive"

    def __init__(self, season_period: int = 24) -> None:
        self.period = season_period

    def predict(self, series: np.ndarray, horizon: int = 1) -> np.ndarray:
        preds = []
        for h in range(1, horizon + 1):
            idx = -(self.period - ((h - 1) % self.period))
            try:
                preds.append(float(series[idx]))
            except IndexError:
                preds.append(float(series[-1]))
        return np.array(preds, dtype=np.float32)

def evaluate_baselines(
    train: np.ndarray,
    test: np.ndarray,
    horizon: int = 1,
) -> pd.DataFrame:
    """
    Run all baselines and return a comparison DataFrame.
    For multi-step, evaluate the first step only for simplicity.
    """
    baselines = [
        PersistenceBaseline(),
        HistoricalMeanBaseline(),
        SeasonalNaiveBaseline(24),
    ]
    rows = []
    for model in baselines:
        preds = model.predict(train, horizon=len(test))
        actual = test[:len(preds)]
        mae  = float(np.mean(np.abs(preds - actual)))
        rmse = float(np.sqrt(np.mean((preds - actual) ** 2)))
        ss_res = np.sum((actual - preds) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        rows.append({"model": model.name, "MAE": round(mae, 3),
                     "RMSE": round(rmse, 3), "R2": round(r2, 3)})
    return pd.DataFrame(rows)
