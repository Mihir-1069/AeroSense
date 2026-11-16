"""
Unit tests for OpenAQ API v3 Client (mocked HTTP) and Explainability Pipeline
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd
import pytest

from src.api.openaq_client import OpenAQClient, OpenAQAuthError
from src.explainability.feature_importance import (
    get_feature_importance,
    permutation_importance,
    shap_values,
)
from src.ml.train import train_models, load_model
from src.features.feature_engineering import build_feature_matrix, FEATURE_COLUMNS
from src.reporting.report_generator import generate_pdf_report


def test_openaq_v3_locations_and_pagination():
    """Verify v3 iso query parameter and safe parsing of string meta.found='>1000'."""
    client = OpenAQClient(api_key="dummy-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "meta": {"limit": 100, "found": ">1000"},
        "results": [{"id": 8118, "name": "Anand Vihar"}],
    }

    with patch("httpx.Client") as mock_http:
        mock_http.return_value.__enter__.return_value.request.return_value = mock_resp
        locs = client.get_locations(country="in", parameter="pm25", limit=100)
        assert len(locs) == 1
        assert locs[0]["id"] == 8118
        call_kwargs = mock_http.return_value.__enter__.return_value.request.call_args.kwargs
        assert call_kwargs["params"]["iso"] == "IN"
        assert call_kwargs["params"]["parameters_id"] == 2


def test_openaq_v3_sensor_hours():
    """Verify v3 /sensors/{id}/hours uses datetime_from and datetime_to."""
    client = OpenAQClient(api_key="dummy-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "meta": {"limit": 1000, "found": 1},
        "results": [{"value": 85.4, "datetimeTo": {"utc": "2026-01-01T01:00:00Z"}}],
    }

    with patch("httpx.Client") as mock_http:
        mock_http.return_value.__enter__.return_value.request.return_value = mock_resp
        res = client.get_measurements(
            location_id=8118,
            parameter="pm25",
            date_from="2026-01-01T00:00:00Z",
            date_to="2026-01-02T00:00:00Z",
            sensor_id=999,
        )
        assert len(res) == 1
        call_args = mock_http.return_value.__enter__.return_value.request.call_args
        assert "/sensors/999/hours" in call_args.args[1]
        assert call_args.kwargs["params"]["datetime_from"] == "2026-01-01T00:00:00Z"


def test_openaq_auth_error():
    client = OpenAQClient(api_key="bad-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"

    with patch("httpx.Client") as mock_http:
        mock_http.return_value.__enter__.return_value.request.return_value = mock_resp
        with pytest.raises(OpenAQAuthError):
            client.get_countries()


def test_explainability_across_model_families(tmp_path):
    """Test feature importance, permutation importance, and SHAP on Ridge, RandomForest, and HistGradientBoosting."""
    dts = pd.date_range("2026-01-01", periods=150, freq="h", tz="UTC")
    vals = 80 + 20 * np.sin(np.arange(150) * 2 * np.pi / 24) + np.random.normal(0, 2, 150)
    df = pd.DataFrame({"datetime_utc": dts, "value": vals, "location_id": 1, "parameter": "pm25"})

    res = train_models(
        df,
        model_names=["Ridge", "RandomForest", "HistGradientBoosting"],
        save_dir=tmp_path,
    )
    assert len(res) == 3

    feat_df = build_feature_matrix(df)
    feats = [c for c in FEATURE_COLUMNS if c in feat_df.columns]
    X = feat_df[feats].values
    y = feat_df["value"].values

    for name in ["Ridge", "RandomForest", "HistGradientBoosting"]:
        md = load_model(name, model_dir=tmp_path)
        assert md is not None
        assert "test_metrics" in md

        # Native importance works for Ridge & RandomForest; Permutation works for all
        if name in ["Ridge", "RandomForest"]:
            imp = get_feature_importance(md)
            assert imp is not None and not imp.empty
        perm = permutation_importance(md, X[-30:], y[-30:], n_repeats=2)
        assert perm is not None and not perm.empty

        sv_res = shap_values(md, X[-30:], max_samples=15)
        assert sv_res is not None
        sv, _ = sv_res
        assert sv.shape[0] == 15


def test_pdf_report_generation(tmp_path):
    dts = pd.date_range("2026-01-01", periods=48, freq="h", tz="UTC")
    df = pd.DataFrame({"datetime_utc": dts, "value": np.linspace(30, 140, 48), "parameter": "pm25"})
    metrics_df = pd.DataFrame([{"model": "Ridge", "test_MAE": 9.45, "test_RMSE": 11.95, "test_R2": 0.906, "train_time_s": 0.01}])
    pdf_file = tmp_path / "test_report.pdf"
    out = generate_pdf_report("test_ds", df, output_path=pdf_file, metrics_df=metrics_df)
    assert out.exists()
    assert out.stat().st_size > 500
