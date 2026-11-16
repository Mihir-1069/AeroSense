"""
AeroSense AI — US EPA AQI Calculator
Implements the US EPA AQI (Revised Equation, 2012).
Reference: https://www.airnow.gov/sites/default/files/2020-05/aqi-technical-assistance-document-sept2018.pdf
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Breakpoint tables — (C_lo, C_hi, I_lo, I_hi)
# PM2.5: µg/m³ 24-h avg; PM10: µg/m³ 24-h avg
# O3: ppm 8-h avg; NO2: ppb 1-h avg; SO2: ppb 1-h avg; CO: ppm 8-h avg
EPA_BREAKPOINTS: Dict[str, List[Tuple[float, float, int, int]]] = {
    "pm25": [
        (0.0,   12.0,   0,  50),
        (12.1,  35.4,  51, 100),
        (35.5,  55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ],
    "pm10": [
        (0,   54,   0,  50),
        (55,  154,  51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 504, 301, 400),
        (505, 604, 401, 500),
    ],
    "o3_8h": [   # ppm
        (0.000, 0.054,  0,  50),
        (0.055, 0.070, 51, 100),
        (0.071, 0.085, 101, 150),
        (0.086, 0.105, 151, 200),
        (0.106, 0.200, 201, 300),
    ],
    "no2": [     # ppb
        (0,   53,   0,  50),
        (54,  100,  51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650, 1249, 201, 300),
        (1250, 1649, 301, 400),
        (1650, 2049, 401, 500),
    ],
    "so2": [     # ppb
        (0,   35,   0,  50),
        (36,  75,  51, 100),
        (76,  185, 101, 150),
        (186, 304, 151, 200),
        (305, 604, 201, 300),
        (605, 804, 301, 400),
        (805, 1004, 401, 500),
    ],
    "co": [      # ppm
        (0.0,  4.4,   0,  50),
        (4.5,  9.4,  51, 100),
        (9.5, 12.4, 101, 150),
        (12.5, 15.4, 151, 200),
        (15.5, 30.4, 201, 300),
        (30.5, 40.4, 301, 400),
        (40.5, 50.4, 401, 500),
    ],
}

EPA_CATEGORIES = [
    (0,   50,  "Good",                  "green",   "Air quality is satisfactory."),
    (51,  100, "Moderate",              "yellow",  "Acceptable; may affect very sensitive people."),
    (101, 150, "Unhealthy for Sensitive", "orange","Sensitive groups may experience effects."),
    (151, 200, "Unhealthy",             "red",     "Everyone may experience effects."),
    (201, 300, "Very Unhealthy",        "purple",  "Health alert; serious effects for everyone."),
    (301, 500, "Hazardous",             "maroon",  "Emergency health warning."),
]

@dataclass
class EpaSubIndex:
    pollutant: str
    concentration: float
    sub_index: int
    unit: str

@dataclass
class EpaAQIResult:
    aqi: Optional[int]
    category: str
    color: str
    health_message: str
    dominant_pollutant: str
    sub_indices: List[EpaSubIndex]
    standard: str = "US EPA"
    is_complete: bool = True
    missing_pollutants: List[str] = None  # type: ignore[assignment]
    calculated_pollutants: List[str] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.missing_pollutants is None:
            self.missing_pollutants = []
        if self.calculated_pollutants is None:
            self.calculated_pollutants = []

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item, default=None):
        return getattr(self, item, default)

def _epa_interp(c: float, c_lo: float, c_hi: float, i_lo: int, i_hi: int) -> int:
    return round(((i_hi - i_lo) / (c_hi - c_lo)) * (c - c_lo) + i_lo)

def calculate_epa_sub_index(pollutant: str, concentration: float) -> Optional[Tuple[int, str]]:
    """Return (sub_index, unit_label) or None."""
    key = pollutant.lower()
    # Remap "o3" to "o3_8h"
    lookup_key = "o3_8h" if key == "o3" else key
    bps = EPA_BREAKPOINTS.get(lookup_key)
    if bps is None:
        return None
    unit = "ppm" if key in ("o3", "co") else ("ppb" if key in ("no2", "so2") else "µg/m³")
    for c_lo, c_hi, i_lo, i_hi in bps:
        if c_lo <= concentration <= c_hi:
            return _epa_interp(concentration, c_lo, c_hi, i_lo, i_hi), unit
    if concentration > bps[-1][1]:
        return 500, unit
    return None

def _get_epa_category(aqi: int) -> Tuple[str, str, str]:
    for lo, hi, cat, color, msg in EPA_CATEGORIES:
        if lo <= aqi <= hi:
            return cat, color, msg
    return "Hazardous", "maroon", "Emergency health warning."

def calculate_epa_aqi(
    measurements: Dict[str, float] | float,
    pollutant: Optional[str] = None,
) -> EpaAQIResult:
    """
    Calculate US EPA AQI from a dict or single float.

    Args:
        measurements: {pollutant: concentration} or float concentration.
        pollutant: pollutant name if measurements is a float.
    """
    if isinstance(measurements, (int, float)):
        pol_key = (pollutant or "pm25").lower()
        if measurements < 0:
            return EpaAQIResult(
                aqi=None, category="Unknown", color="gray",
                health_message="Invalid negative concentration.",
                dominant_pollutant=pol_key, sub_indices=[], is_complete=False,
            )
        measurements = {pol_key: float(measurements)}

    sub_indices: List[EpaSubIndex] = []
    computed: List[str] = []
    missing: List[str] = []

    for pol, conc in measurements.items():
        if conc < 0:
            missing.append(pol.lower())
            continue
        result = calculate_epa_sub_index(pol, float(conc))
        if result is not None:
            si, unit = result
            sub_indices.append(EpaSubIndex(pol.lower(), float(conc), si, unit))
            computed.append(pol.lower())
        else:
            missing.append(pol.lower())

    if not sub_indices:
        return EpaAQIResult(
            aqi=None, category="Unavailable", color="gray",
            health_message="Insufficient data.", dominant_pollutant="N/A",
            sub_indices=[], is_complete=False,
            missing_pollutants=list(measurements.keys()), calculated_pollutants=[],
        )

    dominant = max(sub_indices, key=lambda s: s.sub_index)
    aqi = dominant.sub_index
    cat, color, msg = _get_epa_category(aqi)

    return EpaAQIResult(
        aqi=aqi, category=cat, color=color, health_message=msg,
        dominant_pollutant=dominant.pollutant,
        sub_indices=sub_indices, is_complete=len(missing) == 0,
        missing_pollutants=missing, calculated_pollutants=computed,
    )

# Alias for backward compatibility
calculate_us_epa_aqi = calculate_epa_aqi
