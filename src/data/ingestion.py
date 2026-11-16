"""
AeroSense AI — Data Ingestion
Coordinates API calls, raw storage, and provenance tracking.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.api.openaq_client import OpenAQClient
from src.config import settings
from src.utils.helpers import utcnow_str

log = logging.getLogger(__name__)

PROVENANCE_COLS = [
    "location_id", "location_name", "city", "country",
    "latitude", "longitude", "sensor_id",
    "parameter", "unit", "value", "datetime_utc",
    "source_provider", "api_endpoint", "retrieved_at",
]


def _parse_measurement(
    raw: Dict[str, Any],
    location_id: int,
    parameter: str,
    location_meta: Optional[Dict[str, Any]] = None,
) -> Optional[Dict]:
    """Extract flat record from an OpenAQ v3 sensor hours/measurements dict."""
    try:
        value = raw.get("value")
        if value is None:
            return None

        # OpenAQ v3 /hours has top-level datetimeTo/datetimeFrom; /measurements has period.datetimeTo
        period = raw.get("period") or {}
        dt_to = raw.get("datetimeTo") or period.get("datetimeTo") or raw.get("date") or raw.get("datetime") or {}
        if isinstance(dt_to, dict):
            dt = dt_to.get("utc") or dt_to.get("local") or ""
        else:
            dt = str(dt_to)

        param_obj = raw.get("parameter") or {}
        unit = param_obj.get("units") or raw.get("unit") or "µg/m³"
        meta = location_meta or {}
        coords = raw.get("coordinates") or {}

        return {
            "location_id": location_id,
            "location_name": meta.get("location_name") or raw.get("locationName", ""),
            "city": meta.get("city") or raw.get("city", ""),
            "country": meta.get("country") or raw.get("country", ""),
            "latitude": meta.get("latitude") if meta.get("latitude") is not None else coords.get("latitude"),
            "longitude": meta.get("longitude") if meta.get("longitude") is not None else coords.get("longitude"),
            "sensor_id": meta.get("sensor_id") or raw.get("sensorsId", raw.get("sensor_id")),
            "parameter": param_obj.get("name", parameter),
            "unit": unit,
            "value": float(value),
            "datetime_utc": dt,
            "source_provider": "OpenAQ",
            "api_endpoint": f"/sensors/{meta.get('sensor_id', 'unknown')}/hours" if meta.get("sensor_id") else f"/locations/{location_id}/measurements",
            "retrieved_at": utcnow_str(),
        }
    except Exception as exc:
        log.debug("Could not parse measurement: %s — %s", raw, exc)
        return None


class DataIngestion:
    """Manages data fetching from OpenAQ API and local raw storage."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.client = OpenAQClient(api_key=api_key)
        self.raw_dir = settings.RAW_DIR

    # ------------------------------------------------------------------
    # Country / Location discovery
    # ------------------------------------------------------------------
    def fetch_countries(self) -> pd.DataFrame:
        log.info("Fetching countries from OpenAQ…")
        countries = self.client.get_countries()
        if not countries:
            log.warning("No countries returned.")
            return pd.DataFrame()
        df = pd.DataFrame(countries)
        self._save_raw(df, "countries")
        return df

    def fetch_locations(
        self,
        country_iso: str,
        limit: int = 500,
        parameter: Optional[str] = None,
    ) -> pd.DataFrame:
        log.info("Fetching locations for country=%s…", country_iso)
        locs = self.client.get_locations(country=country_iso, parameter=parameter, limit=limit)
        if not locs:
            log.warning("No locations found for %s.", country_iso)
            return pd.DataFrame()

        records = []
        for loc in locs:
            coords = loc.get("coordinates") or {}
            sensors = loc.get("sensors") or []
            sensors_map = {}
            param_names = []
            for s in sensors:
                p = s.get("parameter") or {}
                p_name = str(p.get("name", "")).lower()
                if p_name:
                    param_names.append(p_name)
                    if s.get("id") is not None:
                        sensors_map[p_name] = int(s["id"])

            dt_last_obj = loc.get("datetimeLast") or {}
            last_updated = dt_last_obj.get("utc", "") if isinstance(dt_last_obj, dict) else (loc.get("lastUpdated") or "")

            records.append({
                "location_id": loc.get("id"),
                "location_name": loc.get("name", ""),
                "city": loc.get("locality") or loc.get("city") or "",
                "country": loc.get("country", {}).get("code", country_iso)
                           if isinstance(loc.get("country"), dict) else loc.get("country", country_iso),
                "latitude": coords.get("latitude"),
                "longitude": coords.get("longitude"),
                "is_active": bool(last_updated) or loc.get("isActive", True),
                "parameters": json.dumps(param_names),
                "sensors_map": json.dumps(sensors_map),
                "last_updated": last_updated,
            })

        df = pd.DataFrame(records)
        if "last_updated" in df.columns:
            df = df.sort_values("last_updated", ascending=False).reset_index(drop=True)
        self._save_raw(df, f"locations_{country_iso}")
        return df

    # ------------------------------------------------------------------
    # Measurements
    # ------------------------------------------------------------------
    def fetch_measurements(
        self,
        location_id: int,
        parameter: str = "pm25",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 1000,
        sensor_id: Optional[int] = None,
        location_meta: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """Fetch measurements and return as a DataFrame with provenance."""
        log.info("Fetching %s measurements for location %d…", parameter, location_id)

        raw = self.client.get_measurements(
            location_id=location_id,
            parameter=parameter,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            sensor_id=sensor_id,
        )
        if not raw:
            log.warning("No measurements returned for location %d / %s.", location_id, parameter)
            return pd.DataFrame(columns=PROVENANCE_COLS)

        meta = dict(location_meta or {})
        if sensor_id is not None:
            meta["sensor_id"] = sensor_id

        records = [_parse_measurement(r, location_id, parameter, location_meta=meta) for r in raw]
        records = [r for r in records if r is not None]

        if not records:
            return pd.DataFrame(columns=PROVENANCE_COLS)

        df = pd.DataFrame(records)
        self._save_raw(df, f"measurements_{location_id}_{parameter}")
        log.info("Fetched %d %s records for location %d.", len(df), parameter, location_id)
        return df

    def fetch_measurements_bulk(
        self,
        location_ids: List[int],
        parameter: str = "pm25",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        frames = []
        for loc_id in location_ids:
            try:
                df = self.fetch_measurements(loc_id, parameter, date_from, date_to, limit)
                frames.append(df)
            except Exception as exc:
                log.warning("Skipped location %d: %s", loc_id, exc)
        if not frames:
            return pd.DataFrame(columns=PROVENANCE_COLS)
        return pd.concat(frames, ignore_index=True)

    # ------------------------------------------------------------------
    # Date helpers
    # ------------------------------------------------------------------
    @staticmethod
    def default_date_range(days: int = 30) -> tuple[str, str]:
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days)
        return start.strftime("%Y-%m-%dT%H:%M:%SZ"), now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------
    def _save_raw(self, df: pd.DataFrame, name: str) -> Path:
        if df.empty:
            return self.raw_dir
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.raw_dir / f"{name}_{ts}.parquet"
        table = pa.Table.from_pandas(df, preserve_index=False)
        pq.write_table(table, path)
        log.debug("Saved raw %s → %s", name, path.name)
        return path
