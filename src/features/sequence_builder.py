"""
AeroSense AI — Sequence Builder for Deep Learning
Builds sliding-window (X, y) sequences for LSTM/GRU/TCN/Transformer.
"""
from __future__ import annotations

import logging
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

log = logging.getLogger(__name__)


def build_sequences(
    series: pd.Series,
    lookback: int = 24,
    horizon: int = 1,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build overlapping (X, y) sequences from a univariate time series.

    Args:
        series:   Clean, sorted, regularly-spaced series of values.
        lookback: Number of past steps used as input.
        horizon:  Number of future steps to predict.

    Returns:
        X: (n_samples, lookback, 1)
        y: (n_samples, horizon)
    """
    if hasattr(series, "values"):
        values = series.values.astype(np.float32)
    else:
        values = np.asarray(series, dtype=np.float32)
    X, y = [], []
    for i in range(len(values) - lookback - horizon + 1):
        X.append(values[i : i + lookback])
        y.append(values[i + lookback : i + lookback + horizon])
    X_arr = np.array(X, dtype=np.float32).reshape(-1, lookback, 1)
    y_arr = np.array(y, dtype=np.float32)
    log.debug("Sequences: X=%s, y=%s", X_arr.shape, y_arr.shape)
    return X_arr, y_arr


def chronological_split(
    X: np.ndarray,
    y: np.ndarray,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
) -> Tuple[Tuple, Tuple, Tuple]:
    """Strictly chronological train / val / test split."""
    n = len(X)
    n_train = int(n * train_ratio)
    n_val   = int(n * val_ratio)
    X_train, y_train = X[:n_train], y[:n_train]
    X_val,   y_val   = X[n_train : n_train + n_val], y[n_train : n_train + n_val]
    X_test,  y_test  = X[n_train + n_val :], y[n_train + n_val :]
    log.info(
        "Split: train=%d, val=%d, test=%d", len(X_train), len(X_val), len(X_test)
    )
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


def fit_scaler(values: np.ndarray) -> Tuple[np.ndarray, MinMaxScaler]:
    """Fit MinMaxScaler on training values and return scaled + scaler."""
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values.reshape(-1, 1)).flatten()
    return scaled, scaler
