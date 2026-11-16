"""
AeroSense AI — Data Storage
Parquet read/write helpers, CSV exports, metadata management.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.config import settings

log = logging.getLogger(__name__)


def save_processed(
    df: pd.DataFrame,
    name: str,
    base_dir: Optional[Path] = None,
) -> Path:
    base = base_dir or settings.PROCESSED_DIR
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{name}.parquet"
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, path)
    log.info("Saved processed → %s (%d rows)", path.name, len(df))
    return path


def load_processed(name: str, base_dir: Optional[Path] = None) -> Optional[pd.DataFrame]:
    base = base_dir or settings.PROCESSED_DIR
    path = base / f"{name}.parquet"
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    log.debug("Loaded %s (%d rows).", path.name, len(df))
    return df


def save_features(df: pd.DataFrame, name: str) -> Path:
    return save_processed(df, name, base_dir=settings.FEATURES_DIR)


def load_features(name: str) -> Optional[pd.DataFrame]:
    return load_processed(name, base_dir=settings.FEATURES_DIR)


def export_csv(df: pd.DataFrame, name: str) -> Path:
    settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = settings.EXPORTS_DIR / f"{name}_{ts}.csv"
    df.to_csv(path, index=False)
    log.info("Exported CSV → %s", path.name)
    return path


def list_raw_files(pattern: str = "*.parquet") -> list[Path]:
    return sorted(settings.RAW_DIR.glob(pattern))


def list_processed_files(pattern: str = "*.parquet") -> list[Path]:
    return sorted(settings.PROCESSED_DIR.glob(pattern))


def latest_raw(prefix: str) -> Optional[pd.DataFrame]:
    """Load the most recent raw parquet file matching a prefix."""
    files = sorted(settings.RAW_DIR.glob(f"{prefix}*.parquet"))
    if not files:
        return None
    return pd.read_parquet(files[-1])
