"""
AeroSense AI — Complete Submission Deliverable Builder
Generates publication-grade academic deliverables in reports/:
  1. AeroSense_Project_Synopsis.pdf & .md
  2. AeroSense_Research_Paper.pdf & .md
  3. AeroSense_Final_Project_Report.pdf & .md
  4. AeroSense_Presentation.pptx (16-slide widescreen deck with embedded real charts)

Includes structured placeholders for all 4 project group members, supervisor, and institute.
"""
from __future__ import annotations

import html
from pathlib import Path
from typing import List, Tuple

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from src.config import settings

REPORTS_DIR = settings.REPORTS_DIR
FIG_DIR = REPORTS_DIR / "figures"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Shared Team & Faculty Metadata
TEAM_MEMBERS = [
    ["Aryan Saini", "ID: 23030173 | Roll: 2301315012", "2023 - 2027 | Sem 7 | CSE-DS", "Data Engineering, OpenAQ v3 API & Parquet Pipeline"],
    ["Ayaan Ali", "ID: 23030175 | Roll: 2301315013", "2023 - 2027 | Sem 7 | CSE-DS", "Feature Synthesis, CPCB/EPA AQI Engine & Baselines"],
    ["Kawalpreet Kaur", "ID: 23030255 | Roll: 2301315019", "2023 - 2027 | Sem 7 | CSE-DS", "ML/DL Model Architectures, Training & Benchmarking"],
    ["Mihir Kumar", "ID: 23030268 | Roll: 2301315022", "2023 - 2027 | Sem 7 | CSE-DS", "SHAP Explainability, 10-Page Streamlit UI & Reporting"],
]

INSTITUTE_META = {
    "project_title": "Air Pollution Pattern Analysis and AQI Forecasting (AeroSense AI: Global Air Pollution Pattern Analysis and AQI Forecasting Using Machine Learning and Deep Learning)",
    "short_project_title": "Air Pollution Pattern Analysis and AQI Forecasting",
    "app_name": "AeroSense AI",
    "tagline": "Understand Pollution. Predict Tomorrow. Build a Cleaner Future.",
    "degree": "B.Tech in Computer Science & Engineering (Data Science) [CSE-DS] — Semester 7",
    "department": "Department of Computer Science and Engineering (CSE-DS)",
    "institute": "Quantum School of Technology, Quantum University",
    "city_state": "Roorkee - 247167, Uttarakhand, India",
    "session": "Batch 2023 - 2027 | 7th Sem (Session: 2026-27)",
    "guide": "Mr. Abhishek Kumar (QU0125261068)",
    "hod": "HoD, CSE & Dean Academics, Quantum University",
}

# ReportLab Styling Helpers
def _build_styles():
    base = getSampleStyleSheet()
    styles = {
        "TitleHero": ParagraphStyle(
            "TitleHero", parent=base["Title"], fontName="Helvetica-Bold", fontSize=20,
            leading=25, textColor=colors.HexColor("#0F172A"), alignment=TA_CENTER, spaceAfter=10
        ),
        "SubHero": ParagraphStyle(
            "SubHero", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=11,
            leading=15, textColor=colors.HexColor("#0284C7"), alignment=TA_CENTER, spaceAfter=14
        ),
        "H1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=14,
            leading=18, textColor=colors.HexColor("#0369A1"), spaceBefore=14, spaceAfter=6,
            keepWithNext=True
        ),
        "H2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
            leading=15, textColor=colors.HexColor("#0F172A"), spaceBefore=10, spaceAfter=4,
            keepWithNext=True
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["Normal"], fontName="Helvetica", fontSize=9.8,
            leading=14, textColor=colors.HexColor("#1E293B"), alignment=TA_JUSTIFY, spaceAfter=6
        ),
        "Bullet": ParagraphStyle(
            "Bullet", parent=base["Normal"], fontName="Helvetica", fontSize=9.5,
            leading=13.5, textColor=colors.HexColor("#1E293B"), leftIndent=14, spaceAfter=3
        ),
        "Caption": ParagraphStyle(
            "Caption", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=8.5,
            leading=11, textColor=colors.HexColor("#475569"), alignment=TA_CENTER, spaceBefore=3, spaceAfter=10
        ),
        "CenterBold": ParagraphStyle(
            "CenterBold", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10.5,
            leading=14, textColor=colors.HexColor("#0F172A"), alignment=TA_CENTER, spaceAfter=6
        ),
        "Center": ParagraphStyle(
            "Center", parent=base["Normal"], fontName="Helvetica", fontSize=9.8,
            leading=14, textColor=colors.HexColor("#334155"), alignment=TA_CENTER, spaceAfter=4
        ),
        "Formula": ParagraphStyle(
            "Formula", parent=base["Normal"], fontName="Courier-Bold", fontSize=9,
            leading=13, textColor=colors.HexColor("#0F172A"), alignment=TA_CENTER,
            backColor=colors.HexColor("#F1F5F9"), spaceBefore=4, spaceAfter=6
        ),
    }
    return styles

def _styled_table(data: List[List[str]], col_widths: List[float], header_bg: str = "#0369A1") -> Table:
    cell_style = ParagraphStyle("TCell", fontName="Helvetica", fontSize=8.3, leading=11, textColor=colors.HexColor("#0F172A"))
    head_style = ParagraphStyle("THead", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white)
    wrapped = []
    for r_idx, row in enumerate(data):
        st = head_style if r_idx == 0 else cell_style
        wrapped.append([Paragraph(html.escape(str(c)), st) for c in row])

    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t

def _add_figure(elements: list, fig_name: str, caption: str, styles: dict, width_in: float = 6.3):
    p = FIG_DIR / fig_name
    if not p.exists():
        return
    from PIL import Image as PILImage
    with PILImage.open(p) as im:
        w, h = im.size
    aspect = h / float(w)
    img = Image(str(p), width=width_in * inch, height=width_in * aspect * inch)
    elements.append(Spacer(1, 4))
    elements.append(img)
    elements.append(Paragraph(caption, styles["Caption"]))

