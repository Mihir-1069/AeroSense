"""Quantum University formatted Project Synopsis builder (PDF + Markdown)."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.config import settings
from src.reporting.academic_references import get_ieee_references


class _SynopsisDocTemplate(SimpleDocTemplate):
    """Track top-level section starting page numbers relative to body start."""

    def __init__(self, filename: str, section_pages: Dict[str, int], **kwargs):
        super().__init__(filename, **kwargs)
        self.section_pages = section_pages

    def afterFlowable(self, flowable) -> None:
        if isinstance(flowable, Paragraph) and getattr(flowable, "_syn_section", None):
            title = flowable._syn_section
            if title not in self.section_pages:
                # Pages 1-2 are Cover and Index; Abstract starts at display page 01.
                self.section_pages[title] = max(1, self.page - 2)


def _syn_styles() -> dict[str, ParagraphStyle]:
    return {
        "CoverTitle": ParagraphStyle(
            "SynCoverTitle", fontName="Times-Bold", fontSize=17, leading=22,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=14,
        ),
        "CoverSub": ParagraphStyle(
            "SynCoverSub", fontName="Times-Bold", fontSize=12.5, leading=17,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=6,
        ),
        "CoverItalic": ParagraphStyle(
            "SynCoverItalic", fontName="Times-Italic", fontSize=12, leading=16,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=6,
        ),
        "CoverPlain": ParagraphStyle(
            "SynCoverPlain", fontName="Times-Roman", fontSize=11.5, leading=16,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=3,
        ),
        "CoverDept": ParagraphStyle(
            "SynCoverDept", fontName="Times-Bold", fontSize=12, leading=17,
            alignment=TA_CENTER, textColor=colors.black, spaceAfter=3,
        ),
        "IndexTitle": ParagraphStyle(
            "SynIndexTitle", fontName="Times-Bold", fontSize=16, leading=20,
            alignment=TA_CENTER, textColor=colors.black, spaceBefore=6, spaceAfter=16,
        ),
        "H1": ParagraphStyle(
            "SynH1", fontName="Times-Bold", fontSize=14, leading=18,
            alignment=TA_LEFT, textColor=colors.black, spaceBefore=12, spaceAfter=6,
            keepWithNext=True,
        ),
        "H2": ParagraphStyle(
            "SynH2", fontName="Times-Bold", fontSize=12, leading=16,
            alignment=TA_LEFT, textColor=colors.black, spaceBefore=12, spaceAfter=6,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "SynBody", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_JUSTIFY, textColor=colors.black, firstLineIndent=24, spaceAfter=6,
        ),
        "Bullet": ParagraphStyle(
            "SynBullet", fontName="Times-Roman", fontSize=12, leading=18,
            alignment=TA_JUSTIFY, textColor=colors.black, leftIndent=18, spaceAfter=4,
        ),
        "Ref": ParagraphStyle(
            "SynRef", fontName="Times-Roman", fontSize=10.5, leading=15,
            alignment=TA_JUSTIFY, textColor=colors.black, leftIndent=22, firstLineIndent=-22, spaceAfter=4,
        ),
        "Caption": ParagraphStyle(
            "SynCaption", fontName="Times-Italic", fontSize=10.5, leading=14,
            alignment=TA_CENTER, textColor=colors.black, spaceBefore=3, spaceAfter=10,
        ),
        "Formula": ParagraphStyle(
            "SynFormula", fontName="Times-Bold", fontSize=11, leading=16,
            alignment=TA_CENTER, textColor=colors.black, backColor=colors.HexColor("#F4F4F5"),
            spaceBefore=6, spaceAfter=8,
        ),
    }


def _syn_table(data: List[List[str]], col_widths: List[float], font_pt: float = 10.0) -> Table:
    st_head = ParagraphStyle("SynTH", fontName="Times-Bold", fontSize=font_pt, leading=font_pt + 3, alignment=TA_CENTER)
    st_cell = ParagraphStyle("SynTC", fontName="Times-Roman", fontSize=font_pt, leading=font_pt + 3, alignment=TA_LEFT)
    rows = []
    for r_i, row in enumerate(data):
        style = st_head if r_i == 0 else st_cell
        rows.append([Paragraph(html.escape(str(c)), style) for c in row])
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def _draw_syn_footer(canvas, doc) -> None:
    # Unnumbered on Cover (page 1) and INDEX (page 2); numbered 01, 02... from Abstract onward.
    if doc.page <= 2:
        return
    canvas.saveState()
    canvas.setFont("Times-Roman", 11)
    canvas.setFillColor(colors.black)
    canvas.drawCentredString(A4[0] / 2.0, 1.3 * cm, f"{doc.page - 2:02d}")
    canvas.restoreState()


def _section_heading(title: str, styles: dict[str, ParagraphStyle], tag: str) -> Paragraph:
    p = Paragraph(html.escape(title), styles["H1"])
    p._syn_section = tag
    return p


ABSTRACT_TEXT = (
    "Urban air pollution, particularly fine particulate matter with aerodynamic diameter at or below 2.5 micrometers (PM2.5), "
    "constitutes a primary environmental threat to human respiratory and cardiovascular health across rapidly urbanizing "
    "corridors of India and the wider world. Conventional air quality monitoring portals frequently present raw historical plots "
    "without transparent multi-standard Air Quality Index (AQI) decomposition, reproducible missing-value governance, leakage-free "
    "machine learning evaluation, or human-interpretable driver attribution. This project presents AeroSense AI, an end-to-end "
    "modular platform built in Python and Streamlit for real-time global air pollution pattern analysis and predictive AQI forecasting. "
    "The system integrates an authenticated OpenAQ API v3 REST ingestion engine supporting country-level station discovery and "
    "sensor-scoped hourly querying, paired with schema validation, non-negative physical range filtering, Interquartile Range (IQR) "
    "spike suppression, and bounded linear temporal interpolation (up to six hours) with explicit imputation flags stored in "
    "Snappy-compressed Apache Parquet files. Regulatory intelligence is computed across both the Indian Central Pollution Control Board "
    "(CPCB 2014) National Air Quality Index and the US Environmental Protection Agency (US EPA 2018) standards using exact "
    "piecewise-linear sub-index interpolation accompanied by explicit sensor completeness warnings. To eliminate lookahead bias, "
    "AeroSense synthesizes thirty-four leakage-free cyclical calendar harmonics, autoregressive lags, shifted rolling aggregations, "
    "and momentum trends evaluated strictly under chronological 70% training, 15% validation, and 15% held-out testing splits across "
    "three naive baselines, six traditional machine learning regressors (Linear Regression, Ridge, Random Forest, Extra Trees, "
    "Histogram Gradient Boosting, and XGBoost), and four PyTorch deep sequence architectures (LSTM, GRU, Dilated Causal TCN, and "
    "Encoder-only Transformer). Empirical telemetry collected over thirty days across Delhi, Lucknow, and Hyderabad (n = 2,157 hourly "
    "observations) demonstrates severe WHO 24-hour exceedance rates between 92.2% and 98.6%. Under controlled 90-day evaluation "
    "(n = 2,161), one-step Linear Regression (9.449 ug/m3 MAE, R2 = 0.906) and PyTorch Transformer (9.580 ug/m3 MAE, R2 = 0.903) "
    "vastly outperform Seasonal Naive baselines (30.966 ug/m3 MAE). On live Delhi R K Puram telemetry (n = 639), Linear Regression "
    "reaches 23.803 ug/m3 MAE (R2 = 0.854), reducing error by 57.1% relative to Seasonal Naive while revealing why linear models "
    "outperform bounded tree ensembles during severe November smog peaks reaching 501.00 ug/m3. Verified SHAP explanations, public health "
    "audits, automated reporting deliverables, and a 46-test automated QA suite confirm production readiness for academic and policy research."
)

INTRO_SECTIONS: list[tuple[str, str]] = [
    (
        "1.1 Atmospheric Background and Fine Particulate Hazard",
        "Ambient air pollution is recognized by the World Health Organization (WHO) and global epidemiological consortia as the single largest environmental contributor to premature cardiovascular and respiratory morbidity worldwide. Among regulated criteria pollutants—which encompass fine particulate matter (PM2.5), coarse respirable particulate matter (PM10), nitrogen dioxide (NO2), sulfur dioxide (SO2), carbon monoxide (CO), ground-level ozone (O3), and ammonia (NH3)—PM2.5 exerts disproportionate physiological harm because particles smaller than 2.5 micrometers bypass upper nasopharyngeal filtration, penetrate deep into pulmonary alveoli, cross the alveolar-capillary barrier, and enter systemic bloodstream circulation. Chronic and acute exposure triggers endothelial dysfunction, systemic oxidative stress, asthma exacerbation, chronic obstructive pulmonary disease (COPD), ischemic heart disease, stroke, and impaired pediatric lung maturation. In rapidly industrializing South Asian urban basins, populations experience both persistently elevated annual background concentrations and severe episodic autumn-winter haze spikes spanning multiple consecutive weeks."
    ),
    (
        "1.2 Air Quality Dynamics Across the Indo-Gangetic Plain and Global Megacities",
        "India occupies a particularly acute position within global atmospheric pollution dynamics, especially across the densely populated Indo-Gangetic Plain (IGP) stretching from Punjab and Haryana through Delhi, Uttar Pradesh, Bihar, and West Bengal. Bounded to the north by the Himalayan mountain wall, the IGP acts as a topographic basin where wintertime radiative cooling generates shallow nocturnal planetary boundary layers (PBL) and strong low-level thermal inversions. When mixed-layer heights collapse below 200 to 400 meters between late evening and early morning, locally emitted diesel exhaust, power-plant sulfate aerosols, construction dust, brick-kiln smoke, solid-fuel domestic combustion, and regional post-harvest agricultural residue plumes accumulate rapidly near breathing level. Live continuous monitoring observations ingested directly from OpenAQ API v3 during this research (October 17 to November 16, 2026) empirically verify this spatial and diurnal structure: R K Puram in New Delhi recorded a 30-day mean PM2.5 of 177.81 plus or minus 95.74 ug/m3 (peaking at 501.00 ug/m3), Talkatora in Lucknow averaged 85.64 plus or minus 50.82 ug/m3 (peaking at 265.00 ug/m3), and Zoo Park in Hyderabad averaged 52.71 plus or minus 19.43 ug/m3. Diurnal aggregation cleanly captures morning traffic peaks (08:00–10:00 IST), convective midday dilution troughs (13:00–16:00 IST), and steep nocturnal boundary-layer buildup after 19:00 IST. Crucially, while our Phase 1 deployment prioritizes India (ISO country code IN and primary pollutant PM2.5), atmospheric monitoring needs are universal, motivating an extensible architecture able to query any international city or pollutant supported on OpenAQ without altering application source code."
    ),
    (
        "1.3 Regulatory Standards — WHO 2021, Indian CPCB and US EPA Frameworks",
        "Effective communication of raw microgram-per-cubic-meter concentrations to citizens, clinicians, and municipal administrators depends on standardized Air Quality Index (AQI) translation. However, regulatory frameworks diverge substantially in breakpoint thresholds, averaging durations, and category semantics. In September 2021, following extensive dose-response meta-analyses demonstrating cardiovascular harm even at low ambient doses, the WHO tightened its 24-hour PM2.5 Air Quality Guideline to 15 ug/m3 and annual guideline to 5 ug/m3. By contrast, India's Central Pollution Control Board (CPCB 2014) National Air Quality Index adopts a six-category scale ranging from Good (0–50 AQI, corresponding to 0–30 ug/m3 PM2.5 24-hour average) and Satisfactory (51–100 AQI, 31–60 ug/m3—marking the Indian 24-hour NAAQS limit of 60 ug/m3) through Moderate (101–200), Poor (201–300), Very Poor (301–400), and Severe (401–500, exceeding 250 ug/m3 PM2.5). Simultaneously, the US Environmental Protection Agency (US EPA 2018 TAD and 2024 updates) employs distinct concentration breakpoints and six health tiers spanning Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, and Hazardous. A frequent scientific flaw in student dashboards and commercial portals is calculating a single AQI number from one available pollutant (often PM2.5 alone) while presenting it as an official regulatory index without disclosing absent gaseous sensors. AeroSense AI resolves this ambiguity structurally by computing both CPCB and US EPA sub-indices transparently while returning explicit completeness booleans (is_complete) and missing-pollutant lists."
    ),
    (
        "1.4 Real-Time Environmental Telemetry and the OpenAQ API v3 Transition",
        "Acquiring reproducible, verifiable environmental time series programmatically requires interfacing cleanly with open atmospheric data infrastructure. OpenAQ serves as the preeminent global open-data aggregator unifying government regulatory telemetry networks such as CPCB, DPCC, UPPCB, and TSPCB alongside international monitoring agencies. Importantly, OpenAQ permanently retired its unauthenticated v1 and v2 API endpoints, migrating strictly to OpenAQ API v3 with mandatory X-API-Key header authentication and a restructured sensor-centric schema. Unlike v2 endpoints that returned measurements directly under location queries, OpenAQ v3 requires a multi-hop protocol: first discovering active stations via GET /v3/locations filtered by ISO country code and parameter identifiers; second inspecting nested sensor objects to map target pollutants to unique integer sensor_id keys; and third paginating time-bounded series via GET /v3/sensors/{id}/hours or /measurements constrained by UTC ISO-8601 timestamps. Real-world government feeds exhibit irregular sensor dropouts, communication glitches, negative zero-drift noise, unit heterogeneities (ppb vs. ppm vs. ug/m3), and occasional rate-limiting (HTTP 429) or malformed metadata strings. Building an academic-grade data engineering layer therefore demands exponential-backoff retries, full API provenance stamping, physical range enforcement, IQR outlier rejection, and bounded temporal gap handling that never fabricates multi-day sensor blackouts."
    ),
    (
        "1.5 Methodological Flaws in Existing Forecasting Dashboards — Temporal Leakage",
        "Alongside ingestion challenges, applied air quality machine learning research exhibits widespread methodological contamination that compromises real-world reliability. Air pollutant series are strongly non-stationary and positively autocorrelated across consecutive hours (with lag-1 Pearson correlation frequently exceeding 0.85). Yet numerous published notebooks and student projects routinely apply randomized cross-validation or train_test_split(..., shuffle=True) across hourly feature matrices. When rows are randomly shuffled, measurements at timestamps t - 1 and t + 1 sit inside the training fold while timestamp t resides in the test fold, permitting tree ensembles and neural networks to interpolate across adjacent neighbors rather than forecast genuinely unseen future episodes. Similarly, computing rolling means, rolling standard deviations, or scaling statistics across the full unsplit series leaks future mean and variance estimates backward into training inputs. Both practices yield artificially inflated R2 scores exceeding 0.97 during offline evaluation followed by severe degradation when deployed operationally. AeroSense AI enforces strict chronological partitioning (70% earliest observations for training, 15% middle observations for validation and hyperparameter/early-stopping control, and final 15% held-out future observations exclusively for test scoring), shifts all rolling windows strictly onto lag-1 values, and benchmarks every learned model against explicit naive baselines including Persistence, Historical Mean, and 24-hour Seasonal Naive predictors."
    ),
    (
        "1.6 Comparative Modeling Paradigms — Linear, Ensemble ML and Deep Sequence Networks",
        "A central scientific motivation of AeroSense AI is systematically comparing forecasting model families across stationary and non-stationary pollution regimes rather than assuming deep learning or boosted decision trees universally dominate. Traditional tabular machine learning models—Ordinary Least Squares Linear Regression, L2-regularized Ridge Regression, Random Forests, Extremely Randomized Trees (ExtraTrees), Histogram Gradient Boosting, and XGBoost—operate on explicit domain-engineered features encoding circular diurnal/seasonal time phases, short-term autoregressive lags, and momentum differentials. Conversely, end-to-end deep sequence models in PyTorch—Long Short-Term Memory (LSTM), Gated Recurrent Units (GRU), Dilated Causal Temporal Convolutional Networks (TCN), and multi-head Self-Attention Transformers—ingest normalized three-dimensional sliding-window tensors (batch, lookback, 1) directly, learning temporal hierarchy without manual lag selection. Crucially, our empirical findings reveal an essential domain trade-off under acute seasonal drift: during clean stationary autumn-to-winter transitions, linear regressors, ensemble trees, and attention Transformers achieve nearly equivalent accuracy (9.45–9.93 ug/m3 MAE). However, when live Delhi R K Puram PM2.5 escalates past 450–500 ug/m3 in November—far exceeding October training peaks—tree-based ensembles suffer accuracy loss because piecewise-constant leaf averages cannot extrapolate linearly beyond training bounds. Meanwhile, univariate 24-hour direct deep sequence forecasting compounds uncertainty over multi-day horizons when meteorological boundary-layer variables are absent. Presenting these honest comparative diagnostics provides deep educational and research value for final-year data science engineering."
    ),
    (
        "1.7 Explainable AI, Spatial Decision Support and End-to-End Platform Scope",
        "High-stakes environmental forecasting cannot operate solely as an opaque black box when public health advisories, school closures, or traffic curbs depend on predicted indices. Consequently, AeroSense AI embeds unified Explainable AI (XAI) diagnostics supporting native feature importances, model-agnostic permutation importance, LinearSHAP with preprocessing pipeline unwrapping, TreeSHAP additive attributions, and residual distribution audits. Across held-out test evaluations, TreeSHAP confirms that short-term atmospheric persistence (lag_1) and diurnal boundary-layer harmonics (hour_sin, hour) govern instantaneous PM2.5 predictability in physically coherent ways. Complementary geospatial hotspot modules map monitoring stations using MapLibre dark-matter layers, regional Indian geographic contrasts, and geodesic Haversine inter-station proximity matrices, while a Public Health Advisory engine translates exposure levels against WHO 2021 and CPCB NAAQS thresholds into targeted respiratory and indoor air quality directives for vulnerable cohorts. Finally, an automated reporting suite compiles interactive browser views alongside publication-ready Markdown, HTML, ReportLab PDF, and ZIP reproducibility archives. Built around ten decoupled Streamlit pages plus comprehensive automated verification (46 passing unit, pipeline, bootstrap, chart, and headless AppTest UI tests), AeroSense AI delivers a complete, transparent, and extensible blueprint for modern environmental data science."
    ),
    (
        "1.8 Six-Layer Modular Software Architecture, Parquet Lakehouse Governance and Self-Healing Cloud Deployment",
        "To guarantee long-term maintainability, testability, and portability across both local developer workstations and ephemeral cloud hosting environments such as Streamlit Community Cloud, AeroSense AI enforces a strict six-layer modular architecture. Layer 1 (Configuration and Logging Governance in src/config/settings.py and src/utils/logging_config.py) centralizes directory path resolution, chronological split constants (TRAIN_RATIO = 0.70, VAL_RATIO = 0.15), rotating 5-megabyte log handlers, and API credential masking so sensitive keys are never exposed in terminal output or browser widgets. Layer 2 (External Telemetry Acquisition and Data Engineering in src/api/ and src/data/) encapsulates synchronous TLS 1.3 HTTP communication with OpenAQ API v3, two-phase station and sensor-hours discovery, physical domain validation, composite key deduplication, Tukey IQR x 3 extreme spike removal, and bounded <= 6-hour piecewise-linear temporal interpolation. Rather than depending on external relational database servers that complicate deployment, AeroSense AI implements a local-first analytical lakehouse using Snappy-compressed Apache Parquet files divided into immutable raw ingestion snapshots (data/raw/) and validated analytical tables (data/processed/) carrying explicit boolean imputation provenance (is_imputed). Furthermore, because ephemeral cloud containers boot without git-ignored binary Parquet datasets or serialized .pkl model artifacts, we engineered an idempotent self-healing bootstrap service (src/data/bootstrap.py). Invoked at the top of app.py and every analytical page via @st.cache_resource, ensure_ready() automatically synchronizes OPENAQ_API_KEY from st.secrets into runtime environment memory, seeds 90-day reference calibration benchmarks for Delhi Anand Vihar and Mumbai Bandra when data/processed/ is empty, and trains five baseline scikit-learn pipelines in under one second when models/ml/ contains no saved artifacts—while preserving tracked experimental benchmark CSV ledgers in experiments/results/. Layer 3 (Domain Mathematics and Feature Synthesis in src/aqi/ and src/features/) decouples regulatory CPCB and US EPA sub-index calculation and 34-feature/3D-tensor synthesis from downstream estimators. Layer 4 (Machine Learning and PyTorch Deep Sequence Modeling in src/ml/ and src/dl/) unifies three naive baselines, six scikit-learn and XGBoost pipelines, and four custom PyTorch nn.Module sequence architectures under identical chronological evaluation loops. Layer 5 (Explainable AI and Automated Academic Publishing in src/explainability/ and src/reporting/) provides pipeline-unwrapped TreeSHAP, LinearSHAP, permutation importance, residual diagnostics, and automated generation of Quantum University formatted PDF reports, IEEE research papers, synopses, and 16-slide PowerPoint decks. Finally, Layer 6 (Interactive Presentation and Automated Quality Assurance across app.py, pages/01..10, src/visualization/, and tests/) delivers ten specialized analytical workspaces rendered with Plotly MapLibre dark-matter maps and verified continuously by 46 automated Pytest and headless Streamlit AppTest assertions."
    ),
    (
        "1.9 Quantitative Summary of Empirical Benchmarks, Non-Stationary Regime Insights and Team Workstream Integration",
        "The empirical contribution of AeroSense AI rests on rigorous, zero-fabrication benchmarking across both controlled 90-day multi-month reference series (n = 2,161 hourly observations at Delhi Anand Vihar) and live 30-day OpenAQ API v3 telemetry ingested across three physiographically distinct Indian urban airsheds: R K Puram in New Delhi (DPCC station ID 17, n = 639 valid hours, mean 177.81 plus or minus 95.74 ug/m3), Talkatora District Industries Center in Lucknow (CPCB station ID 407, n = 641 valid hours, mean 85.64 plus or minus 50.82 ug/m3), and Zoo Park in Hyderabad (TSPCB station ID 2456, n = 627 valid hours, mean 52.71 plus or minus 19.43 ug/m3). Across the live Indian monitoring cohort, hourly PM2.5 concentrations breached the World Health Organization 24-hour guideline of 15 ug/m3 during 98.6% of monitored hours in Delhi, 92.2% in Lucknow, and 97.4% in Hyderabad, while exceeding India's national 24-hour NAAQS threshold of 60 ug/m3 during 92.3%, 68.3%, and 36.0% of hours respectively. On the controlled 90-day chronological benchmark (1,495 training rows, 309 validation rows, and 309 unseen future test rows), 1-step hourly forecasting models achieved a 61.7% to 69.5% reduction in Mean Absolute Error relative to the 24-hour Seasonal Naive baseline (30.966 ug/m3 MAE, R2 = 0.008), led by Ordinary Least Squares Linear Regression (9.449 ug/m3 MAE, 11.947 ug/m3 RMSE, R2 = 0.906), Ridge Regression (9.457 ug/m3 MAE, R2 = 0.906), PyTorch Encoder-only Transformer (9.580 ug/m3 MAE, 12.124 ug/m3 RMSE, R2 = 0.903), and Random Forest (9.930 ug/m3 MAE, R2 = 0.898). More importantly, chronological evaluation on the live Delhi R K Puram stream exposed a fundamental physical-mathematical divergence during non-stationary November smog episodes reaching 501.00 ug/m3: Linear Regression (23.803 ug/m3 MAE, R2 = 0.854) and Ridge (24.714 ug/m3 MAE, R2 = 0.839) outperformed Random Forest (26.534 ug/m3), Extra Trees (31.829 ug/m3), Histogram Gradient Boosting (32.799 ug/m3), and XGBoost (33.479 ug/m3) by 10% to 29% because regression tree leaves are mathematically constrained to the convex hull of training targets [min(y_train), max(y_train)], whereas linear autoregressive weights extrapolate smoothly along lag_1 and diff_1 gradients. Quantitative TreeSHAP attribution across held-out test instances confirmed that immediate atmospheric inertia (lag_1, mean |SHAP| = 26.91 ug/m3, 74.38% share) and diurnal boundary-layer harmonics (hour_sin = 2.58 ug/m3, hour = 2.09 ug/m3, trend_24 = 1.39 ug/m3) dominate short-term predictability. Execution of this research was structured across four coordinated B.Tech CSE-DS engineering workstreams under the guidance of Mr. Abhishek Kumar (QU0125261068): Aryan Saini (Roll No. 2301315012) engineered the OpenAQ v3 API client, ingestion, validation, cleaning, Parquet storage, and Cloud bootstrap; Ayaan Ali (Roll No. 2301315013) developed the CPCB/US EPA AQI calculators, 34-feature engineering matrix, sequence windowing, and naive baselines; Kawalpreet Kaur (Roll No. 2301315019) implemented and benchmarked the six tabular ML pipelines and four PyTorch deep sequence architectures; and Mihir Kumar (Roll No. 2301315022) built the SHAP explainability module, 10-page Streamlit UI, MapLibre spatial analytics, automated academic reporting generators, and 46-test quality assurance suite."
    ),
]

METHODOLOGY_STEPS = [
    ("Stage 1 — Authenticated OpenAQ v3 Extraction", "Queries GET /v3/locations (ISO filter, parameters_id mapping) and GET /v3/sensors/{id}/hours with X-API-Key authentication, retry with exponential backoff, pagination handling both integer and string meta.found, and full provenance stamping."),
    ("Stage 2 — Validation, Cleaning and Parquet Persistence", "Validates schema columns and physical bounds (e.g., PM2.5 in [0, 1000] ug/m3), deduplicates station-hour keys, suppresses IQR x 3 outliers, normalizes ppb/ppm to ug/m3, resamples hourly with bounded <= 6h linear interpolation (is_imputed), and persists Parquet datasets."),
    ("Stage 3 — Dual-Standard AQI Engine", "Applies piecewise-linear breakpoint interpolation for Indian CPCB (2014) and US EPA (2018) criteria pollutants, resolves the maximum sub-index dominant pollutant, and flags incomplete sensor coverage explicitly via is_complete."),
    ("Stage 4 — Leakage-Free Feature and Sequence Engineering", "Synthesizes trigonometric cyclical features (sin/cos of hour, day-of-week, month), autoregressive lags (1..24h), shifted lag-1 rolling statistics (mean, std, min, max over 3, 6, 12, 24h), and momentum trend_24, plus (N, lookback, 1) tensors scaled using training-only MinMaxScaler."),
    ("Stage 5 — Chronological ML and PyTorch DL Modeling", "Partitions sorted timestamps 70% Train / 15% Val / 15% Test; trains 3 baselines, 6 tabular ML regressors, and 4 PyTorch deep architectures (LSTM, GRU, Dilated Causal TCN, Transformer) with Adam, ReduceLROnPlateau, gradient clipping, and early stopping."),
    ("Stage 6 — Explainability and Spatial Health Intelligence", "Extracts native tree/linear importances, permutation importance, LinearSHAP/TreeSHAP attributions, residual diagnostics, Haversine station matrices, and WHO/CPCB cohort advisories."),
    ("Stage 7 — Streamlit Cloud Delivery and Academic Reporting", "Exposes all workflows across app.py and 10 interactive pages with auto-bootstrapped offline benchmarks, secrets sync, and automated Markdown/HTML/PDF/PPTX/ZIP export pipelines."),
]

OBJECTIVES_LIST = [
    "Design and implement an authenticated, fault-tolerant OpenAQ API v3 data acquisition client supporting India-first analysis (ISO: IN, PM2.5) with zero-code-rewrite extensibility to international regions.",
    "Build a reproducible data engineering pipeline preserving raw ingestion snapshots separately from validated, outlier-filtered, and bounded-imputed Apache Parquet analytical datasets.",
    "Develop dual-standard Indian CPCB National AQI (2014) and US EPA (2018) calculators providing sub-index decomposition, dominant pollutant detection, and explicit incomplete-panel transparency.",
    "Eliminate temporal data leakage through strict 70% / 15% / 15% chronological splitting and shifted historical rolling features compared rigorously against Persistence, Historical Mean, and 24-hour Seasonal Naive baselines.",
    "Benchmark six tabular Machine Learning algorithms (Linear Regression, Ridge, Random Forest, Extra Trees, HistGradientBoosting, XGBoost) against four PyTorch Deep Sequence models (LSTM, GRU, TCN, Transformer) across controlled and live Delhi telemetry.",
    "Integrate Explainable AI (TreeSHAP, LinearSHAP, Permutation Importance, and residual audits), spatial hotspot mapping, and WHO 2021 public health risk guidance inside a unified 10-page Streamlit UI.",
    "Deliver reproducible documentation, Quantum University formatted thesis deliverables, automated Markdown/HTML/PDF/ZIP reporting, and a passing automated pytest QA suite.",
]


def _word_count(text: str) -> int:
    return len(text.split())


def build_qu_synopsis(team_members: list, meta: dict) -> tuple[Path, Path]:
    """Build Quantum University formatted Synopsis PDF and Markdown companion."""
    assert 300 <= _word_count(ABSTRACT_TEXT) <= 500, f"Abstract word count out of 300-500 bounds: {_word_count(ABSTRACT_TEXT)}"
    intro_words = sum(_word_count(body) for _, body in INTRO_SECTIONS)
    assert intro_words >= 2000, f"Introduction must be >= 2000 words, got {intro_words}"

    styles = _syn_styles()
    pdf_path = settings.REPORTS_DIR / "AeroSense_Project_Synopsis.pdf"
    md_path = settings.REPORTS_DIR / "AeroSense_Project_Synopsis.md"
    fig_dir = settings.REPORTS_DIR / "figures"
    qu_logo = fig_dir / "qu_logo.png"
    ieee_refs = get_ieee_references()

    def _compile(index_pages: Dict[str, int]) -> Dict[str, int]:
        tracked: Dict[str, int] = {}
        doc = _SynopsisDocTemplate(
            str(pdf_path),
            section_pages=tracked,
            pagesize=A4,
            leftMargin=2.5 * cm,
            rightMargin=2.0 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.2 * cm,
        )
        el: list = []

        # PAGE 1 — OFFICIAL QUANTUM UNIVERSITY COVER PAGE
        el.append(Spacer(1, 0.35 * inch))
        el.append(Paragraph("Air Pollution Pattern Analysis and AQI Forecasting", styles["CoverTitle"]))
        el.append(Spacer(1, 0.15 * inch))
        el.append(Paragraph("SYNOPSIS OF THE PROJECT", styles["CoverSub"]))
        el.append(Paragraph("Submitted by", styles["CoverItalic"]))
        el.append(Spacer(1, 0.08 * inch))
        for name, ids, _, _ in team_members:
            clean_ids = ids.replace("ID:", "Student ID:").replace("Roll:", "Roll No:")
            el.append(Paragraph(f"<b>{html.escape(name)}</b> ({html.escape(clean_ids)})", styles["CoverPlain"]))
        el.append(Spacer(1, 0.06 * inch))
        el.append(Paragraph(f"<i>Under the Guidance of {html.escape(meta['guide'])}</i>", styles["CoverPlain"]))
        el.append(Spacer(1, 0.22 * inch))
        el.append(Paragraph("In Partial Fulfillment of the Requirements for<br/>the Degree of", styles["CoverSub"]))
        el.append(Spacer(1, 0.10 * inch))
        el.append(Paragraph("BACHELOR OF TECHNOLOGY", ParagraphStyle("SynDeg", parent=styles["CoverSub"], fontSize=13.5)))
        el.append(Paragraph("7th SEM (CSE-DS) &nbsp;|&nbsp; Batch 2023 - 2027", styles["CoverSub"]))
        el.append(Spacer(1, 0.22 * inch))
        if qu_logo.exists():
            img = Image(str(qu_logo), width=2.2 * inch, height=1.25 * inch)
            img.hAlign = "CENTER"
            el.append(img)
        el.append(Spacer(1, 0.22 * inch))
        el.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", styles["CoverDept"]))
        el.append(Paragraph("QUANTUM SCHOOL OF TECHNOLOGY", styles["CoverDept"]))
        el.append(Paragraph("QUANTUM UNIVERSITY", styles["CoverDept"]))
        el.append(Paragraph("ROORKEE - 247167", styles["CoverDept"]))
        el.append(Spacer(1, 0.25 * inch))
        el.append(Paragraph("Session: 2026-27", styles["CoverSub"]))
        el.append(PageBreak())

        # PAGE 2 — OFFICIAL INDEX PAGE
        el.append(Spacer(1, 0.2 * inch))
        el.append(Paragraph("INDEX", styles["IndexTitle"]))
        topics = [
            "Abstract",
            "Introduction",
            "Problem Analysis / Literature Review",
            "Proposed Methodology",
            "Objectives",
            "References",
        ]
        idx_rows = [["S NO", "Topics", "Page No."]]
        for i, topic in enumerate(topics, start=1):
            pnum = index_pages.get(topic, i)
            idx_rows.append([str(i), topic, f"{pnum:02d}"])
        el.append(_syn_table(idx_rows, [2.2 * cm, 11.3 * cm, 3.0 * cm], font_pt=11.0))
        el.append(PageBreak())

        # PAGE 3+ — BODY SECTIONS (NO COLONS OR UNDERLINES IN HEADINGS)
        el.append(Paragraph("Air Pollution Pattern Analysis and AQI Forecasting", styles["CoverTitle"]))
        el.append(Spacer(1, 0.08 * inch))

        # 1. Abstract (300-500 words)
        el.append(_section_heading("Abstract", styles, "Abstract"))
        el.append(Paragraph(html.escape(ABSTRACT_TEXT), styles["Body"]))

        # 2. Introduction (>= 2000 words)
        el.append(_section_heading("Introduction", styles, "Introduction"))
        for sub_title, sub_body in INTRO_SECTIONS:
            el.append(Paragraph(html.escape(sub_title), styles["H2"]))
            el.append(Paragraph(html.escape(sub_body), styles["Body"]))

        # 3. Problem Analysis / Literature Review (25 papers reviewed)
        el.append(_section_heading("Problem Analysis and Literature Review", styles, "Problem Analysis / Literature Review"))
        el.append(Paragraph(
            "An exhaustive literature survey encompassing 25 peer-reviewed foundational and contemporary studies [1]-[25] was "
            "conducted across epidemiological health assessments, atmospheric dispersion across the Indo-Gangetic Plain, regulatory "
            "index methodologies, machine learning regression, deep sequence modeling, temporal validation rigor, and Explainable AI. "
            "Epidemiological investigations by Chowdhury et al. [8], Guttikunda and Goel [11], and WHO [23] establish the acute mortality "
            "and morbidity burden of PM2.5 across Indian cities, while Archer-Nicholls et al. [1] detail seasonal agricultural biomass and "
            "boundary-layer trapping across northern India. Standard regulatory conversion benchmarks are defined in CPCB (2014) [5] and US EPA (2018) [21], "
            "whereas OpenAQ [18] specifies the sensor-level REST v3 architecture.",
            styles["Body"]
        ))
        el.append(Paragraph(
            "Across predictive modeling literature, early classical ensembles and regularized tree frameworks by Breiman [4], Friedman [9], "
            "Geurts et al. [10], Chen and Guestrin [6], and Ke et al. [13] demonstrated strong non-linear tabular predictive capability, applied "
            "specifically to Delhi and Indian monitoring stations by Sengupta et al. [20], Masood and Ahmad [16], and Nair et al. [17]. "
            "Simultaneously, sequence learning breakthroughs including LSTM by Hochreiter and Schmidhuber [12], GRU by Cho et al. [7], "
            "Dilated Causal TCN by Bai et al. [2], hybrid CNN-LSTM by Qi et al. [19], Attention-TCN by Liu et al. [14], Transformer attention by "
            "Vaswani et al. [22], Informer by Zhou et al. [25], and haze Transformers by Zhang et al. [24] advanced temporal forecasting. "
            "However, Bergmeir and Benitez [3] demonstrated why naive cross-validation leaks temporally dependent series, and Lundberg and Lee [15] "
            "introduced SHAP to counter black-box opacity. Synthesizing these 25 studies exposes three unresolved gaps addressed directly by AeroSense AI: "
            "(1) randomized leakage in student/applied air-quality pipelines, (2) silent omission of partial-sensor AQI disclaimers, and "
            "(3) lack of honest comparison showing when linear regression outperforms bounded trees during extreme pollution surges.",
            styles["Body"]
        ))

        lit_rows = [
            ["Ref", "Authors & Year", "Methodology Focus", "Key Finding & Identified Gap"],
            ["[1]", "Archer-Nicholls et al., 2019", "IGP PM2.5 transport", "Quantified winter inversion episodes; lacks live forecasting UI"],
            ["[2]", "Bai et al., 2018", "Dilated Causal TCN", "Proved TCN causality & parallel speed over RNNs"],
            ["[3]", "Bergmeir & Benitez, 2012", "Time-series CV rigor", "Showed shuffled split leakage on autocorrelated data"],
            ["[4]", "Breiman, 2001", "Random Forests", "Bagged trees robust to variance but bounded in extrapolation"],
            ["[5]", "CPCB, 2014", "Indian National AQI", "Defined 8-pollutant breakpoints; requires partial disclosure"],
            ["[6]", "Chen & Guestrin, 2016", "XGBoost Boosting", "High tabular efficiency; misses extremes past train max"],
            ["[7]", "Cho et al., 2014", "GRU Sequence Cells", "Compact gated recurrence ideal for medium hourly series"],
            ["[8]", "Chowdhury et al., 2019", "Indian Mortality Burden", "Linked ambient PM2.5 to heavy regional mortality across IGP"],
            ["[12]", "Hochreiter & Schmidhuber, 1997", "LSTM Architecture", "Mitigated vanishing gradients; high horizon=24 variance"],
            ["[15]", "Lundberg & Lee, 2017", "SHAP Game Theory", "Unified additive explanations; absent in legacy dashboards"],
            ["[17]", "Nair et al., 2023", "Explainable Indian AQI", "Combined GBDT + SHAP; omitted DL Transformer comparison"],
            ["[22]", "Vaswani et al., 2017", "Self-Attention Transformer", "Global lag context (9.580 MAE on AeroSense benchmark)"],
            ["[24]", "Zhang et al., 2023", "Haze-Regime Transformer", "Highlighted non-stationary haze distribution shifts"],
        ]
        el.append(_syn_table(lit_rows, [1.2 * cm, 3.8 * cm, 4.1 * cm, 7.4 * cm], font_pt=9.0))
        el.append(Spacer(1, 6))

        # 4. Proposed Methodology
        el.append(_section_heading("Proposed Methodology", styles, "Proposed Methodology"))
        el.append(Paragraph(
            "AeroSense AI organizes environmental analytics into a seven-stage modular workflow separating data ingestion, cleaning, "
            "regulatory indexing, feature construction, model training, explainable attribution, and multi-page visualization.",
            styles["Body"]
        ))
        el.append(_syn_table(
            [["Pipeline Stage", "Engineering Specification & Design Guarantee"]] + [[s, d] for s, d in METHODOLOGY_STEPS],
            [4.8 * cm, 11.7 * cm],
            font_pt=9.5,
        ))
        el.append(Spacer(1, 6))
        el.append(Paragraph("I_p = round( ((I_hi - I_lo) / (BP_hi - BP_lo)) * (C_p - BP_lo) + I_lo );   AQI = max_p(I_p)", styles["Formula"]))
        uml_path = fig_dir / "fig6_uml_system_design.png"
        if uml_path.exists():
            el.append(Image(str(uml_path), width=6.1 * inch, height=4.2 * inch))
            el.append(Paragraph("Figure 1  End-to-End AeroSense AI Data Flow, UML Architecture and Execution Control Flow", styles["Caption"]))

        # 5. Objectives
        el.append(_section_heading("Objectives", styles, "Objectives"))
        for idx, obj in enumerate(OBJECTIVES_LIST, start=1):
            el.append(Paragraph(f"{idx}. {html.escape(obj)}", styles["Bullet"]))

        # 6. References (25 IEEE references matching sample Page 4)
        el.append(_section_heading("References", styles, "References"))
        for ref in ieee_refs:
            el.append(Paragraph(html.escape(ref), styles["Ref"]))

        doc.build(el, onFirstPage=_draw_syn_footer, onLaterPages=_draw_syn_footer)
        return tracked

    pass1_pages = _compile({})
    _compile(pass1_pages)

    # Markdown Synopsis Companion
    team_md = "\n".join(
        f"| {m[0]} | {m[1]} | {m[2]} | {m[3]} |" for m in team_members
    )
    refs_md = "\n".join(f"- {r}" for r in ieee_refs)
    intro_md = "\n\n".join(f"### {t}\n{b}" for t, b in INTRO_SECTIONS)
    obj_md = "\n".join(f"{i}. {o}" for i, o in enumerate(OBJECTIVES_LIST, start=1))

    md_text = f"""# SYNOPSIS OF THE PROJECT
