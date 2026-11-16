"""
AeroSense AI — Data Cleaning
Missing-value treatment, outlier handling, normalisation.
"""
from __future__ import annotations

import logging
from typing import Literal

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

ImputeStrategy = Literal["forward_fill", "interpolate", "station_median", "none"]

def clean_measurements(
    df: pd.DataFrame,
    impute: ImputeStrategy = "interpolate",
    max_gap_hours: int = 6,
) -> pd.DataFrame:
    """
    Clean a validated measurements DataFrame.

    Steps:
      1. Sort by location and datetime.
      2. Remove extreme outliers (IQR fence × 3).
      3. Optionally impute short gaps.
      4. Add is_imputed flag.
    """
    if df.empty:
        return df

    df = df.copy()
    if "datetime_utc" in df.columns:
        df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], utc=True, errors="coerce")
        df = df.dropna(subset=["datetime_utc"])

    df = df.sort_values(["location_id", "parameter", "datetime_utc"]).reset_index(drop=True)
    df["is_imputed"] = False

    # Outlier removal (IQR × 3 per location-parameter)
    if "location_id" in df.columns and "parameter" in df.columns and len(df) >= 4:
        try:
            q1 = df.groupby(["location_id", "parameter"])["value"].transform(lambda s: s.quantile(0.25))
            q3 = df.groupby(["location_id", "parameter"])["value"].transform(lambda s: s.quantile(0.75))
            iqr = q3 - q1
            lo = q1 - 3 * iqr
            hi = q3 + 3 * iqr
            valid_mask = df["value"].isna() | ((df["value"] >= lo) & (df["value"] <= hi))
            df = df[valid_mask].copy().reset_index(drop=True)
        except Exception as e:
            log.warning("Outlier filter skipped: %s", e)

    if impute == "none" or df.empty:
        return df

    # Imputation per location-parameter
    groups = []
    group_cols = [c for c in ["location_id", "parameter"] if c in df.columns]

    if not group_cols:
        return df

    for keys, grp in df.groupby(group_cols):
        loc = keys[0] if isinstance(keys, tuple) else keys
        param = keys[1] if isinstance(keys, tuple) and len(keys) > 1 else grp["parameter"].iloc[0]

        grp = grp.set_index("datetime_utc").sort_index()

        # Resample to hourly to expose missing timestamps
        grp_resampled = grp.resample("h").first()
        grp_resampled["location_id"] = loc
        grp_resampled["parameter"] = param

        # Preserve static station/provenance metadata across resampled rows
        meta_cols = [
            c for c in [
                "location_name", "city", "country", "latitude", "longitude",
                "sensor_id", "unit", "source_provider", "api_endpoint", "retrieved_at",
                "data_source", "is_benchmark",
            ]
            if c in grp_resampled.columns
        ]
        if meta_cols:
            grp_resampled[meta_cols] = grp_resampled[meta_cols].ffill().bfill()

        was_missing = grp_resampled["value"].isna()

        if impute == "interpolate":
            grp_resampled["value"] = grp_resampled["value"].interpolate(
                method="time", limit=max_gap_hours, limit_direction="both"
            )
        elif impute == "forward_fill":
            grp_resampled["value"] = grp_resampled["value"].ffill(limit=max_gap_hours)
        elif impute == "station_median":
            med = grp["value"].median()
            grp_resampled["value"] = grp_resampled["value"].fillna(med)

        now_present = grp_resampled["value"].notna()
        grp_resampled["is_imputed"] = was_missing & now_present

        grp = grp_resampled.reset_index()
        groups.append(grp)

    if not groups:
        return df

    df = pd.concat(groups, ignore_index=True)
    imputed_count = int(df["is_imputed"].sum())
    log.info("Cleaning complete: %d values imputed (strategy=%s).", imputed_count, impute)
    return df

def normalise_units(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure all PM values are in µg/m³.
    Convert ppb NO2/SO2/O3 to µg/m³ using standard conversion factors.
    """
    if df.empty or "unit" not in df.columns:
        return df

    df = df.copy()
    PPB_FACTORS = {
        "no2": 1.88,
        "so2": 2.62,
        "o3":  2.00,
        "co":  1.15,
    }
    ppb_mask = df["unit"].str.lower().isin(["ppb", "ppm"])
    if ppb_mask.any():
        for param, factor in PPB_FACTORS.items():
            m = ppb_mask & (df["parameter"].str.lower() == param)
            if m.any():
                df.loc[m, "value"] *= factor
                df.loc[m, "unit"] = "µg/m³"
    return df

# Alias for backward compatibility
clean_dataset = clean_measurements
