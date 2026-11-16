"""
Unit tests for Feature Engineering & Sequence Building
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest

from src.features.feature_engineering import build_feature_matrix, FEATURE_COLUMNS
from src.features.sequence_builder import build_sequences


@pytest.fixture
def sample_timeseries():
    """Create a synthetic 100-hour continuous series."""
    dts = pd.date_range("2026-01-01 00:00:00", periods=100, freq="h", tz="UTC")
    values = 50.0 + 10.0 * np.sin(np.arange(100) * 2 * np.pi / 24)
    return pd.DataFrame({
        "datetime_utc": dts,
        "value": values,
        "location_id": 1,
        "parameter": "pm25",
    })


def test_build_feature_matrix_shapes(sample_timeseries):
    feat_df = build_feature_matrix(sample_timeseries)
    assert not feat_df.empty
    assert "value" in feat_df.columns
    # Check that lag columns are created
    assert "lag_1" in feat_df.columns
    assert "lag_3" in feat_df.columns
    assert "lag_24" in feat_df.columns
    # Check cyclical time features
    assert "hour_sin" in feat_df.columns
    assert "hour_cos" in feat_df.columns
    # Check rolling features
    assert "roll_mean_6" in feat_df.columns
    assert "roll_mean_24" in feat_df.columns


def test_build_sequences_dl():
    values = np.arange(100, dtype=np.float32)
    lookback = 24
    horizon = 12
    X, y = build_sequences(values, lookback=lookback, horizon=horizon)

    expected_samples = len(values) - lookback - horizon + 1
    assert len(X) == expected_samples
    assert len(y) == expected_samples
    assert X.shape[1] == lookback
    assert y.shape[1] == horizon
    # Verify sequence alignment
    np.testing.assert_array_equal(X[0, :, 0], values[:lookback])
    np.testing.assert_array_equal(y[0], values[lookback:lookback + horizon])
