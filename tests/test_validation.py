"""
Unit tests for Data Ingestion, Validation, and Storage
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest

from src.data.validation import validate_measurements
from src.data.cleaning import clean_dataset

def test_validate_measurements_clean():
    df = pd.DataFrame({
        "location_id": [1, 1, 1],
        "parameter": ["pm25", "pm25", "pm25"],
        "value": [25.0, 30.0, 45.0],
        "datetime_utc": ["2026-01-01 01:00:00", "2026-01-01 02:00:00", "2026-01-01 03:00:00"],
    })
    cleaned, report = validate_measurements(df)
    assert len(cleaned) == 3
    assert report.missing_value == 0
    assert report.invalid_range == 0

def test_validate_measurements_out_of_range():
    df = pd.DataFrame({
        "location_id": [1, 1],
        "parameter": ["pm25", "pm25"],
        "value": [25.0, 5000.0],  # 5000 is physically implausible for PM2.5
        "datetime_utc": ["2026-01-01 01:00:00", "2026-01-01 02:00:00"],
    })
    cleaned, report = validate_measurements(df)
    assert len(cleaned) == 1
    assert report.invalid_range == 1

def test_validate_measurements_duplicates():
    df = pd.DataFrame({
        "location_id": [1, 1],
        "parameter": ["pm25", "pm25"],
        "value": [25.0, 26.0],
        "datetime_utc": ["2026-01-01 01:00:00", "2026-01-01 01:00:00"],  # same timestamp
    })
    cleaned, report = validate_measurements(df)
    assert len(cleaned) == 1
    assert report.duplicates == 1

def test_clean_dataset_interpolation():
    # Dataset with a small gap
    dts = pd.date_range("2026-01-01 00:00:00", periods=5, freq="h", tz="UTC")
    df = pd.DataFrame({
        "location_id": 1,
        "parameter": "pm25",
        "value": [10.0, np.nan, 30.0, 40.0, 50.0],
        "datetime_utc": dts,
    })
    cleaned_df = clean_dataset(df)
    assert cleaned_df["value"].isna().sum() == 0
    # Interpolated value should be around 20.0
    assert 19.0 <= cleaned_df["value"].iloc[1] <= 21.0
