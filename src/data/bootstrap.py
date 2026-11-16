from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.config import settings
from src.data.seed_benchmark import seed_all_benchmarks
from src.data.storage import list_processed_files, load_processed
from src.ml.train import train_models
from src.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)

_DEFAULT_BOOTSTRAP_MODELS = [
    "LinearRegression",
    "Ridge",
    "RandomForest",
    "ExtraTrees",
    "HistGradientBoosting",
]


def sync_streamlit_secrets() -> bool:
    """Populate OPENAQ_API_KEY from Streamlit secrets when env var is missing."""
    if settings.api_key_configured():
        return True
    try:
        secret_key = st.secrets.get("OPENAQ_API_KEY", "")
    except Exception:
        secret_key = ""
    clean_key = str(secret_key).strip() if secret_key else ""
    if clean_key and clean_key != "your_openaq_api_key_here":
        os.environ["OPENAQ_API_KEY"] = clean_key
        settings.OPENAQ_API_KEY = clean_key
        logger.info("Synced OPENAQ_API_KEY from Streamlit secrets")
        return True
    return False


def _ensure_datasets() -> bool:
    """Seed reference benchmark datasets if no processed parquet files exist."""
    if list_processed_files():
        return False
    logger.info("No processed datasets found; seeding reference calibration benchmarks.")
    seed_all_benchmarks()
    return True


def _ensure_baseline_models() -> bool:
    """Train lightweight baseline ML models if saved artifacts are missing."""
    settings.ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    if list(settings.ML_MODELS_DIR.glob("*.pkl")):
        return False
    files = list_processed_files()
    if not files:
        return False
    preferred = next((f.stem for f in files if "delhi" in f.stem.lower()), files[0].stem)
    df = load_processed(preferred)
    if df is None or df.empty:
        return False
    results_csv = Path(settings.PROJECT_ROOT) / "experiments" / "results" / "ml_benchmark_results.csv"
    existing_csv = results_csv.read_bytes() if results_csv.exists() else None
    try:
        train_models(
            df,
            target_col="value",
            dt_col="datetime_utc",
            model_names=_DEFAULT_BOOTSTRAP_MODELS,
            save_dir=settings.ML_MODELS_DIR,
        )
        if existing_csv is not None:
            results_csv.write_bytes(existing_csv)
        logger.info("Bootstrapped baseline ML models from %s", preferred)
        return True
    except Exception as exc:
        logger.warning("Baseline model bootstrap skipped: %s", exc)
        return False


@st.cache_resource(show_spinner=False)
def _bootstrap_artifacts_once() -> tuple[bool, bool]:
    """Initialize logging, datasets, and baseline ML models once per server process."""
    setup_logging(level=settings.LOG_LEVEL, log_dir=settings.LOGS_DIR)
    seeded_data = _ensure_datasets()
    seeded_models = _ensure_baseline_models()
    return seeded_data, seeded_models


def ensure_ready() -> dict:
    """Ensure API secrets, benchmark datasets, and baseline models are available."""
    secret_ok = sync_streamlit_secrets()
    seeded_data, seeded_models = _bootstrap_artifacts_once()
    return {
        "api_key_ready": secret_ok,
        "seeded_datasets": seeded_data,
        "seeded_models": seeded_models,
    }
