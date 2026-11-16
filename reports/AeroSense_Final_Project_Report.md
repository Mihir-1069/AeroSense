# FINAL YEAR PROJECT REPORT
## AeroSense: Intelligent Global Air Quality Monitoring, Analysis and Forecasting Using Machine Learning and Deep Learning
**Platform:** AeroSense AI — *"Understand Pollution. Predict Tomorrow. Build a Cleaner Future."*  
**Institution:** [University / Institute Name Placeholder] | **Department:** [Department Name Placeholder] | **Session:** [Academic Year 2025-2026]

### Project Group Members (4 Students)
| Student Name | Roll No. / USN | Email | Engineering Ownership |
| :--- | :--- | :--- | :--- |
| [Member 1 Full Name] | [Roll No. / USN 1] | [Email 1] | Data Engineering, OpenAQ v3 API & Parquet Pipeline |
| [Member 2 Full Name] | [Roll No. / USN 2] | [Email 2] | Feature Synthesis, CPCB/EPA AQI Engine & Baselines |
| [Member 3 Full Name] | [Roll No. / USN 3] | [Email 3] | ML/DL Model Architectures, Training & Benchmarking |
| [Member 4 Full Name] | [Roll No. / USN 4] | [Email 4] | SHAP Explainability, 10-Page Streamlit UI & Reporting |

**Guide:** [Prof. / Dr. Guide Name Placeholder, Designation] | **HOD:** [Prof. / Dr. HOD Name Placeholder, Head of Department]

---

## Executive Summary & Chapter Guide
This Markdown document accompanies the full multi-chapter PDF thesis ([AeroSense_Final_Project_Report.pdf](AeroSense_Final_Project_Report.pdf)).

### Verified Live OpenAQ v3 Station Statistics (Oct–Nov 2026)
| Station | Valid Hours | Mean ± Std (µg/m³) | Min - Max | WHO Breach (>15) | NAAQS Breach (>60) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| R K Puram, Delhi - DPCC | 639 | 177.81 ± 95.74 | 1.00 - 501.00 | 98.6% | 92.3% |
| Talkatora, Lucknow - CPCB | 641 | 85.64 ± 50.82 | 4.34 - 265.00 | 92.2% | 68.3% |
| Zoo Park, Hyderabad - TSPCB | 627 | 52.71 ± 19.43 | 9.50 - 87.00 | 97.4% | 36.0% |

### Controlled Benchmark (Delhi Anand Vihar, n=2,161, 70/15/15 Split)
- **LinearRegression (h=1)**: `MAE = 9.449`, `RMSE = 11.947`, `R² = 0.906`
- **Ridge (h=1)**: `MAE = 9.457`, `RMSE = 11.948`, `R² = 0.906`
- **Transformer (PyTorch h=1)**: `MAE = 9.580`, `RMSE = 12.124`, `R² = 0.903`
- **RandomForest (h=1)**: `MAE = 9.930`, `RMSE = 12.402`, `R² = 0.898`
- **HistGradientBoosting (h=1)**: `MAE = 10.149`, `RMSE = 12.534`, `R² = 0.896`
- **GRU (PyTorch h=1)**: `MAE = 10.161`, `RMSE = 12.976`, `R² = 0.889`
- **XGBoost (h=1)**: `MAE = 10.319`, `RMSE = 13.023`, `R² = 0.888`
- **ExtraTrees (h=1)**: `MAE = 10.575`, `RMSE = 13.139`, `R² = 0.886`
- **LSTM (PyTorch h=1)**: `MAE = 10.838`, `RMSE = 13.579`, `R² = 0.878`
- **TCN (PyTorch h=1)**: `MAE = 11.851`, `RMSE = 14.653`, `R² = 0.858`
- **LSTM Multi-Step (h=24)**: `MAE = 30.288`, `RMSE = 37.029`, `R² = 0.094`
- **Seasonal Naive Baseline**: `MAE = 30.966`, `RMSE = 38.726`, `R² = 0.008`

### Live R K Puram Telemetry Evaluation (n=639)
- **LinearRegression**: `MAE = 23.803`, `RMSE = 30.540`, `R² = 0.854` (`57.1%` lower MAE than Seasonal Naive `55.515`).

### Verification
- `python -m pytest tests/ -v`: **41/41 passed** (`0` failures, `0` skipped).
