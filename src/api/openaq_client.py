"""
AeroSense AI — OpenAQ API v3 Client
Secure, robust HTTP client with authentication, retry, pagination, and caching.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional

import httpx

from src.config import settings

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class OpenAQError(Exception):
    """Base exception for OpenAQ client errors."""

class OpenAQAuthError(OpenAQError):
    """401/403 — invalid or missing API key."""

class OpenAQRateLimitError(OpenAQError):
    """429 — rate limit exceeded."""

class OpenAQNotFoundError(OpenAQError):
    """404 — resource not found."""

class OpenAQServerError(OpenAQError):
    """5xx — server-side error."""

class OpenAQConnectionError(OpenAQError):
    """Network/timeout error."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class OpenAQClient:
    """
    Thread-safe synchronous client for the OpenAQ API v3.

    Usage::

        client = OpenAQClient(api_key="your-key")
        countries = client.get_countries()
        locations = client.get_locations(country="IN", limit=100)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = settings.OPENAQ_BASE_URL,
        timeout: int = settings.OPENAQ_TIMEOUT_SECONDS,
    ) -> None:
        self._api_key = api_key or settings.OPENAQ_API_KEY or ""
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._last_success: Optional[datetime] = None
        self._last_error: Optional[str] = None
        self._request_count: int = 0

    # ------------------------------------------------------------------
    # Auth headers
    # ------------------------------------------------------------------
    @property
    def _headers(self) -> Dict[str, str]:
        h: Dict[str, str] = {"Accept": "application/json"}
        if self._api_key:
            h["X-API-Key"] = self._api_key
        return h

    # ------------------------------------------------------------------
    # Core request with retry
    # ------------------------------------------------------------------
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        self._request_count += 1

        for attempt in range(1, settings.OPENAQ_MAX_RETRIES + 1):
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.request(
                        method, url, headers=self._headers, params=params
                    )
                self._handle_status(resp)
                data = resp.json()
                self._last_success = datetime.now(timezone.utc)
                return data

            except OpenAQRateLimitError:
                wait = settings.OPENAQ_RETRY_BACKOFF * (2 ** (attempt - 1))
                log.warning("Rate limit hit; waiting %.1fs (attempt %d)", wait, attempt)
                if attempt < settings.OPENAQ_MAX_RETRIES:
                    time.sleep(wait)
                else:
                    raise

            except (OpenAQServerError, httpx.TimeoutException, httpx.NetworkError) as exc:
                wait = settings.OPENAQ_RETRY_BACKOFF * (2 ** (attempt - 1))
                log.warning(
                    "Transient error (%s); retrying in %.1fs (attempt %d/%d)",
                    exc, wait, attempt, settings.OPENAQ_MAX_RETRIES,
                )
                self._last_error = str(exc)
                if attempt < settings.OPENAQ_MAX_RETRIES:
                    time.sleep(wait)
                else:
                    raise OpenAQConnectionError(str(exc)) from exc

            except (OpenAQAuthError, OpenAQNotFoundError, OpenAQError):
                raise

        raise OpenAQError("Exhausted retries without a successful response.")

    @staticmethod
    def _handle_status(resp: httpx.Response) -> None:
        code = resp.status_code
        if code == 200:
            return
        if code == 401:
            raise OpenAQAuthError("Invalid or missing API key (HTTP 401).")
        if code == 403:
            raise OpenAQAuthError("Access forbidden (HTTP 403).")
        if code == 404:
            raise OpenAQNotFoundError(f"Resource not found (HTTP 404): {resp.url}")
        if code == 429:
            raise OpenAQRateLimitError("Rate limit exceeded (HTTP 429).")
        if 500 <= code < 600:
            raise OpenAQServerError(f"Server error HTTP {code}: {resp.text[:200]}")
        raise OpenAQError(f"Unexpected HTTP {code}: {resp.text[:200]}")

    # ------------------------------------------------------------------
    # Paginated helper
    # ------------------------------------------------------------------
    def _paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        result_key: str = "results",
        max_pages: int = settings.OPENAQ_MAX_PAGES,
    ) -> List[Dict[str, Any]]:
        params = dict(params or {})
        params.setdefault("limit", settings.OPENAQ_DEFAULT_LIMIT)
        all_results: List[Dict[str, Any]] = []

        for page in range(1, max_pages + 1):
            params["page"] = page
            data = self._request("GET", endpoint, params=params)
            page_results = data.get(result_key, [])
            all_results.extend(page_results)
            log.debug("Page %d: got %d records (total so far %d)", page, len(page_results), len(all_results))

            # Check if there are more pages
            meta = data.get("meta", {})
            limit = int(meta.get("limit", params["limit"]))
            found_raw = meta.get("found")
            if isinstance(found_raw, int):
                found = found_raw
            elif isinstance(found_raw, str):
                digits = "".join(ch for ch in found_raw if ch.isdigit())
                found = (int(digits) + 1) if (digits and found_raw.startswith(">")) else (int(digits) if digits else len(all_results) + 1)
            else:
                found = len(all_results) + 1

            if not page_results or len(all_results) >= found or len(page_results) < limit:
                break

        return all_results

    # ------------------------------------------------------------------
    # API methods
    # ------------------------------------------------------------------

    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connectivity and authentication.
        Returns a dict with 'ok', 'message', 'api_version', 'authenticated'.
        """
        result: Dict[str, Any] = {
            "ok": False,
            "authenticated": bool(self._api_key),
            "message": "",
            "api_version": "v3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            data = self._request("GET", "/countries", params={"limit": 1})
            result["ok"] = True
            result["message"] = "Connection successful."
            result["total_countries"] = data.get("meta", {}).get("found", "unknown")
        except OpenAQAuthError as e:
            result["message"] = f"Authentication failed: {e}"
        except OpenAQConnectionError as e:
            result["message"] = f"Connection error: {e}"
        except Exception as e:  # noqa: BLE001
            result["message"] = f"Unexpected error: {e}"
        return result

    # ---- Countries -------------------------------------------------------
    def get_countries(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Return all available countries."""
        return self._paginate("/countries", params={"limit": limit})

    def list_countries(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Alias for get_countries."""
        return self.get_countries(limit=limit)

    # ---- Locations -------------------------------------------------------
    def get_locations(
        self,
        country: Optional[str] = None,
        parameter: Optional[str] = None,
        limit: int = 500,
        coordinates: Optional[tuple[float, float]] = None,
        radius: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": min(limit, settings.OPENAQ_DEFAULT_LIMIT)}
        if country:
            params["iso"] = country.upper()
        if parameter:
            params["parameters_id"] = self._resolve_parameter_id(parameter)
        if coordinates:
            params["coordinates"] = f"{coordinates[0]},{coordinates[1]}"
        if radius:
            params["radius"] = radius
        return self._paginate("/locations", params=params, max_pages=3)

    def get_location(self, location_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/locations/{location_id}")

    # ---- Parameters / Pollutants ----------------------------------------
    def get_parameters(self) -> List[Dict[str, Any]]:
        """Return all supported measurement parameters (pollutants)."""
        data = self._request("GET", "/parameters", params={"limit": 100})
        return data.get("results", [])

    # ---- Sensor Measurements (OpenAQ v3) --------------------------------
    def get_sensor_hours(
        self,
        sensor_id: int,
        datetime_from: Optional[str] = None,
        datetime_to: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Fetch hourly aggregated measurements from /v3/sensors/{id}/hours."""
        params: Dict[str, Any] = {"limit": min(limit, 1000)}
        if datetime_from:
            params["datetime_from"] = datetime_from
        if datetime_to:
            params["datetime_to"] = datetime_to
        return self._paginate(
            f"/sensors/{sensor_id}/hours",
            params=params,
            max_pages=settings.OPENAQ_MAX_PAGES,
        )

    def get_sensor_measurements(
        self,
        sensor_id: int,
        datetime_from: Optional[str] = None,
        datetime_to: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Fetch raw measurements from /v3/sensors/{id}/measurements."""
        params: Dict[str, Any] = {"limit": min(limit, 1000)}
        if datetime_from:
            params["datetime_from"] = datetime_from
        if datetime_to:
            params["datetime_to"] = datetime_to
        return self._paginate(
            f"/sensors/{sensor_id}/measurements",
            params=params,
            max_pages=settings.OPENAQ_MAX_PAGES,
        )

    def get_measurements(
        self,
        location_id: int,
        parameter: str = "pm25",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 1000,
        sensor_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch hourly measurements for a location & parameter via OpenAQ v3 sensor endpoints.
        Resolves sensor_id from /locations/{id}/sensors if not provided.
        """
        target_sensor_id = sensor_id
        if target_sensor_id is None:
            sensors = self.get_sensors(location_id)
            target_param = parameter.lower()
            for s in sensors:
                p_info = s.get("parameter") or {}
                if str(p_info.get("name", "")).lower() == target_param:
                    target_sensor_id = s.get("id")
                    break

        if target_sensor_id is None:
            log.warning("No sensor found for location %d / parameter %s.", location_id, parameter)
            return []

        results = self.get_sensor_hours(
            sensor_id=target_sensor_id,
            datetime_from=date_from,
            datetime_to=date_to,
            limit=limit,
        )
        if not results:
            results = self.get_sensor_measurements(
                sensor_id=target_sensor_id,
                datetime_from=date_from,
                datetime_to=date_to,
                limit=limit,
            )
        return results

    def get_latest(
        self,
        location_id: int,
    ) -> List[Dict[str, Any]]:
        """Fetch latest readings for a location from /v3/locations/{id}/latest."""
        data = self._request("GET", f"/locations/{location_id}/latest")
        return data.get("results", [])

    # ---- Sensors --------------------------------------------------------
    def get_sensors(self, location_id: int) -> List[Dict[str, Any]]:
        data = self._request("GET", f"/locations/{location_id}/sensors")
        return data.get("results", [])

    # ---- Countries by ISO -----------------------------------------------
    def get_country_by_iso(self, iso: str) -> Optional[Dict[str, Any]]:
        try:
            data = self._request("GET", "/countries", params={"limit": 1, "iso": iso})
            results = data.get("results", [])
            return results[0] if results else None
        except Exception:
            return None

    # ---- Cities ---------------------------------------------------------
    def get_cities(self, country_iso: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Return distinct cities for a country (derived from location metadata)."""
        locations = self.get_locations(country=country_iso, limit=limit)
        seen: set[str] = set()
        cities = []
        for loc in locations:
            city = loc.get("city") or loc.get("locality") or ""
            if city and city not in seen:
                seen.add(city)
                cities.append({"city": city, "country": country_iso})
        return sorted(cities, key=lambda x: x["city"])

    # ---- Parameter ID resolver ------------------------------------------
    _PARAM_NAME_TO_ID: Dict[str, int] = {
        # These are common OpenAQ v3 parameter IDs; may differ per deployment.
        "pm25": 2,
        "pm10": 1,
        "no2": 7,
        "so2": 9,
        "co": 8,
        "o3": 10,
        "bc": 3,
    }

    def _resolve_parameter_id(self, name: str) -> int:
        return self._PARAM_NAME_TO_ID.get(name.lower(), 2)

    # ---- Status ---------------------------------------------------------
    @property
    def status(self) -> Dict[str, Any]:
        return {
            "api_key_configured": bool(self._api_key),
            "last_success": self._last_success.isoformat() if self._last_success else None,
            "last_error": self._last_error,
            "total_requests": self._request_count,
        }
