"""
Unit tests for Technical Reporting & Export Engine
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest

from src.reporting.report_generator import (
    compute_dataset_summary,
    generate_markdown_report,
    generate_html_report,
    create_export_archive,
)
from src.config import settings

@pytest.fixture
def sample_report_df():
    dts = pd.date_range("2026-01-01 00:00:00", periods=50, freq="h", tz="UTC")
    values = np.linspace(20, 150, 50)
    return pd.DataFrame({
        "datetime_utc": dts,
        "value": values,
        "parameter": "pm25",
        "location_name": "Test Station",
    })

def test_compute_dataset_summary(sample_report_df):
    stats = compute_dataset_summary(sample_report_df)
    assert stats["count"] == 50
    assert stats["min"] == 20.0
    assert stats["max"] == 150.0
    assert "who_exceedance_pct" in stats
    assert "cpcb_distribution" in stats

def test_generate_markdown_report(sample_report_df):
    md = generate_markdown_report("test_ds", sample_report_df)
    assert "# 🌬️ AeroSense AI" in md
    assert "Executive Summary" in md
    assert "Descriptive & Environmental Statistics" in md

def test_generate_html_report(sample_report_df):
    html = generate_html_report("test_ds", sample_report_df)
    assert "<!DOCTYPE html>" in html
    assert "AeroSense AI" in html
    assert "table" in html

def test_create_export_archive(sample_report_df, tmp_path):
    zip_out = tmp_path / "test_export.zip"
    created = create_export_archive("test_ds", sample_report_df, output_zip_path=zip_out)
    assert created.exists()
    assert created.stat().st_size > 0
