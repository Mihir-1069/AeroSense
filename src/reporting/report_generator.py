"""
AeroSense AI — Academic Research & Project Report Generator
Exports research summaries in Markdown, HTML, PDF, and complete project bundles.
"""
from __future__ import annotations

import io
import json
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from src.config import settings
from src.aqi.cpcb import calculate_cpcb_aqi
from src.aqi.us_epa import calculate_us_epa_aqi

logger = logging.getLogger(__name__)

def compute_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute comprehensive descriptive and AQI statistics for a dataset."""
    if df is None or df.empty or "value" not in df.columns:
        return {}

    values = df["value"].dropna()
    dt_col = "datetime_utc" if "datetime_utc" in df.columns else None

    # Temporal range
    if dt_col:
        dt_series = pd.to_datetime(df[dt_col], utc=True, errors="coerce").dropna()
        start_date = str(dt_series.min().date()) if not dt_series.empty else "N/A"
        end_date = str(dt_series.max().date()) if not dt_series.empty else "N/A"
        duration_days = (dt_series.max() - dt_series.min()).days if not dt_series.empty else 0
    else:
        start_date, end_date, duration_days = "N/A", "N/A", 0

    # Descriptive stats
    stats = {
        "count": int(len(values)),
        "mean": float(values.mean()),
        "std": float(values.std()) if len(values) > 1 else 0.0,
        "median": float(values.median()),
        "min": float(values.min()),
        "max": float(values.max()),
        "p25": float(values.quantile(0.25)),
        "p75": float(values.quantile(0.75)),
        "skewness": float(values.skew()) if len(values) > 2 else 0.0,
        "kurtosis": float(values.kurtosis()) if len(values) > 3 else 0.0,
        "start_date": start_date,
        "end_date": end_date,
        "duration_days": duration_days,
    }

    # Primary pollutant detection
    pollutant = df["parameter"].iloc[0] if "parameter" in df.columns else "pm25"
    stats["pollutant"] = str(pollutant).lower()

    # WHO and NAAQS exceedance check
    # WHO 24h PM2.5 guideline: 15 µg/m³, NAAQS Indian standard: 60 µg/m³
    if "pm25" in stats["pollutant"]:
        stats["who_threshold"] = 15.0
        stats["naaqs_threshold"] = 60.0
        stats["who_exceedance_pct"] = float((values > 15.0).mean() * 100)
        stats["naaqs_exceedance_pct"] = float((values > 60.0).mean() * 100)
    elif "pm10" in stats["pollutant"]:
        stats["who_threshold"] = 45.0
        stats["naaqs_threshold"] = 100.0
        stats["who_exceedance_pct"] = float((values > 45.0).mean() * 100)
        stats["naaqs_exceedance_pct"] = float((values > 100.0).mean() * 100)
    else:
        stats["who_threshold"] = 0.0
        stats["naaqs_threshold"] = 0.0
        stats["who_exceedance_pct"] = 0.0
        stats["naaqs_exceedance_pct"] = 0.0

    # CPCB & US EPA AQI distributions
    cpcb_cats = []
    epa_cats = []
    for val in values:
        c_res = calculate_cpcb_aqi(val, stats["pollutant"])
        if c_res.get("category"):
            cpcb_cats.append(c_res["category"])
        e_res = calculate_us_epa_aqi(val, stats["pollutant"])
        if e_res.get("category"):
            epa_cats.append(e_res["category"])

    if cpcb_cats:
        cpcb_counts = pd.Series(cpcb_cats).value_counts(normalize=True) * 100
        stats["cpcb_distribution"] = cpcb_counts.round(1).to_dict()
    else:
        stats["cpcb_distribution"] = {}

    if epa_cats:
        epa_counts = pd.Series(epa_cats).value_counts(normalize=True) * 100
        stats["epa_distribution"] = epa_counts.round(1).to_dict()
    else:
        stats["epa_distribution"] = {}

    return stats

def generate_markdown_report(
    dataset_name: str,
    df: pd.DataFrame,
    metrics_df: Optional[pd.DataFrame] = None,
    dl_results: Optional[List[Dict[str, Any]]] = None,
    location_name: str = "Target Monitoring Station",
) -> str:
    """Generate a publication-grade academic research markdown report."""
    stats = compute_dataset_summary(df)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    pollutant = stats.get("pollutant", "PM2.5").upper()
    who_exc = stats.get("who_exceedance_pct", 0.0)
    naaqs_exc = stats.get("naaqs_exceedance_pct", 0.0)

    md = []
    md.append("# 🌬️ AeroSense AI — Research & Project Technical Report\n")
    md.append("- **Assigned Project Title**: Air Pollution Pattern Analysis and AQI Forecasting")
    md.append(f"- **Platform Title**: {settings.APP_TITLE}")
    md.append("- **Project Team (Batch 2023–2027, Sem 7, CSE-DS)**: Aryan Saini (23030173 / 2301315012), Ayaan Ali (23030175 / 2301315013), Kawalpreet Kaur (23030255 / 2301315019), Mihir Kumar (23030268 / 2301315022)")
    md.append("- **Faculty Assigned**: Mr. Abhishek Kumar (QU0125261068)")
    md.append(f"- **Generated**: {now_str}")
    md.append(f"- **Target Station / Region**: `{location_name}` | **Dataset**: `{dataset_name}`")
    md.append(f"- **System Version**: v{settings.APP_VERSION} | **Phase**: India-First Architecture\n")
    md.append("---")

    md.append("\n## 1. Executive Summary")
    md.append(
        f"This academic research report details the empirical analysis and predictive modeling of atmospheric "
        f"**{pollutant}** concentrations observed at **{location_name}**. A total of **{stats.get('count', 0):,}** "
        f"validated continuous monitoring records spanning from **{stats.get('start_date', 'N/A')}** to "
        f"**{stats.get('end_date', 'N/A')}** ({stats.get('duration_days', 0)} days) were synthesized through "
        f"the AeroSense AI pipeline. Environmental exposure metrics reveal that **{who_exc:.1f}%** of observation "
        f"periods breached the World Health Organization (WHO) 24-hour health guideline, while **{naaqs_exc:.1f}%** "
        f"exceeded Indian National Ambient Air Quality Standards (NAAQS)."
    )

    md.append("\n## 2. Descriptive & Environmental Statistics")
    md.append("| Metric | Observed Value | Unit / Standard Reference |")
    md.append("| :--- | :--- | :--- |")
    md.append(f"| Sample Count (N) | {stats.get('count', 0):,} | Validated observations |")
    md.append(f"| Arithmetic Mean | {stats.get('mean', 0.0):.2f} | µg/m³ |")
    md.append(f"| Standard Deviation (σ) | {stats.get('std', 0.0):.2f} | µg/m³ |")
    md.append(f"| Median (50th percentile) | {stats.get('median', 0.0):.2f} | µg/m³ |")
    md.append(f"| Interquartile Range (IQR) | {stats.get('p25', 0.0):.2f} - {stats.get('p75', 0.0):.2f} | 25th - 75th percentile |")
    md.append(f"| Absolute Range (Min - Max) | {stats.get('min', 0.0):.2f} - {stats.get('max', 0.0):.2f} | µg/m³ |")
    md.append(f"| Distribution Skewness | {stats.get('skewness', 0.0):.3f} | Pearson coefficient |")
    md.append(f"| Distribution Kurtosis | {stats.get('kurtosis', 0.0):.3f} | Excess kurtosis |")
    md.append(f"| WHO Guideline Breach Rate | {who_exc:.1f}% | Threshold: {stats.get('who_threshold', 15.0)} µg/m³ |")
    md.append(f"| NAAQS (CPCB) Breach Rate | {naaqs_exc:.1f}% | Threshold: {stats.get('naaqs_threshold', 60.0)} µg/m³ |")

    md.append("\n## 3. Air Quality Index (AQI) Categorical Distribution")
    md.append("### 3.1 CPCB National Air Quality Index (India)")
    cpcb_dist = stats.get("cpcb_distribution", {})
    if cpcb_dist:
        md.append("| CPCB Category | Proportion (%) | Health Description |")
        md.append("| :--- | :--- | :--- |")
        cpcb_desc = {
            "Good": "Minimal impact (0-50)",
            "Satisfactory": "Minor breathing discomfort to sensitive people (51-100)",
            "Moderate": "Breathing discomfort to people with lungs, asthma and heart diseases (101-200)",
            "Poor": "Breathing discomfort to most people on prolonged exposure (201-300)",
            "Very Poor": "Respiratory illness on prolonged exposure (301-400)",
            "Severe": "Affects healthy people and seriously impacts those with existing diseases (401-500)",
        }
        for cat, pct in cpcb_dist.items():
            desc = cpcb_desc.get(cat, "Standard threshold")
            md.append(f"| **{cat}** | {pct:.1f}% | {desc} |")
    else:
        md.append("_Insufficient data for CPCB categorical distribution._")

    md.append("\n### 3.2 US EPA Air Quality Index")
    epa_dist = stats.get("epa_distribution", {})
    if epa_dist:
        md.append("| US EPA Category | Proportion (%) |")
        md.append("| :--- | :--- |")
        for cat, pct in epa_dist.items():
            md.append(f"| {cat} | {pct:.1f}% |")
    else:
        md.append("_Insufficient data for US EPA distribution._")

    md.append("\n## 4. Machine Learning & Deep Learning Benchmarking")
    md.append(
        "Model training strictly enforced chronological time-series splitting (70% Train, 15% Validation, "
        "15% Held-Out Test) to avoid lookahead bias and temporal leakage. Performance metrics are evaluated "
        "exclusively on the test split."
    )

    if metrics_df is not None and not metrics_df.empty:
        md.append("\n### 4.1 Traditional Machine Learning Models")
        cols = [c for c in ["model", "test_MAE", "test_RMSE", "test_R2", "train_time_s"] if c in metrics_df.columns]
        md.append("| Model Architecture | Test MAE | Test RMSE | Test R² | Training Time (s) |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for _, row in metrics_df[cols].iterrows():
            mae = f"{row.get('test_MAE', 0.0):.3f}" if pd.notnull(row.get('test_MAE')) else "N/A"
            rmse = f"{row.get('test_RMSE', 0.0):.3f}" if pd.notnull(row.get('test_RMSE')) else "N/A"
            r2 = f"{row.get('test_R2', 0.0):.3f}" if pd.notnull(row.get('test_R2')) else "N/A"
            t = f"{row.get('train_time_s', 0.0):.2f}" if pd.notnull(row.get('train_time_s')) else "N/A"
            md.append(f"| **{row.get('model', 'Model')}** | {mae} | {rmse} | {r2} | {t}s |")

    if dl_results:
        md.append("\n### 4.2 Deep Learning Architectures (Sequence Modeling)")
        md.append("| Neural Architecture | Lookback Window | Forecast Horizon | Test MAE | Test RMSE | Test R² | Device |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for res in dl_results:
            m = res.get("metrics", {})
            name = res.get("model_name", "DL Model")
            lb = res.get("lookback", 24)
            hz = res.get("horizon", 24)
            dev = res.get("device", "cpu")
            md.append(
                f"| **{name}** | {lb} hours | {hz} hours | "
                f"{m.get('MAE', 0.0):.3f} | {m.get('RMSE', 0.0):.3f} | {m.get('R2', 0.0):.3f} | `{dev}` |"
            )

    md.append("\n## 5. Methodology & Scientific Validation")
    md.append(
        "1. **Data Ingestion**: Queried authenticated OpenAQ REST API v3 using ISO-8601 UTC timestamps.\n"
        "2. **Data Cleaning**: Non-negative thresholding, median absolute deviation (MAD) filtering, and forward-backward linear interpolation.\n"
        "3. **Feature Engineering**: Cyclical temporal encoding (sin/cos of hour, day-of-week, month), autoregressive lag sequences (1h, 2h, 3h, 6h, 12h, 24h, 48h, 72h), and rolling statistics (mean, std, min, max over 6h, 12h, 24h windows).\n"
        "4. **Model Validation**: Strict temporal order train-validation-test split. Baseline comparison against naive persistence, moving average, and 24h seasonal persistence.\n"
        "5. **Explainability**: SHAP (SHapley Additive exPlanations) TreeExplainer and Permutation Importance for interpretability."
    )

    md.append("\n## 6. Public Health Advisory & Action Plan")
    if who_exc > 75.0 or naaqs_exc > 50.0:
        md.append(
            "> ⚠️ **High Chronic Exposure Risk Detected**: The analyzed region displays sustained periods of hazardous "
            "pollutant levels exceeding public health thresholds. Vulnerable cohorts (pediatric, geriatric, and individuals "
            "with cardiopulmonary conditions) are advised to utilize certified N95/N99 respiratory protection outdoors and "
            "operate indoor HEPA air purification systems."
        )
    else:
        md.append(
            "> ℹ️ **Moderate Exposure Profile**: Pollutant concentrations remain largely within standard parameters, with occasional "
            "localized spikes. Standard ambient outdoor precautions apply during diurnal peak transit hours."
        )

    md.append("\n---\n*Report generated automatically by AeroSense AI Platform. Approved for B.Tech project submission and research review.*")
    return "\n".join(md)

def generate_html_report(
    dataset_name: str,
    df: pd.DataFrame,
    metrics_df: Optional[pd.DataFrame] = None,
    dl_results: Optional[List[Dict[str, Any]]] = None,
    location_name: str = "Target Monitoring Station",
) -> str:
    """Generate a responsive HTML report with modern dark styling and print stylesheet."""
    md_content = generate_markdown_report(dataset_name, df, metrics_df, dl_results, location_name)

    # Basic markdown to HTML table conversion
    import html

    html_lines = []
    in_table = False

    for line in md_content.split("\n"):
        line = line.strip()
        if not line:
            if in_table:
                html_lines.append("</table></div>")
                in_table = False
            html_lines.append("<br>")
            continue

        if line.startswith("# "):
            html_lines.append(f"<h1 class='title'>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2 class='section-title'>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3 class='sub-title'>{html.escape(line[4:])}</h3>")
        elif line.startswith("> "):
            html_lines.append(f"<div class='callout'>{html.escape(line[2:])}</div>")
        elif line.startswith("|") and line.endswith("|"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if all(set(p).issubset({"-", ":", " "}) for p in parts):
                continue  # table separator row
            if not in_table:
                in_table = True
                html_lines.append("<div class='table-container'><table>")
                html_lines.append("<tr>" + "".join(f"<th>{html.escape(p)}</th>" for p in parts) + "</tr>")
            else:
                html_lines.append("<tr>" + "".join(f"<td>{html.escape(p)}</td>" for p in parts) + "</tr>")
        else:
            if in_table:
                html_lines.append("</table></div>")
                in_table = False
            html_lines.append(f"<p>{html.escape(line)}</p>")

    if in_table:
        html_lines.append("</table></div>")

    body_content = "\n".join(html_lines)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AeroSense AI — Technical Report ({html.escape(dataset_name)})</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1F2937;
    background-color: #F9FAFB;
    margin: 0;
    padding: 2.5rem;
  }}
  .container {{
    max-width: 900px;
    margin: 0 auto;
    background: #FFFFFF;
    padding: 3rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  }}
  .title {{
    color: #0F172A;
    font-size: 2rem;
    font-weight: 800;
    border-bottom: 3px solid #0284C7;
    padding-bottom: 0.75rem;
    margin-bottom: 1.5rem;
  }}
  .section-title {{
    color: #0369A1;
    font-size: 1.35rem;
    margin-top: 2rem;
    margin-bottom: 0.75rem;
    border-left: 4px solid #0284C7;
    padding-left: 0.75rem;
  }}
  .sub-title {{
    color: #334155;
    font-size: 1.1rem;
    margin-top: 1.25rem;
  }}
  .table-container {{
    overflow-x: auto;
    margin: 1.25rem 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1.5rem;
    font-size: 0.92rem;
  }}
  th, td {{
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid #E2E8F0;
  }}
  th {{
    background-color: #F1F5F9;
    color: #0F172A;
    font-weight: 600;
  }}
  tr:hover {{
    background-color: #F8FAFC;
  }}
  .callout {{
    background-color: #EFF6FF;
    border-left: 4px solid #2563EB;
    padding: 1rem 1.25rem;
    border-radius: 4px;
    margin: 1.5rem 0;
    color: #1E40AF;
    font-size: 0.95rem;
  }}
  @media print {{
    body {{ background: white; padding: 0; }}
    .container {{ box-shadow: none; padding: 0; max-width: 100%; }}
  }}
</style>
</head>
<body>
<div class="container">
{body_content}
</div>
</body>
</html>
"""
    return html_doc

