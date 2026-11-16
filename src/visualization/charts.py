"""
AeroSense AI — Visualization Charts
Reusable Plotly chart builders for the Streamlit UI.
"""
from __future__ import annotations

from typing import List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PALETTE = {
    "primary":   "#00D4FF",  # cyan
    "secondary": "#7B61FF",  # purple
    "accent":    "#00FF9D",  # green
    "warning":   "#FFA500",  # orange
    "danger":    "#FF4444",  # red
    "bg":        "#0D1117",  # near-black
    "surface":   "#161B22",  # card bg
    "text":      "#E6EDF3",  # soft white
    "muted":     "#8B949E",  # gray
}

AQI_COLORS = {
    "Good":           "#00E400",
    "Satisfactory":   "#92D050",
    "Moderate":       "#FFFF00",
    "Poor":           "#FF7E00",
    "Very Poor":      "#FF0000",
    "Severe":         "#7E0023",
    "Hazardous":      "#7E0023",
    "Unhealthy for Sensitive": "#FF7E00",
    "Unhealthy":      "#FF0000",
    "Very Unhealthy": "#99004C",
}

PLOTLY_TEMPLATE = "plotly_dark"

def _base_layout(**kwargs) -> dict:
    return dict(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor=PALETTE["bg"],
        plot_bgcolor=PALETTE["surface"],
        font=dict(family="Inter, sans-serif", color=PALETTE["text"]),
        margin=dict(l=50, r=30, t=50, b=50),
        **kwargs,
    )

def time_series_chart(
    df: pd.DataFrame,
    x_col: str = "datetime_utc",
    y_col: str = "value",
    title: str = "Pollutant Time Series",
    y_label: str = "Concentration (µg/m³)",
    color_col: Optional[str] = None,
    height: int = 400,
) -> go.Figure:
    fig = px.line(
        df, x=x_col, y=y_col, color=color_col,
        title=title, labels={y_col: y_label, x_col: "Date/Time"},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[PALETTE["primary"], PALETTE["secondary"],
                                  PALETTE["accent"], PALETTE["warning"]],
    )
    fig.update_layout(**_base_layout(height=height))
    fig.update_traces(line_width=1.5)
    return fig

def forecast_chart(
    historical_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    actual_df: Optional[pd.DataFrame] = None,
    dt_col: str = "datetime_utc",
    value_col: str = "value",
    forecast_col: str = "forecast",
    title: str = "Forecast",
    y_label: str = "PM2.5 (µg/m³)",
    height: int = 450,
) -> go.Figure:
    fig = go.Figure()
    # Historical
    fig.add_trace(go.Scatter(
        x=historical_df[dt_col], y=historical_df[value_col],
        name="Observed", line=dict(color=PALETTE["primary"], width=1.5),
        mode="lines",
    ))
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df[dt_col], y=forecast_df[forecast_col],
        name="Forecast", line=dict(color=PALETTE["warning"], width=2, dash="dash"),
        mode="lines",
    ))
    # Actual (test) if provided
    if actual_df is not None and not actual_df.empty:
        fig.add_trace(go.Scatter(
            x=actual_df[dt_col], y=actual_df[value_col],
            name="Actual (test)", line=dict(color=PALETTE["accent"], width=1.5),
            mode="lines",
        ))
    fig.update_layout(
        title=title,
        yaxis_title=y_label,
        xaxis_title="Date/Time",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        **_base_layout(height=height),
    )
    return fig

def aqi_gauge(aqi: int, standard: str = "CPCB") -> go.Figure:
    max_val = 500
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=aqi,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": f"AQI ({standard})", "font": {"size": 20, "color": PALETTE["text"]}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": PALETTE["text"]},
            "bar": {"color": PALETTE["warning"]},
            "bgcolor": PALETTE["surface"],
            "steps": [
                {"range": [0, 50],   "color": "#00E400"},
                {"range": [50, 100], "color": "#92D050"},
                {"range": [100, 200], "color": "#FFFF00"},
                {"range": [200, 300], "color": "#FF7E00"},
                {"range": [300, 400], "color": "#FF0000"},
                {"range": [400, 500], "color": "#7E0023"},
            ],
            "threshold": {"line": {"color": "white", "width": 3}, "value": aqi},
        },
    ))
    fig.update_layout(**_base_layout(height=280))
    return fig