def _footer_canvas(title_short: str):
    def _draw(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(0.7 * inch, 0.45 * inch, title_short)
        canvas.drawRightString(A4[0] - 0.7 * inch, 0.45 * inch, f"Page {doc.page}")
        canvas.restoreState()
    return _draw

# 1. PROJECT SYNOPSIS (PDF + MD — Quantum University Format)
def build_synopsis():
    from src.reporting.synopsis_builder import build_qu_synopsis
    return build_qu_synopsis(TEAM_MEMBERS, INSTITUTE_META)

# 2. IEEE-STYLE RESEARCH PAPER (PDF + MD)
def build_research_paper():
    styles = _build_styles()
    pdf_path = REPORTS_DIR / "AeroSense_Research_Paper.pdf"
    md_path = REPORTS_DIR / "AeroSense_Research_Paper.md"

    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4,
        leftMargin=0.65 * inch, rightMargin=0.65 * inch,
        topMargin=0.65 * inch, bottomMargin=0.65 * inch,
    )
    el = []

    el.append(Paragraph("RESEARCH MANUSCRIPT (IEEE TECHNICAL FORMAT)", styles["SubHero"]))
    el.append(Paragraph(
        "AeroSense AI: Leakage-Free Machine Learning, Deep Sequence Modeling, and Explainable Air Quality Forecasting Using Real-Time OpenAQ v3 Telemetry",
        styles["TitleHero"]
    ))
    el.append(Paragraph(
        "<b>Aryan Saini</b><sup>1</sup>, <b>Ayaan Ali</b><sup>1</sup>, <b>Kawalpreet Kaur</b><sup>1</sup>, <b>Mihir Kumar</b><sup>1</sup>, and <b>Mr. Abhishek Kumar</b><sup>1</sup><br/>"
        "<i><sup>1</sup>Department of Computer Science &amp; Engineering (Data Science) [CSE-DS], Batch 2023 - 2027, Semester 7</i><br/>"
        "<i>Student IDs / Roll Nos.: 23030173 / 2301315012, 23030175 / 2301315013, 23030255 / 2301315019, 23030268 / 2301315022 | Faculty Guide ID: QU0125261068</i>",
        styles["Center"]
    ))
    el.append(Spacer(1, 8))

    el.append(Paragraph(
        "<b><i>Abstract</i>—Rapid urbanization across South Asia has intensified acute fine particulate matter (PM2.5) episodes, necessitating accurate short-term forecasting and transparent regulatory Air Quality Index (AQI) analytics. Many empirical forecasting studies suffer from temporal data leakage via shuffled cross-validation and fail to disclose sensor gaps when computing composite AQI indices. This paper presents AeroSense AI, an open, modular ML/DL engineering platform combining OpenAQ API v3 data acquisition, bounded physical cleaning, dual Indian CPCB and US EPA AQI calculators, 34 engineered temporal/lag/rolling features, and strict chronological (70%/15%/15%) benchmarking across 3 naive baselines, 6 tabular ML algorithms, and 4 PyTorch deep learning architectures (LSTM, GRU, Temporal Convolutional Network, and Encoder-only Transformer). Experiments on live 30-day Indian telemetry (Delhi R K Puram, Lucknow Talkatora, Hyderabad Zoo Park; 2,157 records) reveal WHO 24-hour exceedance rates of 92.2%–98.6%. Under strict chronological testing, autoregressive linear regressors (MAE = 23.803 µg/m³, R² = 0.854 on live Delhi R K Puram; MAE = 9.449 µg/m³, R² = 0.906 on 90-day calibration data) and self-attention Transformers (MAE = 9.580 µg/m³, R² = 0.903) significantly outperform seasonal naive baselines (55.515 and 30.966 µg/m³ MAE). Notably, tree ensembles degrade under autumn-to-winter distributional shift due to bounded leaf extrapolation, highlighting critical architectural trade-offs validated by TreeSHAP attribution (lag_1 mean |SHAP| = 26.91 µg/m³).</b>",
        styles["Body"]
    ))
    el.append(Paragraph("<b><i>Index Terms</i>—Air Quality Forecasting, PM2.5, OpenAQ API v3, Chronological Validation, Deep Sequence Modeling, SHAP Explainability, CPCB AQI.</b>", styles["Body"]))

    el.append(Paragraph("I. INTRODUCTION", styles["H1"]))
    el.append(Paragraph(
        "Fine particulate matter (PM2.5, aerodynamic diameter ≤ 2.5 µm) penetrates deep into human alveolar tissues and systemic circulation, elevating cardiopulmonary mortality. Across the Indo-Gangetic Plain (IGP), nocturnal boundary-layer inversions, regional biomass burning, and vehicular emissions produce extreme diurnal and seasonal swings. While open telemetry networks such as OpenAQ aggregate regulatory ground monitors worldwide, transforming raw sensor streams into reproducible forecasts requires rigorous engineering: handling OpenAQ v3 sensor-level pagination, auditing out-of-range spikes, avoiding lookahead bias in feature generation, and reporting AQI completeness honestly.",
        styles["Body"]
    ))

    el.append(Paragraph("II. RELATED WORK & IDENTIFIED GAPS", styles["H1"]))
    el.append(Paragraph(
        "Prior air quality modeling literature utilizes ARIMA, Random Forests, XGBoost, and recurrent neural networks (LSTM/GRU). However, three methodological weaknesses persist across applied student and academic implementations: (1) randomized k-fold or train_test_split partitioning that leaks temporally adjacent autocorrelated readings from future hours into training batches; (2) computing rolling statistics over unshifted target series; and (3) reporting CPCB/EPA AQI as complete even when gaseous sensors (SO2, CO, O3) are offline. AeroSense AI eliminates all three defects structurally.",
        styles["Body"]
    ))

    el.append(Paragraph("III. DATA ACQUISITION & PREPROCESSING PIPELINE", styles["H1"]))
    el.append(Paragraph(
        "Live observations are queried via an authenticated OpenAQ API v3 client (X-API-Key) targeting /v3/locations (filtered by ISO code and parameters_id) and /v3/sensors/{id}/hours with UTC ISO-8601 datetime_from/datetime_to bounds. Validation enforces non-negative sensor thresholds (PM2.5 ∈ [0, 1000] µg/m³) and station-timestamp deduplication. Cleaning applies per-station IQR × 3 outlier removal and hourly resampling with bounded linear time interpolation (limit = 6 hours), recording an explicit is_imputed boolean mask while preserving static coordinates and provenance metadata.",
        styles["Body"]
    ))

    live_tbl = [
        ["Live OpenAQ v3 Station (Oct-Nov 2026)", "Valid Hours", "Mean ± Std (µg/m³)", "Min - Max", "WHO Breach (>15)", "NAAQS Breach (>60)"],
        ["R K Puram, Delhi - DPCC (ID: 17)", "639", "177.81 ± 95.74", "1.00 - 501.00", "98.6%", "92.3%"],
        ["Talkatora, Lucknow - CPCB (ID: 407)", "641", "85.64 ± 50.82", "4.34 - 265.00", "92.2%", "68.3%"],
        ["Zoo Park, Hyderabad - TSPCB (ID: 2456)", "627", "52.71 ± 19.43", "9.50 - 87.00", "97.4%", "36.0%"],
    ]
    el.append(_styled_table(live_tbl, [2.05 * inch, 0.72 * inch, 1.15 * inch, 0.95 * inch, 1.0 * inch, 1.03 * inch]))
    el.append(Spacer(1, 6))
    _add_figure(el, "fig1_live_station_profiles.png", "Fig. 1. Live OpenAQ v3 Indian station daily trends (A) and IST diurnal boundary-layer profiles (B).", styles, width_in=6.5)

    el.append(Paragraph("IV. METHODOLOGY & MATHEMATICAL FORMULATION", styles["H1"]))
    el.append(Paragraph(
        "A. Dual-Standard AQI Computation: For each criteria pollutant p, sub-index I_p is computed via piecewise-linear interpolation between regulatory breakpoints [BP_lo, BP_hi] and AQI bounds [I_lo, I_hi], assigning AQI = max_p(I_p) alongside an explicit is_complete boolean.",
        styles["Body"]
    ))
    el.append(Paragraph("I_p = round( ((I_hi - I_lo) / (BP_hi - BP_lo)) * (C_p - BP_lo) + I_lo )", styles["Formula"]))
    el.append(Paragraph(
        "B. Leakage-Free Feature Engineering: Calendar periodicities are projected onto orthogonal trigonometric harmonics: hour_sin = sin(2π·h/24), hour_cos = cos(2π·h/24), and similarly for day-of-week (period 7) and month (period 12). Autoregressive lags (1, 3, 6, 12, 24 h), shifted rolling aggregations (mean, std, min, max over 3, 6, 12, 24 h computed strictly on y_{t-1}), and momentum trend_24 = y_{t-1} - y_{t-24} form the tabular design matrix.",
        styles["Body"]
    ))
    el.append(Paragraph(
        "C. Deep Sequence Architectures: Univariate MinMax-scaled sliding windows X ∈ R^(N × 24 × 1) feed four PyTorch architectures trained under Adam (lr=0.001), MSE loss, gradient clipping (max norm 1.0), ReduceLROnPlateau, and early stopping: (1) 2-layer LSTM (hidden=64), (2) 2-layer GRU (hidden=64), (3) 4-level dilated causal TCN (dilation=2^i, kernel=3, BatchNorm + Dropout=0.2), and (4) Encoder-only Transformer (d_model=64, 4 attention heads, 2 encoder layers with learned positional embeddings).",
        styles["Body"]
    ))

    el.append(Paragraph("V. EXPERIMENTAL RESULTS & EMPIRICAL ANALYSIS", styles["H1"]))
    el.append(Paragraph(
        "All experiments strictly enforce chronological 70% Train / 15% Validation / 15% Held-Out Test partitioning. Table II reports controlled 90-day hourly benchmark evaluations (Delhi Anand Vihar, n=2,161) comparing 3 baselines, 6 ML algorithms, and 4 PyTorch DL models at 1-hour horizon alongside 24-hour multi-step LSTM.",
        styles["Body"]
    ))

    bench_tbl = [
        ["Model", "Category / Horizon", "Test MAE (µg/m³)", "Test RMSE (µg/m³)", "Test R²", "Train Time"],
        ["LinearRegression", "ML Tabular (h=1)", "9.449", "11.947", "0.906", "0.03s"],
        ["Ridge (alpha=1.0)", "ML Tabular (h=1)", "9.457", "11.948", "0.906", "0.00s"],
        ["Transformer (PyTorch)", "DL Attention (h=1)", "9.580", "12.124", "0.903", "12.3s"],
        ["RandomForest", "ML Ensemble (h=1)", "9.930", "12.402", "0.898", "0.26s"],
        ["HistGradientBoosting", "ML Boosting (h=1)", "10.149", "12.534", "0.896", "5.75s"],
        ["GRU (PyTorch)", "DL Recurrent (h=1)", "10.161", "12.976", "0.889", "9.3s"],
        ["XGBoost", "ML Boosting (h=1)", "10.319", "13.023", "0.888", "3.82s"],
        ["ExtraTrees", "ML Ensemble (h=1)", "10.575", "13.139", "0.886", "0.15s"],
        ["LSTM (PyTorch)", "DL Recurrent (h=1)", "10.838", "13.579", "0.878", "4.2s"],
        ["TCN (PyTorch)", "DL Causal Conv (h=1)", "11.851", "14.653", "0.858", "4.4s"],
        ["Seasonal Naive (24h)", "Baseline", "30.966", "38.726", "0.008", "—"],
        ["Historical Mean", "Baseline", "32.139", "39.182", "-0.016", "—"],
        ["Persistence", "Baseline", "40.117", "49.392", "-0.614", "—"],
        ["LSTM Multi-Step (h=24)", "DL Direct 24h", "30.288", "37.029", "0.094", "9.0s"],
    ]
    el.append(_styled_table(bench_tbl, [1.55 * inch, 1.35 * inch, 1.05 * inch, 1.1 * inch, 0.85 * inch, 0.9 * inch]))
    el.append(Spacer(1, 6))
    _add_figure(el, "fig2_model_benchmark.png", "Fig. 2. Controlled 1-step chronological test comparison across traditional ML and PyTorch DL architectures.", styles, width_in=6.5)

    el.append(Paragraph(
        "Live Telemetry Benchmark & Non-Stationarity Finding: Evaluated on live OpenAQ R K Puram (n=639, Oct-Nov 2026), LinearRegression achieved MAE = 23.803 µg/m³ (R² = 0.854) and Ridge achieved 24.714 µg/m³ (R² = 0.839), whereas RandomForest (26.534 MAE, R² = 0.802), HistGradientBoosting (32.799 MAE, R² = 0.744), and XGBoost (33.479 MAE, R² = 0.714) suffered higher error during November peak smog excursions (up to 501.0 µg/m³). Because axis-aligned decision trees predict piecewise-constant leaf averages bounded by max(y_train), they cannot extrapolate linearly beyond training peaks under acute seasonal regime shifts, whereas linear/ridge regressors extrapolate smoothly along lag_1 and trend_24.",
        styles["Body"]
    ))
    _add_figure(el, "fig3_forecast_residuals.png", "Fig. 3. Chronological test split forecast trajectory (A) and residual distribution (B).", styles, width_in=6.5)

    el.append(Paragraph("VI. EXPLAINABLE AI & PUBLIC HEALTH IMPLICATIONS", styles["H1"]))
    el.append(Paragraph(
        "TreeSHAP attribution on the held-out test set identifies immediate persistence lag_1 (mean |SHAP| = 26.91 µg/m³) as the primary predictive driver, followed by diurnal boundary-layer phase hour_sin (2.58 µg/m³), hour (2.09 µg/m³), and 24-hour momentum trend_24 (1.39 µg/m³). Concurrently, live CPCB compliance auditing reveals 24.3% Very Poor and 6.8% Severe hourly conditions across the monitored Indian stations.",
        styles["Body"]
    ))
    _add_figure(el, "fig4_shap_importance.png", "Fig. 4. Top-10 Mean |SHAP| feature attributions explaining PM2.5 test predictions.", styles, width_in=5.8)
    _add_figure(el, "fig5_aqi_exceedance.png", "Fig. 5. Live CPCB AQI categorical breakdown (A) and WHO vs. Indian NAAQS breach rates (B).", styles, width_in=6.5)

    el.append(Paragraph("VII. CONCLUSION & FUTURE WORK", styles["H1"]))
    el.append(Paragraph(
        "AeroSense AI establishes a reproducible, rigorously tested (41/41 pytest pass rate) framework bridging raw OpenAQ v3 streams and explainable air quality forecasting. Future Phase 2 expansion will integrate ECMWF ERA5 meteorological reanalysis (planetary boundary-layer height, wind vectors, relative humidity) and spatial Graph Neural Networks (ST-GNNs) across global cities.",
        styles["Body"]
    ))

    el.append(Paragraph("REFERENCES", styles["H1"]))
    refs = [
        "[1] Central Pollution Control Board (CPCB), 'National Air Quality Index,' Ministry of Environment, Forest & Climate Change, Govt. of India, 2014.",
        "[2] U.S. EPA, 'Technical Assistance Document for the Reporting of Daily Air Quality — the Air Quality Index (AQI),' EPA-454/B-18-007, 2018.",
        "[3] World Health Organization, 'WHO Global Air Quality Guidelines: Particulate Matter, Ozone, Nitrogen Dioxide, Sulfur Dioxide and Carbon Monoxide,' 2021.",
        "[4] S. Hochreiter and J. Schmidhuber, 'Long Short-Term Memory,' Neural Computation, vol. 9, no. 8, pp. 1735-1780, 1997.",
        "[5] S. Bai, J. Z. Kolter, and V. Koltun, 'An Empirical Evaluation of Generic Convolutional and Recurrent Networks for Sequence Modeling,' arXiv:1803.01271, 2018.",
        "[6] A. Vaswani et al., 'Attention Is All You Need,' Advances in Neural Information Processing Systems (NeurIPS), 2017.",
        "[7] S. M. Lundberg and S.-I. Lee, 'A Unified Approach to Interpreting Model Predictions,' NeurIPS, 2017.",
        "[8] OpenAQ API v3 Documentation, https://docs.openaq.org/, Accessed Nov. 2026.",
    ]
    for r in refs:
        el.append(Paragraph(r, styles["Bullet"]))

    doc.build(el, onFirstPage=_footer_canvas("AeroSense AI — IEEE Research Manuscript"), onLaterPages=_footer_canvas("AeroSense AI — IEEE Research Manuscript"))

    md_text = f"""# AeroSense AI: Leakage-Free Machine Learning, Deep Sequence Modeling, and Explainable Air Quality Forecasting Using Real-Time OpenAQ v3 Telemetry

**Authors:** Aryan Saini (ID: 23030173, Roll: 2301315012), Ayaan Ali (ID: 23030175, Roll: 2301315013), Kawalpreet Kaur (ID: 23030255, Roll: 2301315019), Mihir Kumar (ID: 23030268, Roll: 2301315022) | **Faculty Guide:** Mr. Abhishek Kumar (QU0125261068)  
**Affiliation:** {INSTITUTE_META['department']} | **Batch / Sem:** {INSTITUTE_META['session']}

---

## Abstract
AeroSense AI unifies OpenAQ v3 live ingestion, bounded data validation/imputation, dual Indian CPCB & US EPA AQI transparency, 34 engineered time-series features, strict chronological (70/15/15) benchmarking across 3 naive baselines, 6 ML algorithms, and 4 PyTorch deep learning architectures (LSTM, GRU, TCN, Transformer), plus SHAP interpretability. Live 30-day Indian telemetry (`n = 2,157` rows across Delhi R K Puram, Lucknow Talkatora, Hyderabad Zoo Park) documents WHO exceedance rates of `92.2%–98.6%`. Chronological testing achieves `9.449 µg/m³` MAE (`R² = 0.906`) for LinearRegression and `9.580 µg/m³` (`R² = 0.903`) for Transformer on controlled data, and `23.803 µg/m³` MAE (`R² = 0.854`, 57.1% improvement over Seasonal Naive) on live Delhi R K Puram measurements.

## Observed Live OpenAQ v3 Station Statistics (Oct–Nov 2026)
| Station | Valid Hours | Mean ± Std (µg/m³) | Min - Max | WHO Breach (>15) | NAAQS Breach (>60) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| R K Puram, Delhi - DPCC | 639 | 177.81 ± 95.74 | 1.00 - 501.00 | 98.6% | 92.3% |
| Talkatora, Lucknow - CPCB | 641 | 85.64 ± 50.82 | 4.34 - 265.00 | 92.2% | 68.3% |
| Zoo Park, Hyderabad - TSPCB | 627 | 52.71 ± 19.43 | 9.50 - 87.00 | 97.4% | 36.0% |

## Controlled Benchmark Comparison (90-Day Delhi Anand Vihar, n=2,161)
- **Top ML (1-step)**: `LinearRegression` (`MAE=9.449`, `RMSE=11.947`, `R²=0.906`), `Ridge` (`9.457`, `0.906`), `RandomForest` (`9.930`, `0.898`), `HistGradientBoosting` (`10.149`, `0.896`), `XGBoost` (`10.319`, `0.888`), `ExtraTrees` (`10.575`, `0.886`).
- **PyTorch DL (1-step)**: `Transformer` (`MAE=9.580`, `RMSE=12.124`, `R²=0.903`), `GRU` (`10.161`, `0.889`), `LSTM` (`10.838`, `0.878`), `TCN` (`11.851`, `0.858`).
- **PyTorch DL (24-step Multi-Horizon)**: `LSTM` (`MAE=30.288`, `RMSE=37.029`, `R²=0.094`).
- **Baselines**: `Seasonal Naive` (`30.966`, `R²=0.008`), `Historical Mean` (`32.139`, `R²=-0.016`), `Persistence` (`40.117`, `R²=-0.614`).

## Live Delhi R K Puram Evaluation (n=639)
- **LinearRegression**: `MAE=23.803`, `RMSE=30.540`, `R²=0.854`
- **Ridge**: `MAE=24.714`, `RMSE=32.074`, `R²=0.839`
- **RandomForest**: `MAE=26.534`, `RMSE=35.573`, `R²=0.802`
- **Seasonal Naive Baseline**: `MAE=55.515`, `RMSE=71.767`, `R²=0.165`

![Live Stations](figures/fig1_live_station_profiles.png)
![Model Benchmark](figures/fig2_model_benchmark.png)
![Forecast Residuals](figures/fig3_forecast_residuals.png)
![SHAP Attribution](figures/fig4_shap_importance.png)
![AQI Exceedance](figures/fig5_aqi_exceedance.png)
"""
    md_path.write_text(md_text, encoding="utf-8")
    return pdf_path, md_path

