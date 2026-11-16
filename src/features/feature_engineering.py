"""
AeroSense AI — Feature Engineering
Time-series features for ML and DL forecasting without target leakage.
"""
from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

def add_temporal_features(df: pd.DataFrame, dt_col: str = "datetime_utc") -> pd.DataFrame:
    """Add calendar features derived from the datetime column."""
    df = df.copy()
    dt = pd.to_datetime(df[dt_col], utc=True)
    df["hour"]        = dt.dt.hour
    df["day_of_week"] = dt.dt.dayofweek          # 0=Mon, 6=Sun
    df["day_of_month"]= dt.dt.day
    df["month"]       = dt.dt.month
    df["quarter"]     = dt.dt.quarter
    df["is_weekend"]  = (dt.dt.dayofweek >= 5).astype(int)
    # Cyclical encoding for hour and month
    df["hour_sin"]    = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"]    = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"]   = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"]   = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"]     = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"]     = np.cos(2 * np.pi * df["day_of_week"] / 7)
    # Season (meteorological): DJF=0, MAM=1, JJA=2, SON=3
    season_map = {12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1,
                  6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3}
    df["season"] = df["month"].map(season_map)
    return df

def add_lag_features(
    df: pd.DataFrame,
    target_col: str = "value",
    lags: List[int] = [1, 3, 6, 12, 24],
    group_col: Optional[str] = "location_id",
) -> pd.DataFrame:
    """Add lag features. Groups by location if group_col is specified."""
    df = df.copy()
    if group_col and group_col in df.columns:
        for lag in lags:
            df[f"lag_{lag}"] = df.groupby(group_col)[target_col].shift(lag)
    else:
        for lag in lags:
            df[f"lag_{lag}"] = df[target_col].shift(lag)
    return df

def add_rolling_features(
    df: pd.DataFrame,
    target_col: str = "value",
    windows: List[int] = [3, 6, 12, 24],
    group_col: Optional[str] = "location_id",
) -> pd.DataFrame:
    """Add rolling mean, std, min, max features."""
    df = df.copy()
    for w in windows:
        def _roll(s, w=w):
            return s.shift(1).rolling(w, min_periods=max(1, w // 2))

        if group_col and group_col in df.columns:
            grp = df.groupby(group_col)[target_col]
            df[f"roll_mean_{w}"] = grp.transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())
            df[f"roll_std_{w}"]  = grp.transform(lambda s: s.shift(1).rolling(w, min_periods=2).std())
            df[f"roll_min_{w}"]  = grp.transform(lambda s: s.shift(1).rolling(w, min_periods=1).min())
            df[f"roll_max_{w}"]  = grp.transform(lambda s: s.shift(1).rolling(w, min_periods=1).max())
        else:
            rolled = df[target_col].shift(1).rolling(w, min_periods=1)
            df[f"roll_mean_{w}"] = rolled.mean()
            df[f"roll_std_{w}"]  = rolled.std()
            df[f"roll_min_{w}"]  = rolled.min()
            df[f"roll_max_{w}"]  = rolled.max()
    return df

def add_trend_feature(
    df: pd.DataFrame,
    target_col: str = "value",
    window: int = 24,
    group_col: Optional[str] = "location_id",
) -> pd.DataFrame:
    """Add a simple linear trend over the last `window` observations."""
    df = df.copy()
    def _trend(s: pd.Series) -> pd.Series:
        def _slope(x):
            if len(x) < 2:
                return 0.0
            xs = np.arange(len(x))
            return float(np.polyfit(xs, x, 1)[0])
        return s.shift(1).rolling(window, min_periods=2).apply(_slope, raw=True)

    if group_col and group_col in df.columns:
        df[f"trend_{window}"] = df.groupby(group_col)[target_col].transform(_trend)
    else:
        df[f"trend_{window}"] = _trend(df[target_col])
    return df

def build_feature_matrix(
    df: pd.DataFrame,
    target_col: str = "value",
    dt_col: str = "datetime_utc",
    lags: List[int] = [1, 3, 6, 12, 24],
    rolling_windows: List[int] = [3, 6, 12, 24],
    trend_window: int = 24,
    group_col: Optional[str] = "location_id",
    drop_na: bool = True,
) -> pd.DataFrame:
    """Full feature pipeline: temporal + lags + rolling + trend."""
    df = df.sort_values([group_col, dt_col] if group_col and group_col in df.columns else [dt_col])
    df = add_temporal_features(df, dt_col)
    df = add_lag_features(df, target_col, lags, group_col)
    df = add_rolling_features(df, target_col, rolling_windows, group_col)
    df = add_trend_feature(df, target_col, trend_window, group_col)
    if drop_na:
        before = len(df)
        df = df.dropna()
        log.info("Feature matrix: %d → %d rows after dropping NaN.", before, len(df))
    log.info("Feature matrix ready: %d rows × %d cols.", len(df), len(df.columns))
    return df.reset_index(drop=True)

FEATURE_COLUMNS = [
    "hour", "day_of_week", "day_of_month", "month", "quarter",
    "is_weekend", "hour_sin", "hour_cos", "month_sin", "month_cos",
    "dow_sin", "dow_cos", "season",
    "lag_1", "lag_3", "lag_6", "lag_12", "lag_24",
    "roll_mean_3", "roll_std_3", "roll_min_3", "roll_max_3",
    "roll_mean_6", "roll_std_6", "roll_min_6", "roll_max_6",
    "roll_mean_12", "roll_std_12", "roll_min_12", "roll_max_12",
    "roll_mean_24", "roll_std_24", "roll_min_24", "roll_max_24",
    "trend_24",
]
