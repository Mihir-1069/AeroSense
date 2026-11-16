from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import settings
from src.data import bootstrap, seed_benchmark, storage


def test_sync_streamlit_secrets_picks_up_secret(monkeypatch):
    monkeypatch.setattr(settings, "OPENAQ_API_KEY", None)
    monkeypatch.delenv("OPENAQ_API_KEY", raising=False)
    monkeypatch.setattr(bootstrap, "st", type("MockSt", (), {"secrets": {"OPENAQ_API_KEY": "valid_test_secret_1234"}})())

    assert bootstrap.sync_streamlit_secrets() is True
    assert settings.OPENAQ_API_KEY == "valid_test_secret_1234"
    assert os.environ["OPENAQ_API_KEY"] == "valid_test_secret_1234"


def test_sync_streamlit_secrets_rejects_placeholder(monkeypatch):
    monkeypatch.setattr(settings, "OPENAQ_API_KEY", None)
    monkeypatch.delenv("OPENAQ_API_KEY", raising=False)
    monkeypatch.setattr(bootstrap, "st", type("MockSt", (), {"secrets": {"OPENAQ_API_KEY": "your_openaq_api_key_here"}})())

    assert bootstrap.sync_streamlit_secrets() is False


def test_bootstrap_seeds_empty_workspace(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    proc_dir = tmp_path / "processed"
    ml_dir = tmp_path / "ml_models"
    proj_dir = tmp_path / "proj"
    for d in (raw_dir, proc_dir, ml_dir, proj_dir):
        d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(settings, "RAW_DIR", raw_dir)
    monkeypatch.setattr(settings, "PROCESSED_DIR", proc_dir)
    monkeypatch.setattr(settings, "ML_MODELS_DIR", ml_dir)
    monkeypatch.setattr(settings, "PROJECT_ROOT", proj_dir)
    monkeypatch.setattr(seed_benchmark, "settings", settings)
    monkeypatch.setattr(storage, "settings", settings)
    monkeypatch.setattr(bootstrap, "_DEFAULT_BOOTSTRAP_MODELS", ["LinearRegression", "Ridge"])

    assert bootstrap._ensure_datasets() is True
    assert len(list(proc_dir.glob("*.parquet"))) >= 2
    assert bootstrap._ensure_datasets() is False

    assert bootstrap._ensure_baseline_models() is True
    assert len(list(ml_dir.glob("*.pkl"))) == 2
    assert bootstrap._ensure_baseline_models() is False