## Air Pollution Pattern Analysis and AQI Forecasting
**Platform Name:** {meta['app_name']} — *"{meta['tagline']}"*  
**Institution:** Department of Computer Science and Engineering, Quantum School of Technology, Quantum University, Roorkee - 247167  
**Degree / Batch / Semester:** Bachelor of Technology (CSE-DS) | Batch 2023 - 2027 | 7th Sem | Session: 2026-27  
**Faculty Assigned:** {meta['guide']}

### Group Members
| Student Name | Student ID & Roll No. | Batch / Sem / Branch | Primary Engineering Ownership |
| :--- | :--- | :--- | :--- |
{team_md}

---

## Abstract
{ABSTRACT_TEXT}

## Introduction
{intro_md}

## Problem Analysis and Literature Review
Reviewed 25 peer-reviewed publications [1]-[25] spanning Indo-Gangetic Plain aerosol physics, CPCB/US EPA/WHO standards, OpenAQ v3 telemetry, temporal cross-validation rigor, ensemble ML bounds, PyTorch LSTM/GRU/TCN/Transformer modeling, and SHAP interpretability.

## Proposed Methodology
""" + "\n".join(f"- **{s}:** {d}" for s, d in METHODOLOGY_STEPS) + f"""

## Objectives
{obj_md}

## References
{refs_md}
"""
    md_path.write_text(md_text, encoding="utf-8")
    return pdf_path, md_path