def correlation_heatmap(corr: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title=title, template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(**_base_layout(height=400))
    return fig

def bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    y_label: str = "",
    color_col: Optional[str] = None,
    height: int = 350,
) -> go.Figure:
    fig = px.bar(
        df, x=x_col, y=y_col, color=color_col,
        title=title, labels={y_col: y_label},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[PALETTE["primary"], PALETTE["secondary"],
                                  PALETTE["accent"], PALETTE["warning"]],
    )
    fig.update_layout(**_base_layout(height=height))
    return fig

def box_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    y_label: str = "",
    height: int = 400,
) -> go.Figure:
    fig = px.box(
        df, x=x_col, y=y_col, title=title,
        labels={y_col: y_label},
        template=PLOTLY_TEMPLATE,
        color=x_col,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(**_base_layout(height=height))
    return fig

def scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    color_col: Optional[str] = None,
    height: int = 400,
) -> go.Figure:
    fig = px.scatter(
        df, x=x_col, y=y_col, color=color_col,
        title=title, opacity=0.6,
        template=PLOTLY_TEMPLATE,
        trendline="ols",
        color_discrete_sequence=[PALETTE["primary"]],
    )
    fig.update_layout(**_base_layout(height=height))
    return fig

def map_scatter(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    color_col: str = "value",
    hover_col: str = "location_name",
    title: str = "Monitoring Stations",
    height: int = 500,
) -> go.Figure:
    df_clean = df.dropna(subset=[lat_col, lon_col, color_col])
    if df_clean.empty:
        fig = go.Figure()
        fig.update_layout(title="No location data available", **_base_layout(height=height))
        return fig

    fig = px.scatter_map(
        df_clean,
        lat=lat_col, lon=lon_col,
        color=color_col,
        hover_name=hover_col,
        color_continuous_scale="YlOrRd",
        title=title,
        zoom=4,
        height=height,
    )
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        **_base_layout(height=height),
    )
    return fig

def feature_importance_bar(
    df: pd.DataFrame,
    title: str = "Feature Importance",
    top_n: int = 15,
    height: int = 400,
) -> go.Figure:
    df = df.head(top_n)
    fig = px.bar(
        df, x="importance", y="feature", orientation="h",
        title=title, template=PLOTLY_TEMPLATE,
        color="importance",
        color_continuous_scale="Viridis",
    )
    fig.update_layout(**_base_layout(height=height))
    fig.update_yaxes(autorange="reversed")
    return fig

def residual_plot(
    df: pd.DataFrame,
    x_col: str = "actual",
    res_col: str = "residual",
    title: str = "Residual Analysis",
    height: int = 350,
) -> go.Figure:
    fig = px.scatter(
        df, x=x_col, y=res_col,
        title=title, opacity=0.5,
        template=PLOTLY_TEMPLATE,
        labels={x_col: "Actual Value", res_col: "Residual"},
    )
    fig.add_hline(y=0, line_dash="dash", line_color=PALETTE["muted"])
    fig.update_layout(**_base_layout(height=height))
    return fig

def loss_curves(history: dict, title: str = "Training Loss", height: int = 300) -> go.Figure:
    epochs = list(range(1, len(history.get("train_loss", [])) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=epochs, y=history.get("train_loss", []),
                             name="Train Loss", line=dict(color=PALETTE["primary"])))
    fig.add_trace(go.Scatter(x=epochs, y=history.get("val_loss", []),
                             name="Val Loss", line=dict(color=PALETTE["warning"])))
    fig.update_layout(title=title, xaxis_title="Epoch", yaxis_title="MSE Loss",
                      **_base_layout(height=height))
    return fig