def generate_pdf_report(
    dataset_name: str,
    df: pd.DataFrame,
    output_path: Path,
    metrics_df: Optional[pd.DataFrame] = None,
    dl_results: Optional[List[Dict[str, Any]]] = None,
    location_name: str = "Target Monitoring Station",
) -> Path:
    """Generate a clean PDF report using ReportLab with table formatting."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0369A1"),
        spaceAfter=10,
    )
    h2_style = ParagraphStyle(
        "ReportH2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )

    elements = []
    stats = compute_dataset_summary(df)

    # Title & Header
    elements.append(Paragraph(f"AeroSense AI — Technical Research Report", title_style))
    elements.append(
        Paragraph(
            "<b>Assigned Project Title</b>: Air Pollution Pattern Analysis and AQI Forecasting | "
            "<b>Faculty Guide</b>: Mr. Abhishek Kumar (QU0125261068)<br/>"
            "<b>Team (Batch 2023-2027, Sem 7, CSE-DS)</b>: Aryan Saini (23030173/2301315012), "
            "Ayaan Ali (23030175/2301315013), Kawalpreet Kaur (23030255/2301315019), "
            "Mihir Kumar (23030268/2301315022)<br/>"
            f"<b>Location</b>: {location_name} | <b>Dataset</b>: {dataset_name} | "
            f"<b>Date</b>: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            body_style,
        )
    )
    elements.append(Spacer(1, 10))

    # Summary
    elements.append(Paragraph("1. Executive Summary", h2_style))
    pollutant = stats.get("pollutant", "PM2.5").upper()
    who_exc = stats.get("who_exceedance_pct", 0.0)
    naaqs_exc = stats.get("naaqs_exceedance_pct", 0.0)
    summary_text = (
        f"This empirical report summarizes continuous ambient air quality observations for <b>{pollutant}</b> "
        f"over {stats.get('duration_days', 0)} days ({stats.get('count', 0):,} records). "
        f"Ambient concentrations breached WHO 24-hr guidelines during {who_exc:.1f}% of observed periods and "
        f"exceeded Indian NAAQS standards during {naaqs_exc:.1f}% of periods."
    )
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 10))

    # Descriptive Stats Table
    elements.append(Paragraph("2. Descriptive Statistics", h2_style))
    table_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["Total Records", f"{stats.get('count', 0):,}", "Mean", f"{stats.get('mean', 0.0):.2f} µg/m³"],
        ["Standard Dev", f"{stats.get('std', 0.0):.2f} µg/m³", "Median", f"{stats.get('median', 0.0):.2f} µg/m³"],
        ["Minimum", f"{stats.get('min', 0.0):.2f} µg/m³", "Maximum", f"{stats.get('max', 0.0):.2f} µg/m³"],
        ["WHO Breach %", f"{who_exc:.1f}%", "NAAQS Breach %", f"{naaqs_exc:.1f}%"],
    ]
    t = Table(table_data, colWidths=[130, 130, 130, 130])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 10))

    # Models Table if available
    if metrics_df is not None and not metrics_df.empty:
        elements.append(Paragraph("3. Model Benchmarking (Held-out Test Split)", h2_style))
        ml_data = [["Model", "Test MAE", "Test RMSE", "Test R²", "Time (s)"]]
        for _, r in metrics_df.iterrows():
            ml_data.append(
                [
                    str(r.get("model", "")),
                    f"{r.get('test_MAE', 0.0):.3f}",
                    f"{r.get('test_RMSE', 0.0):.3f}",
                    f"{r.get('test_R2', 0.0):.3f}",
                    f"{r.get('train_time_s', 0.0):.2f}",
                ]
            )
        t_ml = Table(ml_data, colWidths=[150, 90, 90, 90, 90])
        t_ml.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0284C7")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ]
            )
        )
        elements.append(t_ml)

    doc.build(elements)
    logger.info(f"PDF report successfully built at: {output_path}")
    return output_path

def create_export_archive(
    dataset_name: str,
    df: pd.DataFrame,
    metrics_df: Optional[pd.DataFrame] = None,
    output_zip_path: Optional[Path] = None,
) -> Path:
    """Bundle data, report, and metrics into a compressed ZIP file."""
    if output_zip_path is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_zip_path = settings.DATA_DIR / "exports" / f"AeroSense_{dataset_name}_{timestamp}.zip"

    output_zip_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Write dataset CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        zipf.writestr(f"{dataset_name}_data.csv", csv_buffer.getvalue())

        # Write markdown report
        md_text = generate_markdown_report(dataset_name, df, metrics_df=metrics_df)
        zipf.writestr(f"RESEARCH_REPORT_{dataset_name}.md", md_text)

        # Write HTML report
        html_text = generate_html_report(dataset_name, df, metrics_df=metrics_df)
        zipf.writestr(f"RESEARCH_REPORT_{dataset_name}.html", html_text)

        # Write metrics CSV if provided
        if metrics_df is not None and not metrics_df.empty:
            m_buf = io.StringIO()
            metrics_df.to_csv(m_buf, index=False)
            zipf.writestr("model_benchmarking_metrics.csv", m_buf.getvalue())

    logger.info(f"Complete export archive created: {output_zip_path}")
    return output_zip_path
