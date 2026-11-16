# 🎓 Final-Year B.Tech Data Science Project Report

**Assigned Project Title:** Air Pollution Pattern Analysis and AQI Forecasting  
**Institution:** Department of Computer Science & Engineering, Quantum School of Technology, Quantum University, Roorkee - 247167  
**Full Platform Title:** AeroSense: Intelligent Global Air Quality Monitoring, Analysis and Forecasting Using Machine Learning and Deep Learning  
**Application Name:** AeroSense AI  
**Tagline:** *Understand Pollution. Predict Tomorrow. Build a Cleaner Future.*  
**Batch / Current Semester / Branch:** `2023 - 2027` | Semester `7` | `CSE-DS`  
**Faculty Assigned:** `Mr. Abhishek Kumar (QU0125261068)`

### Project Group Members
| Batch | Student ID | Name | Current Sem. | Branch | Roll No. | Primary Engineering Scope |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- |
| 2023 - 2027 | 23030173 | **Aryan Saini** | 7 | CSE-DS | 2301315012 | Data Engineering, OpenAQ v3 API & Parquet Pipeline |
| 2023 - 2027 | 23030175 | **Ayaan Ali** | 7 | CSE-DS | 2301315013 | Feature Synthesis, CPCB/EPA AQI Engine & Baselines |
| 2023 - 2027 | 23030255 | **Kawalpreet Kaur** | 7 | CSE-DS | 2301315019 | ML/DL Model Architectures, Training & Benchmarking |
| 2023 - 2027 | 23030268 | **Mihir Kumar** | 7 | CSE-DS | 2301315022 | SHAP Explainability, 10-Page Streamlit UI & Reporting |

---

## Abstract
Urban air pollution—particularly fine particulate matter ($\text{PM}_{2.5}$)—poses severe cardiopulmonary health risks across rapidly industrializing regions such as the Indo-Gangetic Plain in India. Existing air quality portals often lack integrated exploratory analysis, multi-standard AQI transparency, leakage-free machine learning vs. deep learning benchmarking, and explainable diagnostics in one unified pipeline. **AeroSense AI** addresses this gap through an end-to-end modular Python and Streamlit platform powered by OpenAQ API v3 data, Apache Parquet storage, dual Indian CPCB & US EPA AQI calculators, 6 traditional ML algorithms, 4 PyTorch deep sequence architectures (LSTM, GRU, TCN, Transformer), SHAP explainability, and automated PDF/HTML/Markdown academic reporting.

---

## 1. Problem Statement & Motivation
1. **Fragmented Tooling**: Researchers and public health analysts frequently rely on ad-hoc scripts to convert raw telemetry into cleaned series, regulatory AQI indices, and predictive models.
2. **Temporal Data Leakage in Naive ML Benchmarks**: Standard random train-test splits inflate forecasting accuracy on autocorrelated atmospheric time series.
3. **Lack of Transparency & Provenance**: Monitoring stations rarely measure all 6 criteria pollutants simultaneously; reporting an index without disclosing missing pollutants is scientifically misleading.
4. **Need for India-First, Globally Extensible Architecture**: India faces acute diurnal and seasonal PM2.5 extremes while requiring an architecture that generalizes seamlessly across international ISO country codes.

---

## 2. System Design & Pipeline
The platform implements a 7-stage reproducible workflow:
1. **Ingestion (`src/api/openaq_client.py`, `src/data/ingestion.py`)**: Queries OpenAQ API v3 (`/v3/locations`, `/v3/sensors/{id}/hours`, `/v3/sensors/{id}/measurements`) with retry handling and provenance stamping (`source_provider`, `api_endpoint`, `retrieved_at`).
2. **Validation & Cleaning (`src/data/validation.py`, `src/data/cleaning.py`)**: Performs schema validation, physical range checks, deduplication, IQR $\times 3$ outlier filtering, and bounded temporal interpolation (`is_imputed` tracking).
3. **AQI Intelligence (`src/aqi/cpcb.py`, `src/aqi/us_epa.py`)**: Computes CPCB (2014) and US EPA sub-indices, dominant pollutant identification, and explicit completeness flags (`is_complete`).
4. **Feature Synthesis (`src/features/`)**: Generates cyclical harmonics (`hour_sin/cos`, `dow_sin/cos`, `month_sin/cos`), lagged measurements (`lag_1..lag_24`), and rolling statistics on shifted series (`roll_mean`, `roll_std`, `roll_min`, `roll_max`), plus sliding-window tensors `(N, lookback, 1)` for deep learning.
5. **Model Training & Chronological Evaluation (`src/ml/`, `src/dl/`)**: Strictly separates the timeline into 70% Train / 15% Validation / 15% Held-Out Test.
6. **Explainability (`src/explainability/feature_importance.py`)**: Extracts coefficients/tree importances, permutation importance, SHAP explanations, and residual distributions.
7. **Interactive Delivery & Reporting (`app.py`, `pages/`, `src/reporting/report_generator.py`)**: Exposes all stages across 10 Streamlit pages and generates Markdown, HTML, PDF, and ZIP reproducibility artifacts.

