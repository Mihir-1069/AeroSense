from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.visualization.charts import map_scatter


def test_map_scatter_uses_map_style_and_renders():
    df = pd.DataFrame({
        "latitude": [28.6469, 19.0596],
        "longitude": [77.3160, 72.8295],
        "value": [145.0, 65.0],
        "location_name": ["Delhi (Anand Vihar)", "Mumbai (Bandra)"],
    })
    fig = map_scatter(df, title="Test Map", height=450)
    assert fig.layout.height == 450
    if "map" in fig.layout:
        assert fig.layout.map.style == "carto-darkmatter"


def test_map_scatter_handles_empty_coordinates():
    df = pd.DataFrame({"latitude": [None], "longitude": [None], "value": [50.0]})
    fig = map_scatter(df, height=350)
    assert fig.layout.title.text == "No location data available"
