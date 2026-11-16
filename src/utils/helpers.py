"""
AeroSense AI — General Helpers / Utilities
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utcnow_str() -> str:
    return utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_json(obj: Any) -> Any:
    """Make an object JSON-serialisable (best effort)."""
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, pd.DataFrame):
        return f"<DataFrame {obj.shape}>"
    return str(obj)


def hash_string(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[:8]


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=safe_json)


def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def human_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024  # type: ignore[assignment]
    return f"{num_bytes:.1f} TB"


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def format_pct(value: float, decimals: int = 1) -> str:
    return f"{value * 100:.{decimals}f}%"


def df_memory(df: pd.DataFrame) -> str:
    return human_size(df.memory_usage(deep=True).sum())
