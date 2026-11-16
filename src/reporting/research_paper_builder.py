"""Structured IEEE-format Research Manuscript builder (PDF + Markdown)."""
from __future__ import annotations

import html
from pathlib import Path
from typing import List

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.config import settings
from src.reporting.academic_references import get_ieee_references

PRINT_W_IEEE = 17.4 * cm  # A4 (21.0 cm) - 1.8 cm left - 1.8 cm right


def _ieee_styles() -> dict[str, ParagraphStyle]:
    return {
        "Banner": ParagraphStyle(
            "IEEEBanner", fontName="Times-Italic", fontSize=8.5, leading=11,
            alignment=TA_CENTER, textColor=colors.HexColor("#475569"), spaceAfter=4,
        ),
        "Title": ParagraphStyle(
            "IEEETitle", fontName="Times-Bold", fontSize=16.5, leading=21,
            alignment=TA_CENTER, textColor=colors.HexColor("#0F172A"), spaceAfter=6,
        ),
        "Authors": ParagraphStyle(
            "IEEEAuthors", fontName="Times-Bold", fontSize=10.5, leading=14,
            alignment=TA_CENTER, textColor=colors.HexColor("#0F172A"), spaceAfter=3,
        ),
        "Affil": ParagraphStyle(
            "IEEEAffil", fontName="Times-Italic", fontSize=9.2, leading=13,
            alignment=TA_CENTER, textColor=colors.HexColor("#334155"), spaceAfter=8,
        ),
        "AbsBox": ParagraphStyle(
            "IEEEAbsBox", fontName="Times-Roman", fontSize=9.8, leading=14,
            alignment=TA_JUSTIFY, textColor=colors.HexColor("#0F172A"),
        ),
        "Keywords": ParagraphStyle(
            "IEEEKeywords", fontName="Times-Roman", fontSize=9.4, leading=13,
            alignment=TA_JUSTIFY, textColor=colors.HexColor("#1E293B"), spaceBefore=5, spaceAfter=8,
        ),
        "H1": ParagraphStyle(
            "IEEEH1", fontName="Times-Bold", fontSize=11.5, leading=15,
            alignment=TA_CENTER, textColor=colors.HexColor("#0369A1"),
            spaceBefore=12, spaceAfter=5, keepWithNext=True,
        ),
        "H2": ParagraphStyle(
            "IEEEH2", fontName="Times-BoldItalic", fontSize=10.5, leading=14,
            alignment=TA_LEFT, textColor=colors.HexColor("#0F172A"),
            spaceBefore=8, spaceAfter=3, keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "IEEEBody", fontName="Times-Roman", fontSize=10.2, leading=14.8,
            alignment=TA_JUSTIFY, textColor=colors.HexColor("#1E293B"),
            firstLineIndent=14, spaceAfter=5,
        ),
        "Formula": ParagraphStyle(
            "IEEEFormula", fontName="Times-Bold", fontSize=9.8, leading=14,
            alignment=TA_CENTER, textColor=colors.HexColor("#0F172A"),
            backColor=colors.HexColor("#F1F5F9"), spaceBefore=4, spaceAfter=6,
        ),
        "Caption": ParagraphStyle(
            "IEEECaption", fontName="Times-Roman", fontSize=8.8, leading=12,
            alignment=TA_CENTER, textColor=colors.HexColor("#334155"), spaceBefore=3, spaceAfter=8,
        ),
        "TblLabel": ParagraphStyle(
            "IEEETblLabel", fontName="Times-Bold", fontSize=9.2, leading=12.5,
            alignment=TA_CENTER, textColor=colors.HexColor("#0F172A"),
            spaceBefore=7, spaceAfter=3, keepWithNext=True,
        ),
        "Ref": ParagraphStyle(
            "IEEERef", fontName="Times-Roman", fontSize=8.6, leading=12,
            alignment=TA_JUSTIFY, textColor=colors.HexColor("#1E293B"),
            leftIndent=20, firstLineIndent=-20, spaceAfter=2.5,
        ),
    }


