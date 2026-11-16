"""
Unit tests for Machine Learning & Deep Learning Models
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest
import torch

from src.ml.train import train_models
from src.ml.baselines import evaluate_baselines
from src.dl.models import LSTMForecaster, GRUForecaster, TCNForecaster, TransformerForecaster


@pytest.fixture
def dummy_train_df():
    """Create a 120-hour dataset suitable for quick ML model training."""
    dts = pd.date_range("2026-01-01 00:00:00", periods=120, freq="h", tz="UTC")
    values = 60.0 + 15.0 * np.sin(np.arange(120) * 2 * np.pi / 24) + np.random.normal(0, 3, 120)
    return pd.DataFrame({
        "datetime_utc": dts,
        "value": values,
        "location_id": 1,
        "parameter": "pm25",
    })


def test_ml_train_fast(dummy_train_df, tmp_path):
    """Test fast ML training with LinearRegression and Ridge."""
    results_df = train_models(dummy_train_df, model_names=["LinearRegression", "Ridge"], save_dir=tmp_path)
    assert not results_df.empty
    assert "test_MAE" in results_df.columns
    assert "test_RMSE" in results_df.columns
    assert "test_R2" in results_df.columns
    # Check that MAE is non-negative
    for mae in results_df["test_MAE"]:
        assert mae >= 0.0


def test_baselines():
    """Test naive baseline forecasts."""
    train = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    test = np.array([55.0, 58.0, 62.0])
    df = evaluate_baselines(train, test)
    assert not df.empty
    assert "MAE" in df.columns
    assert "model" in df.columns


def test_dl_model_shapes():
    """Test that all DL PyTorch models forward pass correctly."""
    batch_size = 4
    lookback = 24
    horizon = 12
    x = torch.randn(batch_size, lookback, 1)

    # 1. LSTM
    lstm = LSTMForecaster(input_size=1, hidden_size=16, output_size=horizon, num_layers=1)
    out_lstm = lstm(x)
    assert out_lstm.shape == (batch_size, horizon)

    # 2. GRU
    gru = GRUForecaster(input_size=1, hidden_size=16, output_size=horizon, num_layers=1)
    out_gru = gru(x)
    assert out_gru.shape == (batch_size, horizon)

    # 3. TCN
    tcn = TCNForecaster(input_size=1, num_channels=16, output_size=horizon, num_levels=2)
    out_tcn = tcn(x)
    assert out_tcn.shape == (batch_size, horizon)

    # 4. Transformer
    trans = TransformerForecaster(input_size=1, d_model=16, nhead=2, output_size=horizon, num_encoder_layers=1)
    out_trans = trans(x)
    assert out_trans.shape == (batch_size, horizon)
