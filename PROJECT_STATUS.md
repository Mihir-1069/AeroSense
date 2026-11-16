# AeroSense AI — Project Status

**Project:** Air Pollution Pattern Analysis and AQI Forecasting (AeroSense AI: Intelligent Global Air Quality Monitoring, Analysis and Forecasting Using Machine Learning and Deep Learning)  
**Institution:** Department of Computer Science & Engineering, Quantum School of Technology, Quantum University, Roorkee - 247167  
**Team (Batch 2023 - 2027 | Sem 7 | CSE-DS):** Aryan Saini (`23030173` / `2301315012`), Ayaan Ali (`23030175` / `2301315013`), Kawalpreet Kaur (`23030255` / `2301315019`), Mihir Kumar (`23030268` / `2301315022`)  
**Faculty Assigned:** `Mr. Abhishek Kumar (QU0125261068)`  
**Location:** `c:\Users\mihir\Desktop\AeroSense`  
**Status:** Complete & Verified  

## Component Checklist

- [x] **Core Configuration & Logging**: `src/config/settings.py`, `src/utils/logging_config.py`, `src/utils/helpers.py`, `.env.example`, `.gitignore`, `requirements.txt`
- [x] **OpenAQ API v3 Client**: `src/api/openaq_client.py` (`/locations`, `/sensors/{id}/hours`, `/sensors/{id}/measurements`, `X-API-Key`, retry/backoff, pagination)
- [x] **Data Pipeline**: `src/data/ingestion.py`, `src/data/validation.py`, `src/data/cleaning.py`, `src/data/storage.py`, `src/data/seed_benchmark.py`
- [x] **Benchmark Data Seeded**: `delhi_anand_vihar_pm25_benchmark.parquet` (2,161 rows) & `mumbai_bandra_pm25_benchmark.parquet` (2,161 rows)
- [x] **Feature Store & Sequences**: `src/features/feature_engineering.py`, `src/features/sequence_builder.py`
- [x] **Dual AQI Calculators**: `src/aqi/cpcb.py` (India CPCB 2014), `src/aqi/us_epa.py` (US EPA)
- [x] **ML & DL Forecasting**: `src/ml/baselines.py`, `src/ml/train.py`, `src/dl/models.py`, `src/dl/trainer.py`
- [x] **Persisted Model Artifacts**: 6 ML models (`.pkl`), 1 DL LSTM checkpoint (`.pt`), and `experiments/results/ml_benchmark_results.csv`
- [x] **Explainable AI & Visualization**: `src/explainability/feature_importance.py`, `src/visualization/charts.py`
- [x] **Academic Reporting Engine**: `src/reporting/report_generator.py` (Markdown, HTML, ReportLab PDF, ZIP bundle)
- [x] **10-Page Streamlit Application**: `app.py` + `pages/01` through `pages/10`
- [x] **Automated Testing**: `tests/` (46/46 tests passing via `pytest`, including Streamlit Cloud bootstrap, `map_scatter`, and AppTest smoke checks)
- [x] **Documentation**: `README.md`, `docs/ARCHITECTURE.md`, `docs/METHODOLOGY.md`, `docs/BTECH_PROJECT_REPORT.md`