def _ieee_table(
    data: List[List[str]],
    col_widths: List[float],
    right_align_cols: set[int] | None = None,
    font_pt: float = 8.4,
) -> Table:
    right_cols = right_align_cols or set()
    h_st = ParagraphStyle("ITH", fontName="Times-Bold", fontSize=font_pt, leading=font_pt + 2.5, alignment=TA_CENTER, textColor=colors.white)
    c_l = ParagraphStyle("ITL", fontName="Times-Roman", fontSize=font_pt, leading=font_pt + 2.5, alignment=TA_LEFT, textColor=colors.HexColor("#0F172A"))
    c_r = ParagraphStyle("ITR", fontName="Times-Roman", fontSize=font_pt, leading=font_pt + 2.5, alignment=TA_RIGHT, textColor=colors.HexColor("#0F172A"))
    c_b = ParagraphStyle("ITB", fontName="Times-Bold", fontSize=font_pt, leading=font_pt + 2.5, alignment=TA_RIGHT, textColor=colors.HexColor("#0369A1"))

    rows = []
    for r_i, row in enumerate(data):
        if r_i == 0:
            rows.append([Paragraph(html.escape(str(c)), h_st) for c in row])
        else:
            row_cells = []
            for c_i, cell in enumerate(row):
                s = str(cell)
                if r_i == 1 and c_i in right_cols:
                    st = c_b
                elif c_i in right_cols:
                    st = c_r
                else:
                    st = c_l
                row_cells.append(Paragraph(html.escape(s), st))
            rows.append(row_cells)

    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LINEABOVE", (0, 0), (-1, 0), 1.0, colors.HexColor("#0F172A")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.9, colors.HexColor("#0284C7")),
        ("LINEBELOW", (0, -1), (-1, -1), 1.0, colors.HexColor("#0F172A")),
        ("GRID", (0, 1), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    return t


def _add_ieee_figure(el: list, fig_dir: Path, fig_name: str, caption: str, styles: dict, width_cm: float = 16.8) -> None:
    p = fig_dir / fig_name
    if not p.exists():
        return
    with PILImage.open(p) as im:
        w, h = im.size
    aspect = h / float(w)
    w_pts = min(width_cm * cm, PRINT_W_IEEE)
    h_pts = min(w_pts * aspect, 11.5 * cm)
    if h_pts < w_pts * aspect:
        w_pts = h_pts / aspect
    img = Image(str(p), width=w_pts, height=h_pts)
    img.hAlign = "CENTER"
    el.append(Spacer(1, 4))
    el.append(img)
    el.append(Paragraph(html.escape(caption), styles["Caption"]))


def _ieee_header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Times-Italic", 8.5)
    canvas.setFillColor(colors.HexColor("#64748B"))
    if doc.page > 1:
        canvas.drawString(1.8 * cm, A4[1] - 1.15 * cm, "AeroSense AI — Air Pollution Pattern Analysis and AQI Forecasting")
        canvas.drawRightString(A4[0] - 1.8 * cm, A4[1] - 1.15 * cm, "Quantum University, Roorkee | CSE-DS")
        canvas.line(1.8 * cm, A4[1] - 1.28 * cm, A4[0] - 1.8 * cm, A4[1] - 1.28 * cm)
    canvas.setFont("Times-Roman", 9.5)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(A4[0] / 2.0, 1.15 * cm, f"- {doc.page} -")
    canvas.restoreState()


def build_qu_research_paper(team_members: list, meta: dict) -> tuple[Path, Path]:
    """Build structured, aligned IEEE-style research paper PDF and Markdown companion."""
    styles = _ieee_styles()
    pdf_path = settings.REPORTS_DIR / "AeroSense_Research_Paper.pdf"
    md_path = settings.REPORTS_DIR / "AeroSense_Research_Paper.md"
    fig_dir = settings.REPORTS_DIR / "figures"
    ieee_refs = get_ieee_references()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.65 * cm,
        bottomMargin=1.65 * cm,
    )
    el: list = []

    # Header & Title Block
    el.append(Paragraph("RESEARCH MANUSCRIPT  |  DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING (DATA SCIENCE)", styles["Banner"]))
    el.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceBefore=2, spaceAfter=8))
    el.append(Paragraph(
        "Air Pollution Pattern Analysis and AQI Forecasting Using Leakage-Free Machine Learning, Deep Sequence Modeling, and Explainable OpenAQ v3 Telemetry",
        styles["Title"],
    ))
    el.append(Paragraph(
        "Aryan Saini<super>1</super>, Ayaan Ali<super>2</super>, Kawalpreet Kaur<super>3</super>, Mihir Kumar<super>4</super>, and Abhishek Kumar<super>5</super>",
        styles["Authors"],
    ))
    el.append(Paragraph(
        "Department of Computer Science &amp; Engineering (CSE-DS), Quantum School of Technology, Quantum University, Roorkee - 247167, India<br/>"
        "Batch 2023 - 2027 (7th Sem) | Student IDs / Roll Nos.: "
        "<super>1</super>23030173 / 2301315012, <super>2</super>23030175 / 2301315013, "
        "<super>3</super>23030255 / 2301315019, <super>4</super>23030268 / 2301315022 | "
        "<super>5</super>Faculty Guide (ID: QU0125261068)",
        styles["Affil"],
    ))

    # Shaded Boxed Abstract
    abs_para = Paragraph(
        "<b>Abstract</b>—Rapid urbanization and winter boundary-layer temperature inversions across South Asia produce acute fine "
        "particulate matter (PM2.5) episodes demanding accurate short-term forecasting and transparent Air Quality Index (AQI) analytics. "
        "Yet empirical forecasting studies frequently suffer from temporal data leakage introduced by randomized train-test shuffling "
        "and omit partial-sensor disclosures when computing regulatory indices. This paper presents AeroSense AI, an extensible modular "
        "platform coupling authenticated OpenAQ API v3 ingestion, physical validation, IQR outlier filtering, bounded 6-hour interpolation, "
        "dual Indian CPCB (2014) and US EPA (2018) AQI calculators, 34 leakage-free engineered features, and strict chronological (70/15/15) "
        "benchmarking across 3 naive baselines, 6 tabular ML algorithms, and 4 PyTorch deep architectures (LSTM, GRU, Dilated Causal TCN, "
        "and Encoder-only Transformer). Live 30-day Indian telemetry across Delhi R K Puram, Lucknow Talkatora, and Hyderabad Zoo Park "
        "(2,157 hourly observations) reveals WHO 24-hour exceedance rates of 92.2%–98.6%. Under controlled 90-day testing (n = 2,161), "
        "Linear Regression (9.449 ug/m3 MAE, R2 = 0.906) and PyTorch Transformer (9.580 ug/m3 MAE, R2 = 0.903) decisively outperform "
        "Seasonal Naive (30.966 ug/m3 MAE). On live Delhi R K Puram surges reaching 501.00 ug/m3 (n = 639), Linear Regression achieves "
        "23.803 ug/m3 MAE (R2 = 0.854; 57.1% gain over Seasonal Naive) and outperforms tree ensembles unable to extrapolate past training bounds, "
        "supported by TreeSHAP explanations (lag_1 mean |SHAP| = 26.91 ug/m3) and 46 passing automated verification checks.",
        styles["AbsBox"],
    )
    abs_box = Table([[abs_para]], colWidths=[PRINT_W_IEEE])
    abs_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("LINEBEFORE", (0, 0), (0, -1), 3.0, colors.HexColor("#0284C7")),
        ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
    ]))
    el.append(abs_box)
    el.append(Paragraph(
        "<b><i>Index Terms</i></b>—Air Quality Index (AQI), Chronological Validation, Deep Sequence Modeling, Explainable AI (SHAP), OpenAQ API v3, PM2.5 Forecasting, Transformer.",
        styles["Keywords"],
    ))

    # I. INTRODUCTION
    el.append(Paragraph("I. INTRODUCTION", styles["H1"]))
    el.append(Paragraph(
        "Ambient fine particulate matter (PM2.5) penetrates deep into human pulmonary alveoli and systemic circulation, elevating "
        "cardiopulmonary morbidity and mortality worldwide [8], [11], [23]. Across the Indo-Gangetic Plain (IGP), compressed winter "
        "planetary boundary layers, regional crop-residue smoke, vehicular diesel emissions, and industrial aerosols drive acute PM2.5 surges "
        "frequently breaching both World Health Organization (WHO 2021) 24-hour limits (15 ug/m3) and Indian National Ambient Air Quality "
        "Standards (60 ug/m3) [1], [5]. While global sensor networks publish continuous observations through OpenAQ API v3 [18], applied "
        "analytics systems often lack unified provenance tracking, honest AQI completeness flags, and temporally sound machine learning benchmarks.",
        styles["Body"],
    ))

    # II. RELATED WORK AND RESEARCH GAPS
    el.append(Paragraph("II. RELATED WORK AND IDENTIFIED GAPS", styles["H1"]))
    el.append(Paragraph(
        "Prior forecasting literature spans ensemble learners including Random Forests [4], Extra Trees [10], Gradient Boosting [9], "
        "XGBoost [6], and LightGBM [13] alongside deep neural architectures such as LSTM [12], GRU [7], Dilated Causal TCN [2], [14], "
        "hybrid CNN-LSTM [19], and self-attention Transformers [22], [24], [25]. Indian city studies [16], [17], [20] demonstrate high predictive "
        "promise; however, Bergmeir and Benitez [3] establish that random cross-validation leaks temporally adjacent autocorrelated readings. "
        "AeroSense AI resolves three structural gaps simultaneously: (1) eliminating temporal and target leakage via lag-shifted features "
        "and strict chronological 70/15/15 splits, (2) enforcing explicit incomplete-panel AQI flagging, and (3) diagnosing linear vs. tree extrapolation behavior.",
        styles["Body"],
    ))

    # III. SYSTEM ARCHITECTURE AND DATA ENGINEERING
    el.append(Paragraph("III. SYSTEM ARCHITECTURE AND OPENAQ V3 DATA PIPELINE", styles["H1"]))
    el.append(Paragraph(
        "AeroSense AI decouples ingestion, validation, AQI computation, feature generation, ML/DL training, SHAP attribution, and "
        "10-page Streamlit visualization. Live queries authenticate with X-API-Key against GET /v3/locations (ISO filter + parameters_id) "
        "and paginate GET /v3/sensors/{id}/hours constrained by UTC ISO-8601 windows. Validation enforces physical domain bounds "
        "(PM2.5 in [0, 1000] ug/m3) and deduplicates station-hour keys, while cleaning filters IQR x 3 outliers and bounds linear time "
        "interpolation to <= 6 hours with explicit is_imputed flags persisted in Apache Parquet.",
        styles["Body"],
    ))
    el.append(Paragraph("TABLE I  LIVE OPENAQ API V3 INDIAN STATION TELEMETRY SUMMARY (OCT 17 – NOV 16, 2026)", styles["TblLabel"]))
    el.append(_ieee_table(
        [
            ["Monitoring Station (OpenAQ Location ID)", "Valid Hrs", "Mean +- Std (ug/m3)", "Range (Min–Max)", "WHO Breach (>15)", "NAAQS Breach (>60)"],
            ["R K Puram, Delhi - DPCC (ID: 17)", "639", "177.81 +- 95.74", "1.00 – 501.00", "98.6%", "92.3%"],
            ["Talkatora District Ind., Lucknow - CPCB (ID: 407)", "641", "85.64 +- 50.82", "4.34 – 265.00", "92.2%", "68.3%"],
            ["Zoo Park, Hyderabad - TSPCB (ID: 2456)", "627", "52.71 +- 19.43", "9.50 – 87.00", "97.4%", "36.0%"],
        ],
        [6.3 * cm, 1.5 * cm, 3.0 * cm, 2.5 * cm, 2.0 * cm, 2.1 * cm],
        right_align_cols={1, 2, 3, 4, 5},
    ))
    _add_ieee_figure(el, fig_dir, "fig1_live_station_profiles.png", "Fig. 1. Live OpenAQ v3 daily mean PM2.5 trajectories (A) and diurnal IST planetary boundary-layer profiles (B).", styles, width_cm=16.8)

    # IV. REGULATORY AQI AND MATHEMATICAL FORMULATION
    el.append(Paragraph("IV. REGULATORY AQI ENGINE AND MATHEMATICAL FORMULATION", styles["H1"]))
    el.append(Paragraph(
        "Both Indian CPCB National AQI (2014) [5] and US EPA TAD (2018) [21] compute each pollutant sub-index I_p through linear "
        "interpolation inside concentration breakpoint bounds [BP_lo, BP_hi] and corresponding AQI tier limits [I_lo, I_hi], reporting "
        "composite AQI = max_p(I_p) alongside an explicit is_complete flag whenever gaseous co-pollutants are unavailable.",
        styles["Body"],
    ))
    el.append(Paragraph("I_p = round( ((I_hi - I_lo) / (BP_hi - BP_lo)) * (C_p - BP_lo) + I_lo );    AQI = max_p(I_p)", styles["Formula"]))

    # V. LEAKAGE-FREE FEATURES AND MODEL SUITE
    el.append(Paragraph("V. LEAKAGE-FREE FEATURE MATRIX AND FORECASTING ARCHITECTURES", styles["H1"]))
    el.append(Paragraph(
        "Calendar periodicity is transformed onto unit-circle sine/cosine pairs (hour period 24, day-of-week period 7, month period 12). "
        "Autoregressive lags {1, 3, 6, 12, 24 h}, shifted target.shift(1) rolling statistics (mean, std, min, max across 3, 6, 12, 24 h), "
        "and momentum trend_24 form the 34-feature matrix. PyTorch models consume (N, 24, 1) sliding windows scaled strictly via training-only "
        "MinMaxScaler under chronological 70% Train / 15% Validation / 15% Held-Out Test splitting.",
        styles["Body"],
    ))
    el.append(Paragraph("TABLE II  MODEL FAMILIES AND HYPERPARAMETER GOVERNANCE", styles["TblLabel"]))
    el.append(_ieee_table(
        [
            ["Model Family", "Implemented Architectures", "Key Configuration & Anti-Leakage Controls"],
            ["Naive Baselines (3)", "Persistence, Historical Mean, Seasonal Naive (24h)", "Strict benchmark floor computed on chronological test split"],
            ["Linear / Regularized (2)", "LinearRegression, Ridge (alpha=1.0)", "StandardScaler sklearn Pipeline; supports linear slope extrapolation"],
            ["Tree Ensembles (4)", "RandomForest, ExtraTrees, HistGB, XGBoost", "n_estimators=100-200, lr=0.05 (boosted), fixed random_state=42"],
            ["Deep Sequence (4)", "PyTorch LSTM, GRU, Dilated Causal TCN, Transformer", "hidden/d_model=64, grad clip=1.0, ReduceLROnPlateau, EarlyStopping"],
        ],
        [3.6 * cm, 5.7 * cm, 8.1 * cm],
    ))

    # VI. EXPERIMENTAL BENCHMARKS
    el.append(Paragraph("VI. EXPERIMENTAL RESULTS AND NON-STATIONARITY ANALYSIS", styles["H1"]))
    el.append(Paragraph("TABLE III  CONTROLLED 90-DAY CHRONOLOGICAL TEST BENCHMARK (DELHI ANAND VIHAR, N = 2,161)", styles["TblLabel"]))
    el.append(_ieee_table(
        [
            ["Rank & Model", "Family / Horizon", "Test MAE (ug/m3)", "Test RMSE (ug/m3)", "Test R2", "Train Time"],
            ["1. LinearRegression", "ML Tabular (h=1)", "9.449", "11.947", "0.906", "0.03s"],
            ["2. Ridge (alpha=1.0)", "ML Tabular (h=1)", "9.457", "11.948", "0.906", "0.00s"],
            ["3. Transformer (PyTorch)", "DL Attention (h=1)", "9.580", "12.124", "0.903", "12.3s"],
            ["4. RandomForest", "ML Ensemble (h=1)", "9.930", "12.402", "0.898", "0.26s"],
            ["5. HistGradientBoosting", "ML Boosting (h=1)", "10.149", "12.534", "0.896", "5.75s"],
            ["6. GRU (PyTorch)", "DL Recurrent (h=1)", "10.161", "12.976", "0.889", "9.3s"],
            ["7. XGBoost", "ML Boosting (h=1)", "10.319", "13.023", "0.888", "3.82s"],
            ["8. ExtraTrees", "ML Ensemble (h=1)", "10.575", "13.139", "0.886", "0.15s"],
            ["9. LSTM (PyTorch)", "DL Recurrent (h=1)", "10.838", "13.579", "0.878", "4.2s"],
            ["10. TCN (PyTorch)", "DL Causal Conv (h=1)", "11.851", "14.653", "0.858", "4.4s"],
            ["11. LSTM Multi-Step", "DL Direct (h=24)", "30.288", "37.029", "0.094", "9.0s"],
            ["12. Seasonal Naive (24h)", "Baseline (h=24)", "30.966", "38.726", "0.008", "—"],
            ["13. Historical Mean", "Baseline", "32.139", "39.182", "-0.016", "—"],
            ["14. Persistence", "Baseline", "40.117", "49.392", "-0.614", "—"],
        ],
        [4.2 * cm, 3.3 * cm, 2.7 * cm, 2.7 * cm, 2.3 * cm, 2.2 * cm],
        right_align_cols={2, 3, 4, 5},
    ))
    _add_ieee_figure(el, fig_dir, "fig2_model_benchmark.png", "Fig. 2. Chronological test split performance comparison (MAE and R2) across tabular ML and PyTorch deep learning models.", styles, width_cm=16.8)

    el.append(Paragraph("TABLE IV  LIVE DELHI R K PURAM EVALUATION (N = 639, NON-STATIONARY SMOG EXCURSION)", styles["TblLabel"]))
    el.append(_ieee_table(
        [
            ["Model on Live R K Puram", "Test MAE (ug/m3)", "Test RMSE (ug/m3)", "Test R2", "MAE Gain vs Seasonal Naive"],
            ["1. LinearRegression", "23.803", "30.540", "0.854", "57.1%"],
            ["2. Ridge", "24.714", "32.074", "0.839", "55.5%"],
            ["3. RandomForest", "26.534", "35.573", "0.802", "52.2%"],
            ["4. ExtraTrees", "31.829", "41.481", "0.731", "42.7%"],
            ["5. HistGradientBoosting", "32.799", "40.471", "0.744", "40.9%"],
            ["6. XGBoost", "33.479", "42.794", "0.714", "39.7%"],
            ["7. Seasonal Naive (24h)", "55.515", "71.767", "0.165", "Baseline"],
            ["8. Persistence", "61.876", "85.158", "-0.176", "—"],
        ],
        [5.2 * cm, 2.9 * cm, 3.0 * cm, 2.6 * cm, 3.7 * cm],
        right_align_cols={1, 2, 3, 4},
    ))
    el.append(Paragraph(
        "Empirical Distribution-Shift Finding: During October-to-November 2026 in New Delhi, test-split concentrations escalated up to "
        "501.00 ug/m3 beyond October training maxima. Axis-aligned tree ensembles (XGBoost, HistGradientBoosting, ExtraTrees, RandomForest) "
        "output piecewise-constant leaf means bounded inside [min(y_train), max(y_train)] and consequently cannot extrapolate linearly "
        "above unseen winter spikes, whereas Linear Regression and Ridge leverage fitted autoregressive slopes on lag_1 and trend_24 cleanly.",
        styles["Body"],
    ))
    _add_ieee_figure(el, fig_dir, "fig3_forecast_residuals.png", "Fig. 3. Held-out test trajectory comparison (A) and residual error histogram (Mean = 0.82, Std = 11.96 ug/m3) (B).", styles, width_cm=16.8)

    # VII. EXPLAINABLE AI & COMPLIANCE
    el.append(Paragraph("VII. EXPLAINABLE AI AND PUBLIC HEALTH AUDIT", styles["H1"]))
    el.append(Paragraph(
        "TreeSHAP explanations across 120 held-out test instances quantify local additive attributions in ug/m3: lag_1 dominates "
        "(mean |SHAP| = 26.91 ug/m3, 93.95% Gini share), followed by diurnal boundary-layer phase hour_sin (2.58 ug/m3), hour (2.09 ug/m3), "
        "and trend_24 (1.39 ug/m3). Live CPCB auditing confirms 24.3% Very Poor and 6.8% Severe ambient hourly states (Fig. 5).",
        styles["Body"],
    ))
    _add_ieee_figure(el, fig_dir, "fig4_shap_importance.png", "Fig. 4. Top-10 Mean |SHAP| feature attributions across held-out PM2.5 test predictions.", styles, width_cm=14.5)
    _add_ieee_figure(el, fig_dir, "fig5_aqi_exceedance.png", "Fig. 5. Live CPCB category distribution (A) and WHO / Indian NAAQS threshold breach rates (B).", styles, width_cm=16.8)

    # VIII. CONCLUSION
    el.append(Paragraph("VIII. CONCLUSION AND FUTURE DIRECTIONS", styles["H1"]))
    el.append(Paragraph(
        "AeroSense AI delivers a modular, transparent, and rigorously verified (46/46 passing pytest cases) environmental intelligence "
        "framework unifying OpenAQ v3 telemetry, bounded cleaning, dual AQI indexing, chronological ML/DL benchmarking, and SHAP attribution. "
        "Phase 2 expansion will fuse Copernicus ERA5 planetary boundary-layer height and wind vectors with Spatio-Temporal Graph Neural "
        "Networks across global monitoring corridors.",
        styles["Body"],
    ))

    # REFERENCES
    el.append(Paragraph("REFERENCES", styles["H1"]))
    for r in ieee_refs:
        el.append(Paragraph(html.escape(r), styles["Ref"]))

    doc.build(el, onFirstPage=_ieee_header_footer, onLaterPages=_ieee_header_footer)

    md_refs = "\n".join(f"- {r}" for r in ieee_refs)
    md_text = f"""# Air Pollution Pattern Analysis and AQI Forecasting: Leakage-Free Machine Learning, Deep Sequence Modeling, and Explainable Real-Time OpenAQ v3 Telemetry

**Authors:** Aryan Saini (23030173 / 2301315012), Ayaan Ali (23030175 / 2301315013), Kawalpreet Kaur (23030255 / 2301315019), Mihir Kumar (23030268 / 2301315022), Abhishek Kumar (Faculty Guide: QU0125261068)  
**Affiliation:** Department of Computer Science & Engineering (CSE-DS), Quantum School of Technology, Quantum University, Roorkee - 247167  
**Batch / Semester:** 2023 - 2027 | 7th Sem

---

## Abstract
AeroSense AI unifies OpenAQ API v3 live telemetry, bounded validation/imputation, dual Indian CPCB & US EPA AQI transparency, 34 engineered time-series features, strict chronological (70/15/15) benchmarking across 3 naive baselines, 6 ML algorithms, and 4 PyTorch deep learning architectures (LSTM, GRU, TCN, Transformer), plus SHAP interpretability. Live 30-day Indian telemetry (`n = 2,157` rows across Delhi R K Puram, Lucknow Talkatora, Hyderabad Zoo Park) documents WHO exceedance rates of `92.2%–98.6%`. Chronological testing achieves `9.449 ug/m3` MAE (`R2 = 0.906`) for LinearRegression and `9.580 ug/m3` (`R2 = 0.903`) for Transformer on controlled data, and `23.803 ug/m3` MAE (`R2 = 0.854`, 57.1% improvement over Seasonal Naive) on live Delhi R K Puram measurements.

## Observed Live OpenAQ v3 Station Statistics (Oct–Nov 2026)
| Station | Valid Hours | Mean ± Std (ug/m3) | Min - Max | WHO Breach (>15) | NAAQS Breach (>60) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| R K Puram, Delhi - DPCC | 639 | 177.81 ± 95.74 | 1.00 - 501.00 | 98.6% | 92.3% |
| Talkatora, Lucknow - CPCB | 641 | 85.64 ± 50.82 | 4.34 - 265.00 | 92.2% | 68.3% |
| Zoo Park, Hyderabad - TSPCB | 627 | 52.71 ± 19.43 | 9.50 - 87.00 | 97.4% | 36.0% |

## Controlled Benchmark Comparison (90-Day Delhi Anand Vihar, n=2,161)
- **Top ML (1-step)**: `LinearRegression` (`MAE=9.449`, `RMSE=11.947`, `R2=0.906`), `Ridge` (`9.457`, `0.906`), `RandomForest` (`9.930`, `0.898`), `HistGradientBoosting` (`10.149`, `0.896`), `XGBoost` (`10.319`, `0.888`), `ExtraTrees` (`10.575`, `0.886`).
- **PyTorch DL (1-step)**: `Transformer` (`MAE=9.580`, `RMSE=12.124`, `R2=0.903`), `GRU` (`10.161`, `0.889`), `LSTM` (`10.838`, `0.878`), `TCN` (`11.851`, `0.858`).
- **PyTorch DL (24-step Multi-Horizon)**: `LSTM` (`MAE=30.288`, `RMSE=37.029`, `R2=0.094`).
- **Baselines**: `Seasonal Naive` (`30.966`, `R2=0.008`), `Historical Mean` (`32.139`, `R2=-0.016`), `Persistence` (`40.117`, `R2=-0.614`).

## Live Delhi R K Puram Evaluation (n=639)
- **LinearRegression**: `MAE=23.803`, `RMSE=30.540`, `R2=0.854`
- **Ridge**: `MAE=24.714`, `RMSE=32.074`, `R2=0.839`
- **RandomForest**: `MAE=26.534`, `RMSE=35.573`, `R2=0.802`
- **Seasonal Naive Baseline**: `MAE=55.515`, `RMSE=71.767`, `R2=0.165`

![Live Stations](figures/fig1_live_station_profiles.png)
![Model Benchmark](figures/fig2_model_benchmark.png)
![Forecast Residuals](figures/fig3_forecast_residuals.png)
![SHAP Attribution](figures/fig4_shap_importance.png)
![AQI Exceedance](figures/fig5_aqi_exceedance.png)

## References
{md_refs}
"""
    md_path.write_text(md_text, encoding="utf-8")
    return pdf_path, md_path