# 3. COMPLETE FINAL-YEAR B.TECH PROJECT REPORT (PDF + MD)
def build_project_report():
    from src.reporting.detailed_project_report import build_detailed_project_report
    return build_detailed_project_report(
        styles=_build_styles(),
        team_members=TEAM_MEMBERS,
        meta=INSTITUTE_META,
        styled_table=_styled_table,
        add_figure=_add_figure,
        footer_canvas=_footer_canvas,
    )

# 4. POWERPOINT PRESENTATION (16-SLIDE WIDESCREEN PPTX)
def build_presentation():
    pptx_path = REPORTS_DIR / "AeroSense_Presentation.pptx"
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # Palette
    DARK_BG = RGBColor(13, 17, 23)
    LIGHT_BG = RGBColor(248, 250, 252)
    CYAN = RGBColor(0, 212, 255)
    BLUE = RGBColor(2, 132, 199)
    VIOLET = RGBColor(124, 58, 237)
    NAVY = RGBColor(15, 23, 42)
    SLATE = RGBColor(51, 65, 85)
    MUTED = RGBColor(148, 163, 184)
    WHITE = RGBColor(255, 255, 255)
    CARD_DARK = RGBColor(22, 27, 34)
    BORDER = RGBColor(203, 213, 225)

    def _set_bg(slide, color):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = color

    def _add_header(slide, title: str, subtitle: str, page_num: int):
        _set_bg(slide, LIGHT_BG)
        # Top dark bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.05))
        bar.fill.solid()
        bar.fill.fore_color.rgb = DARK_BG
        bar.line.fill.background()

        # Cyan accent strip
        acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.05), Inches(13.333), Inches(0.06))
        acc.fill.solid()
        acc.fill.fore_color.rgb = CYAN
        acc.line.fill.background()

        tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.14), Inches(11.5), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = "Calibri"
        p1.font.size = Pt(24)
        p1.font.bold = True
        p1.font.color.rgb = WHITE
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.name = "Calibri"
        p2.font.size = Pt(12.5)
        p2.font.color.rgb = CYAN

        # Footer
        ft = slide.shapes.add_textbox(Inches(0.6), Inches(7.1), Inches(12.1), Inches(0.3))
        ft_p = ft.text_frame.paragraphs[0]
        ft_p.text = f"AeroSense AI  |  Final-Year B.Tech Data Science Project  |  Slide {page_num}/16"
        ft_p.font.size = Pt(10)
        ft_p.font.color.rgb = RGBColor(100, 116, 139)

    def _add_card(slide, left, top, width, height, title_txt: str, body_lines: List[str], accent=BLUE):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = BORDER
        box.line.width = Pt(1)

        strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(0.1), Inches(height))
        strip.fill.solid()
        strip.fill.fore_color.rgb = accent
        strip.line.fill.background()

        tb = slide.shapes.add_textbox(Inches(left + 0.22), Inches(top + 0.14), Inches(width - 0.34), Inches(height - 0.25))
        tf = tb.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = title_txt
        p0.font.name = "Calibri"
        p0.font.size = Pt(15)
        p0.font.bold = True
        p0.font.color.rgb = NAVY
        p0.space_after = Pt(6)

        for line in body_lines:
            p = tf.add_paragraph()
            p.text = line
            p.font.name = "Calibri"
            p.font.size = Pt(12.5)
            p.font.color.rgb = SLATE
            p.space_after = Pt(4)

    def _add_table(slide, left, top, width, height, data: List[List[str]], font_pt=10.5):
        rows, cols = len(data), len(data[0])
        shape = slide.shapes.add_table(rows, cols, Inches(left), Inches(top), Inches(width), Inches(height))
        tbl = shape.table
        for r_i, row in enumerate(data):
            for c_i, val in enumerate(row):
                cell = tbl.cell(r_i, c_i)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                cell.fill.solid()
                cell.fill.fore_color.rgb = BLUE if r_i == 0 else (WHITE if r_i % 2 == 1 else RGBColor(241, 245, 249))
                p = cell.text_frame.paragraphs[0]
                p.text = str(val)
                p.font.name = "Calibri"
                p.font.size = Pt(font_pt)
                p.font.bold = (r_i == 0)
                p.font.color.rgb = WHITE if r_i == 0 else NAVY

    # SLIDE 1: TITLE SLIDE
    s1 = prs.slides.add_slide(blank)
    _set_bg(s1, DARK_BG)
    accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(0.85), Inches(1.4), Inches(0.08))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = CYAN
    accent_bar.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(0.7), Inches(1.05), Inches(11.9), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "AeroSense AI"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p2 = tf1.add_paragraph()
    p2.text = INSTITUTE_META["project_title"]
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p3 = tf1.add_paragraph()
    p3.text = f"\"{INSTITUTE_META['tagline']}\"   |   {INSTITUTE_META['degree']}"
    p3.font.size = Pt(14)
    p3.font.color.rgb = MUTED

    # 4 Group Member Cards
    for idx, m in enumerate(TEAM_MEMBERS):
        x_pos = 0.7 + idx * 3.05
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x_pos), Inches(3.8), Inches(2.85), Inches(1.95))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_DARK
        card.line.color.rgb = CYAN
        card.line.width = Pt(1)
        ctb = s1.shapes.add_textbox(Inches(x_pos + 0.15), Inches(3.92), Inches(2.55), Inches(1.75))
        ctf = ctb.text_frame
        ctf.word_wrap = True
        cp0 = ctf.paragraphs[0]
        cp0.text = f"Team Member {idx + 1}"
        cp0.font.size = Pt(11)
        cp0.font.bold = True
        cp0.font.color.rgb = CYAN
        for val, sz, col in [(m[0], 13, WHITE), (m[1], 10.5, MUTED), (m[2], 10, MUTED), (m[3], 10, RGBColor(203, 213, 225))]:
            cp = ctf.add_paragraph()
            cp.text = val
            cp.font.size = Pt(sz)
            cp.font.color.rgb = col

    bot = s1.shapes.add_textbox(Inches(0.7), Inches(6.15), Inches(11.9), Inches(0.9))
    btf = bot.text_frame
    bp = btf.paragraphs[0]
    bp.text = f"Supervised By: {INSTITUTE_META['guide']}"
    bp.font.size = Pt(13)
    bp.font.color.rgb = WHITE
    bp2 = btf.add_paragraph()
    bp2.text = f"{INSTITUTE_META['department']}  |  {INSTITUTE_META['institute']}  |  {INSTITUTE_META['session']}"
    bp2.font.size = Pt(12)
    bp2.font.color.rgb = MUTED

    # SLIDE 2: MOTIVATION
    s2 = prs.slides.add_slide(blank)
    _add_header(s2, "Motivation & Air Quality Urgency", "Why real-time India-first monitoring + predictive forecasting matters", 2)
    _add_card(s2, 0.6, 1.4, 5.9, 2.5, "Severe Respiratory Burden Across India", [
        "• PM2.5 penetrates deep alveoli and enters systemic circulation.",
        "• Winter boundary-layer inversions trap emissions across the Indo-Gangetic Plain.",
        "• WHO 2021 24h Guideline: 15 µg/m³ vs Indian CPCB NAAQS: 60 µg/m³."
    ], BLUE)
    _add_card(s2, 6.8, 1.4, 5.9, 2.5, "Observed OpenAQ v3 Live Snapshot (Oct–Nov 2026)", [
        "• Delhi (R K Puram): Mean 177.81 µg/m³ | Peak 501.00 | 98.6% WHO breach.",
        "• Lucknow (Talkatora): Mean 85.64 µg/m³ | Peak 265.00 | 92.2% WHO breach.",
        "• Hyderabad (Zoo Park): Mean 52.71 µg/m³ | 97.4% WHO breach."
    ], RGBColor(220, 38, 38))
    _add_card(s2, 0.6, 4.2, 12.1, 2.5, "Limitations in Conventional Pollution Dashboards", [
        "1. Historical-only views lack forward 1h–24h forecasting to guide vulnerable citizens before severe episodes arrive.",
        "2. Many ML benchmarks suffer temporal leakage (random k-fold / unshifted rolling features), overstating real-world performance.",
        "3. Incomplete sensor panels often produce misleading AQI numbers without disclosing missing criteria pollutants."
    ], VIOLET)

    # SLIDE 3: PROBLEM STATEMENT & OBJECTIVES
    s3 = prs.slides.add_slide(blank)
    _add_header(s3, "Problem Statement & Engineering Objectives", "Building a reproducible, leakage-free air pollution intelligence platform", 3)
    _add_card(s3, 0.6, 1.4, 5.9, 5.3, "Core Objectives", [
        "1. Live Ingestion: Authenticated OpenAQ API v3 client with automatic retry/backoff, pagination & Parquet provenance.",
        "2. Validated Cleaning: Physical bounds enforcement, IQR×3 outlier filtering, and bounded 6h interpolation (is_imputed tracking).",
        "3. Dual AQI Engine: Indian CPCB (2014) + US EPA calculators with is_complete transparency.",
        "4. Chronological ML & DL: Compare Baselines, 6 ML algorithms, and 4 PyTorch sequence models (LSTM, GRU, TCN, Transformer).",
        "5. XAI & Delivery: SHAP attribution, 10-page Streamlit interface, automated PDF/HTML/MD/ZIP academic exports."
    ], BLUE)
    _add_card(s3, 6.8, 1.4, 5.9, 5.3, "Geographical & Architectural Strategy", [
        "Phase 1 (Current): India-First Implementation",
        "  • Default ISO: IN | Primary Pollutant: PM2.5 (plus PM10, NO2, SO2, CO, O3).",
        "  • Built-in Delhi Anand Vihar & Mumbai Bandra calibration benchmarks + live DPCC/CPCB/TSPCB ingestion.",
        "",
        "Phase 2 (Extensible Design): Global Coverage",
        "  • Parameterized by ISO country code via OpenAQ v3.",
        "  • Zero code rewrites needed to analyze US, GB, DE, CN, or global megacities."
    ], VIOLET)

    # SLIDE 4: ARCHITECTURE
    s4 = prs.slides.add_slide(blank)
    _add_header(s4, "End-to-End Modular Architecture", "Strict separation of acquisition, engineering, modeling, XAI & UI", 4)
    layers = [
        ("Presentation Layer (app.py + 10 Streamlit Pages)", "Global Explorer • Analytics • AQI • Forecasting Studio • Benchmarking • XAI • Spatial • Health • Reports • Diagnostics", DARK_BG, WHITE),
        ("Explainability, Visualization & Reporting", "SHAP (Tree/Linear/Explainer) • Permutation Importance • Plotly Dark Charts • ReportLab PDF / HTML / ZIP", BLUE, WHITE),
        ("ML & PyTorch DL Modeling Engine", "Baselines (3) • Linear/Ridge/RF/ET/HistGB/XGBoost (6) • LSTM / GRU / TCN / Transformer (4) | Strict 70/15/15 Split", VIOLET, WHITE),
        ("Feature Store & Dual AQI Engine", "Cyclical Harmonics (sin/cos) • Lags (1..24h) • Shifted Rolling Stats • CPCB India & US EPA Calculators", RGBColor(13, 148, 136), WHITE),
        ("Data Pipeline & OpenAQ v3 Client", "OpenAQ /v3/locations & /sensors/{id}/hours • Schema & Bounds Validation • IQR Filter • Parquet Store", RGBColor(30, 41, 59), WHITE),
    ]
    for i, (t, desc, bgc, fgc) in enumerate(layers):
        top = 1.4 + i * 1.12
        sh = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top), Inches(11.7), Inches(0.95))
        sh.fill.solid()
        sh.fill.fore_color.rgb = bgc
        sh.line.fill.background()
        tb = s4.shapes.add_textbox(Inches(1.0), Inches(top + 0.1), Inches(11.3), Inches(0.75))
        tf = tb.text_frame
        p1 = tf.paragraphs[0]
        p1.text = t
        p1.font.size = Pt(14.5)
        p1.font.bold = True
        p1.font.color.rgb = CYAN if bgc == DARK_BG else fgc
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = RGBColor(226, 232, 240)

    # SLIDE 5: DATA PIPELINE
    s5 = prs.slides.add_slide(blank)
    _add_header(s5, "OpenAQ API v3 & Reproducible Data Pipeline", "Real-world sensor ingestion with schema validation & provenance", 5)
    _add_card(s5, 0.6, 1.4, 5.9, 5.3, "OpenAQ v3 Discovery & Sensor Querying", [
        "• Header Authentication: X-API-Key stored securely in .env (gitignored).",
        "• Endpoint 1: GET /v3/locations?iso=IN&parameters_id=2 resolves active sensors.",
        "• Endpoint 2: GET /v3/sensors/{id}/hours?datetime_from=...&datetime_to=...",
        "• Safe Pagination: Parses integer and string meta.found (e.g. '>1000').",
        "• Provenance Stamping: Tracks location_id, sensor_id, api_endpoint, retrieved_at."
    ], BLUE)
    _add_card(s5, 6.8, 1.4, 5.9, 5.3, "Validation, Cleaning & Storage (Apache Parquet)", [
        "• Physical Bounds: Rejects impossible readings (e.g., PM2.5 outside [0, 1000]).",
        "• Deduplication: Unique keys on (location_id, parameter, datetime_utc).",
        "• Outlier Removal: Per-station IQR × 3 fence removal.",
        "• Bounded Imputation: Linear time interpolation capped at 6 hours (is_imputed=True); longer gaps stay NaN.",
        "• Metadata Preservation: Coordinates & station labels carried across resampled hours."
    ], RGBColor(13, 148, 136))

    # SLIDE 6: LIVE TELEMETRY CHART
    s6 = prs.slides.add_slide(blank)
    _add_header(s6, "Live Indian Air Quality Exploratory Patterns", "30-day OpenAQ v3 multi-station observations (Oct 17 – Nov 16, 2026)", 6)
    s6.shapes.add_picture(str(FIG_DIR / "fig1_live_station_profiles.png"), Inches(0.55), Inches(1.3), width=Inches(12.2))
    _add_card(s6, 0.6, 5.65, 12.1, 1.25, "Physical & Atmospheric Interpretation", [
        "Bimodal diurnal peaks align with morning rush-hour + nocturnal thermal inversion (20:00–23:00 IST), with midday mixing trough (13:00–16:00 IST). Notice Delhi R K Puram surges above 300 µg/m³ in early November."
    ], BLUE)

    # SLIDE 7: AQI ENGINE
    s7 = prs.slides.add_slide(blank)
    _add_header(s7, "Dual-Standard AQI Intelligence Engine", "Indian CPCB (2014) & US EPA calculators with completeness guarantees", 7)
    s7.shapes.add_picture(str(FIG_DIR / "fig5_aqi_exceedance.png"), Inches(0.55), Inches(1.3), width=Inches(12.2))
    _add_card(s7, 0.6, 5.65, 12.1, 1.25, "Sub-Index Transparency & Regulatory Compliance", [
        "Piecewise-linear interpolation across 6 categories (Good→Severe). Live stations spent 24.3% in Very Poor and 6.8% in Severe. System explicitly flags partial AQI (is_complete=False) when gaseous co-pollutants are unavailable."
    ], RGBColor(220, 38, 38))

    # SLIDE 8: FEATURES & VALIDATION
    s8 = prs.slides.add_slide(blank)
    _add_header(s8, "Feature Engineering & Leakage-Free Validation", "Preventing temporal data leakage in time-series forecasting", 8)
    _add_card(s8, 0.6, 1.4, 5.9, 5.3, "34 Leakage-Free Supervised Features", [
        "• Calendar Harmonics: sin/cos pairs for hour (24h), day-of-week (7d), month (12m).",
        "• Autoregressive Lags: lag_1, lag_3, lag_6, lag_12, lag_24.",
        "• Shifted Rolling Windows (strictly on y_{t-1}): mean, std, min, max over 3h, 6h, 12h, 24h.",
        "• Momentum Feature: trend_24 = y_{t-1} - y_{t-24}.",
        "• Deep Learning Tensors: Sliding windows (N, lookback=24, 1) scaled using training-only MinMaxScaler."
    ], BLUE)
    _add_card(s8, 6.8, 1.4, 5.9, 5.3, "Strict Chronological Split (70% / 15% / 15%)", [
        "Why Random Splits Fail in Air Quality ML:",
        "  • Consecutive hours exhibit autocorrelation φ1 ≈ 0.85.",
        "  • Random splits place t-1 and t+1 in train while testing on t, causing fake R² > 0.98.",
        "",
        "AeroSense Enforcement:",
        "  • Train: First 70% chronological timestamps.",
        "  • Validation: Next 15% (early stopping & LR decay).",
        "  • Held-Out Test: Final 15% (unseen evaluation only)."
    ], VIOLET)

    # SLIDE 9: MODEL ARCHITECTURES
    s9 = prs.slides.add_slide(blank)
    _add_header(s9, "Machine Learning & Deep Learning Model Suite", "Comparing 3 baselines, 6 tabular ML algorithms, and 4 PyTorch architectures", 9)
    arch_tbl = [
        ["Family", "Models Implemented", "Key Hyperparameters / Architecture Details"],
        ["Naive Baselines (3)", "Persistence, Historical Mean, Seasonal Naive (24h)", "Reference benchmarks required to prove learned skill"],
        ["Linear / Regularized (2)", "LinearRegression, Ridge (alpha=1.0)", "StandardScaler sklearn Pipeline; linear extrapolation capability"],
        ["Bagging Ensembles (2)", "RandomForest, ExtraTrees", "n_estimators=100, n_jobs=-1, random_state=42"],
        ["Gradient Boosting (2)", "HistGradientBoosting, XGBoost", "max_iter=200 / n_estimators=200, lr=0.05, early_stopping"],
        ["Recurrent DL (2)", "PyTorch LSTM, PyTorch GRU", "2 stacked layers, hidden_size=64, dropout=0.2, FC projection"],
        ["Convolutional DL (1)", "PyTorch Temporal Convolutional Net (TCN)", "4 causal dilated 1D blocks (dilation=1,2,4,8), chomp padding, BN"],
        ["Attention DL (1)", "PyTorch Encoder-Only Transformer", "d_model=64, nhead=4, 2 encoder layers, positional embedding"],
    ]
    _add_table(s9, 0.6, 1.5, 12.1, 5.1, arch_tbl, font_pt=12)

    # SLIDE 10: BENCHMARKING RESULTS
    s10 = prs.slides.add_slide(blank)
    _add_header(s10, "Experimental Benchmarking Results", "Controlled 90-day evaluation (n=2,161) on chronological 15% test split", 10)
    s10.shapes.add_picture(str(FIG_DIR / "fig2_model_benchmark.png"), Inches(0.55), Inches(1.25), width=Inches(8.1))
    bm_tbl = [
        ["Model", "MAE", "RMSE", "R²"],
        ["LinearRegression", "9.449", "11.947", "0.906"],
        ["Ridge", "9.457", "11.948", "0.906"],
        ["Transformer (h=1)", "9.580", "12.124", "0.903"],
        ["RandomForest", "9.930", "12.402", "0.898"],
        ["HistGradientBoosting", "10.149", "12.534", "0.896"],
        ["GRU (h=1)", "10.161", "12.976", "0.889"],
        ["XGBoost", "10.319", "13.023", "0.888"],
        ["LSTM (h=1)", "10.838", "13.579", "0.878"],
        ["TCN (h=1)", "11.851", "14.653", "0.858"],
        ["LSTM (h=24 multi)", "30.288", "37.029", "0.094"],
        ["Seasonal Naive", "30.966", "38.726", "0.008"],
    ]
    _add_table(s10, 8.8, 1.3, 4.0, 5.4, bm_tbl, font_pt=10.5)

    # SLIDE 11: FORECAST & ENGINEERING INSIGHT
    s11 = prs.slides.add_slide(blank)
    _add_header(s11, "Forecast Trajectory & Critical ML Engineering Insights", "Evaluating non-stationary extremes on live Delhi R K Puram telemetry", 11)
    s11.shapes.add_picture(str(FIG_DIR / "fig3_forecast_residuals.png"), Inches(0.55), Inches(1.25), width=Inches(12.2))
    _add_card(s11, 0.6, 5.4, 12.1, 1.5, "Key Research Finding: Why Linear/Ridge Beat Trees on Live Delhi R K Puram (n=639)", [
        "• On live Oct–Nov 2026 Delhi data, LinearRegression (MAE 23.80 µg/m³, R² 0.854) beat RandomForest (26.53, 0.802) and XGBoost (33.48, 0.714), achieving a 57.1% gain over Seasonal Naive (55.52 MAE).",
        "• Root Cause: November smog spikes reached 501.0 µg/m³—exceeding training maxima. Decision tree leaves output bounded averages and cannot extrapolate beyond training range, unlike linear autoregressive slopes."
    ], VIOLET)

    # SLIDE 12: EXPLAINABLE AI
    s12 = prs.slides.add_slide(blank)
    _add_header(s12, "Explainable AI: SHAP & Feature Attributions", "Interpreting atmospheric drivers behind model forecasts", 12)
    s12.shapes.add_picture(str(FIG_DIR / "fig4_shap_importance.png"), Inches(0.55), Inches(1.4), width=Inches(7.7))
    _add_card(s12, 8.5, 1.4, 4.2, 5.1, "SHAP Findings (Test Split)", [
        "• Top Driver: lag_1 contributes 26.91 µg/m³ mean |SHAP| (93.95% Gini importance).",
        "• Diurnal Phase: hour_sin (2.58) & hour (2.09) encode boundary-layer expansion & inversion timing.",
        "• Momentum: trend_24 (1.39) captures multi-hour accumulation/dispersion direction.",
        "• Pipeline Compatibility: Supports TreeExplainer, LinearExplainer (scaled), & Permutation fallback."
    ], RGBColor(13, 148, 136))

    # SLIDE 13: STREAMLIT PLATFORM
    s13 = prs.slides.add_slide(blank)
    _add_header(s13, "10-Page Interactive Streamlit Application Suite", "End-to-end operational access without editing source code", 13)
    pages_tbl = [
        ["Page", "Capabilities", "Page", "Capabilities"],
        ["01 Data Explorer", "Live OpenAQ v3 fetch + Parquet preview + CSV", "06 Explainable AI", "Native/Permutation importance, SHAP, Residuals"],
        ["02 Analytics", "Diurnal, daily, DOW, distributions, correlations", "07 Spatial Hotspots", "Station map, hotspot ranking, Haversine matrix"],
        ["03 AQI Intelligence", "CPCB & US EPA gauges, sub-indices, completeness", "08 Health Advisory", "WHO vs NAAQS audit, cohort risk, simulator"],
        ["04 Forecasting Studio", "Interactive ML & PyTorch DL training studio", "09 Research Reports", "Markdown, HTML, ReportLab PDF, ZIP exporter"],
        ["05 Benchmarking", "Unified ML + DL held-out test leaderboard", "10 Diagnostics", "In-UI API key .env editor, ping, GPU/CPU & logs"],
    ]
    _add_table(s13, 0.6, 1.5, 12.1, 5.0, pages_tbl, font_pt=11.5)

    # SLIDE 14: SOFTWARE ENGINEERING & QA
    s14 = prs.slides.add_slide(blank)
    _add_header(s14, "Software Engineering Rigor & Automated QA", "Verified 41/41 pytest test suite + headless UI & Playwright verification", 14)
    _add_card(s14, 0.6, 1.5, 5.9, 5.1, "41/41 Passing Automated Tests (Pytest)", [
        "• test_aqi.py (12 tests): CPCB & US EPA breakpoints + negative guards.",
        "• test_features.py (2 tests): Feature matrix & DL sequence shapes.",
        "• test_validation.py (4 tests): Schema checks, outliers, interpolation.",
        "• test_ml_dl.py (3 tests): ML training, baselines, PyTorch forward pass.",
        "• test_reporting.py (4 tests): Summary stats, MD, HTML, ZIP archive.",
        "• test_api_and_explainability.py (5 tests): OpenAQ v3, SHAP, PDF.",
        "• test_streamlit_pages.py (11 tests): AppTest across app.py + 10 pages."
    ], RGBColor(22, 163, 74))
    _add_card(s14, 6.8, 1.5, 5.9, 5.1, "Production Hygiene & Reproducibility", [
        "• Live Browser QA: Verified rendered Home, Data Explorer, System Diagnostics (200 OK ping), & Model Benchmarking via Chromium.",
        "• Secret Security: .env gitignored; API key editable safely via UI.",
        "• Test Isolation: Tests write to tmp_path so production models and experiment CSVs remain uncorrupted.",
        "• Reproducible Seed: Fixed ML/DL random seeds (42) + experiment config JSON."
    ], BLUE)

    # SLIDE 15: CONCLUSION & ROADMAP
    s15 = prs.slides.add_slide(blank)
    _add_header(s15, "Conclusion, Limitations & Phase 2 Roadmap", "Transitioning from India-first hourly forecasting to global multi-modal AI", 15)
    _add_card(s15, 0.6, 1.5, 5.9, 5.1, "Key Contributions & Current Limitations", [
        "• Delivered an authentic, end-to-end air quality analytics & forecasting platform running live on OpenAQ v3 telemetry.",
        "• Demonstrated empirically why leakage-free chronological testing and linear extrapolation matter under extreme pollution regimes.",
        "• Limitation: Univariate station forecasting lacks meteorological drivers (wind, humidity, mixing height) needed for 24–72h multi-step horizon accuracy."
    ], BLUE)
    _add_card(s15, 6.8, 1.5, 5.9, 5.1, "Phase 2 Global Expansion Roadmap", [
        "1. Meteorological Fusion: Integrate Copernicus ERA5 wind vectors, boundary-layer height, temperature, and precipitation.",
        "2. Spatio-Temporal GNNs: Model cross-station pollutant advection between upwind and downwind city monitors.",
        "3. Automated Scheduled Ingestion: Background cron pipelines updating regional forecasts and issuing threshold alerts.",
        "4. Multi-City Expansion: Scale seamlessly across global OpenAQ ISO countries."
    ], VIOLET)

    # SLIDE 16: THANK YOU / Q&A
    s16 = prs.slides.add_slide(blank)
    _set_bg(s16, DARK_BG)
    tb16 = s16.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(1.8))
    tf16 = tb16.text_frame
    p = tf16.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "Thank You — Questions & Live Demo"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = CYAN
    p2 = tf16.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    p2.text = f"{INSTITUTE_META['app_name']}  |  {INSTITUTE_META['tagline']}"
    p2.font.size = Pt(16)
    p2.font.color.rgb = WHITE

    team_sum = [["Student Name", "Student ID & Roll No.", "Batch / Sem / Branch", "Role"]] + TEAM_MEMBERS
    _add_table(s16, 1.0, 3.6, 11.3, 2.3, team_sum, font_pt=11.5)

    bot16 = s16.shapes.add_textbox(Inches(0.8), Inches(6.25), Inches(11.7), Inches(0.7))
    bp16 = bot16.text_frame.paragraphs[0]
    bp16.alignment = PP_ALIGN.CENTER
    bp16.text = f"Guide: {INSTITUTE_META['guide']}   |   {INSTITUTE_META['institute']}   |   {INSTITUTE_META['session']}"
    bp16.font.size = Pt(12.5)
    bp16.font.color.rgb = MUTED

    prs.save(str(pptx_path))
    return pptx_path

if __name__ == "__main__":
    syn_pdf, syn_md = build_synopsis()
    res_pdf, res_md = build_research_paper()
    rep_pdf, rep_md = build_project_report()
    ppt = build_presentation()
    title_pdf = REPORTS_DIR / "Air_Pollution_Pattern_Analysis_and_AQI_Forecasting.pdf"
    for p in [syn_pdf, syn_md, res_pdf, res_md, rep_pdf, title_pdf, rep_md, ppt]:
        print(f"Built deliverable: {p} ({p.stat().st_size:,} bytes)")
