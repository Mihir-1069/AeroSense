"""
AeroSense AI — Application Settings
Centralised configuration loaded from environment variables and .env file.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Resolve project root and load .env
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)

# API
OPENAQ_API_KEY: Optional[str] = os.getenv("OPENAQ_API_KEY")
OPENAQ_BASE_URL: str = "https://api.openaq.org/v3"
OPENAQ_TIMEOUT_SECONDS: int = 30
OPENAQ_MAX_RETRIES: int = 3
OPENAQ_RETRY_BACKOFF: float = 1.5          # seconds for first retry
OPENAQ_DEFAULT_LIMIT: int = 1000           # records per page
OPENAQ_MAX_PAGES: int = 20                 # hard cap on pagination

# Optional providers
CDSAPI_KEY: Optional[str] = os.getenv("CDSAPI_KEY")
CDSAPI_URL: str = os.getenv("CDSAPI_URL", "https://cds.climate.copernicus.eu/api/v2")

# Storage
DATA_DIR:    Path = PROJECT_ROOT / os.getenv("DATA_DIR",    "data")
MODELS_DIR:  Path = PROJECT_ROOT / os.getenv("MODELS_DIR",  "models")
LOGS_DIR:    Path = PROJECT_ROOT / os.getenv("LOGS_DIR",    "logs")
REPORTS_DIR: Path = PROJECT_ROOT / os.getenv("REPORTS_DIR", "reports")

RAW_DIR       = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR  = DATA_DIR / "features"
EXPORTS_DIR   = DATA_DIR / "exports"
METADATA_DIR  = DATA_DIR / "metadata"

ML_MODELS_DIR = MODELS_DIR / "ml"
DL_MODELS_DIR = MODELS_DIR / "dl"

# Ensure directories exist at import time
for _d in [RAW_DIR, PROCESSED_DIR, FEATURES_DIR, EXPORTS_DIR, METADATA_DIR,
           ML_MODELS_DIR, DL_MODELS_DIR, LOGS_DIR, REPORTS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# Application
APP_ENV: str    = os.getenv("APP_ENV", "development")
LOG_LEVEL: str  = os.getenv("LOG_LEVEL", "INFO")
CACHE_TTL: int  = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

APP_NAME     = "AeroSense AI"
APP_TITLE    = "AeroSense: Intelligent Global Air Quality Monitoring, Analysis and Forecasting Using Machine Learning and Deep Learning"
APP_SUBTITLE = "Intelligent Global Air Quality Monitoring, Analysis & Forecasting"
APP_TAGLINE  = "Understand Pollution. Predict Tomorrow. Build a Cleaner Future."
APP_VERSION  = "1.0.0"

# Defaults for the UI
DEFAULT_COUNTRY     = "IN"          # India
DEFAULT_COUNTRY_NAME = "India"
DEFAULT_POLLUTANT   = "pm25"
DEFAULT_DATE_RANGE_DAYS = 30        # how many days to fetch by default
SUPPORTED_POLLUTANTS = ["pm25", "pm10", "no2", "so2", "co", "o3"]

# ML / DL
ML_RANDOM_STATE   = 42
DL_RANDOM_SEED    = 42
DL_LOOKBACK_DEFAULT  = 24          # hours
DL_FORECAST_DEFAULT  = 24          # hours
DL_BATCH_SIZE     = 32
DL_MAX_EPOCHS     = 100
DL_EARLY_STOP_PATIENCE = 10
DL_LEARNING_RATE  = 1e-3

TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
# test = remaining 0.15 (chronological split)

# Validation helpers
def api_key_configured() -> bool:
    """Return True when the OpenAQ API key looks non-empty and non-placeholder."""
    key = OPENAQ_API_KEY or ""
    return bool(key) and key != "your_openaq_api_key_here"

def masked_api_key() -> str:
    """Return a safely masked version of the API key for display."""
    key = OPENAQ_API_KEY or ""
    if not key or key == "your_openaq_api_key_here":
        return "NOT CONFIGURED"
    return f"{key[:4]}{'*' * 8}{key[-4:]}" if len(key) > 8 else "***"
