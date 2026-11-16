# PROJECT SYNOPSIS
## AeroSense: Intelligent Global Air Quality Monitoring, Analysis and Forecasting Using Machine Learning and Deep Learning
**Application Name:** AeroSense AI — *"Understand Pollution. Predict Tomorrow. Build a Cleaner Future."*  
**Institution:** [University / Institute Name Placeholder] | **Department:** [Department Name Placeholder] | **Session:** [Academic Year 2025-2026]

### Group Members (4 Students)
| Member Name | Roll No. / ID | Email | Role |
| :--- | :--- | :--- | :--- |
| [Member 1 Full Name] | [Roll No. / USN 1] | [Email 1] | Data Engineering, OpenAQ v3 API & Parquet Pipeline |
| [Member 2 Full Name] | [Roll No. / USN 2] | [Email 2] | Feature Synthesis, CPCB/EPA AQI Engine & Baselines |
| [Member 3 Full Name] | [Roll No. / USN 3] | [Email 3] | ML/DL Model Architectures, Training & Benchmarking |
| [Member 4 Full Name] | [Roll No. / USN 4] | [Email 4] | SHAP Explainability, 10-Page Streamlit UI & Reporting |

**Supervisor:** [Prof. / Dr. Guide Name Placeholder, Designation]  
**Head of Department:** [Prof. / Dr. HOD Name Placeholder, Head of Department]

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
