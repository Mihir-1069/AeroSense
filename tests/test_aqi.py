"""
Unit tests for AQI Intelligence Engines (CPCB India & US EPA)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from src.aqi.cpcb import calculate_cpcb_aqi
from src.aqi.us_epa import calculate_us_epa_aqi


class TestCPCBAQI:
    """Tests for Indian Central Pollution Control Board (CPCB) AQI."""

    def test_cpcb_good_category(self):
        # PM2.5: 0-30 -> AQI 0-50 (Good)
        res = calculate_cpcb_aqi(15.0, "pm25")
        assert res["category"] == "Good"
        assert 0 <= res["aqi"] <= 50
        assert res["color"] == "#00E400"

    def test_cpcb_satisfactory_category(self):
        # PM2.5: 31-60 -> AQI 51-100 (Satisfactory)
        res = calculate_cpcb_aqi(45.0, "pm25")
        assert res["category"] == "Satisfactory"
        assert 51 <= res["aqi"] <= 100

    def test_cpcb_moderate_category(self):
        # PM2.5: 61-90 -> AQI 101-200 (Moderate)
        res = calculate_cpcb_aqi(75.0, "pm25")
        assert res["category"] == "Moderate"
        assert 101 <= res["aqi"] <= 200

    def test_cpcb_poor_category(self):
        # PM2.5: 91-120 -> AQI 201-300 (Poor)
        res = calculate_cpcb_aqi(110.0, "pm25")
        assert res["category"] == "Poor"
        assert 201 <= res["aqi"] <= 300

    def test_cpcb_very_poor_category(self):
        # PM2.5: 121-250 -> AQI 301-400 (Very Poor)
        res = calculate_cpcb_aqi(180.0, "pm25")
        assert res["category"] == "Very Poor"
        assert 301 <= res["aqi"] <= 400

    def test_cpcb_severe_category(self):
        # PM2.5: 250+ -> AQI 401-500 (Severe)
        res = calculate_cpcb_aqi(320.0, "pm25")
        assert res["category"] == "Severe"
        assert res["aqi"] >= 401

    def test_cpcb_pm10(self):
        # PM10: 0-50 -> Good
        res = calculate_cpcb_aqi(30.0, "pm10")
        assert res["category"] == "Good"

    def test_cpcb_invalid_or_negative(self):
        res = calculate_cpcb_aqi(-10.0, "pm25")
        assert res["aqi"] is None or res["category"] == "Unknown"


class TestUSEPAAQI:
    """Tests for US Environmental Protection Agency (EPA) AQI."""

    def test_epa_good(self):
        # PM2.5: 0-12.0 -> AQI 0-50
        res = calculate_us_epa_aqi(8.0, "pm25")
        assert res["category"] == "Good"
        assert 0 <= res["aqi"] <= 50

    def test_epa_moderate(self):
        # PM2.5: 12.1-35.4 -> AQI 51-100
        res = calculate_us_epa_aqi(25.0, "pm25")
        assert res["category"] == "Moderate"
        assert 51 <= res["aqi"] <= 100

    def test_epa_unhealthy(self):
        # PM2.5: 55.5-150.4 -> AQI 151-200
        res = calculate_us_epa_aqi(85.0, "pm25")
        assert res["category"] == "Unhealthy"
        assert 151 <= res["aqi"] <= 200

    def test_epa_hazardous(self):
        # PM2.5: 250.5+ -> AQI 301-500
        res = calculate_us_epa_aqi(350.0, "pm25")
        assert res["category"] == "Hazardous"
        assert res["aqi"] >= 301
