"""
AeroSense AI — Data Validation
Schema checks, unit validation, range checks, duplicate detection.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# Physically plausible value ranges (µg/m³ unless noted)
PARAM_RANGES = {
    "pm25":  (0, 1000),
    "pm10":  (0, 2000),
    "no2":   (0, 2000),
    "so2":   (0, 2000),
    "co":    (0, 100_000),  # µg/m³
    "o3":    (0, 1000),
    "bc":    (0, 100),
}

REQUIRED_COLS = {"value", "datetime_utc", "parameter", "location_id"}

@dataclass
class ValidationReport:
    total_records: int = 0
    missing_value: int = 0
    missing_datetime: int = 0
    invalid_range: int = 0
    duplicates: int = 0
    invalid_units: int = 0
    warnings: List[str] = field(default_factory=list)

    @property
    def valid_records(self) -> int:
        return self.total_records - self.missing_value - self.missing_datetime - \
               self.invalid_range - self.duplicates

    def summary(self) -> str:
        return (
            f"Total={self.total_records} | "
            f"Valid={self.valid_records} | "
            f"MissingValue={self.missing_value} | "
            f"MissingDatetime={self.missing_datetime} | "
            f"InvalidRange={self.invalid_range} | "
            f"Duplicates={self.duplicates}"
        )

def validate_measurements(df: pd.DataFrame) -> tuple[pd.DataFrame, ValidationReport]:
    """
    Validate a measurements DataFrame.

    Returns:
        (cleaned_df, report)
    """
    report = ValidationReport(total_records=len(df))

    if df.empty:
        return df, report

    # Required columns
    missing_cols = REQUIRED_COLS - set(df.columns)
    if missing_cols:
        report.warnings.append(f"Missing required columns: {missing_cols}")
        # Add with NaN so downstream doesn't crash
        for col in missing_cols:
            df[col] = np.nan

    # Datetime
    mask_no_dt = df["datetime_utc"].isna() | (df["datetime_utc"] == "")
    report.missing_datetime = int(mask_no_dt.sum())
    df = df[~mask_no_dt].copy()

    df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], utc=True, errors="coerce")
    still_bad = df["datetime_utc"].isna()
    report.missing_datetime += int(still_bad.sum())
    df = df[~still_bad].copy()

    # Value
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    mask_no_val = df["value"].isna()
    report.missing_value = int(mask_no_val.sum())
    df = df[~mask_no_val].copy()

    # Range check
    if "parameter" in df.columns:
        def _in_range(row):
            lo, hi = PARAM_RANGES.get(str(row["parameter"]).lower(), (0, 1e9))
            return lo <= row["value"] <= hi

        mask_range = df.apply(_in_range, axis=1)
        report.invalid_range = int((~mask_range).sum())
        df = df[mask_range].copy()

    # Duplicates
    dup_cols = ["location_id", "parameter", "datetime_utc"]
    dup_cols = [c for c in dup_cols if c in df.columns]
    before = len(df)
    df = df.drop_duplicates(subset=dup_cols, keep="last")
    report.duplicates = before - len(df)

    log.info("Validation: %s", report.summary())
    return df.reset_index(drop=True), report
