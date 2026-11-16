# 🌬️ AeroSense AI

**AeroSense: Intelligent Global Air Quality Monitoring, Analysis and Forecasting Using Machine Learning and Deep Learning**

> *Understand Pollution. Predict Tomorrow. Build a Cleaner Future.*

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/Deep%20Learning-PyTorch-EE4C2C.svg)](https://pytorch.org/)
[![OpenAQ](https://img.shields.io/badge/Data-OpenAQ%20API%20v3-00D4FF.svg)](https://docs.openaq.org/)

---

## 🎯 Project Overview

**AeroSense AI** is a modular, research-oriented environmental intelligence and air quality forecasting platform designed with an **India-first** implementation (`IN` / PM2.5) and global scalability across countries via **OpenAQ API v3**.

Built as a production-grade multi-page **Streamlit** application suitable for final-year **B.Tech Data Science** submission, academic research, and reproducible ML/DL benchmarking, the platform strictly separates data acquisition, validation, cleaning, feature engineering, AQI computation, ML/DL modeling, explainability, reporting, and presentation logic.

### Key Capabilities
1. **Real-Time & Historical OpenAQ v3 Integration (`src/api/openaq_client.py`)**: Authenticated REST client (`X-API-Key`) supporting `/v3/locations` (`iso` & `parameters_id` discovery), `/v3/sensors/{id}/hours`, `/v3/sensors/{id}/measurements`, automatic retry with exponential backoff, pagination, and full provenance tracking.
2. **Reproducible Data Pipeline (`src/data/`)**: Automated schema checks, physical bounds validation, deduplication, IQR outlier filtering, temporal gap interpolation, unit normalization, and Apache Parquet persistence. Also includes calibrated Indian reference benchmark datasets (`Delhi - Anand Vihar` and `Mumbai - Bandra`) so all analytics and modeling workflows can be evaluated immediately offline.
3. **Dual-Standard AQI Engine (`src/aqi/`)**: Exact piecewise-linear sub-index interpolation for both **Indian CPCB National AQI (2014)** and **US EPA AQI**, clearly marking partial/indicative AQI when fewer pollutants are available.
4. **Machine Learning Forecasting (`src/ml/`)**: Traditional baselines (`Persistence`, `Historical Mean`, `Seasonal Naive`) alongside `LinearRegression`, `Ridge`, `RandomForest`, `ExtraTrees`, `HistGradientBoosting`, and `XGBoost`, trained with strict **70% / 15% / 15% chronological splits** to eliminate temporal lookahead leakage.
5. **Deep Learning Sequence Modeling (`src/dl/`)**: PyTorch implementations of **LSTM**, **GRU**, **Temporal Convolutional Network (TCN)**, and **Encoder-only Transformer**, with sliding-window sequence generation, `MinMaxScaler`, gradient clipping, LR scheduling, and early stopping.
6. **Explainable AI (`src/explainability/`)**: Native feature importance, permutation importance, SHAP (`TreeExplainer`, `LinearExplainer`, `Explainer`), and residual diagnostics.
7. **Health Risk & Research Reporting (`src/reporting/`, `pages/`)**: WHO 2021 vs. Indian NAAQS compliance auditing, spatial hotspot identification, and automated **Markdown / HTML / PDF / ZIP** research bundle generation.

---

## 🏗️ Modular Project Structure

```text
AeroSense/
├── app.py                                 # Main Streamlit entry point & platform dashboard
├── requirements.txt                       # Python package dependencies
├── .env.example                           # Environment & OpenAQ API key template
├── pages/                                 # 10-page interactive Streamlit interface
│   ├── 01_Global_Data_Explorer.py         # Live OpenAQ v3 extractor & local Parquet explorer
│   ├── 02_Pollution_Analytics.py          # Temporal, statistical, spatial & correlation EDA
│   ├── 03_AQI_Intelligence.py             # CPCB (India) & US EPA multi-pollutant AQI calculators
│   ├── 04_Forecasting_Studio.py           # Interactive ML & DL training studio
│   ├── 05_Model_Benchmarking.py           # Held-out test split leaderboard & metric comparisons
│   ├── 06_Explainable_AI.py               # Feature importance, SHAP values & residual analysis
│   ├── 07_Spatial_Hotspot_Analysis.py     # Geospatial map, hotspot ranking & geodesic distances
│   ├── 08_Health_Risk_and_Advisory.py     # WHO/NAAQS standard audit & vulnerable cohort guidance
│   ├── 09_Research_Reports.py             # Markdown, HTML, PDF & ZIP academic report exporter
│   └── 10_System_Diagnostics.py           # OpenAQ API key editor, connectivity ping, hardware & logs
├── src/
│   ├── config/settings.py                 # Central paths, defaults, API & ML/DL hyperparameters
│   ├── api/openaq_client.py               # OpenAQ v3 HTTP client
│   ├── data/                              # ingestion.py, validation.py, cleaning.py, storage.py, seed_benchmark.py
│   ├── features/                          # feature_engineering.py, sequence_builder.py
│   ├── aqi/                               # cpcb.py, us_epa.py
│   ├── ml/                                # baselines.py, train.py
│   ├── dl/                                # models.py, trainer.py
│   ├── explainability/                    # feature_importance.py
│   ├── visualization/                     # charts.py
│   ├── reporting/                         # report_generator.py
│   └── utils/                             # helpers.py, logging_config.py
├── data/                                  # raw/, processed/, features/, exports/, metadata/
├── models/                                # ml/*.pkl, dl/*.pt
├── experiments/results/                   # Saved benchmark metrics (ml_benchmark_results.csv)
├── tests/                                 # Pytest suite (AQI, features, validation, ML/DL, API, XAI, PDF)
└── docs/                                  # ARCHITECTURE.md, METHODOLOGY.md, BTECH_PROJECT_REPORT.md
```

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure OpenAQ API v3 Key (Optional for Reference Data, Required for Live Queries)
Copy `.env.example` to `.env` and add your free API key from [explore.openaq.org/register](https://explore.openaq.org/register), **or** configure it directly in the **🛠️ System Diagnostics** page inside the Streamlit app:
```env
OPENAQ_API_KEY=your_openaq_api_key_here
```

### 3. Seed Reference Benchmarks (Optional if offline)
```bash
python -m src.data.seed_benchmark
```

### 4. Launch the Application
```bash
streamlit run app.py
```

### 5. Run Automated Tests
```bash
python -m pytest tests/ -v
```

---

## 📊 Observed Benchmark Performance

### Controlled 90-Day Delhi Anand Vihar Benchmark (`n = 2,161`, 70/15/15 Chronological Split)

| Model | Family | Test MAE (µg/m³) | Test RMSE (µg/m³) | Test R² |
| :--- | :--- | :---: | :---: | :---: |
| **LinearRegression** | ML (1-step) | 9.449 | 11.947 | 0.906 |
| **Ridge** | ML (1-step) | 9.457 | 11.948 | 0.906 |
| **Transformer** | PyTorch DL (1-step) | 9.580 | 12.124 | 0.903 |
| **RandomForest** | ML (1-step) | 9.930 | 12.402 | 0.898 |
| **HistGradientBoosting** | ML (1-step) | 10.149 | 12.534 | 0.896 |
| **GRU** | PyTorch DL (1-step) | 10.161 | 12.976 | 0.889 |
| **XGBoost** | ML (1-step) | 10.319 | 13.023 | 0.888 |
| **ExtraTrees** | ML (1-step) | 10.575 | 13.139 | 0.886 |
| **LSTM** | PyTorch DL (1-step) | 10.838 | 13.579 | 0.878 |
| **TCN** | PyTorch DL (1-step) | 11.851 | 14.653 | 0.858 |
| **Seasonal Naive (24h)** | Baseline | 30.966 | 38.726 | 0.008 |

### Live OpenAQ API v3 Delhi R K Puram Telemetry (`n = 639`, Oct–Nov 2026)
- **LinearRegression**: `MAE = 23.803 µg/m³`, `RMSE = 30.540`, `R² = 0.854` (**57.1% MAE reduction** vs. Seasonal Naive `55.515 µg/m³`).

---

## 📁 Academic Deliverables (`reports/`)
All submission-ready project artifacts are populated with the official team & faculty metadata in [reports/](reports/):

### 👨‍🎓 Project Team & Faculty Guide
- **Project Title:** Air Pollution Pattern Analysis and AQI Forecasting *(AeroSense AI)*
- **Institution:** Department of Computer Science & Engineering, Quantum School of Technology, Quantum University, Roorkee - 247167
- **Batch / Current Semester / Branch:** `2023 - 2027` | Semester `7` | `CSE-DS`
- **Faculty Assigned:** `Mr. Abhishek Kumar (QU0125261068)`

| Batch | Student ID | Name | Current Sem. | Branch | Roll No. | Primary Engineering Ownership |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- |
| 2023 - 2027 | 23030173 | **Aryan Saini** | 7 | CSE-DS | 2301315012 | Data Engineering, OpenAQ v3 API & Parquet Pipeline |
| 2023 - 2027 | 23030175 | **Ayaan Ali** | 7 | CSE-DS | 2301315013 | Feature Synthesis, CPCB/EPA AQI Engine & Baselines |
| 2023 - 2027 | 23030255 | **Kawalpreet Kaur** | 7 | CSE-DS | 2301315019 | ML/DL Model Architectures, Training & Benchmarking |
| 2023 - 2027 | 23030268 | **Mihir Kumar** | 7 | CSE-DS | 2301315022 | SHAP Explainability, 10-Page Streamlit UI & Reporting |

- **Project Synopsis**: [AeroSense_Project_Synopsis.pdf](reports/AeroSense_Project_Synopsis.pdf) | [Markdown](reports/AeroSense_Project_Synopsis.md)
- **Presentation Deck (16 Slides)**: [AeroSense_Presentation.pptx](reports/AeroSense_Presentation.pptx)
- **IEEE-Format Research Paper**: [AeroSense_Research_Paper.pdf](reports/AeroSense_Research_Paper.pdf) | [Markdown](reports/AeroSense_Research_Paper.md)
- **Final-Year B.Tech Project Report (Quantum University Format)**: [AeroSense_Final_Project_Report.pdf](reports/AeroSense_Final_Project_Report.pdf) | [Air_Pollution_Pattern_Analysis_and_AQI_Forecasting.pdf](reports/Air_Pollution_Pattern_Analysis_and_AQI_Forecasting.pdf) | [Markdown](reports/AeroSense_Final_Project_Report.md)

## 📚 Documentation
- [System Architecture](docs/ARCHITECTURE.md)
- [Mathematical & Modeling Methodology](docs/METHODOLOGY.md)
- [B.Tech Final-Year Project Report & Viva Guide](docs/BTECH_PROJECT_REPORT.md)
