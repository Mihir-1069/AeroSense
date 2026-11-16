"""
AeroSense AI — India CPCB AQI Calculator
Implements the official CPCB National Air Quality Index (2014) methodology.
Reference: https://cpcb.nic.in/displaypdf.php?id=bmFxaS9OQVFJLnBkZg==
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

# Breakpoint tables — (BPlo, BPhi, Ilo, Ihi) per pollutant
# Units:  PM2.5 µg/m³ 24h avg, PM10 µg/m³ 24h avg
#         NO2 µg/m³ 24h avg, SO2 µg/m³ 24h avg
#         CO mg/m³ 8h avg, O3 µg/m³ 8h avg, NH3 µg/m³ 24h avg
CPCB_BREAKPOINTS: Dict[str, List[Tuple[float, float, int, int]]] = {
    "pm25": [
        (0, 30,   0,  50),
        (31, 60,  51, 100),
        (61, 90,  101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (251, 500, 401, 500),
    ],
    "pm10": [
        (0, 50,   0,  50),
        (51, 100, 51, 100),
        (101, 250, 101, 200),
        (251, 350, 201, 300),
        (351, 430, 301, 400),
        (431, 600, 401, 500),
    ],
    "no2": [
        (0, 40,   0,  50),
        (41, 80,  51, 100),
        (81, 180, 101, 200),
        (181, 280, 201, 300),
        (281, 400, 301, 400),
        (401, 800, 401, 500),
    ],
    "so2": [
        (0, 40,   0,  50),
        (41, 80,  51, 100),
        (81, 380, 101, 200),
        (381, 800, 201, 300),
        (801, 1600, 301, 400),
        (1601, 2620, 401, 500),
    ],
    "co": [   # mg/m³ 8-h
        (0, 1.0,  0,  50),
        (1.1, 2.0, 51, 100),
        (2.1, 10.0, 101, 200),
        (10.1, 17.0, 201, 300),
        (17.1, 34.0, 301, 400),
        (34.1, 50.0, 401, 500),
    ],
    "o3": [   # µg/m³ 8-h
        (0, 50,   0,  50),
        (51, 100, 51, 100),
        (101, 168, 101, 200),
        (169, 208, 201, 300),
        (209, 748, 301, 400),
        (749, 1000, 401, 500),
    ],
}

CPCB_CATEGORIES = [
    (0,   50,  "Good",          "Air quality is satisfactory."),
    (51,  100, "Satisfactory",  "Minor discomfort for sensitive people."),
    (101, 200, "Moderate",      "Discomfort for people with lung/heart conditions."),
    (201, 300, "Poor",          "Breathing discomfort for most people."),
    (301, 400, "Very Poor",     "Respiratory illness possible on prolonged exposure."),
    (401, 500, "Severe",        "Affects healthy people; serious risk for diseased."),
]

CPCB_COLORS = {
    "Good": "#00E400",
    "Satisfactory": "#92D050",
    "Moderate": "#FFFF00",
    "Poor": "#FF7E00",
    "Very Poor": "#FF0000",
    "Severe": "#7E0023",
    "Unavailable": "#808080",
    "Unknown": "#808080",
}

@dataclass
class SubIndex:
    pollutant: str
    concentration: float
    sub_index: int
    unit: str = "µg/m³"

@dataclass
class CpcbAQIResult:
    aqi: Optional[int]
    category: str
    health_message: str
    dominant_pollutant: str
    sub_indices: List[SubIndex]
    standard: str = "CPCB (India)"
    color: str = "#808080"
    is_complete: bool = True
    missing_pollutants: List[str] = None   # type: ignore[assignment]
    calculated_pollutants: List[str] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.missing_pollutants is None:
            self.missing_pollutants = []
        if self.calculated_pollutants is None:
            self.calculated_pollutants = []
        if self.color == "#808080" and self.category in CPCB_COLORS:
            self.color = CPCB_COLORS[self.category]

    @property
    def health_implication(self) -> str:
        return self.health_message

    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, item, default=None):
        return getattr(self, item, default)

def _linear_interpolate(c: float, bp_lo: float, bp_hi: float, i_lo: int, i_hi: int) -> int:
    """Piecewise linear interpolation per CPCB formula."""
    return round(((i_hi - i_lo) / (bp_hi - bp_lo)) * (c - bp_lo) + i_lo)

def calculate_sub_index(pollutant: str, concentration: float) -> Optional[int]:
    """Calculate sub-index for a single pollutant."""
    bps = CPCB_BREAKPOINTS.get(pollutant.lower())
    if bps is None:
        return None
    for bp_lo, bp_hi, i_lo, i_hi in bps:
        if bp_lo <= concentration <= bp_hi:
            return _linear_interpolate(concentration, bp_lo, bp_hi, i_lo, i_hi)
    if concentration > bps[-1][1]:
        return 500
    return None

def _get_category(aqi: int) -> Tuple[str, str]:
    for lo, hi, cat, msg in CPCB_CATEGORIES:
        if lo <= aqi <= hi:
            return cat, msg
    return "Severe", "Hazardous conditions."

def calculate_cpcb_aqi(
    measurements: Dict[str, float] | float,
    pollutant: Optional[str] = None,
) -> CpcbAQIResult:
    """
    Calculate CPCB AQI from a dict of {pollutant: concentration} or a single value + pollutant name.

    Args:
        measurements: e.g. {"pm25": 60.0} or float 60.0
        pollutant: pollutant key (e.g. "pm25") if measurements is a float.
    """
    if isinstance(measurements, (int, float)):
        pol_key = (pollutant or "pm25").lower()
        if measurements < 0:
            return CpcbAQIResult(
                aqi=None, category="Unknown",
                health_message="Invalid negative concentration.",
                dominant_pollutant=pol_key, sub_indices=[], is_complete=False,
            )
        measurements = {pol_key: float(measurements)}

    sub_indices: List[SubIndex] = []
    computed: List[str] = []
    missing: List[str] = []

    for pol, conc in measurements.items():
        key = pol.lower()
        if key not in CPCB_BREAKPOINTS:
            continue
        if conc < 0:
            missing.append(key)
            continue
        si = calculate_sub_index(key, float(conc))
        if si is not None:
            sub_indices.append(SubIndex(key, float(conc), si))
            computed.append(key)
        else:
            missing.append(key)

    if not sub_indices:
        return CpcbAQIResult(
            aqi=None, category="Unknown",
            health_message="Insufficient data to calculate AQI.",
            dominant_pollutant="N/A",
            sub_indices=[],
            is_complete=False,
            missing_pollutants=list(measurements.keys()),
            calculated_pollutants=[],
        )

    dominant = max(sub_indices, key=lambda s: s.sub_index)
    aqi = dominant.sub_index
    cat, msg = _get_category(aqi)

    return CpcbAQIResult(
        aqi=aqi,
        category=cat,
        health_message=msg,
        dominant_pollutant=dominant.pollutant,
        sub_indices=sub_indices,
        is_complete=len(missing) == 0,
        missing_pollutants=missing,
        calculated_pollutants=computed,
    )
