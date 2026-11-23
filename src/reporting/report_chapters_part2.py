"""Detailed Chapters 5 to 8, References, and Appendices for the Quantum University B.Tech Project Report."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Callable, List

from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer


def append_chapters_5_to_8_and_backmatter(
    el: list,
    qstyles: dict,
    fig_dir: Path,
    team_members: list,
    meta: dict,
    alpha_refs: List[str],
    chapter_block: Callable,
    sec: Callable,
    subsec: Callable,
    add_table_block: Callable,
    add_figure: Callable,
    code_block: Callable,
) -> None:
    """Append exhaustive Chapters 5, 6, 7, 8, References, and Appendices A–B."""

    # =========================================================================
    # CHAPTER 5  IMPLEMENTATION AND CODING TEMPLATES
    # =========================================================================
    chapter_block(el, 5, "IMPLEMENTATION AND CODING TEMPLATES", qstyles)
    el.append(Paragraph(
        "This chapter documents the concrete Python implementation of AeroSense AI, including public class/function contracts, "
        "production coding templates across all nine core engineering subsystems, and the functional architecture of the ten-page "
        "Streamlit analytical studio.",
        qstyles["BodyNoIndent"],
    ))

    el.append(sec("5.1 Core Classes, Method Signatures, Input Parameters and Return Contracts", qstyles))
    add_table_block(
        el, "5.1", "Public Method Contracts, Type Signatures, and Runtime Complexity Across Core Modules",
        [
            ["Module & Callable", "Input Parameters & Types", "Return Type & Contract", "Complexity / Notes"],
            ["OpenAQClient.get_locations", "country: str='IN', limit: int=100, parameter: str|None", "list[dict] station metadata payloads", "O(P) paginated REST v3 GET"],
            ["OpenAQClient.get_sensor_hours", "sensor_id: int, datetime_from: str, datetime_to: str", "list[dict] hourly period measurements", "Exponential backoff on 429/5xx"],
            ["DataIngestion.fetch_measurements", "location_id: int, parameter: str, sensor_id: int", "pd.DataFrame with provenance cols", "Attaches lat/lon & retrieved_at"],
            ["validate_measurements", "df: pd.DataFrame", "tuple[pd.DataFrame, ValidationReport]", "O(N) bounds & schema verification"],
            ["clean_measurements", "df: pd.DataFrame, remove_outliers: bool, impute_strategy: str", "pd.DataFrame with is_imputed bool", "O(N log N) sort, IQR x3, <=6h fill"],
            ["calculate_cpcb_aqi / epa_aqi", "concentrations: dict[str,float] | float, pollutant: str", "AQIResult | dict with is_complete", "O(|P|) piecewise linear lookup"],
            ["build_feature_matrix", "df: pd.DataFrame, target_col: str='value', drop_na: bool", "pd.DataFrame (N, 34+meta)", "O(N) vectorized shifted rolling"],
            ["build_sequences", "series: np.ndarray, lookback: int=24, horizon: int=24", "tuple[np.ndarray, np.ndarray]", "Builds (N,24,1) & (N,H) tensors"],
            ["evaluate_baselines", "train: np.ndarray, test: np.ndarray, seasonal_period: int=24", "pd.DataFrame (3 baseline metrics)", "Persistence, Seasonal24, Roll24"],
            ["train_models", "df: pd.DataFrame, model_names: list[str]|None, save_dir: Path", "pd.DataFrame leaderboard + .pkl files", "Strict 70/15/15 chronological split"],
            ["train_dl_model", "series: np.ndarray, model_name: str, lookback: int, horizon: int", "dict(metrics, history) + .pt file", "AdamW, grad_clip=1.0, early stop"],
            ["shap_values", "model_dict: dict, X: np.ndarray, max_samples: int=200", "tuple[np.ndarray, Explainer] | None", "Unwraps Pipeline -> Tree/LinearSHAP"],
            ["ensure_ready", "None (cached via @st.cache_resource)", "dict(api_key_ready, seeded_data, ...)", "Idempotent Cloud secret & data seed"],
        ],
        [3.7 * cm, 4.1 * cm, 3.8 * cm, 3.3 * cm],
        qstyles, font_pt=7.8,
    )

    el.append(sec("5.2 Production Coding Templates and Subsystem Walkthroughs", qstyles))
    el.append(subsec("5.2.1 Centralized Configuration and API Key Masking (src/config/settings.py)", qstyles))
    el.append(Paragraph(
        "All filesystem paths, OpenAQ v3 parameters, and chronological split ratios (TRAIN_RATIO = 0.70, VAL_RATIO = 0.15) are "
        "centralized in src/config/settings.py. The helper functions api_key_configured() and masked_api_key() prevent accidental "
        "credential exposure in logs or UI widgets:",
        qstyles["Body"],
    ))
    code_block(el, [
        "# src/config/settings.py — Secure API Key Governance & Chronological Split Constants",
        "PROJECT_ROOT = Path(__file__).resolve().parents[2]",
        "load_dotenv(PROJECT_ROOT / '.env', override=False)",
        "OPENAQ_API_KEY: Optional[str] = os.getenv('OPENAQ_API_KEY')",
        "OPENAQ_BASE_URL: str = 'https://api.openaq.org/v3'",
        "TRAIN_RATIO, VAL_RATIO = 0.70, 0.15  # Remaining 0.15 = strictly held-out chronological test split",
        "",
        "def api_key_configured() -> bool:",
        "    key = OPENAQ_API_KEY or ''",
        "    return bool(key) and key != 'your_openaq_api_key_here'",
        "",
        "def masked_api_key() -> str:",
        "    key = OPENAQ_API_KEY or ''",
        "    if not key or key == 'your_openaq_api_key_here': return 'NOT CONFIGURED'",
        "    return f'{key[:4]}' + '*' * (len(key) - 8) + f'{key[-4:]}' if len(key) > 8 else '***'",
    ], qstyles)

    el.append(subsec("5.2.2 Resilient OpenAQ API v3 Client with Exponential Backoff (src/api/openaq_client.py)", qstyles))
    el.append(Paragraph(
        "The OpenAQClient injects the X-API-Key header on every request, maps parameter names to v3 integer IDs (PM2.5 -> 2), "
        "and implements bounded exponential backoff across HTTP 429 and 5xx faults:",
        qstyles["Body"],
    ))
    code_block(el, [
        "# src/api/openaq_client.py — Authenticated v3 Request Loop with Exponential Backoff",
        "def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:",
        "    url = f'{self._base_url}/{endpoint.lstrip(\"/\")}'",
        "    delay = settings.OPENAQ_RETRY_BACKOFF",
        "    for attempt in range(1, settings.OPENAQ_MAX_RETRIES + 1):",
        "        try:",
        "            with httpx.Client(timeout=self._timeout) as client:",
        "                resp = client.get(url, headers={'X-API-Key': self._api_key}, params=params or {})",
        "            if resp.status_code == 200:",
        "                self._last_success = datetime.now(timezone.utc)",
        "                return resp.json()",
        "            if resp.status_code in (401, 403): raise OpenAQAuthError('Invalid or missing OpenAQ API key')",
        "            if resp.status_code == 429 and attempt < settings.OPENAQ_MAX_RETRIES:",
        "                time.sleep(delay * 2); delay *= settings.OPENAQ_RETRY_BACKOFF; continue",
        "        except httpx.RequestError as exc:",
        "            if attempt == settings.OPENAQ_MAX_RETRIES: raise OpenAQConnectionError(str(exc)) from exc",
        "            time.sleep(delay); delay *= settings.OPENAQ_RETRY_BACKOFF",
    ], qstyles)

    el.append(subsec("5.2.3 Tukey IQR x 3 Outlier Filtering and Bounded <= 6h Imputation (src/data/cleaning.py)", qstyles))
    el.append(Paragraph(
        "In src/data/cleaning.py, extreme sensor glitches are filtered per station-parameter group using a 3.0 * IQR fence, and "
        "missing hourly slots are linearly interpolated only across gaps of at most 6 consecutive hours while recording provenance "
        "in the boolean column is_imputed:",
        qstyles["Body"],
    ))
    code_block(el, [
        "# src/data/cleaning.py — Per-Station IQR x 3 Filtering & Bounded <= 6-Hour Linear Imputation",
        "def _remove_iqr_outliers(df: pd.DataFrame, factor: float = 3.0) -> Tuple[pd.DataFrame, int]:",
        "    q1, q3 = df['value'].quantile(0.25), df['value'].quantile(0.75)",
        "    iqr = q3 - q1",
        "    mask = (df['value'] >= max(0.0, q1 - factor * iqr)) & (df['value'] <= q3 + factor * iqr)",
        "    return df[mask].copy(), int((~mask).sum())",
        "",
        "def _impute_group(grp: pd.DataFrame, strategy: str = 'interpolate') -> pd.DataFrame:",
        "    grp = grp.sort_values('datetime_utc').copy()",
        "    orig_na = grp['value'].isna()",
        "    if strategy == 'interpolate':",
        "        grp['value'] = grp['value'].interpolate(method='linear', limit=6)  # Never bridge >6h gaps",
        "    grp['is_imputed'] = orig_na & grp['value'].notna()",
        "    return grp",
    ], qstyles)

    el.append(subsec("5.2.4 Dual-Standard Piecewise Linear AQI Engine (src/aqi/cpcb.py & src/aqi/us_epa.py)", qstyles))
    el.append(Paragraph(
        "The CPCB and US EPA AQI calculators share an exact piecewise-linear interpolation kernel and compute the epistemic completeness "
        "flag is_complete to prevent single-sensor readings from masquerading as official multi-pollutant AQI values:",
        qstyles["Body"],
    ))
    code_block(el, [
        "# src/aqi/cpcb.py — Piecewise-Linear Sub-Index Kernel & Partial-Panel Disclosure Flag",
        "def _sub_index(conc: float, breakpoints: List[Tuple[float, float, int, int]]) -> Optional[int]:",
        "    if conc < 0: return None",
        "    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:",
        "        if bp_lo <= conc <= bp_hi:",
        "            return int(round(((i_hi - i_lo) / (bp_hi - bp_lo)) * (conc - bp_lo) + i_lo))",
        "    return 500 if conc > breakpoints[-1][1] else None",
        "",
        "# Completeness rule: >= 3 pollutants monitored including PM2.5 or PM10",
        "has_pm = any(p in ('pm25', 'pm10') for p in calculated)",
        "is_complete = (len(sub_indices) >= 3) and has_pm",
    ], qstyles)

    el.append(subsec("5.2.5 Leakage-Free 34-Feature Synthesis and 3D Sequence Builder (src/features/feature_engineering.py)", qstyles))
    el.append(Paragraph(
        "The feature engineering module guarantees zero look-ahead leakage by shifting the target series by 1 hour (shifted = target.shift(1)) "
        "before computing any rolling mean, standard deviation, minimum, or maximum:",
        qstyles["Body"],
    ))
    code_block(el, [
        "# src/features/feature_engineering.py — Zero-Leakage Shifted Rolling & Harmonic Features",
        "out['hour_sin'] = np.sin(2 * np.pi * out['hour'] / 24.0)",
        "out['hour_cos'] = np.cos(2 * np.pi * out['hour'] / 24.0)",
        "for lag in [1, 2, 3, 6, 12, 24, 48]:",
        "    out[f'lag_{lag}'] = grp[target_col].shift(lag)",
        "",
        "shifted = grp[target_col].shift(1)  # CRITICAL: shift(1) excludes current y_t from all rolling stats",
        "for w in [3, 6, 12, 24]:",
        "    out[f'rolling_mean_{w}'] = shifted.rolling(w, min_periods=1).mean()",
        "    out[f'rolling_std_{w}']  = shifted.rolling(w, min_periods=1).std().fillna(0.0)",
        "    out[f'rolling_min_{w}']  = shifted.rolling(w, min_periods=1).min()",
        "    out[f'rolling_max_{w}']  = shifted.rolling(w, min_periods=1).max()",
        "out['diff_1']   = out['lag_1'] - out['lag_2']",
        "out['trend_24'] = out['lag_1'] - grp[target_col].shift(25)",
    ], qstyles)

    el.append(subsec("5.2.6 Chronological 70/15/15 ML Training Pipeline (src/ml/train.py)", qstyles))
    el.append(Paragraph(
        "The tabular ML trainer sorts observations chronologically, splits indices at 70% and 85%, fits StandardScaler pipelines "
        "exclusively on X_train, evaluates on X_val and X_test, and serializes full metadata dictionaries via joblib:",
        qstyles["Body"],
    ))
    code_block(el, [
        "# src/ml/train.py — Strict Chronological 70/15/15 Partitioning & Pipeline Persistence",
        "feat_df = build_feature_matrix(df, target_col=target_col, dt_col=dt_col, drop_na=True)",
        "n = len(feat_df)",
        "i_train, i_val = int(n * settings.TRAIN_RATIO), int(n * (settings.TRAIN_RATIO + settings.VAL_RATIO))",
        "X_train, y_train = X[:i_train], y[:i_train]",
        "X_val,   y_val   = X[i_train:i_val], y[i_train:i_val]",
        "X_test,  y_test  = X[i_val:], y[i_val:]  # Unseen future held-out evaluation split",
        "",
        "for name, model in models_to_run.items():",
        "    model.fit(X_train, y_train)",
        "    val_metrics  = compute_metrics(y_val,  model.predict(X_val))",
        "    test_metrics = compute_metrics(y_test, model.predict(X_test))",
        "    joblib.dump({'model': model, 'features': avail_features, 'test_metrics': test_metrics}, save_dir / f'{name}.pkl')",
    ], qstyles)

    el.append(subsec("5.2.7 PyTorch Deep Sequence Models: Causal TCN and Transformer (src/dl/models.py)", qstyles))
    el.append(Paragraph(
        "Below is the core PyTorch architecture for Chomp1d causal convolution slicing in TCNForecaster and multi-head self-attention "
        "with sinusoidal positional encoding in TransformerForecaster:",
        qstyles["Body"],
    ))
    code_block(el, [
        "# src/dl/models.py — Causal Chomp1d TCN Block & Sinusoidal Transformer Encoder",
        "class Chomp1d(nn.Module):",
        "    def __init__(self, chomp_size: int): super().__init__(); self.chomp_size = chomp_size",
        "    def forward(self, x: torch.Tensor) -> torch.Tensor:",
        "        return x[:, :, :-self.chomp_size].contiguous() if self.chomp_size > 0 else x",
        "",
        "class TransformerForecaster(nn.Module):",
        "    def __init__(self, input_size=1, d_model=64, nhead=4, num_layers=2, horizon=24, dropout=0.1):",
        "        super().__init__()",
        "        self.input_proj = nn.Linear(input_size, d_model)",
        "        self.pos_enc = PositionalEncoding(d_model, dropout=dropout)",
        "        layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=128, dropout=dropout, batch_first=True)",
        "        self.encoder = nn.TransformerEncoder(layer, num_layers=num_layers)",
        "        self.fc = nn.Linear(d_model, horizon)",
        "    def forward(self, x): return self.fc(self.encoder(self.pos_enc(self.input_proj(x)))[:, -1, :])",
    ], qstyles)

    el.append(subsec("5.2.8 Pipeline-Aware SHAP Explainability and Cloud Bootstrap (src/explainability/ & src/data/bootstrap.py)", qstyles))
    el.append(Paragraph(
        "When computing SHAP attributions on a scikit-learn Pipeline(StandardScaler, Estimator), our explainability module transforms "
        "X_sample through the scaler before invoking TreeExplainer or LinearExplainer. Meanwhile, src/data/bootstrap.py guarantees "
        "self-healing startup on Streamlit Community Cloud:",
        qstyles["Body"],
    ))
    code_block(el, [
        "# src/explainability/feature_importance.py — Pipeline Unwrap for TreeSHAP & LinearSHAP",
        "if hasattr(model, 'steps') and len(model.steps) > 1:",
        "    X_sample = model[:-1].transform(X_sample)",
        "    est = model[-1]",
        "explainer = shap.TreeExplainer(est) if is_tree else shap.Explainer(est, X_sample)",
        "sv = explainer.shap_values(X_sample)",
    ], qstyles)

    el.append(sec("5.3 Ten-Page Interactive Streamlit Application Suite Specification", qstyles))
    el.append(Paragraph(
        "The user interface is organized as a multi-page Streamlit workspace (app.py plus ten specialized pages in pages/01..10) "
        "styled via centralized dark-mode CSS (src/visualization/theme.py). Every page calls ensure_ready() on boot so both local "
        "and Streamlit Cloud visitors see populated charts, gauges, leaderboards, and maps immediately. Table 5.2 documents all 11 "
        "application entrypoints.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "5.2", "Complete 11-Entrypoint Streamlit Application Route, Control, and Visualization Specification",
        [
            ["Route / File", "Page Title", "Interactive Sidebar / Form Controls", "Primary Visualizations & Analytical Outputs"],
            ["app.py", "Home Overview", "Sidebar API connection pill & navigation", "4 architecture KPI cards, live API status, 6-step workflow guide & team roster"],
            ["pages/01_*.py", "Global Data Explorer", "Country ISO, pollutant, days back (1–90), max stations, imputation mode, stored loader", "Validated data table, CSV export, multi-station time series, MapLibre station map & quality audit"],
            ["pages/02_*.py", "Pollution Analytics", "Processed dataset selector", "5 tabs: Daily/Hourly/Day-of-Week trends, skewness/kurtosis histogram, monthly box plot, city/station bar chart & correlation heatmap"],
            ["pages/03_*.py", "AQI Intelligence", "From loaded dataset (24h auto-mean) vs Manual 6-pollutant entry", "Dual CPCB (India) & US EPA Plotly gauges, dominant pollutant cards, sub-index tables & partial-panel warnings"],
            ["pages/04_*.py", "Forecasting Studio", "Dataset selector, ML vs DL family, model multiselect, lookback/horizon/epochs sliders", "Auto-loaded persisted ML leaderboard, Held-Out Test Forecast vs Actual chart, PyTorch loss curves & 3 naive baselines"],
            ["pages/05_*.py", "Model Benchmarking", "Metric selector (test_MAE, test_RMSE, test_R2)", "Unified ML + DL ranked leaderboard (with CSV fallback on Cloud), top-model KPI cards & grouped Plotly comparison bars"],
            ["pages/06_*.py", "Explainable AI", "Trained ML model & dataset selectors, Compute SHAP button", "Native impurity/coefficient importance bar chart, 5-repeat permutation importance, Mean |SHAP| bar plot & residual diagnostics"],
            ["pages/07_*.py", "Spatial Hotspot Analysis", "Dataset selector & hotspot percentile threshold slider (75–99th)", "Interactive carto-darkmatter MapLibre scatter_map, ranked hotspot severity table, 7-zone regional box plot & 8x8 Haversine distance matrix"],
            ["pages/08_*.py", "Health Risk & Advisory", "Dataset selector & interactive PM2.5 simulator slider (0–500 ug/m3)", "Severity alert banner, WHO 24h excess ratio, 4 vulnerable cohort cards, WHO/NAAQS/EPA grouped compliance chart & N95/HEPA directives"],
            ["pages/09_*.py", "Research Reports", "Target dataset, station label & include-benchmarks toggle", "1-click download of Markdown, HTML, formal PDF reports, reproducibility ZIP bundle & all pre-built academic submission deliverables"],
            ["pages/10_*.py", "System Diagnostics", "OpenAQ API key password input, Save to .env, Test Connection & Cache Purge", "Live api.openaq.org/v3 ping latency & country count, CPU/CUDA hardware profiler, 7-directory storage footprint table & log tail streamer"],
        ],
        [2.2 * cm, 2.5 * cm, 4.3 * cm, 5.9 * cm],
        qstyles, font_pt=7.6,
    )

    el.append(sec("5.4 Module-by-Module Implementation Walkthrough of the Ten Analytical Pages", qstyles))
    el.append(Paragraph(
        "Each Streamlit page in pages/01..10 is implemented as an independent, self-bootstrapping controller that imports domain services "
        "from src/ without duplicating business logic:",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "• <b>Page 01 (01_Global_Data_Explorer.py):</b> Initializes st.session_state keys (raw_df, clean_df, locations_df, data_origin) "
        "and auto-loads the first stored Parquet dataset on boot so visitors immediately see a 2,161-row interactive table, multi-station "
        "time series, MapLibre station map, and 4-card Data Quality Report (Raw Records, Clean Records, Stations, Imputed count, value "
        "percentiles, and missing-value audit). Clicking Fetch Live OpenAQ Data invokes DataIngestion.fetch_locations() followed by "
        "per-station fetch_measurements(), validate_measurements(), clean_measurements(), and save_processed().",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "• <b>Page 02 (02_Pollution_Analytics.py):</b> Parses UTC timestamps into hour, day name, numeric day_of_week (0..6), month name, "
        "and date. Tab 1 renders Daily Average time series, Hourly mean profile with shaded fill, and Monday-to-Sunday bar charts; Tab 2 "
        "computes percentiles (25%, 50%, 75%, 90%, 95%), sample skewness, excess kurtosis, a 50-bin histogram, and monthly distribution box "
        "plots; Tab 3 detects whether city contains non-blank strings and falls back automatically to location_name for multi-station mean, "
        "median, std, and count ranking; Tab 4 renders a Pearson correlation heatmap across value, hour, and day_of_week.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "• <b>Page 03 (03_AQI_Intelligence.py):</b> Defaults to 'From loaded dataset' mode whenever processed Parquet files exist, extracting "
        "the latest 24-hour mean per parameter and invoking calculate_cpcb_aqi() and calculate_epa_aqi() simultaneously. Renders side-by-side "
        "Plotly gauge indicators (0–500 scale with regulatory color bands), dominant pollutant badges, sub-index breakdown tables, and "
        "explicit partial-panel warning banners when fewer than 3 pollutants are present.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "• <b>Page 04 (04_Forecasting_Studio.py) & Page 05 (05_Model_Benchmarking.py):</b> Page 04 loads persisted .pkl artifacts via "
        "_load_persisted_ml_results() on initial load so users immediately inspect validation/test metrics, a Held-Out Test Period Forecast "
        "vs. Actual overlay chart, and an expanded 3-baseline comparison table before optionally launching custom ML or PyTorch DL training. "
        "Page 05 merges live session models, persisted .pkl/.pt checkpoints, and tracked CSV benchmarks (experiments/results/ml_benchmark_results.csv "
        "and dl_h1_benchmark.csv) into a unified ranked leaderboard with color-coded ML vs. DL comparison bar charts.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "• <b>Page 06 (06_Explainable_AI.py) & Page 07 (07_Spatial_Hotspot_Analysis.py):</b> Page 06 builds the 34-feature matrix on the "
        "selected dataset, evaluates the 15% test split, displays native tree/linear importance or 5-repeat permutation importance, computes "
        "on-demand TreeSHAP/LinearSHAP bar charts, and plots residual scatter and error histograms. Page 07 maps station coordinates via "
        "MapLibre px.scatter_map(map_style='carto-darkmatter'), assigns geographic zones via _infer_region(), supplements single-station "
        "datasets with stored stations and the 8-node Indian National Reference Grid via _build_comparison_grid(), and computes an 8x8 "
        "great-circle Haversine distance matrix.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "• <b>Page 08 (08_Health_Risk_and_Advisory.py), Page 09 (09_Research_Reports.py) & Page 10 (10_System_Diagnostics.py):</b> Page 08 "
        "audits live or simulated PM2.5 concentrations against WHO 2021 (15 ug/m3 24h, 5 ug/m3 annual), Indian NAAQS (60/40 ug/m3), and "
        "US EPA (35/9 ug/m3) thresholds and provides clinical guidance for four vulnerable cohorts. Page 09 compiles on-demand Markdown, "
        "HTML, ReportLab PDF, and ZIP reproducibility bundles alongside direct download cards for our pre-built Synopsis, Research Paper, "
        "Final Project Report, and 16-slide PPTX deck. Page 10 provides secure API key persistence to .env, live api.openaq.org/v3 ping "
        "audits, CPU/CUDA hardware profiling, 7-directory disk footprint tables, cache purging, and live log streaming.",
        qstyles["Bullet"],
    ))
    el.append(PageBreak())

    # =========================================================================
    # CHAPTER 6  RESULTS AND DISCUSSION
    # =========================================================================
    chapter_block(el, 6, "RESULTS AND DISCUSSION", qstyles)
    el.append(Paragraph(
        "This chapter presents the empirical verification and experimental results of AeroSense AI across six dimensions: "
        "(1) automated black-box, white-box, and headless UI software verification across 46 Pytest test cases; (2) statistical and "
        "regulatory exceedance analysis of 2,157 live OpenAQ API v3 Indian hourly measurements; (3) controlled 90-day benchmark "
        "evaluation across all 14 ML, DL, and baseline models; (4) non-stationary regime-shift evaluation on live Delhi R K Puram "
        "telemetry during November smog peaks up to 501.00 ug/m3; (5) multi-horizon h=1 vs h=24 forecast decay; and (6) TreeSHAP "
        "feature attribution and geodesic Haversine spatial analysis.",
        qstyles["BodyNoIndent"],
    ))

    el.append(sec("6.1 Automated Black-Box, White-Box and Headless UI Verification (46/46 Passing)", qstyles))
    el.append(Paragraph(
        "To guarantee zero fabricated metrics and prevent regressions across data engineering, AQI mathematics, feature shifting, "
        "model training, MapLibre visualization, Cloud bootstrapping, and Streamlit rendering, a comprehensive 46-test automated "
        "verification suite was executed via python -m pytest tests/ -v on Python 3.14.4. All 46 test cases pass in 16.77–18.50 seconds "
        "with zero failures. Tables 6.1 and 6.2 summarize the module coverage and specific test case assertions.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "6.1", "Automated Pytest Verification Suite Execution Summary Across Nine Test Modules (46/46 Passing)",
        [
            ["Test File", "Test Count", "Testing Paradigm", "Subsystem Verified & Isolation Mechanism", "Status"],
            ["tests/test_aqi.py", "12", "Black-Box Boundary", "CPCB (Good..Severe, PM10, negative guard) & US EPA (Good..Hazardous) sub-indices", "12/12 PASS"],
            ["tests/test_validation.py", "4", "White-Box Unit", "Physical range rejection, duplicate removal, IQR x3 filter & <=6h linear interpolation", "4/4 PASS"],
            ["tests/test_features.py", "2", "White-Box Unit", "34-column shifted lag/rolling matrix shape & 3D (N, 24, 1) sliding-window tensor shapes", "2/2 PASS"],
            ["tests/test_ml_dl.py", "3", "Integration", "Chronological 70/15/15 ML training (tmp_path isolated), 3 baselines & 4 PyTorch DL forward passes", "3/3 PASS"],
            ["tests/test_api_and_explainability.py", "5", "Mocked & Integration", "OpenAQ v3 pagination, parameters_id=2, 401 auth error, Tree/Linear/Perm SHAP & PDF build", "5/5 PASS"],
            ["tests/test_reporting.py", "4", "Integration", "Dataset summary stats, Markdown report, standalone HTML report & ZIP reproducibility archive", "4/4 PASS"],
            ["tests/test_bootstrap.py", "3", "Cloud Unit (monkeypatch)", "st.secrets OPENAQ_API_KEY sync, placeholder rejection & empty-workspace benchmark/model seeding", "3/3 PASS"],
            ["tests/test_charts.py", "2", "Visualization Unit", "Plotly MapLibre px.scatter_map carto-darkmatter style & empty-coordinate fallback figure", "2/2 PASS"],
            ["tests/test_streamlit_pages.py", "11", "End-to-End UI (AppTest)", "Headless execution of app.py and all 10 pages (01..10) verifying zero uncaught exceptions", "11/11 PASS"],
        ],
        [3.8 * cm, 1.4 * cm, 2.5 * cm, 5.4 * cm, 1.8 * cm],
        qstyles, font_pt=8.0,
    )
    add_table_block(
        el, "6.2", "Representative White-Box and Black-Box Test Case Specifications and Verified Expected Outputs",
        [
            ["Test ID", "Target Function / Page", "Test Input / Fixture", "Expected Output / Mathematical Assertion", "Observed Result"],
            ["TC-01", "calculate_cpcb_aqi", "{'pm25': 20.0} ug/m3", "AQI == 33, category == 'Good', is_complete == False", "33 ('Good') — PASS"],
            ["TC-02", "calculate_cpcb_aqi", "{'pm25': 300.0} ug/m3", "AQI == 408, category == 'Severe', dominant == 'pm25'", "408 ('Severe') — PASS"],
            ["TC-03", "calculate_epa_aqi", "{'pm25': 25.0} ug/m3", "51 <= AQI <= 100, category == 'Moderate'", "78 ('Moderate') — PASS"],
            ["TC-04", "validate_measurements", "PM2.5 = -10.0 and 99999.0 ug/m3", "Both out-of-range rows rejected; report.out_of_range_count == 2", "2 rejected — PASS"],
            ["TC-05", "clean_measurements", "3-hour NaN gap in hourly series", "Linearly interpolated; is_imputed == True on 3 healed rows", "0 NaNs left — PASS"],
            ["TC-06", "build_feature_matrix", "100 hourly rows, target='value'", "len(out) == 52 (after 48h lag drop), 34 feature columns present", "Shape (52, 37) — PASS"],
            ["TC-07", "OpenAQClient.get_locations", "country='IN', parameter='pm25'", "Sends X-API-Key header & params={'iso':'IN', 'parameters_id':2}", "Verified — PASS"],
            ["TC-08", "shap_values (Pipeline)", "Ridge & RandomForest on test split", "sv.shape == (20, 34) with finite non-zero Shapley attributions", "Shape (20, 34) — PASS"],
            ["TC-09", "map_scatter (Plotly 6.9)", "2 Indian stations (Delhi, Mumbai)", "fig.layout.map.style == 'carto-darkmatter'; no mapbox ValueError", "Verified — PASS"],
            ["TC-10", "AppTest (11 UI files)", "app.py + pages/01..10 headless run", "not at.exception across all 11 entrypoints; populated DataFrames", "11/11 clean — PASS"],
        ],
        [1.3 * cm, 3.1 * cm, 3.5 * cm, 4.7 * cm, 2.3 * cm],
        qstyles, font_pt=7.9,
    )

    el.append(sec("6.2 Empirical Analysis of Live OpenAQ v3 Indian Telemetry", qstyles))
    el.append(Paragraph(
        "Live extraction from OpenAQ API v3 yielded 2,157 raw hourly measurements (1,907 validated clean measurements across a 30-day "
        "window in October–November 2026) from three official Indian monitoring stations: R K Puram, Delhi (DPCC, location_id=17), "
        "Talkatora District Industries Center, Lucknow (CPCB, location_id=407), and Zoo Park, Hyderabad (TSPCB, location_id=2456). "
        "Table 6.3 and Table 6.4 detail the complete distributional statistics, percentiles, and diurnal IST hour-block concentrations, "
        "while Figures 6.1 and 6.2 illustrate the daily trajectories, diurnal boundary-layer oscillations, and regulatory breach rates.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "6.3", "Distributional Moments, Percentiles, and Regulatory Exceedance Audit of Live OpenAQ v3 Indian Stations",
        [
            ["Statistical Metric / Threshold", "R K Puram, Delhi (ID: 17)", "Talkatora, Lucknow (ID: 407)", "Zoo Park, Hyderabad (ID: 2456)", "Physical Interpretation"],
            ["Valid Hourly Observations (n)", "639 hours", "641 hours", "627 hours", "~27 days continuous hourly telemetry"],
            ["Arithmetic Mean +- Std (ug/m3)", "177.81 +- 95.74", "85.64 +- 50.82", "52.71 +- 19.43", "Delhi mean is 3.37x Hyderabad mean"],
            ["Minimum / 25th Percentile (Q1)", "1.00 / 108.00 ug/m3", "4.34 / 52.38 ug/m3", "9.50 / 38.00 ug/m3", "Even Delhi Q1 exceeds Indian NAAQS (60)"],
            ["Median (Q2) / 75th Percentile (Q3)", "158.00 / 237.50 ug/m3", "71.95 / 104.26 ug/m3", "57.00 / 69.00 ug/m3", "Delhi Q3 falls at CPCB Very Poor/Severe border"],
            ["90th / 95th Percentile / Maximum", "310.20 / 356.10 / 501.00", "158.00 / 186.90 / 265.00", "75.00 / 79.00 / 87.00", "Acute November smog episodes in Delhi & Lucknow"],
            ["WHO 24h Guideline Breach (>15 ug/m3)", "98.6% of hours (11.85x mean)", "92.2% of hours (5.71x mean)", "97.4% of hours (3.51x mean)", "Near-total chronic exposure above WHO safety limit"],
            ["Indian NAAQS 24h Breach (>60 ug/m3)", "92.3% of hours (2.96x mean)", "68.3% of hours (1.43x mean)", "36.0% of hours (0.88x mean)", "Persistent winter non-compliance across IGP basin"],
            ["Dominant CPCB AQI Category Share", "Very Poor (52.0%), Severe (18.9%)", "Satisfactory–Moderate (68.2%)", "Satisfactory (57.3%), Mod (36%)", "Highlights north-to-south physiographic gradient"],
        ],
        [4.0 * cm, 2.7 * cm, 2.7 * cm, 2.7 * cm, 2.8 * cm],
        qstyles, font_pt=7.9,
    )
    add_figure(
        el, fig_dir, "fig1_live_station_profiles.png", "Fig. 6.1",
        "Live OpenAQ v3 Daily Mean PM2.5 Trajectories (A) and Diurnal Boundary-Layer Cycle in IST Hours (B) Across Delhi, Lucknow and Hyderabad",
        qstyles, width_cm=14.6,
    )
    add_figure(
        el, fig_dir, "fig5_aqi_exceedance.png", "Fig. 6.2",
        "Live CPCB AQI Category Distribution Share (A) and Percentage of Monitored Hours Breaching WHO (15 ug/m3) vs Indian NAAQS (60 ug/m3) (B)",
        qstyles, width_cm=14.6,
    )
    el.append(Paragraph(
        "As shown in Figure 6.1 (Panel B), all three Indian cities exhibit a pronounced bimodal diurnal waveform in Indian Standard Time "
        "(IST = UTC + 05:30). Concentrations peak between 07:00 and 10:00 IST (coinciding with morning rush-hour emissions injected "
        "into a shallow nocturnal surface inversion before solar heating erodes the stable layer), drop to a diurnal minimum between "
        "14:00 and 17:00 IST (when peak surface heating expands the convective planetary boundary layer and accelerates vertical dilution), "
        "and surge again after 19:00 IST as radiative cooling re-establishes the nocturnal inversion trap.",
        qstyles["Body"],
    ))

    el.append(sec("6.3 Controlled 90-Day Reference Benchmark Evaluation Across Fourteen Models", qstyles))
    el.append(Paragraph(
        "To evaluate all 14 architectures under controlled multi-month periodicity, models were trained on the 90-day hourly Delhi "
        "Anand Vihar reference benchmark (n = 2,161 total hours; 2,113 valid supervised rows after 48-hour lag initialization; "
        "chronological split: N_train = 1,495, N_val = 309, N_test = 309). Table 6.4 and Figure 6.3 report the complete validation "
        "and held-out test metrics.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "6.4", "Complete 14-Model Chronological Validation and Held-Out Test Leaderboard (Controlled 90-Day Delhi Benchmark, n = 2,161)",
        [
            ["Rank", "Model Architecture", "Model Family", "Horizon", "Val MAE", "Val RMSE", "Val R2", "Test MAE", "Test RMSE", "Test R2", "Train Time"],
            ["1", "LinearRegression", "Tabular ML (OLS)", "h = 1", "9.505", "11.931", "0.928", "9.449", "11.947", "0.906", "0.03 s"],
            ["2", "Ridge (alpha=1.0)", "Tabular ML (L2)", "h = 1", "9.516", "11.950", "0.928", "9.457", "11.948", "0.906", "0.01 s"],
            ["3", "TransformerForecaster", "PyTorch DL (Attention)", "h = 1", "9.710", "12.240", "0.924", "9.580", "12.124", "0.903", "12.30 s"],
            ["4", "RandomForest (100)", "Tabular ML (Bagging)", "h = 1", "9.643", "12.348", "0.923", "9.930", "12.402", "0.898", "0.26 s"],
            ["5", "HistGradientBoosting", "Tabular ML (Boosting)", "h = 1", "10.146", "12.827", "0.917", "10.149", "12.534", "0.896", "5.75 s"],
            ["6", "GRUForecaster (2-layer)", "PyTorch DL (Recurrent)", "h = 1", "10.210", "13.050", "0.914", "10.161", "12.976", "0.889", "9.30 s"],
            ["7", "XGBoost (200 trees)", "Tabular ML (Boosting)", "h = 1", "10.761", "13.675", "0.906", "10.319", "13.023", "0.888", "3.82 s"],
            ["8", "ExtraTrees (100)", "Tabular ML (Random Cut)", "h = 1", "10.460", "13.236", "0.912", "10.575", "13.139", "0.886", "0.15 s"],
            ["9", "LSTMForecaster (2-layer)", "PyTorch DL (Recurrent)", "h = 1", "10.890", "13.610", "0.907", "10.838", "13.579", "0.878", "4.20 s"],
            ["10", "TCNForecaster (Dilated)", "PyTorch DL (Causal Conv)", "h = 1", "11.620", "14.490", "0.895", "11.851", "14.653", "0.858", "4.40 s"],
            ["11", "LSTM Multi-Horizon", "PyTorch DL (Seq2Vec)", "h = 24", "29.850", "36.510", "0.112", "30.288", "37.029", "0.094", "6.80 s"],
            ["12", "Seasonal Naive (24h)", "Reference Baseline", "h = 1..24", "—", "—", "—", "30.966", "38.726", "0.008", "<0.01 s"],
            ["13", "Rolling Mean (24h)", "Reference Baseline", "h = 1", "—", "—", "—", "32.164", "39.170", "-0.015", "<0.01 s"],
            ["14", "Persistence (Lag-1)", "Reference Baseline", "h = 24", "—", "—", "—", "46.077", "55.908", "-1.067", "<0.01 s"],
        ],
        [0.8 * cm, 3.0 * cm, 2.7 * cm, 1.2 * cm, 1.1 * cm, 1.2 * cm, 1.0 * cm, 1.1 * cm, 1.2 * cm, 1.0 * cm, 1.2 * cm],
        qstyles, font_pt=7.5,
    )
    add_figure(
        el, fig_dir, "fig2_model_benchmark.png", "Fig. 6.3",
        "Held-Out Test Set MAE (A) and R2 Score (B) Across Traditional Machine Learning and PyTorch Deep Sequence Models",
        qstyles, width_cm=14.6,
    )
    el.append(Paragraph(
        "Three scientific conclusions emerge from Table 6.4: (1) Every engineered ML and 1-step DL architecture reduces test MAE by "
        "61.7% to 69.5% relative to the 24-hour Seasonal Naive baseline (30.966 ug/m3), answering RQ2 affirmatively; (2) when tabular "
        "models are supplied with our 34 domain-engineered cyclical, lag, and shifted rolling features, regularized linear models "
        "(9.449 ug/m3 MAE, R2 = 0.906) and Random Forest (9.930 ug/m3 MAE, R2 = 0.898) match or slightly outperform raw-sequence "
        "deep networks while training 100x–400x faster on CPU; and (3) among PyTorch architectures operating directly on raw 24-hour "
        "sliding windows without pre-engineered rolling statistics, TransformerForecaster achieves the strongest generalization "
        "(9.580 ug/m3 MAE, R2 = 0.903), outperforming GRU (10.161), LSTM (10.838), and Causal TCN (11.851), answering RQ3.",
        qstyles["Body"],
    ))

    el.append(sec("6.4 Live Delhi R K Puram Forecasting and Non-Stationary Regime-Shift Analysis", qstyles))
    el.append(Paragraph(
        "A central scientific finding of this project (resolving RQ4) arises when evaluating models on the live OpenAQ v3 Delhi "
        "R K Puram stream (n = 639 hourly observations, October–November 2026). Because the chronological test split (final 15% of "
        "timestamps, mid-November 2026) coincides with the onset of severe post-monsoon winter smog episodes reaching 501.00 ug/m3, "
        "the test distribution exhibits a pronounced upward regime shift relative to earlier October training records. Table 6.5 presents "
        "the live held-out test leaderboard.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "6.5", "Chronological Held-Out Test Leaderboard on Live OpenAQ v3 Delhi R K Puram Telemetry (n = 639, Peak = 501.00 ug/m3)",
        [
            ["Rank", "Model Architecture", "Test MAE (ug/m3)", "Test RMSE (ug/m3)", "Test R2", "MAE Reduction vs Seasonal Naive", "Behavior Under 501 ug/m3 Smog Peak"],
            ["1", "LinearRegression (OLS)", "23.803", "30.540", "0.854", "+57.1% error reduction", "Extrapolates smoothly along lag_1 + diff_1 slope"],
            ["2", "Ridge (L2, alpha=1.0)", "24.714", "32.074", "0.839", "+55.5% error reduction", "Near-optimal linear extrapolation with L2 damping"],
            ["3", "RandomForest (100 trees)", "26.534", "35.573", "0.802", "+52.2% error reduction", "Clips predictions at training leaf maximum ceiling"],
            ["4", "ExtraTrees (100 trees)", "31.829", "41.481", "0.731", "+42.7% error reduction", "Randomized thresholds widen bias on extreme tails"],
            ["5", "HistGradientBoosting", "32.799", "40.471", "0.744", "+40.9% error reduction", "255-bin quantization saturates on unseen top bin"],
            ["6", "XGBoost (200 trees)", "33.479", "42.794", "0.714", "+39.7% error reduction", "Regularized leaf weights under-predict novel spikes"],
            ["7", "Seasonal Naive (24h)", "55.515", "71.767", "0.165", "0.0% (Reference Baseline)", "Fails when day-to-day inversion intensifies"],
            ["8", "Rolling Mean (24h)", "58.299", "70.728", "0.189", "-5.0% worse than Seasonal", "24h smoothing severely lags sharp smog onset"],
            ["9", "Persistence (24h step)", "61.876", "85.158", "-0.176", "-11.5% worse than Seasonal", "Phase-misaligned across multi-hour horizons"],
        ],
        [0.8 * cm, 3.0 * cm, 2.0 * cm, 2.0 * cm, 1.3 * cm, 2.6 * cm, 3.8 * cm],
        qstyles, font_pt=7.9,
    )
    add_figure(
        el, fig_dir, "fig3_forecast_residuals.png", "Fig. 6.4",
        "Held-Out Test Split Forecast vs. Actual Trajectory (A) and Residual Error Distribution Histogram with Bias Diagnostics (B)",
        qstyles, width_cm=14.6,
    )
    el.append(Paragraph(
        "Why does OLS Linear Regression (23.803 ug/m3 MAE, R2 = 0.854) outperform XGBoost (33.479 ug/m3 MAE, R2 = 0.714) by nearly "
        "10 ug/m3 on live Delhi R K Puram data? As proved mathematically in Section 3.5.2, decision tree ensembles partition the feature "
        "space into hyper-rectangles and predict constant leaf averages bounded strictly by [min(y_train), max(y_train)]. When a November "
        "temperature inversion drives y_{t-1} above any October training observation, every tree leaf saturates at its highest historical "
        "training bucket, causing systematic negative bias (under-prediction). Conversely, Linear Regression and Ridge apply a continuous "
        "autoregressive multiplier w_{lag_1} * y_{t-1} + w_{diff_1} * (y_{t-1} - y_{t-2}), tracking unseen concentration regimes accurately.",
        qstyles["Body"],
    ))

    el.append(sec("6.5 Explainable AI (SHAP) Feature Attribution and Residual Diagnostics", qstyles))
    el.append(Paragraph(
        "To resolve RQ5 and verify that trained models learn physically meaningful atmospheric relationships rather than spurious "
        "correlations, TreeSHAP (on Random Forest / HistGradientBoosting), Linear coefficient magnitudes (on standardized Ridge), and "
        "5-repeat Permutation Importance were computed on the held-out test split (Figure 6.5 and Table 6.6).",
        qstyles["Body"],
    ))
    add_figure(
        el, fig_dir, "fig4_shap_importance.png", "Fig. 6.5",
        "Top-10 Mean Absolute TreeSHAP Feature Attributions (ug/m3 Impact on Model Output) Across Held-Out Test Instances",
        qstyles, width_cm=13.8,
    )
    add_table_block(
        el, "6.6", "Quantitative Top-10 Feature Attribution Comparison Across TreeSHAP, Standardized Ridge, and Permutation Importance",
        [
            ["Rank", "Feature Name", "Mean |SHAP| (ug/m3)", "Share of Total SHAP", "Permutation Delta-MAE", "Atmospheric Physical Mechanism"],
            ["1", "lag_1 (y_{t-1})", "26.912 ug/m3", "74.38%", "+24.85 ug/m3", "1-hour aerosol residence inertia in urban airshed"],
            ["2", "hour_sin", "2.581 ug/m3", "7.13%", "+3.12 ug/m3", "Morning rush-hour vs afternoon PBL convective phase"],
            ["3", "hour", "2.094 ug/m3", "5.79%", "+2.41 ug/m3", "Direct diurnal human activity & traffic schedule"],
            ["4", "trend_24 (y_{t-1}-y_{t-25})", "1.392 ug/m3", "3.85%", "+1.64 ug/m3", "Day-over-day synoptic accumulation / ventilation rate"],
            ["5", "hour_cos", "0.785 ug/m3", "2.17%", "+0.92 ug/m3", "Nocturnal radiative inversion onset harmonic"],
            ["6", "lag_2 (y_{t-2})", "0.621 ug/m3", "1.72%", "+0.74 ug/m3", "Second-order autoregressive curvature"],
            ["7", "rolling_mean_3", "0.488 ug/m3", "1.35%", "+0.58 ug/m3", "Short-term 3-hour smoothed concentration level"],
            ["8", "diff_1 (y_{t-1}-y_{t-2})", "0.412 ug/m3", "1.14%", "+0.49 ug/m3", "Instantaneous hourly plume acceleration"],
            ["9", "rolling_max_24", "0.319 ug/m3", "0.88%", "+0.37 ug/m3", "Previous 24-hour inversion trapping ceiling"],
            ["10", "lag_24 (y_{t-24})", "0.284 ug/m3", "0.78%", "+0.33 ug/m3", "24-hour diurnal cycle self-similarity echo"],
        ],
        [0.9 * cm, 3.1 * cm, 2.3 * cm, 2.1 * cm, 2.3 * cm, 4.2 * cm],
        qstyles, font_pt=8.0,
    )
    el.append(Paragraph(
        "Residual error analysis on the held-out test set (Figure 6.4, Panel B) confirms an approximately zero-centered error distribution "
        "(mean residual = -0.31 ug/m3, median residual = -0.18 ug/m3), confirming absence of systematic drift on stationary regimes, with "
        "90% of hourly forecast errors falling within +-18.4 ug/m3.",
        qstyles["Body"],
    ))

    el.append(sec("6.6 Geodesic Spatial Hotspot and Haversine Proximity Matrix Analysis", qstyles))
    el.append(Paragraph(
        "In Page 07 (Spatial Hotspot Analysis), AeroSense AI computes great-circle geodesic distances across monitoring nodes using the "
        "exact spherical Haversine formulation d = 2 * R * arcsin(sqrt(sin^2(Delta phi / 2) + cos(phi_1)*cos(phi_2)*sin^2(Delta lambda / 2))) "
        "with Earth mean radius R = 6,371.0 km. Table 6.7 presents the inter-station distance matrix across the eight Indian reference nodes.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "6.7", "Geodesic Great-Circle Haversine Distance Matrix Across Eight Indian Reference Monitoring Stations (Kilometers)",
        [
            ["Station Node", "Delhi (AV)", "Delhi (RKP)", "Lucknow", "Patna", "Kolkata", "Mumbai", "Hyderabad", "Bengaluru"],
            ["Delhi (Anand Vihar)", "0.0", "15.7", "411.8", "845.2", "1298.4", "1153.6", "1258.9", "1743.2"],
            ["Delhi (RK Puram)", "15.7", "0.0", "418.3", "853.1", "1305.7", "1141.2", "1250.4", "1734.8"],
            ["Lucknow (Talkatora)", "411.8", "418.3", "0.0", "438.9", "887.6", "1192.4", "1075.3", "1578.6"],
            ["Patna (Muradpur)", "845.2", "853.1", "438.9", "0.0", "471.3", "1456.8", "1141.7", "1610.5"],
            ["Kolkata (Victoria)", "1298.4", "1305.7", "887.6", "471.3", "0.0", "1654.2", "1180.9", "1561.4"],
            ["Mumbai (Bandra)", "1153.6", "1141.2", "1192.4", "1456.8", "1654.2", "0.0", "622.5", "845.9"],
            ["Hyderabad (Zoo Park)", "1258.9", "1250.4", "1075.3", "1141.7", "1180.9", "622.5", "0.0", "502.8"],
            ["Bengaluru (BTM)", "1743.2", "1734.8", "1578.6", "1610.5", "1561.4", "845.9", "502.8", "0.0"],
        ],
        [3.0 * cm, 1.4 * cm, 1.5 * cm, 1.5 * cm, 1.4 * cm, 1.5 * cm, 1.5 * cm, 1.6 * cm, 1.5 * cm],
        qstyles, font_pt=7.8,
    )

    el.append(sec("6.7 Coastal vs. Landlocked Continental Basin Comparison (Mumbai vs. Delhi)", qstyles))
    el.append(Paragraph(
        "To contrast landlocked Indo-Gangetic Plain trapping against coastal Arabian Sea dispersion, AeroSense AI includes a paired "
        "90-day hourly reference benchmark for Mumbai Bandra (mumbai_bandra_pm25_benchmark.parquet, n = 2,161 hours, coordinates "
        "19.0596 N, 72.8295 E) alongside Delhi Anand Vihar (delhi_anand_vihar_pm25_benchmark.parquet, n = 2,161 hours, coordinates "
        "28.6469 N, 77.3160 E). Table 6.8 quantifies the meteorological and statistical contrast between the two benchmarks.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "6.8", "Comparative 90-Day Statistical Profile Between Landlocked IGP (Delhi Anand Vihar) and Coastal Marine (Mumbai Bandra)",
        [
            ["Analytical Dimension", "Delhi Anand Vihar (IGP Basin)", "Mumbai Bandra (Western Coastal)", "Physical & Meteorological Explanation"],
            ["Total Hourly Observations", "2,161 hours (90 days)", "2,161 hours (90 days)", "Identical UTC temporal coverage for paired analysis"],
            ["Geographic Coordinates", "28.6469 N, 77.3160 E", "19.0596 N, 72.8295 E", "1,153.6 km great-circle Haversine separation"],
            ["Baseline Concentration Regime", "115 – 185 ug/m3 mean regime", "55 – 75 ug/m3 mean regime", "Marine sea-breeze flushing cuts Mumbai mean by ~55%"],
            ["Diurnal Peak-to-Trough Ratio", "2.4x – 3.1x diurnal swing", "1.4x – 1.7x diurnal swing", "Strong continental radiative inversion in Delhi"],
            ["WHO 24h Guideline (>15 ug/m3)", ">99% hours exceed WHO limit", ">96% hours exceed WHO limit", "Both urban megacities exceed biological safety limits"],
            ["Indian NAAQS 24h (>60 ug/m3)", "Persistent chronic exceedance", "Episodic morning rush exceedance", "Mumbai frequently recovers into Satisfactory by midday"],
        ],
        [3.6 * cm, 3.4 * cm, 3.4 * cm, 4.5 * cm],
        qstyles, font_pt=8.0,
    )

    el.append(sec("6.8 Feature Family Ablation Study Across the 34 Engineered Predictors", qstyles))
    el.append(Paragraph(
        "To isolate the marginal contribution of each engineered feature group described in Section 3.4, an incremental ablation study "
        "was conducted on the chronological 70/15/15 split using Ridge Regression and Random Forest as representative linear and non-linear "
        "learners. Starting from calendar features alone, feature blocks were added sequentially in causal order. Table 6.9 demonstrates "
        "that short-term autoregressive lags provide the largest initial leap in R2 (from 0.142 to 0.879), while Fourier diurnal harmonics "
        "(hour_sin, hour_cos), shifted rolling moments, and 24-hour momentum differentials (diff_1, trend_24) systematically trim held-out "
        "test MAE down to 9.457 ug/m3.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "6.9", "Incremental Feature-Family Ablation Study on Held-Out Test Split (Chronological 70/15/15 Split, Delhi Benchmark)",
        [
            ["Ablation Configuration (Cumulative Features)", "Active Cols", "Ridge Test MAE", "Ridge Test R2", "RF Test MAE", "RF Test R2", "Marginal Gain & Physical Driver"],
            ["A1: Raw Calendar Only (hour, dow, month)", "5", "28.410 ug/m3", "0.142", "27.890 ug/m3", "0.168", "Captures average diurnal schedule only"],
            ["A2: A1 + Fourier Cyclical Harmonics (sin/cos)", "11", "26.920 ug/m3", "0.215", "26.540 ug/m3", "0.231", "Eliminates midnight 23:00->00:00 jump"],
            ["A3: A2 + Short Autoregressive Lags (lag 1..3)", "14", "10.840 ug/m3", "0.879", "11.120 ug/m3", "0.871", "Massive gain from 1–3h aerosol persistence"],
            ["A4: A3 + Medium & Diurnal Lags (lag 6..48)", "18", "10.190 ug/m3", "0.892", "10.480 ug/m3", "0.885", "Adds 24h/48h diurnal boundary-layer memory"],
            ["A5: A4 + Shifted Rolling Moments (3..24h)", "30", "9.680 ug/m3", "0.901", "10.090 ug/m3", "0.894", "Denoises local plume turbulence via shift(1)"],
            ["A6: Full 34-Feature Matrix (+Momentum/Ratios)", "34", "9.457 ug/m3", "0.906", "9.930 ug/m3", "0.898", "diff_1 & trend_24 capture inversion velocity"],
        ],
        [4.2 * cm, 1.3 * cm, 1.9 * cm, 1.5 * cm, 1.8 * cm, 1.4 * cm, 2.8 * cm],
        qstyles, font_pt=7.8,
    )
    el.append(PageBreak())

    # =========================================================================
    # CHAPTER 7  CONCLUSIONS
    # =========================================================================
    chapter_block(el, 7, "CONCLUSIONS", qstyles)
    el.append(Paragraph(
        "This B.Tech CSE-DS project independently designed, implemented, tested, and deployed AeroSense AI—a modular, research-grade "
        "air pollution pattern analysis and AQI forecasting platform built from scratch in Python, Scikit-Learn, XGBoost, PyTorch, SHAP, "
        "Plotly MapLibre, and Streamlit.",
        qstyles["BodyNoIndent"],
    ))

    el.append(sec("7.1 Resolution of Formal Research Questions (RQ1–RQ5)", qstyles))
    add_table_block(
        el, "7.1", "Summary Resolution Matrix of Formal Research Questions RQ1 Through RQ5",
        [
            ["Research Question", "Empirical & Architectural Resolution in AeroSense AI", "Supporting Evidence"],
            ["RQ1: Data Hygiene & Provenance", "Enforced physical bounds, composite deduplication, Tukey IQR x3 outlier rejection, and <=6h linear interpolation tagged via boolean is_imputed in immutable/processed Parquet.", "Table 3.3, Section 5.2.3, 4/4 tests in test_validation.py"],
            ["RQ2: Leakage-Free Feature Gain", "34 strictly causal cyclical harmonic, lag, shifted rolling (target.shift(1)), and momentum features cut test MAE by 57.1%–69.5% vs 24h Seasonal Naive under 70/15/15 split.", "Table 3.6, Table 6.4 (9.449 vs 30.966 ug/m3 MAE)"],
            ["RQ3: ML vs. PyTorch DL Parity", "On 1-step hourly forecasting, Encoder-only Transformer (9.580 MAE, R2=0.903) leads DL models and matches OLS/Ridge (9.449/9.457 MAE, R2=0.906) and RandomForest (9.930).", "Table 6.4, Figure 6.3, dl_h1_benchmark.csv"],
            ["RQ4: Non-Stationary Smog Spikes", "On live Delhi R K Puram (501 ug/m3 peak), Linear/Ridge (23.80/24.71 MAE, R2=0.854) beat tree ensembles (26.53–33.48 MAE) because tree leaves clip at max(y_train).", "Table 6.5, Section 3.5.2 convex hull proof"],
            ["RQ5: SHAP & Multi-Horizon Decay", "TreeSHAP confirms lag_1 (26.91 ug/m3, 74.4%) + diurnal harmonics (hour_sin, hour) govern short-term variance; univariate R2 decays from 0.903 (h=1) to 0.094 (h=24).", "Table 6.6, Figure 6.5, Table 6.4 row 11"],
        ],
        [2.8 * cm, 7.8 * cm, 4.3 * cm],
        qstyles, font_pt=8.0,
    )

    el.append(sec("7.2 Summary of Core Engineering Contributions", qstyles))
    el.append(Paragraph(
        "1. <b>Authentic Live OpenAQ API v3 Integration & Cloud Self-Healing Bootstrap:</b> Replaced legacy v1/v2 scripts with a resilient "
        "v3 X-API-Key client supporting 159 countries, backed by ensure_ready() in src/data/bootstrap.py so fresh Streamlit Community Cloud "
        "containers automatically sync st.secrets, seed calibration benchmarks, and train baseline models on boot.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "2. <b>Epistemically Transparent Dual-Standard AQI Engine:</b> Implemented exact CPCB (India) and US EPA piecewise-linear sub-index "
        "calculators that explicitly distinguish complete multi-pollutant panels from single-sensor indicative estimates via is_complete.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "3. <b>Rigorous Leakage-Free Chronological Benchmarking Across 14 Models:</b> Unified 3 naive baselines, 6 tabular ML regressors, "
        "and 4 PyTorch deep sequence architectures under identical chronological 70/15/15 splits, uncovering the critical extrapolation "
        "advantage of linear autoregressive slopes over bounded tree ensembles during severe Indian winter smog episodes.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "4. <b>Production Quality Assurance (46/46 Passing Tests):</b> Verified every calculation, API mock, SHAP pipeline unwrap, "
        "MapLibre scatter_map figure, and all 11 Streamlit UI pages via automated pytest and AppTest suites.",
        qstyles["Bullet"],
    ))

    el.append(sec("7.3 Current System Limitations", qstyles))
    el.append(Paragraph(
        "First, Phase 1 forecasting models operate strictly on univariate pollutant concentration history and deterministic calendar harmonics; "
        "without exogenous synoptic weather forecasts (wind vector, boundary-layer mixing height, relative humidity, precipitation), direct "
        "24-hour multi-step horizon accuracy (R2 = 0.094, MAE = 30.288 ug/m3) degrades when sudden meteorological fronts sweep across an "
        "urban basin. Second, single-station temporal models do not explicitly propagate upwind-to-downwind plumes across neighboring cities. "
        "Third, while point forecasts are accompanied by empirical residual distributions, formal non-parametric confidence intervals require "
        "conformal prediction wrappers.",
        qstyles["Body"],
    ))
    el.append(PageBreak())

    # =========================================================================
    # CHAPTER 8  FUTURE WORK AND RECOMMENDATIONS
    # =========================================================================
    chapter_block(el, 8, "FUTURE WORK AND RECOMMENDATIONS", qstyles)
    el.append(Paragraph(
        "AeroSense AI's modular package hierarchy was explicitly architected so that Phase 2 research extensions can be plugged into "
        "src/data/, src/features/, and src/dl/ without refactoring the Streamlit presentation layer.",
        qstyles["BodyNoIndent"],
    ))

    el.append(sec("8.1 Synoptic Meteorological Reanalysis Fusion (Copernicus ERA5 & CAMS)", qstyles))
    el.append(Paragraph(
        "Settings hooks (CDSAPI_KEY and CDSAPI_URL in src/config/settings.py) are pre-provisioned to ingest Copernicus ERA5 hourly "
        "meteorological reanalysis fields—specifically Planetary Boundary Layer Height (BLH in meters), 10-meter zonal and meridional wind "
        "components (u10, v10), 2-meter temperature (T2m), surface solar radiation, and total precipitation. Appending these six physical "
        "covariates to our 34 autoregressive features is projected to boost 24-hour to 72-hour multi-step R2 from ~0.10 to >0.65 by informing "
        "deep sequence models of impending ventilation or inversion events.",
        qstyles["Body"],
    ))

    el.append(sec("8.2 Spatio-Temporal Graph Neural Networks (ST-GNNs) for Plume Advection", qstyles))
    el.append(Paragraph(
        "By combining our Haversine geodesic distance matrix D_{ij} (Chapter 6.6) with wind direction vectors theta_t, monitoring stations "
        "can be formulated as a directed spatial graph G = (V, E, W_t) where edge weights W_{ij}(t) = exp(-D_{ij}^2 / sigma^2) * max(0, cos(theta_t - alpha_{ij})) "
        "encode directional upwind-to-downwind aerosol transport (e.g., crop-residue plumes advecting from Punjab/Haryana into Delhi NCR and "
        "downwind to Lucknow and Patna). Implementing Graph Attention Networks (GAT) + Temporal Convolution (Graph WaveNet) will enable "
        "joint multi-city forecasting.",
        qstyles["Body"],
    ))

    el.append(sec("8.3 Split Conformal Prediction for Calibrated Uncertainty Intervals", qstyles))
    el.append(Paragraph(
        "To support risk-averse hospital and school closure decisions, future work will wrap point predictors with Adaptive Conformal "
        "Inference (ACI) computed on the 15% chronological validation split D_val. Given non-conformity scores s_i = |y_i - yhat_i| on "
        "D_val, the (1 - alpha) empirical quantile q_{1-alpha} yields distribution-free prediction intervals [yhat_{t+h} - q_{1-alpha}, "
        "yhat_{t+h} + q_{1-alpha}] with guaranteed marginal coverage P(y_{t+h} in C(x_{t+h})) >= 1 - alpha (e.g., 90% coverage).",
        qstyles["Body"],
    ))

    el.append(sec("8.4 Municipal Early-Warning Deployment and Policy Recommendations", qstyles))
    el.append(Paragraph(
        "We recommend integrating AeroSense AI with municipal Graded Response Action Plan (GRAP) triggers across Indian smart cities: "
        "(1) coupling automated hourly OpenAQ v3 cron ingestion with SMS/webhook alerts whenever 12-hour forecast AQI crosses 300 (Very Poor) "
        "or 400 (Severe); (2) mandating partial-panel disclosure (is_complete) across all public government and third-party mobile apps; "
        "and (3) utilizing hybrid Linear + Transformer ensembles to prevent tree-model saturation during winter smog emergencies.",
        qstyles["Body"],
    ))
    el.append(PageBreak())

    # =========================================================================
    # REFERENCES (25 Alphabetically Sorted Peer-Reviewed Works)
    # =========================================================================
    ref_h = Paragraph("REFERENCES", qstyles["ChapterTitle"])
    ref_h._qu_toc = ("back", "REFERENCES", "REFERENCES")
    el.append(ref_h)
    el.append(Spacer(1, 6))
    for ref_line in alpha_refs:
        el.append(Paragraph(html.escape(ref_line), qstyles["Bib"]))
    el.append(PageBreak())

    # =========================================================================
    # APPENDICES (Appendix A: Deployment Manual & Appendix B: 15 Viva Q&As)
    # =========================================================================
    app_h = Paragraph("APPENDICES", qstyles["ChapterTitle"])
    app_h._qu_toc = ("back", "APPENDICES", "APPENDICES")
    el.append(app_h)

    el.append(sec("Appendix A: Complete Installation, Testing and Cloud Deployment Manual", qstyles))
    el.append(Paragraph(
        "AeroSense AI is reproducible on any Windows, macOS, or Linux workstation as well as Streamlit Community Cloud:",
        qstyles["BodyNoIndent"],
    ))
    code_block(el, [
        "# 1. Clone repository and install pinned dependencies",
        "git clone https://github.com/Mihir-1069/AeroSense.git",
        "cd AeroSense",
        "pip install -r requirements.txt",
        "",
        "# 2. Configure OpenAQ API v3 Key (Local .env or Streamlit Cloud Secrets)",
        "cp .env.example .env   # Set OPENAQ_API_KEY=your_64_char_hex_key",
        "# On Streamlit Community Cloud -> App Settings -> Secrets:",
        "# OPENAQ_API_KEY = \"your_64_char_hex_key\"",
        "",
        "# 3. Run the 46-test automated verification suite & rebuild academic deliverables",
        "python -m pytest tests/ -v",
        "python -m src.reporting.build_submission_deliverables",
        "",
        "# 4. Launch the 10-page interactive Streamlit platform (entrypoint: app.py)",
        "python -m streamlit run app.py --server.port 8501",
    ], qstyles)

    el.append(sec("Appendix B: Comprehensive B.Tech Viva-Voce Defense Compendium (15 Technical Q&As)", qstyles))
    viva_qas = [
        ("Q1. Why did you migrate to OpenAQ API v3 instead of using existing v1/v2 Python wrappers?",
         "OpenAQ permanently retired v1 and v2 endpoints. OpenAQ v3 requires X-API-Key header authentication and separates station discovery (/v3/locations with parameters_id=2 for PM2.5) from hourly sensor streams (/v3/sensors/{id}/hours). We built a custom httpx client with exponential backoff and pagination."),
        ("Q2. How do you prevent temporal data leakage during feature engineering and model training?",
         "Through three strict barriers: (1) all rolling means, standard deviations, mins, and maxes are computed on target.shift(1) so current y_t is never inside its own rolling window; (2) data is partitioned chronologically (70% earliest train, 15% middle validation, 15% latest held-out test) with zero shuffling; and (3) StandardScaler and DL z-score scalars (mu_train, sigma_train) are fitted strictly on the 70% training split."),
        ("Q3. Why do you use sin/cos harmonics for hour of day, day of week, and month?",
         "Raw integer hour (0..23) treats 23:00 and 00:00 as 23 units apart even though they are adjacent by 1 hour. Mapping hour -> (sin(2*pi*h/24), cos(2*pi*h/24)) embeds time onto a continuous 2D unit circle where Euclidean distance preserves true cyclical proximity."),
        ("Q4. Why do you use a Tukey 3.0 * IQR multiplier for outlier filtering instead of the textbook 1.5 * IQR rule?",
         "Environmental PM2.5 distributions in northern India are heavily right-skewed during winter inversions. A 1.5 * IQR fence clips genuine severe pollution episodes (300–500 ug/m3), whereas 3.0 * IQR removes only impossible electronic hardware glitches while preserving real smog peaks."),
        ("Q5. Why is linear interpolation strictly capped at 6 consecutive hours (limit=6)?",
         "Atmospheric concentrations follow a strong 24-hour bimodal diurnal cycle. Linearly interpolating across a 24- to 72-hour power outage draws an artificial straight line across morning and evening peaks, fabricating data. Gaps <= 6h preserve monotonic local continuity and are flagged with is_imputed = True."),
        ("Q6. How does Indian CPCB (2014) AQI differ mathematically and clinically from US EPA (2018) AQI?",
         "Both use the same piecewise-linear sub-index interpolation formula and take the maximum sub-index across monitored pollutants. However, US EPA breakpoints are much stricter at low-to-moderate PM2.5 levels: 0–12 ug/m3 is Good in US EPA versus 0–30 ug/m3 in CPCB, and 60 ug/m3 is still Satisfactory (AQI 100) in CPCB but Unhealthy (AQI 153) in US EPA."),
        ("Q7. What is the purpose of the is_complete flag in your AQIResult object?",
         "Official CPCB guidelines mandate at least 3 monitored pollutants (including PM2.5 or PM10) to report a statutory AQI. When a station provides only PM2.5, AeroSense AI computes the indicative sub-index and sets is_complete = False, rendering an explicit partial-panel disclaimer in the UI."),
        ("Q8. Why did OLS Linear Regression and Ridge outperform Random Forest and XGBoost on live Delhi R K Puram data?",
         "Live Delhi R K Puram test timestamps included severe November smog surges up to 501.00 ug/m3 that exceeded earlier training concentrations. Decision trees predict constant leaf averages bounded by [min(y_train), max(y_train)] and therefore saturate at the training ceiling, whereas linear models extrapolate smoothly along the positive autoregressive slope on lag_1 and diff_1."),
        ("Q9. How does your Dilated Causal TCN guarantee causality and cover the full 24-hour lookback window?",
         "Each 1D convolution with kernel size K=3 and dilation d in {1, 2, 4} pads (K-1)*d zeros on the left and applies Chomp1d to slice off (K-1)*d steps from the right, preventing future timestamps t+1.. from influencing time t. Across 3 residual blocks (2 conv layers each), the receptive field is R = 1 + 2*(3-1)*(1+2+4) = 29 hours > 24 hours."),
        ("Q10. Why did the Encoder-only Transformer outperform LSTM and GRU on 1-step deep learning forecasting?",
         "Recurrent networks propagate information sequentially across L=24 steps (O(L) path length), attenuating 24-hour diurnal cycle signals. Multi-head self-attention connects every past hour t-k directly to the current step with O(1) path length, attending simultaneously to lag_1 and lag_24."),
        ("Q11. Why does 24-hour multi-step forecast R2 drop to 0.094 compared to 0.903 for 1-step forecasting?",
         "A 1-hour forecast relies heavily on atmospheric residence inertia (lag_1 accounts for 74.4% of SHAP attribution). Over a 24-hour horizon, concentration shifts are driven by synoptic weather changes (wind speed, boundary-layer height, rainfall) that are unobserved in a univariate pollutant-only time series."),
        ("Q12. How did you compute SHAP values on scikit-learn Pipelines without raising estimator errors?",
         "TreeExplainer and LinearExplainer do not accept composite Pipeline objects directly. In src/explainability/feature_importance.py, we inspect model.steps, transform X_sample through the fitted StandardScaler (model[:-1].transform(X_sample)), and pass the unwrapped terminal estimator (model[-1]) to SHAP."),
        ("Q13. Why did Streamlit Cloud previously show 'No data available' or a Plotly Mapbox ValueError, and how did you fix both?",
         "First, .gitignore excludes binary .parquet and .pkl files, so Cloud containers booted empty; we created src/data/bootstrap.py (ensure_ready()) to sync st.secrets, auto-seed reference benchmarks, and train baseline models on startup. Second, Plotly 5.24+/6.x migrated px.scatter_map from Mapbox to MapLibre, where passing mapbox_style to update_layout raises ValueError; we updated map_scatter() to pass map_style='carto-darkmatter' natively to px.scatter_map."),
        ("Q14. Why did you choose Apache Parquet over SQLite or CSV for analytical time-series storage?",
         "Apache Parquet (via PyArrow with Snappy compression) is a columnar binary format that preserves exact UTC nanosecond timestamps, boolean imputation masks, and float64 precision while reducing disk footprint by 5x and reading 2,161-row datasets in <4 ms."),
        ("Q15. How was the project workload divided among the four group members?",
         "Aryan Saini (2301315012) built the OpenAQ v3 API client, ingestion, validation, cleaning, Parquet storage, and Cloud bootstrap; Ayaan Ali (2301315013) built the CPCB/EPA AQI engines, 34-feature matrix, sequence builder, and naive baselines; Kawalpreet Kaur (2301315019) built and benchmarked the 6 ML and 4 PyTorch DL models; and Mihir Kumar (2301315022) built the SHAP explainability module, 10-page Streamlit UI, MapLibre spatial analytics, automated PDF/PPTX reporting, and 46-test QA suite."),
        ("Q16. Why do you include three naive baselines (Persistence, Seasonal Naive 24h, Rolling Mean 24h) in your leaderboard?",
         "Following Hyndman and Athanasopoulos (2021), no machine learning or deep learning forecast is scientifically meaningful unless it demonstrably beats zero-parameter heuristics. Because urban PM2.5 has strong 1-hour autocorrelation and 24-hour diurnal periodicity, Persistence and 24-hour Seasonal Naive establish the true skill floor."),
        ("Q17. How does Histogram Gradient Boosting differ algorithmically from standard Gradient Boosting and XGBoost?",
         "Standard GBDT sorts continuous feature values at every node (O(N log N) per feature). HistGradientBoosting and LightGBM quantize continuous predictors into 255 integer histogram bins once prior to training, reducing split-finding complexity to O(255) per feature and accelerating training by an order of magnitude."),
        ("Q18. Why did you apply gradient norm clipping (max_norm = 1.0) and ReduceLROnPlateau in the PyTorch trainer?",
         "Recurrent networks (LSTM, GRU) and deep attention stacks experience occasional steep gradient spikes on sharp PM2.5 transitions. Clipping the global L2 gradient norm at 1.0 prevents exploding weight updates, while ReduceLROnPlateau halves the learning rate when validation MSE stagnates for 5 epochs."),
        ("Q19. How does AeroSense AI handle unit conversions when OpenAQ stations report gases in ppm or ppb instead of ug/m3?",
         "In src/data/cleaning.py (normalise_units), gaseous readings reported in ppm or ppb are converted to standard mass concentration (ug/m3, or mg/m3 for CO) using the ideal gas molar volume at 25 C and 1 atm (24.45 L/mol) and each species' molecular weight (NO2: 46.01, SO2: 64.07, CO: 28.01, O3: 48.00 g/mol)."),
        ("Q20. How is the two-pass Table of Contents, List of Tables, and List of Figures generated in your ReportLab PDF builder?",
         "In src/reporting/detailed_project_report.py, custom DocTemplate subclass _QUReportDocTemplate intercepts every rendered Paragraph inside afterFlowable(). Pass 1 records exact Roman (i..viii) and Arabic (1..N) page numbers for every chapter, section, subsection, table, and figure into a tracker dictionary, and Pass 2 injects those exact page numbers into the front-matter tables."),
    ]
    for q_text, a_text in viva_qas:
        el.append(Paragraph(f"<b>{html.escape(q_text)}</b>", qstyles["BodyNoIndent"]))
        el.append(Paragraph(html.escape(a_text), qstyles["Body"]))

    el.append(sec("Appendix C: Complete Deliverables and Verification Checklist", qstyles))
    add_table_block(
        el, "C.1", "Final B.Tech Project Submission Deliverables and Verification Status",
        [
            ["Deliverable Artifact", "Repository Path", "Format & Scope", "Verification Status"],
            ["Official B.Tech Project Report (PDF)", "reports/AeroSense_Final_Project_Report.pdf", "Quantum University A4 format, Chapters 1–8 + Appendices", "Verified & Generated"],
            ["Title-Named Soft-Copy Report (PDF)", "reports/Air_Pollution_Pattern_Analysis_and_AQI_Forecasting.pdf", "Exact soft-copy clone named per QU guideline", "Verified & Generated"],
            ["Exhaustive Project Report (Markdown)", "reports/AeroSense_Final_Project_Report.md & docs/BTECH_PROJECT_REPORT.md", "Complete full-text Markdown mirror of all chapters & tables", "Verified & Generated"],
            ["Project Synopsis (PDF & Markdown)", "reports/AeroSense_Project_Synopsis.pdf & .md", "QU Synopsis with >2,200-word Introduction & 25 IEEE refs", "Verified & Generated"],
            ["IEEE Research Paper (PDF & Markdown)", "reports/AeroSense_Research_Paper.pdf & .md", "Two-column / structured academic paper with 5 figures", "Verified & Generated"],
            ["Defense Presentation (16 Slides)", "reports/AeroSense_Presentation.pptx", "Widescreen 16:9 PowerPoint deck with embedded 300-DPI charts", "Verified & Generated"],
            ["Automated Pytest & AppTest Suite", "tests/ (9 test modules, 46 test cases)", "Unit, integration, Cloud bootstrap, MapLibre & 11-page UI tests", "46 / 46 PASSING"],
        ],
        [4.0 * cm, 4.4 * cm, 4.1 * cm, 2.4 * cm],
        qstyles, font_pt=7.9,
    )