---

## 3. Empirical Benchmark Observations (Delhi Anand Vihar Calibration Series)
On the 90-day hourly $\text{PM}_{2.5}$ benchmark dataset (`delhi_anand_vihar_pm25_benchmark`, `2,161` records, chronological 70/15/15 split), the held-out test split yielded the following observed results:

| Model | Family | Test MAE ($\mu g/m^3$) | Test RMSE ($\mu g/m^3$) | Test $R^2$ | Train Time |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **LinearRegression** | ML | 9.449 | 11.947 | 0.906 | 0.04s |
| **Ridge** | ML | 9.457 | 11.948 | 0.906 | 0.00s |
| **RandomForest** | ML | 9.930 | 12.402 | 0.898 | 0.18s |
| **HistGradientBoosting** | ML | 10.149 | 12.534 | 0.896 | 1.77s |
| **XGBoost** | ML | 10.319 | 13.023 | 0.888 | 2.15s |
| **ExtraTrees** | ML | 10.575 | 13.139 | 0.886 | 0.13s |
| **LSTM (24h lookback → 24h multi-step horizon, 12 epochs)** | DL | 30.288 | 37.029 | 0.094 | — |

### Key Analytical Insight (Great Viva Talking Point)
Why do 1-step lag-based ML regressors (`LinearRegression` / `Ridge` / `RandomForest`) achieve ~$9.45\ \mu g/m^3$ MAE and $R^2 \approx 0.906$, whereas a 24-hour multi-step direct sequence LSTM (`horizon=24`) shows higher MAE (`30.288`) after 12 epochs?
- **Forecast Horizon Difficulty**: Single-step (`t+1` hour) prediction benefits heavily from high 1-hour atmospheric autocorrelation ($\phi_1 \approx 0.85$), making linear/regularized autoregressive models (`Ridge`) extraordinarily accurate for next-hour forecasting. Conversely, predicting an entire **24-hour multi-step trajectory simultaneously (`t+1 ... t+24`)** compounds uncertainty over 24 hours ahead and requires deeper hyperparameter tuning / longer epoch training (`50-100` epochs) with meteorological covariates (wind speed, PBL height, temperature) to surpass autoregressive baselines over multi-day horizons.

---

## 4. Verification & Testing
Automated verification using `pytest tests/ -v` executed **30 test cases** across 6 modules with **30/30 passing**:
- `tests/test_aqi.py` (12 tests): CPCB & US EPA categories, PM10, negative/invalid handling.
- `tests/test_features.py` (2 tests): Feature matrix column creation & DL sequence alignment.
- `tests/test_validation.py` (4 tests): Schema checks, out-of-range rejection, deduplication, bounded interpolation.
- `tests/test_ml_dl.py` (3 tests): ML pipeline training, naive baselines, PyTorch LSTM/GRU/TCN/Transformer forward pass shapes.
- `tests/test_reporting.py` (4 tests): Dataset summary statistics, Markdown, HTML, and ZIP archive exports.
- `tests/test_api_and_explainability.py` (5 tests): OpenAQ v3 `iso` & `/sensors/{id}/hours` queries, auth error handling, SHAP & permutation explainability across `Ridge`/`RandomForest`/`HistGradientBoosting`, and PDF generation.

---

## 5. Viva Voce Preparation Q&A
1. **Why use chronological splitting instead of `train_test_split(shuffle=True)`?**  
   Shuffling leaks future autocorrelated observations (`t+1`, `t+2`) into the training set, making models memorize nearby points rather than generalize forward in time.
2. **How does AeroSense handle OpenAQ API v3 differences compared to v2?**  
   OpenAQ v3 enforces `X-API-Key` header authentication, queries `/v3/locations` with `iso` country codes, extracts sensor IDs from the `sensors` array, and fetches measurements via `/v3/sensors/{id}/hours` with `datetime_from` / `datetime_to`.
3. **Why flag `is_complete` in AQI calculations?**  
   Regulatory AQI (CPCB) officially requires minimum pollutant coverage (typically PM2.5 or PM10 plus two additional gaseous pollutants). When a station only deploys a PM2.5 sensor, AeroSense reports an *indicative partial AQI* rather than falsely claiming official full-panel AQI status.
4. **Why include TCN alongside LSTM/GRU/Transformer?**  
   Temporal Convolutional Networks use dilated causal 1-D convolutions, allowing parallelized sequence processing during training without vanishing recurrent gradients while strictly respecting temporal causality.
