# PROJECT SYNOPSIS
## Air Pollution Pattern Analysis and AQI Forecasting (AeroSense AI: Global Air Pollution Pattern Analysis and AQI Forecasting Using Machine Learning and Deep Learning)
**Application Name:** AeroSense AI — *"Understand Pollution. Predict Tomorrow. Build a Cleaner Future."*  
**Programme:** Department of Computer Science & Engineering (Data Science) [CSE-DS] | **Batch / Sem:** Batch 2023 - 2027 | Semester 7

### Group Members (4 Students)
| Student Name | Student ID & Roll No. | Batch / Sem / Branch | Primary Engineering Ownership |
| :--- | :--- | :--- | :--- |
| Aryan Saini | ID: 23030173 | Roll: 2301315012 | 2023 - 2027 | Sem 7 | CSE-DS | Data Engineering, OpenAQ v3 API & Parquet Pipeline |
| Ayaan Ali | ID: 23030175 | Roll: 2301315013 | 2023 - 2027 | Sem 7 | CSE-DS | Feature Synthesis, CPCB/EPA AQI Engine & Baselines |
| Kawalpreet Kaur | ID: 23030255 | Roll: 2301315019 | 2023 - 2027 | Sem 7 | CSE-DS | ML/DL Model Architectures, Training & Benchmarking |
| Mihir Kumar | ID: 23030268 | Roll: 2301315022 | 2023 - 2027 | Sem 7 | CSE-DS | SHAP Explainability, 10-Page Streamlit UI & Reporting |

**Supervisor:** Mr. Abhishek Kumar (QU0125261068)  
**Head of Department:** Head of Department, CSE (Data Science)

---

### 1. Abstract
AeroSense AI is a modular full-stack data science and forecasting platform integrating live **OpenAQ API v3** environmental telemetry, Apache Parquet data pipelines, **Indian CPCB (2014)** & **US EPA** AQI calculators, 6 Scikit-Learn/XGBoost ML models, 4 PyTorch sequence models (LSTM, GRU, TCN, Transformer), SHAP explainability, and automated reporting across a 10-page Streamlit UI.

### 2. Core Objectives
1. Authenticated OpenAQ v3 ingestion with retry/backoff, pagination, and Parquet provenance.
2. Reproducible validation, IQR outlier filtering, and bounded temporal interpolation (`is_imputed` tracking).
3. Dual-standard CPCB & US EPA AQI calculations with incomplete-panel transparency (`is_complete`).
4. Leakage-free **70% / 15% / 15% chronological splitting** comparing naive baselines, ML regressors, and PyTorch DL architectures.
5. Interactive spatial analysis, WHO/NAAQS health risk advisories, SHAP explanations, and verified **41/41 pytest** quality assurance.

### 3. Key Empirical Findings
- **Delhi Anand Vihar Calibration Series (n=2,161)**: `LinearRegression` (MAE `9.449 µg/m³`, R² `0.906`) and PyTorch `Transformer` (MAE `9.580 µg/m³`, R² `0.903`) outperform naive baselines (`30.966–40.117 MAE`).
- **Live OpenAQ v3 Telemetry (R K Puram, Delhi, n=639)**: `LinearRegression` achieves `23.803 µg/m³` MAE (`R² = 0.854`), reducing forecasting error by **57.1%** over Seasonal Naive (`55.515 µg/m³`).
