# AIR POLLUTION PATTERN ANALYSIS AND AQI FORECASTING
**Application Platform:** AeroSense AI — *"Understand Pollution. Predict Tomorrow. Build a Cleaner Future."*  
**Institution:** Department of Computer Science and Engineering, Quantum School of Technology, Quantum University, Roorkee - 247167  
**Degree / Batch / Semester:** Bachelor of Technology in CSE (Data Science) | Batch 2023 - 2027 | Semester 7 | Year: 2026  
**Project Guide:** Mr. Abhishek Kumar (QU0125261068)  

### Project Group Members (Batch 2023 - 2027 | Semester 7 | CSE-DS)
| Student Name | Student ID & Roll No. | Batch / Sem / Branch | Primary Engineering Ownership |
| :--- | :--- | :--- | :--- |
| Aryan Saini | ID: 23030173 | Roll: 2301315012 | 2023 - 2027 | Sem 7 | CSE-DS | Data Engineering, OpenAQ v3 API & Parquet Pipeline |
| Ayaan Ali | ID: 23030175 | Roll: 2301315013 | 2023 - 2027 | Sem 7 | CSE-DS | Feature Synthesis, CPCB/EPA AQI Engine & Baselines |
| Kawalpreet Kaur | ID: 23030255 | Roll: 2301315019 | 2023 - 2027 | Sem 7 | CSE-DS | ML/DL Model Architectures, Training & Benchmarking |
| Mihir Kumar | ID: 23030268 | Roll: 2301315022 | 2023 - 2027 | Sem 7 | CSE-DS | SHAP Explainability, 10-Page Streamlit UI & Reporting |

---

AIR POLLUTION PATTERN ANALYSIS AND AQI FORECASTING

Project report submitted in partial fulfillment of the requirement for
the award of the Degree of **B. Tech**

By

**Aryan Saini** (Roll No. 2301315012)

**Ayaan Ali** (Roll No. 2301315013)

**Kawalpreet Kaur** (Roll No. 2301315019)

**Mihir Kumar** (Roll No. 2301315022)

*Under the Guidance of Mr. Abhishek Kumar (QU0125261068)*

Department of Computer Science and Engineering

Quantum School of Technology

Quantum University, Roorkee

2026


---

## CERTIFICATE

This is to certify that the project report entitled **“Air Pollution Pattern Analysis and AQI Forecasting”** being submitted by **Aryan Saini (Roll No. 2301315012), Ayaan Ali (Roll No. 2301315013), Kawalpreet Kaur (Roll No. 2301315019), and Mihir Kumar (Roll No. 2301315022)** in partial fulfillment for the award of the Degree of Bachelor of Technology in Computer Science and Engineering with specialization in Data Science from Computer Science and Engineering department is a record of bonafide work carried out by them under my guidance and supervision.

(Name & Signature)
**HoD, CSE & Dean Academics, QU**


---

## DECLARATION

We hereby declare that the project entitled **“Air Pollution Pattern Analysis and AQI Forecasting”** submitted for the B. Tech Degree in Computer Science and Engineering with specialization in Data Science (Batch 2023 - 2027, Semester 7) is our original work and the project has not formed the basis or submitted for the award of any degree, diploma, or any other similar titles in any other college, institute, or university.

Place Roorkee

Date November 2026


---

## ACKNOWLEDGEMENTS

The successful completion of any major engineering undertaking depends upon sustained mentorship, constructive critical feedback, and institutional support. We express our deep gratitude to our Project Guide, Mr. Abhishek Kumar (QU0125261068), Department of Computer Science and Engineering, Quantum School of Technology, Quantum University, Roorkee, for his invaluable guidance, methodical advice, and unwavering encouragement throughout every stage of the AeroSense AI platform.

We sincerely thank the Program Officer (CSE), the Head of Department (CSE), and the Dean Academics at Quantum University, Roorkee, for fostering a strong research culture and providing computing facilities during Batch 2023-2027 (7th Semester). We also acknowledge the open environmental science and machine learning communities behind OpenAQ API v3, Central Pollution Control Board (CPCB India), World Health Organization (WHO), Scikit-Learn, XGBoost, PyTorch, SHAP, ReportLab, and Streamlit, whose open standards made authentic real-world validation possible.

Finally, we thank our parents, faculty members, and classmates for their constant encouragement, thoughtful suggestions, and support during testing, benchmarking, and documentation of this project.


---

## TABLE OF CONTENTS


---

## LIST OF TABLES


---

## LIST OF FIGURES


---

## LIST OF ABBREVIATIONS AND SYMBOLS


---

## ABSTRACT

Urban fine particulate matter (PM2.5) air pollution is a critical public health emergency across the Indo-Gangetic Plain and rapidly urbanizing regions worldwide. Existing air quality monitoring portals remain largely constrained to retrospective visualizers that rely on retired APIs, interpolate blindly across multi-day sensor outages, suffer temporal look-ahead leakage from randomized cross-validation and unshifted rolling statistics, fail to disclose incomplete sensor panels when reporting statutory Air Quality Index (AQI) ratings, and deploy black-box predictors without feature attribution. AeroSense AI resolves these methodological and software engineering gaps through an end-to-end, modular environmental intelligence and forecasting platform built from scratch in Python, Scikit-Learn, XGBoost, PyTorch, SHAP, Plotly MapLibre, and Streamlit.

The platform implements an authenticated OpenAQ API v3 client (X-API-Key header, exponential backoff, two-phase station and sensor-hours discovery across 159 countries), deterministic validation, Tukey IQR x 3 anomaly rejection, and bounded <= 6-hour linear interpolation with explicit boolean provenance (is_imputed) persisted in Snappy-compressed Apache Parquet. Dual CPCB (2014) and US EPA (2018) piecewise-linear AQI calculators evaluate sub-indices across six criteria pollutants (PM2.5, PM10, NO2, SO2, CO, O3) and enforce statutory completeness disclosure via is_complete. Thirty-four strictly causal calendar, Fourier cyclical harmonic (sin/cos), autoregressive lag (1..48h), shifted rolling moment (target.shift(1) over 3..24h), and momentum features feed chronological 70% training, 15% validation, and 15% held-out testing splits across 14 models: three naive baselines, six tabular ML regressors, and four PyTorch deep sequence models (LSTM, GRU, Dilated Causal TCN, Transformer).

Live 30-day Indian telemetry extracted via OpenAQ v3 across Delhi R K Puram (n=639, mean 177.81 ug/m3), Lucknow Talkatora (n=641, mean 85.64 ug/m3), and Hyderabad Zoo Park (n=627, mean 52.71 ug/m3) reveals WHO 24-hour guideline (15 ug/m3) breach rates of 92.2% to 98.6%. On the 90-day controlled benchmark (n=2,161), 1-step Linear Regression (9.449 ug/m3 MAE, R2=0.906), Ridge (9.457 ug/m3), and PyTorch Transformer (9.580 ug/m3 MAE, R2=0.903) reduce test error by 69.5% over Seasonal Naive (30.966 ug/m3). On live Delhi R K Puram data featuring severe November smog surges up to 501.00 ug/m3, Linear Regression (23.803 ug/m3 MAE, R2=0.854) and Ridge (24.714 ug/m3) decisively outperform tree ensembles (26.534–33.479 ug/m3 MAE), demonstrating mathematically why unbounded linear slopes succeed where convex-hull-bounded tree leaves saturate. TreeSHAP confirms lag_1 (26.91 ug/m3, 74.4%) and diurnal harmonics govern short-term variance, verified by 46 passing pytest tests.


---

## CHAPTER 1: INTRODUCTION

Ambient air pollution constitutes one of the most severe environmental, epidemiological, and computational challenges of the twenty-first century. Rapid industrialization, high-density vehicular corridors, seasonal agricultural residue burning, and topographic boundary-layer trapping subject billions of urban residents—particularly across South Asia and the Indo-Gangetic Plain (IGP)—to hazardous concentrations of fine particulate matter and reactive trace gases. This opening chapter establishes the atmospheric physical foundations, public health urgency, regulatory divergence, failure modes of conventional environmental portals, formal research questions, and engineering scope of the AeroSense AI platform.


### 1.1 Atmospheric Background, Particulate Micro-Physics and Public Health Burden

Atmospheric pollutants are broadly classified into particulate aerosols and gaseous species. Among regulated criteria pollutants—fine particulate matter (PM2.5), respirable coarse particulate matter (PM10), nitrogen dioxide (NO2), sulfur dioxide (SO2), carbon monoxide (CO), and ground-level ozone (O3)—PM2.5 (suspended solid and liquid droplets with aerodynamic diameter d_a <= 2.5 micrometers) exerts the highest attributable human mortality. Whereas coarse particles (2.5 < d_a <= 10 micrometers) are predominantly intercepted by mucociliary clearance in the nasopharyngeal tract, PM2.5 aerosols bypass upper airway filtration, penetrate deep into terminal bronchioles and pulmonary alveoli, and translocate across the alveolar-capillary membrane directly into systemic arterial circulation.

Once inside the vascular system, transition metals, polycyclic aromatic hydrocarbons (PAHs), black carbon, and secondary inorganic sulfate/nitrate salts adsorbed onto PM2.5 surfaces induce oxidative stress, endothelial dysfunction, systemic inflammation, and prothrombotic cascades. Long-term cohort syntheses by the World Health Organization (WHO Global Air Quality Guidelines, 2021) and the Global Burden of Disease (GBD) study establish causal links between chronic and acute PM2.5 exposure and ischemic heart disease, cerebrovascular stroke, chronic obstructive pulmonary disease (COPD), acute lower respiratory infections, lung adenocarcinoma, adverse birth outcomes, and pediatric neurodevelopmental impairment.

To guide public health interventions, national and international bodies promulgate ambient concentration thresholds. In September 2021, the WHO halved its annual mean PM2.5 guideline from 10 ug/m3 to 5 ug/m3 and reduced its 24-hour mean guideline from 25 ug/m3 to 15 ug/m3. Conversely, India's National Ambient Air Quality Standards (NAAQS), notified by the Central Pollution Control Board (CPCB, 2009), define an annual PM2.5 limit of 40 ug/m3 and a 24-hour limit of 60 ug/m3—reflecting a four-fold to eight-fold regulatory divergence from WHO biological safety thresholds. Similarly, the United States Environmental Protection Agency (US EPA, revised 2024) enforces an annual primary PM2.5 standard of 9.0 ug/m3 and a 24-hour standard of 35 ug/m3. Table 1.1 summarizes these multi-pollutant regulatory benchmarks enforced across the AeroSense AI compliance engine.

**Table 1.1: Multi-Pollutant Ambient Regulatory Standards Across WHO (2021), Indian CPCB NAAQS (2009), and US EPA (2024)**

| Pollutant | Averaging Period | WHO 2021 Guideline | Indian CPCB NAAQS | US EPA NAAQS | Primary Anthropogenic Sources |
| :--- | :--- | :--- | :--- | :--- | :--- |
| PM2.5 | 24-Hour Mean | 15.0 ug/m3 | 60.0 ug/m3 | 35.0 ug/m3 | Combustion, vehicular exhaust, secondary aerosols |
| PM2.5 | Annual Mean | 5.0 ug/m3 | 40.0 ug/m3 | 9.0 ug/m3 | Industrial plumes, biomass burning, power plants |
| PM10 | 24-Hour Mean | 45.0 ug/m3 | 100.0 ug/m3 | 150.0 ug/m3 | Road resuspension dust, construction, crustal soil |
| PM10 | Annual Mean | 15.0 ug/m3 | 60.0 ug/m3 | Discontinued | Quarrying, unpaved transport corridors, brick kilns |
| NO2 | 24-Hour / 1-Hour | 25.0 ug/m3 (24h) | 80.0 ug/m3 (24h) | 100 ppb (1h) | High-temperature diesel/petrol engine combustion |
| SO2 | 24-Hour / 1-Hour | 40.0 ug/m3 (24h) | 80.0 ug/m3 (24h) | 75 ppb (1h) | Coal thermal power stations, high-sulfur fuel oil |
| CO | 8-Hour Mean | 4.0 mg/m3 | 2.0 mg/m3 | 9.0 ppm (~10 mg/m3) | Incomplete hydrocarbon and residential fuel burn |
| O3 | 8-Hour Peak | 100.0 ug/m3 | 100.0 ug/m3 | 0.070 ppm (~137 ug/m3) | Photochemical NOx + VOC reaction under solar UV |


### 1.2 Meteorology and Topography of the Indo-Gangetic Plain vs Peninsular India

Air pollutant concentration at ground level is governed not solely by emission flux, but critically by atmospheric dispersion volume. Across northern India, the Indo-Gangetic Plain forms a vast alluvial trough bounded to the north and northeast by the Himalayan mountain arc. During post-monsoon and winter months (October through February), synoptic wind speeds drop, solar insolation weakens, and rapid nocturnal longwave radiative cooling chills the ground surface relative to aloft air layers. This creates a strong surface temperature inversion that suppresses vertical convective mixing and collapses the Planetary Boundary Layer (PBL) from summer daytime heights exceeding 1,800 meters down to nocturnal winter depths below 100–150 meters.

When continuous urban emissions (vehicular tailpipes, diesel generators, domestic solid-fuel heating, and regional Kharif paddy residue burning) inject particulates into a compressed 120-meter mixing column, ground-level PM2.5 surges non-linearly from baseline levels (~60 ug/m3) to hazardous smog episodes exceeding 400–500 ug/m3 within 12 to 24 hours. By contrast, coastal and Deccan plateau cities (such as Mumbai, Chennai, and Hyderabad) benefit from marine land-sea breeze circulation and deeper convective boundary layers, yielding substantially lower mean concentrations and muted diurnal amplitude.

To anchor our research in real-world atmospheric behavior rather than synthetic assumptions, AeroSense AI extracted 30 days of continuous hourly telemetry (October–November 2026, n = 2,157 raw records, 1,907 validated clean records) directly from the live OpenAQ API v3 across three representative Indian government reference stations summarized in Table 1.2.

**Table 1.2: Live OpenAQ v3 Telemetry Baseline Snapshot Across Three Indian Geographies (Oct–Nov 2026)**

| Monitoring Station & Agency | OpenAQ ID | Physiographic Zone | Valid Hrs | Mean +- Std (ug/m3) | Min–Max (ug/m3) | WHO >15 | NAAQS >60 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| R K Puram, Delhi (DPCC) | 17 | Indo-Gangetic Plain (North) | 639 | 177.81 +- 95.74 | 1.00 – 501.00 | 98.6% | 92.3% |
| Talkatora, Lucknow (CPCB) | 407 | Central Indo-Gangetic Basin | 641 | 85.64 +- 50.82 | 4.34 – 265.00 | 92.2% | 68.3% |
| Zoo Park, Hyderabad (TSPCB) | 2456 | Deccan Peninsular Plateau | 627 | 52.71 +- 19.43 | 9.50 – 87.00 | 97.4% | 36.0% |


### 1.3 Critical Engineering Deficiencies in Existing Air Quality Portals

A rigorous audit of existing academic prototypes, open-source repositories, and public air quality dashboards reveals five pervasive methodological and software engineering failures that compromise their scientific validity:

1. **Reliance on Retired APIs or Fabricated Demo Data:** Following OpenAQ's retirement of legacy v1 and v2 REST endpoints and mandatory enforcement of v3 X-API-Key authentication, numerous existing tools fail at runtime or silently substitute random number generators in place of real sensor observations.

2. **Unbounded Interpolation Across Multi-Day Telemetry Blackouts:** Environmental monitoring stations frequently suffer power or calibration outages lasting 24 to 72 hours. Naive pipelines call pandas.DataFrame.interpolate() across the entire series without a gap ceiling, fabricating synthetic straight lines across multi-day diurnal cycles and corrupting downstream training.

3. **Temporal Look-Ahead Leakage in Feature Engineering and Cross-Validation:** Two subtle forms of data leakage pervade published student notebooks: (a) using randomized k-fold cross-validation or train_test_split(shuffle=True) on autocorrelated time series, allowing future observations at t+1 to train models predicting t; and (b) computing rolling averages via df['value'].rolling(w).mean() without shifting onto y_{t-1}, thereby leaking y_t / w directly into the input vector X_t.

4. **Silent Partial-Panel AQI Misrepresentation:** Official CPCB (2014) AQI computation requires at least three monitored pollutants including PM2.5 or PM10. Most single-sensor dashboards compute a PM2.5 sub-index and display it as an unqualified official AQI without disclosing missing co-pollutants.

5. **Opaque Black-Box Predictions and Unexamined Regime Shifts:** Deep neural networks and tree ensembles are frequently deployed without game-theoretic attribution (SHAP) or analysis of why decision trees fail to extrapolate beyond training bounds during extreme winter smog surges.


### 1.4 Formal Problem Statement and Research Questions

The core problem addressed by this B.Tech project is the design, implementation, and empirical validation of a modular, leakage-free, explainable air quality analytics and forecasting platform (AeroSense AI) capable of ingesting live global OpenAQ API v3 telemetry, enforcing bounded data hygiene, computing epistemically transparent CPCB and US EPA AQI ratings, and benchmarking classical machine learning against deep sequence neural architectures under stationary and non-stationary Indian atmospheric regimes. This investigation is structured around five formal research questions:

• **RQ1 (Data Hygiene & Provenance):** How can live OpenAQ v3 sensor streams be validated, filtered for hardware glitches, and imputed across brief drop-outs (<= 6h) while preserving strict provenance between observed and imputed records?

• **RQ2 (Leakage-Free Feature Synthesis):** How much predictive gain do 34 strictly causal cyclical harmonic, autoregressive lag, shifted rolling moment, and momentum features provide over Persistence and 24-hour Seasonal Naive baselines under a 70/15/15 chronological split?

• **RQ3 (ML vs. Deep Learning Parity):** On 1-step hourly PM2.5 forecasting, how do four PyTorch sequence architectures (LSTM, GRU, Dilated Causal TCN, Encoder-only Transformer) compare against six tabular ML models (Linear Regression, Ridge, Random Forest, Extra Trees, HistGradientBoosting, XGBoost)?

• **RQ4 (Non-Stationary Extrapolation Under Smog Spikes):** Why do regularized linear autoregressive models outperform bounded decision-tree ensembles when live Delhi R K Puram concentrations surge to unseen November peaks (501.00 ug/m3)?

• **RQ5 (Game-Theoretic Explainability & Horizon Decay):** Do TreeSHAP and LinearSHAP attributions align with atmospheric boundary-layer physics, and how rapidly does univariate forecast skill decay from horizon h = 1 to h = 24 hours?


### 1.5 Project Objectives and Team Engineering Ownership

To resolve RQ1–RQ5, the four-member CSE-DS project team divided the AeroSense AI architecture into four cohesive engineering workstreams under the supervision of Mr. Abhishek Kumar (QU0125261068), as documented in Table 1.3.

**Table 1.3: B.Tech CSE-DS Project Team Roster, Roll Numbers, and Modular Engineering Ownership**

| Student Name | Student ID | University Roll No. | Batch / Sem / Branch | Owned Subsystems & Core Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| Aryan Saini | 23030173 | 2301315012 | 2023-2027 | Sem 7 | CSE-DS | OpenAQ API v3 client, rate-limit backoff, ingestion, schema validation, IQR x3 cleaning, <=6h interpolation, Apache Parquet storage & Cloud bootstrap |
| Ayaan Ali | 23030175 | 2301315013 | 2023-2027 | Sem 7 | CSE-DS | Dual CPCB (2014) & US EPA (2018) AQI engines, partial-panel disclosure logic, 34 leakage-free cyclical/lag/rolling features, sliding-window tensors & 3 naive baselines |
| Kawalpreet Kaur | 23030255 | 2301315019 | 2023-2027 | Sem 7 | CSE-DS | 6 scikit-learn/XGBoost ML pipelines, 4 PyTorch DL models (LSTM, GRU, Causal TCN, Transformer), chronological 70/15/15 trainer, early stopping & empirical benchmarking |
| Mihir Kumar | 23030268 | 2301315022 | 2023-2027 | Sem 7 | CSE-DS | Tree/Linear SHAP & permutation explainability, 10-page Streamlit UI, Plotly MapLibre spatial maps, Haversine distance engine, automated PDF/PPTX reporting & 46-test QA suite |


### 1.6 Scope, Geographical Phasing Strategy, and Report Organization

AeroSense AI follows a disciplined two-phase geographical strategy. Phase 1 delivers deep calibration, regulatory compliance, and live sensor validation across India (ISO code IN, primary pollutant PM2.5, with multi-pollutant support for PM10, NO2, SO2, CO, and O3). Phase 2 scales globally without code modification by parameterizing station discovery across all 159 OpenAQ v3 countries. The remainder of this report is organized as follows: Chapter 2 surveys 25 peer-reviewed papers; Chapter 3 derives the complete mathematical formulations of data hygiene, AQI, 34 features, 14 models, and SHAP; Chapter 4 presents software/hardware design, DFDs, UML diagrams, and Parquet schemas; Chapter 5 documents production Python code templates and the 10-page Streamlit UI; Chapter 6 analyzes the 46 automated test cases, live Indian telemetry, and 14-model benchmarks; Chapter 7 summarizes conclusions and limitations; and Chapter 8 outlines Phase 2 extensions, followed by References and Appendices A–B.


---

## CHAPTER 2: LITERATURE SURVEY

A systematic review of twenty-five peer-reviewed journal articles, conference proceedings, and regulatory technical monographs spanning 1970 to 2024 was conducted to ground AeroSense AI in established atmospheric science, statistical learning theory, deep sequence modeling, and game-theoretic explainability.


### 2.1 Taxonomic Evolution of Air Quality Modeling Paradigms

Computational air pollution forecasting has evolved across four distinct generations. First-generation deterministic Chemical Transport Models (CTMs) such as WRF-Chem and CMAQ numerically solve coupled 3D advection-diffusion-reaction partial differential equations over Eulerian grids. While physically comprehensive, CTMs require supercomputing clusters and high-resolution emission inventories that lag rapidly changing urban traffic and biomass burning. Second-generation classical statistical models—most notably Box-Jenkins ARIMA, SARIMAX, and Vector Autoregression (Box et al., 2015)—exploit temporal autocorrelation efficiently on single-station series but assume linear stationarity and struggle with complex non-linear diurnal boundary-layer interactions.

Third-generation non-linear tabular machine learning ensembles—Random Forests (Breiman, 2001), Extra Trees (Geurts et al., 2006), Gradient Boosted Decision Trees (Friedman, 2001), XGBoost (Chen & Guestrin, 2016), and LightGBM (Ke et al., 2017)—achieve high accuracy on engineered lag and rolling features with sub-second CPU training. Fourth-generation deep sequence networks—LSTM (Hochreiter & Schmidhuber, 1997), GRU (Cho et al., 2014), Dilated Causal TCN (Bai et al., 2018), and self-attention Transformers (Vaswani et al., 2017; Zhou et al., 2021)—learn hierarchical representations directly from raw sliding-window tensors.


### 2.2 Thematic Critical Review of Twenty-Five Foundational and Contemporary Works


#### 2.2.1 Epidemiological Burden, Source Apportionment and Regulatory Indexing

Apte et al. (2018) quantified ambient PM2.5-attributable life-expectancy loss globally using non-linear integrated exposure-response curves, demonstrating that South Asian urban populations lose 1.5 to 3.0 years of life expectancy due to winter particulate peaks, and proving that marginal reductions even at high baseline concentrations (>100 ug/m3) yield substantial mortality benefits. Guttikunda and Gurjar (2012) modeled multi-season dispersion across Delhi NCR, establishing that winter morning (06:00–09:00 IST) and nocturnal (20:00–01:00 IST) PM2.5 peaks are driven by planetary boundary-layer compression rather than emission spikes alone. Pant et al. (2019) synthesized Indian receptor-modeling studies, motivating why AeroSense AI incorporates multi-scale rolling windows (3h, 6h, 12h, 24h) and seasonal harmonics. Regulatory frameworks by CPCB (2014), US EPA (2018), and WHO (2021) define the mathematical piecewise-linear sub-index equations and health thresholds codified in src/aqi/.


#### 2.2.2 Classical Autoregression, L2 Regularization and Decision Tree Ensembles

Box et al. (2015) formalized autoregressive integrated moving average processes, demonstrating that differencing (Delta y_t = y_t - y_{t-1}) and seasonal lags (y_{t-24}) stabilize non-stationary environmental series. Hoerl and Kennard (1970) introduced Ridge Regression (L2 penalty alpha ||w||_2^2) to resolve severe multicollinearity among correlated predictors—a crucial foundation for AeroSense AI, where lag_1, rolling_mean_3, and rolling_mean_6 exhibit correlation r > 0.92. Breiman (2001) proved that Random Forests reduce variance via bootstrap aggregation and random feature subspacing, while Geurts et al. (2006) showed that Extremely Randomized Trees (Extra Trees) further reduce variance by randomizing split thresholds. Friedman (2001), Chen and Guestrin (2016), and Ke et al. (2017) developed second-order and histogram-binned gradient boosting (XGBoost and HistGradientBoosting), which we benchmark systematically across stationary and non-stationary PM2.5 regimes.


#### 2.2.3 Applied Machine Learning Studies on Indian Urban PM2.5

Masood and Ahmad (2021) evaluated SVM and ANN models on 2016–2018 Delhi CPCB data, confirming PM2.5 dominance while highlighting missing-data sensitivity. Sengupta et al. (2021) documented multi-city Indian spatial-temporal trends during 2019–2020, motivating our Haversine spatial hotspot module. Kumar and Pande (2023) benchmarked tree ensembles across Indian cities and identified black-box opacity as a primary barrier to regulatory adoption. Nair et al. (2023) applied XGBoost with SHAP to Indian monitoring stations, confirming 1-hour and 24-hour lags as dominant predictors, though without benchmarking against deep sequence Transformers or TCNs.


#### 2.2.4 Deep Sequence Networks: LSTM, GRU, Dilated Causal TCN and Transformers

Hochreiter and Schmidhuber (1997) solved vanishing recurrent gradients via multiplicative forget, input, and output gates in LSTM networks. Cho et al. (2014) simplified gated recurrence into the 2-gate GRU cell, reducing parameter count by 25%—an advantage on medium-sized environmental datasets (n ~ 2,000). Bai et al. (2018) proved that Dilated Causal Temporal Convolutional Networks (TCNs) with exponential dilation d = 2^l, residual connections, and weight normalization match or exceed recurrent networks while training in parallel. Vaswani et al. (2017) introduced multi-head scaled dot-product self-attention, eliminating sequential path length O(L) to O(1). Qi et al. (2019), Zhou et al. (2021), Liu et al. (2022), and Zhang et al. (2023) extended deep sequence and Transformer architectures to PM2.5 forecasting, motivating our unified PyTorch comparison.


#### 2.2.5 Chronological Validation Theory and Game-Theoretic Explainability

Bergmeir and Benitez (2012) and Hyndman and Athanasopoulos (2021) proved that randomized k-fold cross-validation on autocorrelated series induces severe optimistic bias via look-ahead leakage, mandating strict chronological train/validation/test partitioning and Seasonal Naive benchmarking. Finally, Lundberg and Lee (2017) unified local feature attribution under cooperative game-theoretic Shapley values (SHAP), providing the theoretical basis for our TreeSHAP and LinearSHAP diagnostic engine.


### 2.3 Comprehensive Twenty-Five Paper Literature Synthesis Matrix

**Table 2.1: Exhaustive Synthesis Matrix of Twenty-Five Peer-Reviewed References Anchoring AeroSense AI**

| # | Author(s) & Year | Core Method / Focus | Primary Finding & Contribution | Identified Limitation / Gap Addressed |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Apte et al. (2018) | Global PM2.5 Life-Table | South Asia loses 1.5–3.0 yrs life expectancy from PM2.5 | Macro-epidemiology; no real-time forecasting UI |
| 2 | Bai et al. (2018) | Dilated Causal TCN | Exponential dilation d=2^l beats RNNs with parallelism | Requires strict Chomp1d causal slicing on hourly lags |
| 3 | Bergmeir & Benitez (2012) | Time-Series CV Theory | Random k-fold CV leaks future autocorrelation | Frequently violated in applied air quality notebooks |
| 4 | Box et al. (2015) | ARIMA / SARIMAX | Differencing & seasonal lag-24 stabilize trends | Linear stationarity assumption fails on complex features |
| 5 | Breiman (2001) | Random Forests | Bagging + feature subspacing reduces variance | Tree leaves bounded by [min(y_train), max(y_train)] |
| 6 | Chen & Guestrin (2016) | XGBoost GBDT | 2nd-order Taylor loss + L1/L2 tree regularization | Under-predicts unseen non-stationary smog spikes |
| 7 | Cho et al. (2014) | GRU Recurrent Cell | 2-gate recurrence cuts parameters by 25% vs LSTM | Sequential step unrolling limits GPU parallelism |
| 8 | CPCB India (2014) | National AQI Standard | 6-category piecewise breakpoints; >=3 pollutant rule | Public portals rarely flag single-sensor partial AQI |
| 9 | Friedman (2001) | Gradient Boosting | Stagewise additive trees on pseudo-residuals | Prone to overfitting without shrinkage & early stop |
| 10 | Geurts et al. (2006) | Extra Trees | Randomized cut-points reduce variance further | Same convex-hull extrapolation bound as Random Forest |
| 11 | Guttikunda & Gurjar (2012) | Delhi Dispersion Audit | Winter PBL compression drives 2x–3x PM2.5 surges | Offline emissions inventory; no live API pipeline |
| 12 | Hochreiter & Schmidhuber (1997) | LSTM Architecture | Constant error carousel preserves long-term state | Higher parameter overhead on ~2,000-row datasets |
| 13 | Hoerl & Kennard (1970) | Ridge Regression (L2) | Stabilizes multicollinear autoregressive lag matrices | Requires standardized pipelines & cyclical features |
| 14 | Hyndman & Athanasopoulos (2021) | Forecasting Principles | Seasonal Naive & MASE/MAE benchmark standards | Many ML papers omit naive baseline comparisons |
| 15 | Ke et al. (2017) | LightGBM / HistGBDT | 256-bin histogram quantization speeds GBDT 10x | Piecewise-constant leaf outputs clip extreme peaks |
| 16 | Kumar & Pande (2023) | Indian City ML Survey | Ensembles excel on stationary Indian CPCB datasets | Lack of SHAP transparency & live v3 API ingestion |
| 17 | Liu et al. (2022) | Attention-TCN PM2.5 | Receptive field >=24h critical for diurnal cycles | Evaluated offline without regulatory AQI integration |
| 18 | Lundberg & Lee (2017) | SHAP Attribution | Unique additive game-theoretic local explanations | Needs pipeline unwrap for scaled linear/tree models |
| 19 | Masood & Ahmad (2021) | Delhi SVM & ANN | Confirmed PM2.5 dominance across Delhi stations | Sensitive to uncleaned sensor spikes & long gaps |
| 20 | Nair et al. (2023) | XGBoost + SHAP India | lag_1 and lag_24 dominate urban PM2.5 variance | Did not compare against Transformers or Causal TCNs |
| 21 | Pant et al. (2019) | India PM2.5 Review | Synthesized IGP winter inversion & biomass drivers | Called for open reproducible Indian analytics tools |
| 22 | Qi et al. (2019) | Hybrid Deep PM2.5 | Spatial-temporal features boost 1–12h accuracy | High compute cost; lacks lightweight local storage |
| 23 | US EPA (2018) | US EPA AQI Technical | Tighter PM2.5 breakpoints (Good <=12 ug/m3) | Diverges from Indian CPCB categories on moderate air |
| 24 | Vaswani et al. (2017) | Transformer Attention | O(1) path length multi-head self-attention | Requires positional encoding & dropout on short series |
| 25 | WHO (2021) & Zhang (2023) | WHO Guidelines & Trans. | 24h PM2.5 limit 15 ug/m3; attention captures haze | Integrated end-to-end in AeroSense AI health engine |


### 2.4 Comparative Gap Analysis and Architectural Positioning

**Table 2.2: Methodological Capability Comparison Between Prior Works and AeroSense AI**

| Capability / Methodological Dimension | Typical Academic Notebooks | Public AQI Dashboards | AeroSense AI (This Project) |
| :--- | :--- | :--- | :--- |
| Live OpenAQ API v3 Authenticated Ingestion | Rare (mostly static CSVs) | Yes (backend hidden) | Yes (X-API-Key, backoff, sensor hours) |
| Bounded Imputation (<= 6h) & Provenance Mask | No (blind full-series fill) | Undisclosed | Yes (IQR x3 + <=6h linear + is_imputed) |
| Dual CPCB (India) & US EPA + Partial Flag | Single standard or none | Single standard, silent partial | Dual standard + explicit is_complete flag |
| Strict Chronological 70/15/15 Split & Shifted Rolls | Often random k-fold (leaky) | Not applicable | Strict chronological + target.shift(1) |
| Unified 14-Model ML + PyTorch DL + Baselines | 1–3 models only | None or proprietary | 3 Baselines + 6 ML + 4 PyTorch DL models |
| Non-Stationary Smog Extrapolation Audit | Unexamined | Not available | Proven on live Delhi 501 ug/m3 peak |
| Game-Theoretic SHAP + 46 Automated Tests | Rare | No | TreeSHAP, LinearSHAP, Permutation + 46 tests |


---

## CHAPTER 3: METHODOLOGY AND MATHEMATICAL FORMULATION

AeroSense AI implements a deterministic seven-stage data science and deep learning methodology: (1) authenticated OpenAQ API v3 extraction; (2) physical bounds validation, Tukey IQR outlier rejection, and bounded <= 6-hour temporal interpolation; (3) dual-standard CPCB and US EPA piecewise-linear AQI computation; (4) leakage-free 34-feature synthesis and 3D tensor windowing; (5) chronological 70/15/15 model training across 14 architectures; (6) game-theoretic SHAP attribution; and (7) automated publication reporting. Table 3.1 specifies the verified software and hardware stack.

**Table 3.1: Verified Software Stack, Library Versions, and Compute Governance**

| Subsystem Layer | Packages & Verified Versions | Architectural Purpose in AeroSense AI |
| :--- | :--- | :--- |
| Core Runtime | Python 3.12–3.14 (Verified on 3.14.4) | Type-annotated execution across Windows local & Linux Cloud |
| HTTP & Config | httpx >= 0.27.0, python-dotenv >= 1.0.0 | Synchronous TLS 1.3 OpenAQ v3 client, .env & st.secrets sync |
| Data & Storage | pandas >= 2.1.0, numpy >= 1.26.0, pyarrow >= 14.0 | Vectorized time-series transforms & Snappy Parquet I/O |
| Tabular ML | scikit-learn >= 1.4.0, xgboost >= 2.0.0, joblib | StandardScaler pipelines, 6 regressors, .pkl serialization |
| Deep Learning | torch >= 2.2.0 (PyTorch CPU / CUDA) | LSTM, GRU, Dilated Causal TCN, Encoder-only Transformer |
| Explainability | shap >= 0.45.0, scipy >= 1.12.0, statsmodels | TreeExplainer, LinearExplainer, permutation & residual stats |
| UI & Maps | streamlit >= 1.35.0, plotly >= 5.20 (MapLibre 6.9) | 10-page dark-themed studio & carto-darkmatter scatter_map |
| Reporting & QA | reportlab >= 4.0, python-pptx, matplotlib, pytest | 300-DPI charts, QU-format PDF, 16-slide PPTX & 46 unit/UI tests |


### 3.1 Authenticated OpenAQ API v3 Ingestion and Rate-Limit Governance

Unlike retired OpenAQ v1/v2 endpoints that allowed unauthenticated flat queries, OpenAQ API v3 enforces a hierarchical resource topology (Countries -> Locations -> Sensors -> Hours) protected by an HTTP X-API-Key header. AeroSense AI implements a two-phase discovery and extraction protocol in src/api/openaq_client.py and src/data/ingestion.py. In Phase A (Station Discovery), the client queries GET https://api.openaq.org/v3/locations with query parameters iso={COUNTRY_ISO}, parameters_id={PARAM_ID} (where PM2.5 maps to parameter ID 2), and limit=200. For each returned monitoring location, the parser extracts geographic coordinates (latitude, longitude), station metadata, and builds a JSON sensors_map mapping each normalized pollutant code to its unique integer sensor_id.

In Phase B (Hourly Sensor Stream Extraction), the client queries GET https://api.openaq.org/v3/sensors/{sensor_id}/hours with datetime_from, datetime_to, limit=1000, and page=p (up to OPENAQ_MAX_PAGES = 20). Because v3 hourly payloads nest timestamps inside period.datetimeTo.utc (or period.datetimeFrom.utc), our parser extracts the exact interval-ending UTC timestamp alongside the floating-point concentration. Transient rate limits (HTTP 429) and server faults (HTTP 500/502/503/504) are handled via deterministic exponential backoff:

```text
t_sleep(k) = t_0 * (b ^ (k - 1)), where t_0 = 1.5 s, b = 1.5, k in {1, 2, 3}
```

**Table 3.2: OpenAQ API v3 HTTP Status Code Governance and Exception Handling Matrix**

| HTTP Status / Fault | Client Exception Raised | Retry Policy | Diagnostic Action & User Feedback |
| :--- | :--- | :--- | :--- |
| 200 OK | None (Valid JSON) | 0 retries | Update _last_success UTC timestamp; parse results array |
| 401 Unauthorized | OpenAQAuthError | Immediate abort | Invalid or missing X-API-Key; prompt System Diagnostics key setup |
| 403 Forbidden | OpenAQAuthError | Immediate abort | Key lacks resource scope; log masked key prefix/suffix |
| 404 Not Found | OpenAQNotFoundError | Immediate abort | Station or sensor ID retired; skip station cleanly in loop |
| 429 Too Many Requests | OpenAQRateLimitError | Up to 3 backoff retries | Sleep 3.0s * k; raise controlled warning if quota exhausted |
| 500 / 502 / 503 / 504 | OpenAQServerError | Up to 3 backoff retries | Sleep 1.5 * 1.5^(k-1) s; fall back to cached/stored Parquet |
| Timeout / DNS Error | OpenAQConnectionError | Up to 3 backoff retries | 30s socket timeout guard; preserve offline studio operation |


### 3.2 Deterministic Schema Validation, Tukey IQR Filtering and Bounded Imputation

Raw environmental sensor feeds frequently contain negative drift voltages, zero-calibration spikes, duplicate transmission packets, and power-outage gaps. AeroSense AI separates validation (src/data/validation.py) from cleaning (src/data/cleaning.py) and never overwrites raw Parquet snapshots stored in data/raw/. First, unit normalization converts parts-per-million (ppm) or parts-per-billion (ppb) gaseous readings into standard mass concentration (ug/m3 or mg/m3 for CO) at 25 C and 1 atm using molecular weight factors M_w / 24.45. Second, physical domain bounds (Table 3.3) reject impossible sensor glitches.

**Table 3.3: Criteria Pollutant Physical Validation Bounds, Standard Units, and Averaging Windows**

| Pollutant Code | Chemical Species | OpenAQ Parameter ID | Canonical Unit | Valid Physical Range | Regulatory Averaging Window |
| :--- | :--- | :--- | :--- | :--- | :--- |
| pm25 | Fine Particulate Matter (<=2.5 um) | 2 | ug/m3 | [0.0, 2000.0] | 24-Hour Rolling / Daily Mean |
| pm10 | Coarse Particulate Matter (<=10 um) | 1 | ug/m3 | [0.0, 5000.0] | 24-Hour Rolling / Daily Mean |
| no2 | Nitrogen Dioxide | 5 | ug/m3 | [0.0, 2000.0] | 24-Hour (CPCB) / 1-Hour (EPA) |
| so2 | Sulfur Dioxide | 6 | ug/m3 | [0.0, 2000.0] | 24-Hour (CPCB) / 1-Hour (EPA) |
| co | Carbon Monoxide | 4 | mg/m3 (or ug/m3) | [0.0, 100.0] mg/m3 | 8-Hour Rolling Mean |
| o3 | Ground-Level Ozone | 3 | ug/m3 | [0.0, 1000.0] | 8-Hour Rolling Mean |

Third, records are sorted chronologically and deduplicated on the composite primary key (location_id, parameter, datetime_utc). Fourth, per-station statistical anomaly screening computes the 25th percentile (Q1), 75th percentile (Q3), and interquartile range IQR = Q3 - Q1. Unlike standard 1.5 * IQR fences that mistakenly clip legitimate winter smog episodes, AeroSense AI uses an extreme outer Tukey multiplier of k = 3.0, retaining real severe pollution while rejecting isolated electronic surges:

```text
Valid Concentration Domain: y_t in [ max(0, Q_1 - 3.0 * IQR), Q_3 + 3.0 * IQR ]
```

Fifth, each station stream is reindexed onto a complete hourly UTC grid. Missing timestamps are imputed via piecewise linear interpolation strictly when the contiguous gap length Delta t <= 6 hours (limit=6). Every interpolated timestamp is tagged with is_imputed = True, whereas contiguous outages exceeding 6 hours remain NaN (and are subsequently dropped during supervised window construction) so the platform never fabricates diurnal pollution cycles.


### 3.3 Dual-Standard Regulatory AQI Mathematical Formulation (CPCB vs. US EPA)

To translate multi-pollutant physical concentrations into actionable public health indices, AeroSense AI implements both the Indian Central Pollution Control Board National AQI (CPCB, 2014) in src/aqi/cpcb.py and the United States EPA AQI (US EPA, 2018) in src/aqi/us_epa.py. For each monitored pollutant p with concentration C_p falling within breakpoint bracket [BP_lo, BP_hi] corresponding to index interval [I_lo, I_hi], the sub-index I_p is computed via piecewise linear interpolation:

```text
I_p = round( ((I_hi - I_lo) / (BP_hi - BP_lo)) * (C_p - BP_lo) + I_lo ), AQI = max_{p in P} ( I_p )
```

Crucially, official CPCB rules require a minimum of three monitored pollutants (one of which must be PM2.5 or PM10) to issue a statutory AQI. AeroSense AI sets result.is_complete = (len(sub_indices) >= 3 and any(p in {'pm25','pm10'} for p in calculated)) and displays an explicit partial-panel warning banner whenever single-pollutant streams are evaluated. Tables 3.4 and 3.5 document the complete breakpoint matrices verified by our 12 automated test cases in tests/test_aqi.py.

**Table 3.4: Official Indian CPCB (2014) AQI Breakpoint Matrix and Health Impact Categories**

| AQI Category (Index Range) | PM2.5 24h (ug/m3) | PM10 24h (ug/m3) | NO2 24h (ug/m3) | SO2 24h (ug/m3) | CO 8h (mg/m3) | O3 8h (ug/m3) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Good (0 – 50) | 0 – 30 | 0 – 50 | 0 – 40 | 0 – 40 | 0.0 – 1.0 | 0 – 50 |
| Satisfactory (51 – 100) | 31 – 60 | 51 – 100 | 41 – 80 | 41 – 80 | 1.1 – 2.0 | 51 – 100 |
| Moderate (101 – 200) | 61 – 90 | 101 – 250 | 81 – 180 | 81 – 380 | 2.1 – 10.0 | 101 – 168 |
| Poor (201 – 300) | 91 – 120 | 251 – 350 | 181 – 280 | 381 – 800 | 10.1 – 17.0 | 169 – 208 |
| Very Poor (301 – 400) | 121 – 250 | 351 – 430 | 281 – 400 | 801 – 1600 | 17.1 – 34.0 | 209 – 748 |
| Severe (401 – 500) | 251 – 500+ | 431 – 600+ | 401 – 550+ | 1601 – 2100+ | 34.1 – 50.0+ | 749 – 1000+ |

**Table 3.5: Official US EPA AQI Breakpoint Matrix and Severity Comparison Against Indian CPCB**

| US EPA Category (Index Range) | PM2.5 24h (ug/m3) | PM10 24h (ug/m3) | O3 8h (ppm) | CO 8h (ppm) | Key Divergence from Indian CPCB |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Good (0 – 50) | 0.0 – 12.0 | 0 – 54 | 0.000 – 0.054 | 0.0 – 4.4 | EPA Good ceiling (12.0) is 2.5x stricter than CPCB (30) |
| Moderate (51 – 100) | 12.1 – 35.4 | 55 – 154 | 0.055 – 0.070 | 4.5 – 9.4 | 60 ug/m3 is Satisfactory in CPCB but Unhealthy in EPA |
| Unhealthy for Sensitive (101 – 150) | 35.5 – 55.4 | 155 – 254 | 0.071 – 0.085 | 9.5 – 12.4 | Triggers pediatric/asthmatic advisory at 35.5 ug/m3 |
| Unhealthy (151 – 200) | 55.5 – 150.4 | 255 – 354 | 0.086 – 0.105 | 12.5 – 15.4 | Spans CPCB Satisfactory through Very Poor range |
| Very Unhealthy (201 – 300) | 150.5 – 250.4 | 355 – 424 | 0.106 – 0.200 | 15.5 – 30.4 | Converges with CPCB Very Poor upper bound (250 ug/m3) |
| Hazardous (301 – 500) | 250.5 – 500.4 | 425 – 604 | 0.201 – 0.604 | 30.5 – 50.4 | Matches CPCB Severe threshold above 250.5 ug/m3 |

![Fig. 3.1: Piecewise-Linear Sub-Index Transfer Curves Comparing Indian CPCB (2014) and US EPA (2018) PM2.5 Breakpoint Schedules](figures/fig13_aqi_breakpoint_curves.png)
*Fig. 3.1: Piecewise-Linear Sub-Index Transfer Curves Comparing Indian CPCB (2014) and US EPA (2018) PM2.5 Breakpoint Schedules*


### 3.4 Leakage-Free 34-Feature Engineering Mathematical Specification

To transform an hourly univariate series {(t, y_t)} into a rich tabular design matrix X in R^{N x 34} without temporal look-ahead leakage, src/features/feature_engineering.py constructs four orthogonal feature families:

1. **Calendar & Fourier Cyclical Harmonics (11 features):** Raw integer calendar fields (hour in [0,23], day_of_week in [0,6], day_of_month in [1,31], month in [1,12], is_weekend in {0,1}) exhibit artificial metric discontinuities at period boundaries (e.g., 23:00 is 1 hour from 00:00, yet |23 - 0| = 23). We project each periodic variable onto a 2D unit circle via orthogonal sine and cosine harmonics:

```text
hour_sin = sin(2*pi*h / 24), hour_cos = cos(2*pi*h / 24), dow_sin = sin(2*pi*d / 7), month_sin = sin(2*pi*m / 12)
```

2. **Strictly Causal Autoregressive Lags (7 features):** Past concentrations y_{t-k} for k in {1, 2, 3, 6, 12, 24, 48} hours capture immediate persistence (k=1..3), half-day boundary-layer transitions (k=6, 12), and 24-hour/48-hour diurnal cycle memory.

3. **Shifted Rolling Window Moments (12 features — Zero-Leakage Guarantee):** If a rolling mean over window w is computed naively on y_t, then r_t = (1/w)*(y_t + y_{t-1} + ... + y_{t-w+1}) contains the target y_t itself with weight 1/w, allowing a linear model to reconstruct y_t trivially! AeroSense AI computes all rolling moments exclusively on the shifted series s_t = y_{t-1} = target.shift(1):

```text
mu_{t,w} = (1/w) * sum_{j=1}^{w} y_{t-j}, sigma_{t,w} = sqrt( (1/(w-1)) * sum_{j=1}^{w} (y_{t-j} - mu_{t,w})^2 ), w in {3, 6, 12, 24}
```

4. **First-Order & Diurnal Momentum Differentials (4 features):** Rate-of-change predictors capture whether the atmospheric column is actively accumulating or flushing aerosols prior to timestamp t: diff_1 = y_{t-1} - y_{t-2}, trend_24 = y_{t-1} - y_{t-25}, pct_change_1 = (y_{t-1} - y_{t-2}) / (y_{t-2} + epsilon), and ratio_to_rolling_24 = y_{t-1} / (mu_{t,24} + epsilon). Table 3.6 catalogs all 34 features.

**Table 3.6: Complete 34-Feature Engineering Catalog, Mathematical Formulas, and Atmospheric Roles**

| Feature Group | Feature Names (Count) | Exact Mathematical Definition | Physical & Predictive Role |
| :--- | :--- | :--- | :--- |
| Raw Calendar | hour, day_of_week, day_of_month, month, is_weekend (5) | UTC timestamp calendar extraction; is_weekend = I(dow >= 5) | Captures weekday commuter vs weekend emission drop |
| Diurnal Harmonics | hour_sin, hour_cos (2) | sin(2*pi*hour/24), cos(2*pi*hour/24) | Continuous encoding of PBL morning/evening cycle |
| Weekly Harmonics | dow_sin, dow_cos (2) | sin(2*pi*dow/7), cos(2*pi*dow/7) | Smooth weekly industrial activity periodicity |
| Annual Harmonics | month_sin, month_cos (2) | sin(2*pi*month/12), cos(2*pi*month/12) | Seasonal monsoon wash-out vs winter inversion phase |
| Short Lags | lag_1, lag_2, lag_3 (3) | y_{t-1}, y_{t-2}, y_{t-3} | Immediate atmospheric residence & inertia |
| Medium/Diurnal Lags | lag_6, lag_12, lag_24, lag_48 (4) | y_{t-6}, y_{t-12}, y_{t-24}, y_{t-48} | Half-day mixing transition & 1–2 day diurnal echo |
| Rolling Means | rolling_mean_3, _6, _12, _24 (4) | (1/w) * sum_{j=1..w} y_{t-j}  (shifted onto y_{t-1}) | Smoothed local concentration baseline over window w |
| Rolling Volatility | rolling_std_3, _6, _12, _24 (4) | std(y_{t-1}, ..., y_{t-w}) | Measures plume turbulence & onset of smog spikes |
| Rolling Extrema | rolling_min_3..24, rolling_max_3..24 (4) | min_{j=1..w} y_{t-j}, max_{j=1..w} y_{t-j} | Local floor (ventilation) & ceiling (peak accumulation) |
| Momentum / Ratios | diff_1, trend_24, pct_change_1, ratio_to_roll24 (4) | y_{t-1}-y_{t-2}; y_{t-1}-y_{t-25}; y_{t-1}/mu_{t,24} | Velocity of aerosol buildup / boundary-layer collapse |


### 3.5 Mathematical Formulations of All Fourteen Forecasting Architectures

All models are trained and evaluated under a strict chronological split: the earliest 70% of ordered timestamps form D_train, the middle 15% form D_val (used for early stopping and hyperparameter verification), and the final 15% form the unseen held-out test set D_test. No shuffling is ever permitted.


#### 3.5.1 Naive Baselines and Regularized Linear Models (5 Models)

Three parameter-free baselines establish lower bounds on acceptable skill: (1) Persistence predicts yhat_t = y_{t-1}; (2) Seasonal Naive (24h) predicts yhat_t = y_{t-24}; and (3) Rolling Mean (24h) predicts yhat_t = (1/24)*sum_{j=1}^{24} y_{t-j}. Ordinary Least Squares (LinearRegression) and L2-Penalized Ridge Regression wrap a StandardScaler (z = (x - mu_train)/sigma_train) inside a scikit-learn Pipeline and minimize the Tikhonov objective:

```text
J_Ridge(w, b) = sum_{i=1}^{N_train} (y_i - (w^T z_i + b))^2 + alpha * ||w||_2^2, w* = (Z^T Z + alpha * I)^{-1} Z^T y
```

Because yhat = w^T z + b is an unbounded affine hyperplane, Linear and Ridge models possess a critical physical property: when y_{t-1} and diff_1 surge above the highest concentration observed in D_train, the linear predictor extrapolates proportionally along the learned autoregressive slope w_{lag_1} > 0.


#### 3.5.2 Bagging and Gradient Boosted Decision Tree Ensembles (4 Models)

Random Forest (B = 100 trees) and Extra Trees (B = 100 trees) average predictions across bootstrap-aggregated regression trees T_b(x). Crucially, every leaf node R_{b,m} in a regression tree outputs the arithmetic mean of training targets falling into that region. Consequently, for any arbitrary test vector x_test, a tree ensemble is mathematically constrained by the convex hull of training targets:

```text
yhat_Tree(x_test) = (1/B) * sum_{b=1}^{B} T_b(x_test) in [ min(y_train), max(y_train) ]
```

Histogram Gradient Boosting (HistGradientBoostingRegressor) and XGBoost (XGBRegressor) construct stagewise additive ensembles yhat_i^{(M)} = sum_{m=1}^{M} eta * f_m(x_i) by minimizing a second-order Taylor expansion of the squared-error loss with leaf-weight L2 penalty lambda and tree-complexity penalty gamma:

```text
L^{(m)} = sum_{i=1}^{N} [ g_i * f_m(x_i) + (1/2) * h_i * f_m(x_i)^2 ] + gamma * T + (1/2) * lambda * sum_{j=1}^{T} w_j^2
```


#### 3.5.3 PyTorch Deep Sequence Architectures: LSTM, GRU, Causal TCN and Transformer (4 Models)

For deep sequence modeling (src/dl/models.py and src/dl/trainer.py), the training series is z-score normalized using strictly training-split statistics (mu_train, sigma_train) and segmented into 3D sliding-window tensors X_seq in R^{N x L x 1} (lookback L = 24 hours) predicting target vector Y_seq in R^{N x H} (horizon H = 1 or H = 24 hours). All four PyTorch architectures are trained with AdamW (lr = 10^{-3}, weight_decay = 10^{-4}), Huber/MSE loss, gradient norm clipping (max_norm = 1.0), ReduceLROnPlateau, and validation early stopping (patience = 10 epochs):

• **LSTMForecaster (2-layer stacked LSTM, hidden_size = 64):** Maintains separate cell state c_t and hidden state h_t governed by forget gate f_t = sigma(W_f [h_{t-1}, x_t] + b_f), input gate i_t = sigma(W_i [h_{t-1}, x_t] + b_i), candidate c~_t = tanh(W_c [h_{t-1}, x_t] + b_c), and update c_t = f_t * c_{t-1} + i_t * c~_t, projecting final step h_L through a Linear(64 -> H) head.

• **GRUForecaster (2-layer stacked GRU, hidden_size = 64):** Couples forget and input gates into a single update gate z_t = sigma(W_z [h_{t-1}, x_t]) and reset gate r_t = sigma(W_r [h_{t-1}, x_t]), updating h_t = (1 - z_t) * h_{t-1} + z_t * h~_t with 25% fewer parameters than LSTM.

• **TCNForecaster (3-block Dilated Causal Temporal Convolutional Network):** Applies 1D causal convolutions with kernel size K = 3 and exponential dilation factors d_l in {1, 2, 4}. Left-padding of (K - 1)*d_l followed by a Chomp1d module slices off future right-side padding so output at time t depends strictly on x_{ 24-hour lookback.

• **TransformerForecaster (2-layer Encoder-only Transformer, d_model = 64, nhead = 4):** Projects scalar inputs via Linear(1 -> 64), adds deterministic sinusoidal positional encodings PE_{(pos, 2i)} = sin(pos / 10000^{2i/d_model}), applies 4-head scaled dot-product self-attention Attention(Q,K,V) = softmax(Q K^T / sqrt(d_k)) V with pre-norm residual layers, and maps the terminal token to R^H.

**Table 3.7: Complete Architecture, Hyperparameter, and Regularization Specification Across All 14 Models**

| Model Name | Family | Input Representation | Core Hyperparameters & Regularization | Extrapolation Capability |
| :--- | :--- | :--- | :--- | :--- |
| Persistence | Naive Baseline | Scalar y_{t-1} | Parameter-free identity lag_1 | Bounded to last observed value |
| Seasonal Naive (24h) | Naive Baseline | Scalar y_{t-24} | Parameter-free 24h diurnal cycle echo | Bounded to previous day profile |
| Rolling Mean (24h) | Naive Baseline | Window y_{t-24..t-1} | Unweighted 24-hour moving average | Lags rapid inflection points |
| LinearRegression | Tabular ML | 34 Features (Scaled) | StandardScaler + exact OLS normal equation | Unbounded linear slope extrapolation |
| Ridge | Tabular ML | 34 Features (Scaled) | StandardScaler + L2 penalty alpha = 1.0 | Unbounded L2-damped extrapolation |
| RandomForest | Tabular ML | 34 Features | n_estimators=100, max_depth=None, random_state=42 | Convex hull bounded [min, max] |
| ExtraTrees | Tabular ML | 34 Features | n_estimators=100, randomized cut-points, seed=42 | Convex hull bounded [min, max] |
| HistGradientBoosting | Tabular ML | 34 Features | max_iter=200, lr=0.05, max_bins=255, L2=1.0 | Piecewise-constant leaf bounded |
| XGBoost | Tabular ML | 34 Features | n_estimators=200, lr=0.05, max_depth=6, subsample=0.8 | Piecewise-constant leaf bounded |
| LSTMForecaster | PyTorch DL | Tensor (N, 24, 1) | 2 layers, hidden=64, dropout=0.2, AdamW lr=1e-3 | Tanh/linear readout semi-bounded |
| GRUForecaster | PyTorch DL | Tensor (N, 24, 1) | 2 layers, hidden=64, dropout=0.2, grad_clip=1.0 | Sigmoid/tanh gated readout |
| TCNForecaster | PyTorch DL | Tensor (N, 24, 1) | Channels [64,64,64], k=3, dilations [1,2,4], Chomp1d | ReLU + linear head extrapolation |
| TransformerForecaster | PyTorch DL | Tensor (N, 24, 1) | d_model=64, nhead=4, layers=2, FFN=128, dropout=0.1 | Attention + linear projection |


### 3.6 Game-Theoretic Explainable AI (SHAP) and Evaluation Metrics

To audit model decisions, src/explainability/feature_importance.py computes exact Shapley Additive exPlanations (Lundberg & Lee, 2017). For feature j among F predictors, the Shapley attribution phi_j(f, x) averages the marginal contribution of feature j across all coalitions S subseteq F \ {j}:

```text
phi_j(f, x) = sum_{S subseteq F \ {j}} ( |S|! * (|F| - |S| - 1)! / |F|! ) * [ f_{S union {j}}(x_{S union {j}}) - f_S(x_S) ]
```

Our implementation automatically unwraps scikit-learn Pipelines (applying StandardScaler.transform(X_sample) prior to passing the estimator to shap.TreeExplainer for tree models or shap.LinearExplainer for linear models), and complements SHAP with 5-repeat Permutation Importance on D_test.


### 3.7 Residual Diagnostics and Computational Complexity Analysis

Beyond scalar error aggregates (MAE, RMSE, R2), AeroSense AI audits model residuals e_t = y_t - yhat_t for systematic bias (mean residual mu_e = (1/N_test)*sum e_t), asymmetry (sample skewness gamma_1), tail heaviness (excess kurtosis gamma_2), and heteroscedasticity across concentration deciles. Table 3.8 summarizes the asymptotic time and space complexity of every stage in our seven-stage pipeline, proving that the entire tabular ML training and inference workflow executes in O(N * F) to O(B * F * N log N) time on standard multi-core CPU hardware without requiring dedicated GPU clusters.

**Table 3.8: Asymptotic Time and Space Complexity Across AeroSense AI Pipeline Stages**

| Pipeline Stage / Algorithm | Time Complexity (Training / Execution) | Inference Complexity (Per Step) | Memory Footprint |
| :--- | :--- | :--- | :--- |
| OpenAQ v3 Paginated Ingestion | O(P * M) across P pages of M=1000 rows | O(1) cached Parquet read (<4 ms) | O(N) DataFrame buffer |
| Schema Validation & IQR x3 Clean | O(N log N) chronological sort & group quantiles | O(N) single-pass vector filter | O(N) Arrow column arrays |
| 34-Feature Matrix Synthesis | O(N * W) where max rolling window W = 24 | O(F) with F = 34 features | O(34 * N) float64 matrix |
| OLS / Ridge Regression (F=34) | O(N * F^2 + F^3) normal matrix inversion | O(F) inner product (<0.01 ms) | O(F^2) covariance matrix |
| RandomForest / ExtraTrees (B=100) | O(B * F * N log N) recursive partitioning | O(B * D_max) tree traversal | O(B * N_leaves) pointers |
| HistGradientBoosting / XGBoost | O(M_trees * F * N_bins) with N_bins = 255 | O(M_trees * D_max) leaf lookup | O(F * N_bins + M * 2^D) |
| PyTorch LSTM / GRU (L=24, H_d=64) | O(E * N * L * H_d^2) sequential BPTT | O(L * H_d^2) recurrent unroll | O(L * H_d) hidden states |
| PyTorch Dilated Causal TCN (K=3) | O(E * N * L * K * C^2) parallel 1D conv | O(L * K * C^2) parallel conv | O(B_batch * C * L) activations |
| PyTorch Transformer (L=24, d=64) | O(E * N * (L^2 * d + L * d^2)) attention | O(L^2 * d + L * d^2) forward | O(nhead * L^2) attention map |
| TreeSHAP / LinearSHAP Attribution | O(N_s * B * D_max^2) / O(N_s * F) exact | O(B * D_max^2) per explanation | O(N_s * F) Shapley matrix |


---

## CHAPTER 4: SOFTWARE AND HARDWARE DESIGN

AeroSense AI is engineered as a six-layer modular software system separating configuration, external data acquisition, domain mathematics, machine/deep learning training, explainability/reporting, and interactive presentation. This clean decoupling ensures that every algorithmic component can be unit-tested headlessly via Pytest and scaled from India to international monitoring networks without UI code modification.


### 4.1 Six-Layer Modular Software Architecture and Repository Audit

**Table 4.1: Complete Repository Module Inventory, Architectural Layer, and Functional Responsibilities**

| Architectural Layer | Repository File Path | Key Classes / Functions | Engineering Responsibility |
| :--- | :--- | :--- | :--- |
| 1. Config & Logging | src/config/settings.py | PROJECT_ROOT, api_key_configured, masked_api_key | Centralized paths, constants, .env loader & secret masking |
| 1. Config & Logging | src/utils/logging_config.py | setup_logging, get_logger | Idempotent rotating 5 MB file + color console logger |
| 2. API & Data Pipeline | src/api/openaq_client.py | OpenAQClient, OpenAQError hierarchy | Authenticated v3 REST client, pagination, backoff retry |
| 2. API & Data Pipeline | src/data/ingestion.py | DataIngestion.fetch_locations / measurements | Two-phase station discovery & sensor hours extraction |
| 2. API & Data Pipeline | src/data/validation.py | validate_measurements, ValidationReport | Schema enforcement, numeric coercion & physical bounds |
| 2. API & Data Pipeline | src/data/cleaning.py | clean_measurements, normalise_units | Composite deduplication, IQR x3 filter & <=6h interpolation |
| 2. API & Data Pipeline | src/data/storage.py | save_raw, save_processed, load_processed | Immutable raw & processed Snappy Apache Parquet persistence |
| 2. API & Data Pipeline | src/data/seed_benchmark.py | generate_delhi_benchmark, seed_all_benchmarks | Reference 90-day Delhi & Mumbai calibration benchmarks |
| 2. API & Data Pipeline | src/data/bootstrap.py | ensure_ready, sync_streamlit_secrets | Self-healing Streamlit Cloud secret sync & auto-seeding |
| 3. Domain & Features | src/aqi/cpcb.py & us_epa.py | calculate_cpcb_aqi, calculate_epa_aqi | Dual-standard piecewise linear AQI & is_complete flag |
| 3. Domain & Features | src/features/feature_engineering.py | build_feature_matrix, build_sequences | 34 leakage-free tabular features & 3D (N,24,1) DL tensors |
| 4. ML / DL Modeling | src/ml/baselines.py & train.py | evaluate_baselines, train_models, predict | 3 naive baselines + 6 ML pipelines with 70/15/15 split |
| 4. ML / DL Modeling | src/dl/models.py & trainer.py | LSTM/GRU/TCN/TransformerForecaster, train_dl_model | 4 PyTorch sequence models, AdamW, early stop & checkpointing |
| 5. XAI & Reporting | src/explainability/feature_importance.py | get_feature_importance, shap_values, residual_analysis | Pipeline-aware Tree/Linear SHAP, permutation & error stats |
| 5. XAI & Reporting | src/reporting/*.py | build_detailed_project_report, build_synopsis | Automated QU Report, IEEE Paper, Synopsis, PPTX & ZIP |
| 6. Presentation & QA | app.py, pages/01..10, src/visualization/ | apply_theme, map_scatter, forecast_chart | 11-entrypoint Streamlit dark UI, MapLibre & 46 Pytest cases |


### 4.2 Data Flow Diagrams (Context Level-0 and Detailed Level-1 DFD)

At Context Level-0, external entities comprise the OpenAQ API v3 Cloud Server, the Environmental Researcher / End User, and the Local/Cloud File System. At Level-1 (Figure 4.1, Panel A), authenticated HTTPS JSON responses flow into Process 1.0 (Ingestion & Raw Preservation), writing immutable snapshots to D1 (data/raw/*.parquet). Process 2.0 (Validation & IQR/<=6h Cleaning) filters anomalies and writes clean analytical tables with is_imputed flags to D2 (data/processed/*.parquet). Process 3.0 (34-Feature & 3D Tensor Builder) and Process 4.0 (Dual CPCB/EPA AQI Engine) feed Process 5.0 (Chronological 70/15/15 ML/DL Trainer), persisting model binaries to D3 (models/ml/*.pkl, models/dl/*.pt) and evaluation ledgers to D4 (experiments/results/*.csv), which drive Process 6.0 (SHAP Explainability & 10-Page Streamlit UI).


### 4.3 UML Class, Sequence, Control Flow and Use-Case Diagrams

Figure 4.1 illustrates the four formal software design views of AeroSense AI: (A) Level-1 Data Flow Diagram; (B) UML Class Diagram showing composition and inheritance across OpenAQClient, DataIngestion, AQICalculator, FeatureBuilder, MLTrainer, and PyTorch nn.Module subclasses; (C) End-to-End UML Sequence Diagram tracing synchronous method calls from user trigger to rendered Plotly chart; and (D) Runtime Control Flow & Use-Case Governance.

![Fig. 4.1: AeroSense AI Level-1 DFD (A), UML Class Architecture (B), Execution Sequence Diagram (C) and Control Flow / Use-Case Design (D)](figures/fig6_uml_system_design.png)
*Fig. 4.1: AeroSense AI Level-1 DFD (A), UML Class Architecture (B), Execution Sequence Diagram (C) and Control Flow / Use-Case Design (D)*

![Fig. 4.2: End-to-End Seven-Stage AeroSense AI Data Engineering, Feature Synthesis, Chronological Split, and Model Deployment Pipeline](figures/fig07_pipeline_flow.png)
*Fig. 4.2: End-to-End Seven-Stage AeroSense AI Data Engineering, Feature Synthesis, Chronological Split, and Model Deployment Pipeline*

![Fig. 4.3: Six-Layer Modular Software Architecture Depicting Package Boundaries Across Config, Data, Domain, ML/DL, XAI, and Streamlit UI](figures/fig08_layer_architecture.png)
*Fig. 4.3: Six-Layer Modular Software Architecture Depicting Package Boundaries Across Config, Data, Domain, ML/DL, XAI, and Streamlit UI*


### 4.4 Persistent Storage Architecture and Apache Parquet Schemas

Rather than requiring an external database daemon that complicates academic portability and Streamlit Community Cloud hosting, AeroSense AI adopts a local-first analytical lakehouse architecture backed by Snappy-compressed Apache Parquet files. Columnar Parquet storage preserves strict Arrow data types (UTC nanosecond timestamps, int64 IDs, float64 concentrations, boolean flags) and achieves 4x–6x compression over CSV while loading 2,161-row time series in under 4 milliseconds. Tables 4.2 and 4.3 define the exact schemas for processed datasets and serialized model checkpoints.

**Table 4.2: Processed Analytical Dataset Schema (data/processed/*.parquet)**

| Field Name | Apache Arrow / Pandas Dtype | Nullability | Provenance & Analytical Role |
| :--- | :--- | :--- | :--- |
| datetime_utc | datetime64[ns, UTC] | NOT NULL | Monotonic hourly UTC key governing 70/15/15 chronological split |
| location_id | int64 | NOT NULL | Unique OpenAQ v3 monitoring station identifier (e.g., 17, 407, 2456) |
| location_name | string | NOT NULL | Human-readable CPCB/DPCC/TSPCB reference monitor name |
| city / country | string | NOT NULL | City label (with location_name fallback) and ISO-3166 alpha-2 code (IN) |
| latitude / longitude | float64 | NULLABLE | WGS-84 decimal degrees driving MapLibre scatter_map & Haversine matrix |
| sensor_id / parameter | int64 / string | NOT NULL | OpenAQ v3 sensor primary key and pollutant code (pm25, pm10, etc.) |
| unit / value | string / float64 | NOT NULL | Normalized mass unit (ug/m3) and validated concentration reading |
| is_imputed | bool | NOT NULL | False for raw sensor observation; True for <= 6h linear interpolation |
| source_provider / api_endpoint | string | NOT NULL | Audit trail ('OpenAQ API v3' vs 'AeroSense Reference Benchmark') |
| retrieved_at | string (ISO-8601 UTC) | NOT NULL | Exact extraction timestamp ensuring full data lineage |

**Table 4.3: Serialized ML (.pkl) and PyTorch DL (.pt) Model Artifact Dictionary Schema**

| Artifact Key | Value Type | Persisted Content & Runtime Role |
| :--- | :--- | :--- |
| model / model_state | sklearn Pipeline / OrderedDict | Fitted StandardScaler+Estimator or PyTorch state_dict weights |
| features / lookback, horizon | list[str] / int, int | Exact ordered 34 feature names or (L=24, H=1/24) tensor dimensions |
| val_metrics / test_metrics | dict[str, float] | Chronological validation & held-out test {'MAE', 'RMSE', 'R2'} scores |
| train_time_s / pred_time_s | float | Wall-clock training and inference latency in seconds |
| n_features / train_rows | int | Dimensionality verification (34 features, 1,495 training instances) |
| mean / std (DL only) | float | Training-split z-score normalization scalars preventing test leakage |


### 4.5 Self-Healing Cloud Bootstrap and Geodesic Spatial Architecture

When deployed to ephemeral cloud containers (such as Streamlit Community Cloud), git-ignored binary directories (data/processed/, models/ml/) start empty and environment variables reside in st.secrets rather than .env. Our bootstrap module (src/data/bootstrap.py) executes ensure_ready() at the top of app.py and every page (pages/01..10): it synchronizes st.secrets['OPENAQ_API_KEY'] into os.environ and settings.OPENAQ_API_KEY, seeds reference Delhi and Mumbai benchmarks if data/processed/ is empty, and trains five baseline scikit-learn models in < 0.8 seconds if models/ml/*.pkl is absent, while preserving tracked experiment CSVs.


### 4.6 Security, Secret Isolation and Fault-Tolerant Threat Model

Because AeroSense AI interfaces with external authenticated REST endpoints and executes interactive model training in a web browser environment, defense-in-depth controls are enforced across credential storage, network resilience, input sanitization, and UI compatibility. Table 4.4 documents the system threat model and verified mitigations.

**Table 4.4: System Threat Model, Failure Modes, and Verified Engineering Mitigations**

| Risk / Failure Mode | Attack Vector or Operational Trigger | Engineering Mitigation in AeroSense AI | Verification Test |
| :--- | :--- | :--- | :--- |
| API Key Exposure in Git / UI | Committing .env or printing raw key in UI | .gitignore blocks .env; masked_api_key() hides middle chars; st.text_input(type='password') | test_bootstrap.py & git status audit |
| OpenAQ Rate Limit (HTTP 429) | Burst station/sensor queries exceeding quota | Exponential backoff (1.5s * 1.5^k, max 3 retries); graceful fallback to cached Parquet | test_api_and_explainability.py |
| Ephemeral Cloud Cold Start | Streamlit Cloud boots with empty data/ & models/ | ensure_ready() syncs st.secrets, seeds Delhi/Mumbai Parquet & trains 5 baseline ML models | test_bootstrap_seeds_empty_workspace |
| Blank City Strings in OpenAQ v3 | OpenAQ v3 returns city='' on Indian stations | Page 02 checks non-whitespace city strings and falls back cleanly to location_name | AppTest IN_pm25_live_openaq check |
| Plotly Mapbox Deprecation Crash | Plotly >=5.24 scatter_map rejects mapbox_style | map_scatter() passes map_style='carto-darkmatter' natively to px.scatter_map | test_charts.py (2/2 PASS) |
| Insufficient Sample Size (<50) | User selects short 1-day series for ML/DL fit | Pre-flight guard checks len(df) >= 50 (ML) and >= 100 (DL) with actionable error alert | 04_Forecasting_Studio.py guard |
| Corrupted / Extreme Sensor Spike | Hardware fault transmits -999 or 99,999 ug/m3 | Physical bounds filter [0, 2000] + Tukey IQR x 3 fence before feature synthesis | test_validation.py (4/4 PASS) |


---

## CHAPTER 5: IMPLEMENTATION AND CODING TEMPLATES

This chapter documents the concrete Python implementation of AeroSense AI, including public class/function contracts, production coding templates across all nine core engineering subsystems, and the functional architecture of the ten-page Streamlit analytical studio.


### 5.1 Core Classes, Method Signatures, Input Parameters and Return Contracts

**Table 5.1: Public Method Contracts, Type Signatures, and Runtime Complexity Across Core Modules**

| Module & Callable | Input Parameters & Types | Return Type & Contract | Complexity / Notes |
| :--- | :--- | :--- | :--- |
| OpenAQClient.get_locations | country: str='IN', limit: int=100, parameter: str|None | list[dict] station metadata payloads | O(P) paginated REST v3 GET |
| OpenAQClient.get_sensor_hours | sensor_id: int, datetime_from: str, datetime_to: str | list[dict] hourly period measurements | Exponential backoff on 429/5xx |
| DataIngestion.fetch_measurements | location_id: int, parameter: str, sensor_id: int | pd.DataFrame with provenance cols | Attaches lat/lon & retrieved_at |
| validate_measurements | df: pd.DataFrame | tuple[pd.DataFrame, ValidationReport] | O(N) bounds & schema verification |
| clean_measurements | df: pd.DataFrame, remove_outliers: bool, impute_strategy: str | pd.DataFrame with is_imputed bool | O(N log N) sort, IQR x3, <=6h fill |
| calculate_cpcb_aqi / epa_aqi | concentrations: dict[str,float] | float, pollutant: str | AQIResult | dict with is_complete | O(|P|) piecewise linear lookup |
| build_feature_matrix | df: pd.DataFrame, target_col: str='value', drop_na: bool | pd.DataFrame (N, 34+meta) | O(N) vectorized shifted rolling |
| build_sequences | series: np.ndarray, lookback: int=24, horizon: int=24 | tuple[np.ndarray, np.ndarray] | Builds (N,24,1) & (N,H) tensors |
| evaluate_baselines | train: np.ndarray, test: np.ndarray, seasonal_period: int=24 | pd.DataFrame (3 baseline metrics) | Persistence, Seasonal24, Roll24 |
| train_models | df: pd.DataFrame, model_names: list[str]|None, save_dir: Path | pd.DataFrame leaderboard + .pkl files | Strict 70/15/15 chronological split |
| train_dl_model | series: np.ndarray, model_name: str, lookback: int, horizon: int | dict(metrics, history) + .pt file | AdamW, grad_clip=1.0, early stop |
| shap_values | model_dict: dict, X: np.ndarray, max_samples: int=200 | tuple[np.ndarray, Explainer] | None | Unwraps Pipeline -> Tree/LinearSHAP |
| ensure_ready | None (cached via @st.cache_resource) | dict(api_key_ready, seeded_data, ...) | Idempotent Cloud secret & data seed |


### 5.2 Production Coding Templates and Subsystem Walkthroughs


#### 5.2.1 Centralized Configuration and API Key Masking (src/config/settings.py)

All filesystem paths, OpenAQ v3 parameters, and chronological split ratios (TRAIN_RATIO = 0.70, VAL_RATIO = 0.15) are centralized in src/config/settings.py. The helper functions api_key_configured() and masked_api_key() prevent accidental credential exposure in logs or UI widgets:

```python
# src/config/settings.py — Secure API Key Governance & Chronological Split Constants
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / '.env', override=False)
OPENAQ_API_KEY: Optional[str] = os.getenv('OPENAQ_API_KEY')
OPENAQ_BASE_URL: str = 'https://api.openaq.org/v3'
TRAIN_RATIO, VAL_RATIO = 0.70, 0.15  # Remaining 0.15 = strictly held-out chronological test split

def api_key_configured() -> bool:
    key = OPENAQ_API_KEY or ''
    return bool(key) and key != 'your_openaq_api_key_here'

def masked_api_key() -> str:
    key = OPENAQ_API_KEY or ''
    if not key or key == 'your_openaq_api_key_here': return 'NOT CONFIGURED'
    return f'{key[:4]}' + '*' * (len(key) - 8) + f'{key[-4:]}' if len(key) > 8 else '***'
```


#### 5.2.2 Resilient OpenAQ API v3 Client with Exponential Backoff (src/api/openaq_client.py)

The OpenAQClient injects the X-API-Key header on every request, maps parameter names to v3 integer IDs (PM2.5 -> 2), and implements bounded exponential backoff across HTTP 429 and 5xx faults:

```python
# src/api/openaq_client.py — Authenticated v3 Request Loop with Exponential Backoff
def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f'{self._base_url}/{endpoint.lstrip("/")}'
    delay = settings.OPENAQ_RETRY_BACKOFF
    for attempt in range(1, settings.OPENAQ_MAX_RETRIES + 1):
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(url, headers={'X-API-Key': self._api_key}, params=params or {})
            if resp.status_code == 200:
                self._last_success = datetime.now(timezone.utc)
                return resp.json()
            if resp.status_code in (401, 403): raise OpenAQAuthError('Invalid or missing OpenAQ API key')
            if resp.status_code == 429 and attempt < settings.OPENAQ_MAX_RETRIES:
                time.sleep(delay * 2); delay *= settings.OPENAQ_RETRY_BACKOFF; continue
        except httpx.RequestError as exc:
            if attempt == settings.OPENAQ_MAX_RETRIES: raise OpenAQConnectionError(str(exc)) from exc
            time.sleep(delay); delay *= settings.OPENAQ_RETRY_BACKOFF
```


#### 5.2.3 Tukey IQR x 3 Outlier Filtering and Bounded <= 6h Imputation (src/data/cleaning.py)

In src/data/cleaning.py, extreme sensor glitches are filtered per station-parameter group using a 3.0 * IQR fence, and missing hourly slots are linearly interpolated only across gaps of at most 6 consecutive hours while recording provenance in the boolean column is_imputed:

```python
# src/data/cleaning.py — Per-Station IQR x 3 Filtering & Bounded <= 6-Hour Linear Imputation
def _remove_iqr_outliers(df: pd.DataFrame, factor: float = 3.0) -> Tuple[pd.DataFrame, int]:
    q1, q3 = df['value'].quantile(0.25), df['value'].quantile(0.75)
    iqr = q3 - q1
    mask = (df['value'] >= max(0.0, q1 - factor * iqr)) & (df['value'] <= q3 + factor * iqr)
    return df[mask].copy(), int((~mask).sum())

def _impute_group(grp: pd.DataFrame, strategy: str = 'interpolate') -> pd.DataFrame:
    grp = grp.sort_values('datetime_utc').copy()
    orig_na = grp['value'].isna()
    if strategy == 'interpolate':
        grp['value'] = grp['value'].interpolate(method='linear', limit=6)  # Never bridge >6h gaps
    grp['is_imputed'] = orig_na & grp['value'].notna()
    return grp
```


#### 5.2.4 Dual-Standard Piecewise Linear AQI Engine (src/aqi/cpcb.py & src/aqi/us_epa.py)

The CPCB and US EPA AQI calculators share an exact piecewise-linear interpolation kernel and compute the epistemic completeness flag is_complete to prevent single-sensor readings from masquerading as official multi-pollutant AQI values:

```python
# src/aqi/cpcb.py — Piecewise-Linear Sub-Index Kernel & Partial-Panel Disclosure Flag
def _sub_index(conc: float, breakpoints: List[Tuple[float, float, int, int]]) -> Optional[int]:
    if conc < 0: return None
    for bp_lo, bp_hi, i_lo, i_hi in breakpoints:
        if bp_lo <= conc <= bp_hi:
            return int(round(((i_hi - i_lo) / (bp_hi - bp_lo)) * (conc - bp_lo) + i_lo))
    return 500 if conc > breakpoints[-1][1] else None

# Completeness rule: >= 3 pollutants monitored including PM2.5 or PM10
has_pm = any(p in ('pm25', 'pm10') for p in calculated)
is_complete = (len(sub_indices) >= 3) and has_pm
```


#### 5.2.5 Leakage-Free 34-Feature Synthesis and 3D Sequence Builder (src/features/feature_engineering.py)

The feature engineering module guarantees zero look-ahead leakage by shifting the target series by 1 hour (shifted = target.shift(1)) before computing any rolling mean, standard deviation, minimum, or maximum:

```python
# src/features/feature_engineering.py — Zero-Leakage Shifted Rolling & Harmonic Features
out['hour_sin'] = np.sin(2 * np.pi * out['hour'] / 24.0)
out['hour_cos'] = np.cos(2 * np.pi * out['hour'] / 24.0)
for lag in [1, 2, 3, 6, 12, 24, 48]:
    out[f'lag_{lag}'] = grp[target_col].shift(lag)

shifted = grp[target_col].shift(1)  # CRITICAL: shift(1) excludes current y_t from all rolling stats
for w in [3, 6, 12, 24]:
    out[f'rolling_mean_{w}'] = shifted.rolling(w, min_periods=1).mean()
    out[f'rolling_std_{w}']  = shifted.rolling(w, min_periods=1).std().fillna(0.0)
    out[f'rolling_min_{w}']  = shifted.rolling(w, min_periods=1).min()
    out[f'rolling_max_{w}']  = shifted.rolling(w, min_periods=1).max()
out['diff_1']   = out['lag_1'] - out['lag_2']
out['trend_24'] = out['lag_1'] - grp[target_col].shift(25)
```


#### 5.2.6 Chronological 70/15/15 ML Training Pipeline (src/ml/train.py)

The tabular ML trainer sorts observations chronologically, splits indices at 70% and 85%, fits StandardScaler pipelines exclusively on X_train, evaluates on X_val and X_test, and serializes full metadata dictionaries via joblib:

```python
# src/ml/train.py — Strict Chronological 70/15/15 Partitioning & Pipeline Persistence
feat_df = build_feature_matrix(df, target_col=target_col, dt_col=dt_col, drop_na=True)
n = len(feat_df)
i_train, i_val = int(n * settings.TRAIN_RATIO), int(n * (settings.TRAIN_RATIO + settings.VAL_RATIO))
X_train, y_train = X[:i_train], y[:i_train]
X_val,   y_val   = X[i_train:i_val], y[i_train:i_val]
X_test,  y_test  = X[i_val:], y[i_val:]  # Unseen future held-out evaluation split

for name, model in models_to_run.items():
    model.fit(X_train, y_train)
    val_metrics  = compute_metrics(y_val,  model.predict(X_val))
    test_metrics = compute_metrics(y_test, model.predict(X_test))
    joblib.dump({'model': model, 'features': avail_features, 'test_metrics': test_metrics}, save_dir / f'{name}.pkl')
```


#### 5.2.7 PyTorch Deep Sequence Models: Causal TCN and Transformer (src/dl/models.py)

Below is the core PyTorch architecture for Chomp1d causal convolution slicing in TCNForecaster and multi-head self-attention with sinusoidal positional encoding in TransformerForecaster:

```python
# src/dl/models.py — Causal Chomp1d TCN Block & Sinusoidal Transformer Encoder
class Chomp1d(nn.Module):
    def __init__(self, chomp_size: int): super().__init__(); self.chomp_size = chomp_size
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x[:, :, :-self.chomp_size].contiguous() if self.chomp_size > 0 else x

class TransformerForecaster(nn.Module):
    def __init__(self, input_size=1, d_model=64, nhead=4, num_layers=2, horizon=24, dropout=0.1):
        super().__init__()
        self.input_proj = nn.Linear(input_size, d_model)
        self.pos_enc = PositionalEncoding(d_model, dropout=dropout)
        layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=128, dropout=dropout, batch_first=True)
        self.encoder = nn.TransformerEncoder(layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, horizon)
    def forward(self, x): return self.fc(self.encoder(self.pos_enc(self.input_proj(x)))[:, -1, :])
```


#### 5.2.8 Pipeline-Aware SHAP Explainability and Cloud Bootstrap (src/explainability/ & src/data/bootstrap.py)

When computing SHAP attributions on a scikit-learn Pipeline(StandardScaler, Estimator), our explainability module transforms X_sample through the scaler before invoking TreeExplainer or LinearExplainer. Meanwhile, src/data/bootstrap.py guarantees self-healing startup on Streamlit Community Cloud:

```python
# src/explainability/feature_importance.py — Pipeline Unwrap for TreeSHAP & LinearSHAP
if hasattr(model, 'steps') and len(model.steps) > 1:
    X_sample = model[:-1].transform(X_sample)
    est = model[-1]
explainer = shap.TreeExplainer(est) if is_tree else shap.Explainer(est, X_sample)
sv = explainer.shap_values(X_sample)
```


### 5.3 Ten-Page Interactive Streamlit Application Suite Specification

The user interface is organized as a multi-page Streamlit workspace (app.py plus ten specialized pages in pages/01..10) styled via centralized dark-mode CSS (src/visualization/theme.py). Every page calls ensure_ready() on boot so both local and Streamlit Cloud visitors see populated charts, gauges, leaderboards, and maps immediately. Table 5.2 documents all 11 application entrypoints.

**Table 5.2: Complete 11-Entrypoint Streamlit Application Route, Control, and Visualization Specification**

| Route / File | Page Title | Interactive Sidebar / Form Controls | Primary Visualizations & Analytical Outputs |
| :--- | :--- | :--- | :--- |
| app.py | Home Overview | Sidebar API connection pill & navigation | 4 architecture KPI cards, live API status, 6-step workflow guide & team roster |
| pages/01_*.py | Global Data Explorer | Country ISO, pollutant, days back (1–90), max stations, imputation mode, stored loader | Validated data table, CSV export, multi-station time series, MapLibre station map & quality audit |
| pages/02_*.py | Pollution Analytics | Processed dataset selector | 5 tabs: Daily/Hourly/Day-of-Week trends, skewness/kurtosis histogram, monthly box plot, city/station bar chart & correlation heatmap |
| pages/03_*.py | AQI Intelligence | From loaded dataset (24h auto-mean) vs Manual 6-pollutant entry | Dual CPCB (India) & US EPA Plotly gauges, dominant pollutant cards, sub-index tables & partial-panel warnings |
| pages/04_*.py | Forecasting Studio | Dataset selector, ML vs DL family, model multiselect, lookback/horizon/epochs sliders | Auto-loaded persisted ML leaderboard, Held-Out Test Forecast vs Actual chart, PyTorch loss curves & 3 naive baselines |
| pages/05_*.py | Model Benchmarking | Metric selector (test_MAE, test_RMSE, test_R2) | Unified ML + DL ranked leaderboard (with CSV fallback on Cloud), top-model KPI cards & grouped Plotly comparison bars |
| pages/06_*.py | Explainable AI | Trained ML model & dataset selectors, Compute SHAP button | Native impurity/coefficient importance bar chart, 5-repeat permutation importance, Mean |SHAP| bar plot & residual diagnostics |
| pages/07_*.py | Spatial Hotspot Analysis | Dataset selector & hotspot percentile threshold slider (75–99th) | Interactive carto-darkmatter MapLibre scatter_map, ranked hotspot severity table, 7-zone regional box plot & 8x8 Haversine distance matrix |
| pages/08_*.py | Health Risk & Advisory | Dataset selector & interactive PM2.5 simulator slider (0–500 ug/m3) | Severity alert banner, WHO 24h excess ratio, 4 vulnerable cohort cards, WHO/NAAQS/EPA grouped compliance chart & N95/HEPA directives |
| pages/09_*.py | Research Reports | Target dataset, station label & include-benchmarks toggle | 1-click download of Markdown, HTML, formal PDF reports, reproducibility ZIP bundle & all pre-built academic submission deliverables |
| pages/10_*.py | System Diagnostics | OpenAQ API key password input, Save to .env, Test Connection & Cache Purge | Live api.openaq.org/v3 ping latency & country count, CPU/CUDA hardware profiler, 7-directory storage footprint table & log tail streamer |


### 5.4 Module-by-Module Implementation Walkthrough of the Ten Analytical Pages

Each Streamlit page in pages/01..10 is implemented as an independent, self-bootstrapping controller that imports domain services from src/ without duplicating business logic:

• **Page 01 (01_Global_Data_Explorer.py):** Initializes st.session_state keys (raw_df, clean_df, locations_df, data_origin) and auto-loads the first stored Parquet dataset on boot so visitors immediately see a 2,161-row interactive table, multi-station time series, MapLibre station map, and 4-card Data Quality Report (Raw Records, Clean Records, Stations, Imputed count, value percentiles, and missing-value audit). Clicking Fetch Live OpenAQ Data invokes DataIngestion.fetch_locations() followed by per-station fetch_measurements(), validate_measurements(), clean_measurements(), and save_processed().

• **Page 02 (02_Pollution_Analytics.py):** Parses UTC timestamps into hour, day name, numeric day_of_week (0..6), month name, and date. Tab 1 renders Daily Average time series, Hourly mean profile with shaded fill, and Monday-to-Sunday bar charts; Tab 2 computes percentiles (25%, 50%, 75%, 90%, 95%), sample skewness, excess kurtosis, a 50-bin histogram, and monthly distribution box plots; Tab 3 detects whether city contains non-blank strings and falls back automatically to location_name for multi-station mean, median, std, and count ranking; Tab 4 renders a Pearson correlation heatmap across value, hour, and day_of_week.

• **Page 03 (03_AQI_Intelligence.py):** Defaults to 'From loaded dataset' mode whenever processed Parquet files exist, extracting the latest 24-hour mean per parameter and invoking calculate_cpcb_aqi() and calculate_epa_aqi() simultaneously. Renders side-by-side Plotly gauge indicators (0–500 scale with regulatory color bands), dominant pollutant badges, sub-index breakdown tables, and explicit partial-panel warning banners when fewer than 3 pollutants are present.

• **Page 04 (04_Forecasting_Studio.py) & Page 05 (05_Model_Benchmarking.py):** Page 04 loads persisted .pkl artifacts via _load_persisted_ml_results() on initial load so users immediately inspect validation/test metrics, a Held-Out Test Period Forecast vs. Actual overlay chart, and an expanded 3-baseline comparison table before optionally launching custom ML or PyTorch DL training. Page 05 merges live session models, persisted .pkl/.pt checkpoints, and tracked CSV benchmarks (experiments/results/ml_benchmark_results.csv and dl_h1_benchmark.csv) into a unified ranked leaderboard with color-coded ML vs. DL comparison bar charts.

• **Page 06 (06_Explainable_AI.py) & Page 07 (07_Spatial_Hotspot_Analysis.py):** Page 06 builds the 34-feature matrix on the selected dataset, evaluates the 15% test split, displays native tree/linear importance or 5-repeat permutation importance, computes on-demand TreeSHAP/LinearSHAP bar charts, and plots residual scatter and error histograms. Page 07 maps station coordinates via MapLibre px.scatter_map(map_style='carto-darkmatter'), assigns geographic zones via _infer_region(), supplements single-station datasets with stored stations and the 8-node Indian National Reference Grid via _build_comparison_grid(), and computes an 8x8 great-circle Haversine distance matrix.

• **Page 08 (08_Health_Risk_and_Advisory.py), Page 09 (09_Research_Reports.py) & Page 10 (10_System_Diagnostics.py):** Page 08 audits live or simulated PM2.5 concentrations against WHO 2021 (15 ug/m3 24h, 5 ug/m3 annual), Indian NAAQS (60/40 ug/m3), and US EPA (35/9 ug/m3) thresholds and provides clinical guidance for four vulnerable cohorts. Page 09 compiles on-demand Markdown, HTML, ReportLab PDF, and ZIP reproducibility bundles alongside direct download cards for our pre-built Synopsis, Research Paper, Final Project Report, and 16-slide PPTX deck. Page 10 provides secure API key persistence to .env, live api.openaq.org/v3 ping audits, CPU/CUDA hardware profiling, 7-directory disk footprint tables, cache purging, and live log streaming.


### 5.5 Deployed Interactive Application Screenshots (All 11 Entrypoints)

Figures 5.1 through 5.11 capture the live rendered interfaces of app.py and all ten analytical pages (pages/01..10) running on populated Indian OpenAQ v3 and reference benchmark telemetry.

![Fig. 5.1: AeroSense AI Home Overview (app.py) with API Connection Status, Architecture Cards, and Team Roster](screens/cropped/scr01_home.png)
*Fig. 5.1: AeroSense AI Home Overview (app.py) with API Connection Status, Architecture Cards, and Team Roster*

![Fig. 5.2: Page 01 — Global Data Explorer Displaying Validated OpenAQ v3 / Benchmark Telemetry and Quality Report](screens/cropped/scr02_data_explorer.png)
*Fig. 5.2: Page 01 — Global Data Explorer Displaying Validated OpenAQ v3 / Benchmark Telemetry and Quality Report*

![Fig. 5.3: Page 02 — Pollution Analytics Showing Temporal Trends, Diurnal Cycles, and Multi-Station Comparisons](screens/cropped/scr03_analytics.png)
*Fig. 5.3: Page 02 — Pollution Analytics Showing Temporal Trends, Diurnal Cycles, and Multi-Station Comparisons*

![Fig. 5.4: Page 03 — AQI Intelligence Displaying Dual CPCB (India) and US EPA Gauges and Sub-Index Breakdowns](screens/cropped/scr04_aqi_intelligence.png)
*Fig. 5.4: Page 03 — AQI Intelligence Displaying Dual CPCB (India) and US EPA Gauges and Sub-Index Breakdowns*

![Fig. 5.5: Page 04 — Forecasting Studio Displaying Persisted ML Leaderboard, Test Forecast Overlay, and Baselines](screens/cropped/scr05_forecasting_studio.png)
*Fig. 5.5: Page 04 — Forecasting Studio Displaying Persisted ML Leaderboard, Test Forecast Overlay, and Baselines*

![Fig. 5.6: Page 05 — Model Benchmarking Showing Unified 10-Model ML + PyTorch DL Ranked Test Leaderboard](screens/cropped/scr06_model_benchmarking.png)
*Fig. 5.6: Page 05 — Model Benchmarking Showing Unified 10-Model ML + PyTorch DL Ranked Test Leaderboard*

![Fig. 5.7: Page 06 — Explainable AI Showing Feature Importance, SHAP Attributions, and Residual Error Diagnostics](screens/cropped/scr07_explainable_ai.png)
*Fig. 5.7: Page 06 — Explainable AI Showing Feature Importance, SHAP Attributions, and Residual Error Diagnostics*

![Fig. 5.8: Page 07 — Spatial & Hotspot Analysis Displaying MapLibre Dark-Matter Station Map and Regional Contrasts](screens/cropped/scr08_spatial_hotspots.png)
*Fig. 5.8: Page 07 — Spatial & Hotspot Analysis Displaying MapLibre Dark-Matter Station Map and Regional Contrasts*

![Fig. 5.9: Page 08 — Public Health Risk & Advisory Engine Showing WHO/NAAQS Compliance and Cohort Directives](screens/cropped/scr09_health_advisory.png)
*Fig. 5.9: Page 08 — Public Health Risk & Advisory Engine Showing WHO/NAAQS Compliance and Cohort Directives*

![Fig. 5.10: Page 09 — Academic Research & Technical Reports Export Studio with 1-Click PDF/HTML/ZIP Downloads](screens/cropped/scr10_research_reports.png)
*Fig. 5.10: Page 09 — Academic Research & Technical Reports Export Studio with 1-Click PDF/HTML/ZIP Downloads*

![Fig. 5.11: Page 10 — System Diagnostics & Settings Showing OpenAQ v3 Connectivity Audit and Storage Footprint](screens/cropped/scr11_system_diagnostics.png)
*Fig. 5.11: Page 10 — System Diagnostics & Settings Showing OpenAQ v3 Connectivity Audit and Storage Footprint*


---

## CHAPTER 6: RESULTS AND DISCUSSION

This chapter presents the empirical verification and experimental results of AeroSense AI across six dimensions: (1) automated black-box, white-box, and headless UI software verification across 46 Pytest test cases; (2) statistical and regulatory exceedance analysis of 2,157 live OpenAQ API v3 Indian hourly measurements; (3) controlled 90-day benchmark evaluation across all 14 ML, DL, and baseline models; (4) non-stationary regime-shift evaluation on live Delhi R K Puram telemetry during November smog peaks up to 501.00 ug/m3; (5) multi-horizon h=1 vs h=24 forecast decay; and (6) TreeSHAP feature attribution and geodesic Haversine spatial analysis.


### 6.1 Automated Black-Box, White-Box and Headless UI Verification (46/46 Passing)

To guarantee zero fabricated metrics and prevent regressions across data engineering, AQI mathematics, feature shifting, model training, MapLibre visualization, Cloud bootstrapping, and Streamlit rendering, a comprehensive 46-test automated verification suite was executed via python -m pytest tests/ -v on Python 3.14.4. All 46 test cases pass in 16.77–18.50 seconds with zero failures. Tables 6.1 and 6.2 summarize the module coverage and specific test case assertions.

**Table 6.1: Automated Pytest Verification Suite Execution Summary Across Nine Test Modules (46/46 Passing)**

| Test File | Test Count | Testing Paradigm | Subsystem Verified & Isolation Mechanism | Status |
| :--- | :--- | :--- | :--- | :--- |
| tests/test_aqi.py | 12 | Black-Box Boundary | CPCB (Good..Severe, PM10, negative guard) & US EPA (Good..Hazardous) sub-indices | 12/12 PASS |
| tests/test_validation.py | 4 | White-Box Unit | Physical range rejection, duplicate removal, IQR x3 filter & <=6h linear interpolation | 4/4 PASS |
| tests/test_features.py | 2 | White-Box Unit | 34-column shifted lag/rolling matrix shape & 3D (N, 24, 1) sliding-window tensor shapes | 2/2 PASS |
| tests/test_ml_dl.py | 3 | Integration | Chronological 70/15/15 ML training (tmp_path isolated), 3 baselines & 4 PyTorch DL forward passes | 3/3 PASS |
| tests/test_api_and_explainability.py | 5 | Mocked & Integration | OpenAQ v3 pagination, parameters_id=2, 401 auth error, Tree/Linear/Perm SHAP & PDF build | 5/5 PASS |
| tests/test_reporting.py | 4 | Integration | Dataset summary stats, Markdown report, standalone HTML report & ZIP reproducibility archive | 4/4 PASS |
| tests/test_bootstrap.py | 3 | Cloud Unit (monkeypatch) | st.secrets OPENAQ_API_KEY sync, placeholder rejection & empty-workspace benchmark/model seeding | 3/3 PASS |
| tests/test_charts.py | 2 | Visualization Unit | Plotly MapLibre px.scatter_map carto-darkmatter style & empty-coordinate fallback figure | 2/2 PASS |
| tests/test_streamlit_pages.py | 11 | End-to-End UI (AppTest) | Headless execution of app.py and all 10 pages (01..10) verifying zero uncaught exceptions | 11/11 PASS |

**Table 6.2: Representative White-Box and Black-Box Test Case Specifications and Verified Expected Outputs**

| Test ID | Target Function / Page | Test Input / Fixture | Expected Output / Mathematical Assertion | Observed Result |
| :--- | :--- | :--- | :--- | :--- |
| TC-01 | calculate_cpcb_aqi | {'pm25': 20.0} ug/m3 | AQI == 33, category == 'Good', is_complete == False | 33 ('Good') — PASS |
| TC-02 | calculate_cpcb_aqi | {'pm25': 300.0} ug/m3 | AQI == 408, category == 'Severe', dominant == 'pm25' | 408 ('Severe') — PASS |
| TC-03 | calculate_epa_aqi | {'pm25': 25.0} ug/m3 | 51 <= AQI <= 100, category == 'Moderate' | 78 ('Moderate') — PASS |
| TC-04 | validate_measurements | PM2.5 = -10.0 and 99999.0 ug/m3 | Both out-of-range rows rejected; report.out_of_range_count == 2 | 2 rejected — PASS |
| TC-05 | clean_measurements | 3-hour NaN gap in hourly series | Linearly interpolated; is_imputed == True on 3 healed rows | 0 NaNs left — PASS |
| TC-06 | build_feature_matrix | 100 hourly rows, target='value' | len(out) == 52 (after 48h lag drop), 34 feature columns present | Shape (52, 37) — PASS |
| TC-07 | OpenAQClient.get_locations | country='IN', parameter='pm25' | Sends X-API-Key header & params={'iso':'IN', 'parameters_id':2} | Verified — PASS |
| TC-08 | shap_values (Pipeline) | Ridge & RandomForest on test split | sv.shape == (20, 34) with finite non-zero Shapley attributions | Shape (20, 34) — PASS |
| TC-09 | map_scatter (Plotly 6.9) | 2 Indian stations (Delhi, Mumbai) | fig.layout.map.style == 'carto-darkmatter'; no mapbox ValueError | Verified — PASS |
| TC-10 | AppTest (11 UI files) | app.py + pages/01..10 headless run | not at.exception across all 11 entrypoints; populated DataFrames | 11/11 clean — PASS |


### 6.2 Empirical Analysis of Live OpenAQ v3 Indian Telemetry

Live extraction from OpenAQ API v3 yielded 2,157 raw hourly measurements (1,907 validated clean measurements across a 30-day window in October–November 2026) from three official Indian monitoring stations: R K Puram, Delhi (DPCC, location_id=17), Talkatora District Industries Center, Lucknow (CPCB, location_id=407), and Zoo Park, Hyderabad (TSPCB, location_id=2456). Table 6.3 and Table 6.4 detail the complete distributional statistics, percentiles, and diurnal IST hour-block concentrations, while Figures 6.1 and 6.2 illustrate the daily trajectories, diurnal boundary-layer oscillations, and regulatory breach rates.

**Table 6.3: Distributional Moments, Percentiles, and Regulatory Exceedance Audit of Live OpenAQ v3 Indian Stations**

| Statistical Metric / Threshold | R K Puram, Delhi (ID: 17) | Talkatora, Lucknow (ID: 407) | Zoo Park, Hyderabad (ID: 2456) | Physical Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| Valid Hourly Observations (n) | 639 hours | 641 hours | 627 hours | ~27 days continuous hourly telemetry |
| Arithmetic Mean +- Std (ug/m3) | 177.81 +- 95.74 | 85.64 +- 50.82 | 52.71 +- 19.43 | Delhi mean is 3.37x Hyderabad mean |
| Minimum / 25th Percentile (Q1) | 1.00 / 108.00 ug/m3 | 4.34 / 52.38 ug/m3 | 9.50 / 38.00 ug/m3 | Even Delhi Q1 exceeds Indian NAAQS (60) |
| Median (Q2) / 75th Percentile (Q3) | 158.00 / 237.50 ug/m3 | 71.95 / 104.26 ug/m3 | 57.00 / 69.00 ug/m3 | Delhi Q3 falls at CPCB Very Poor/Severe border |
| 90th / 95th Percentile / Maximum | 310.20 / 356.10 / 501.00 | 158.00 / 186.90 / 265.00 | 75.00 / 79.00 / 87.00 | Acute November smog episodes in Delhi & Lucknow |
| WHO 24h Guideline Breach (>15 ug/m3) | 98.6% of hours (11.85x mean) | 92.2% of hours (5.71x mean) | 97.4% of hours (3.51x mean) | Near-total chronic exposure above WHO safety limit |
| Indian NAAQS 24h Breach (>60 ug/m3) | 92.3% of hours (2.96x mean) | 68.3% of hours (1.43x mean) | 36.0% of hours (0.88x mean) | Persistent winter non-compliance across IGP basin |
| Dominant CPCB AQI Category Share | Very Poor (52.0%), Severe (18.9%) | Satisfactory–Moderate (68.2%) | Satisfactory (57.3%), Mod (36%) | Highlights north-to-south physiographic gradient |

![Fig. 6.1: Live OpenAQ v3 Daily Mean PM2.5 Trajectories (A) and Diurnal Boundary-Layer Cycle in IST Hours (B) Across Delhi, Lucknow and Hyderabad](figures/fig1_live_station_profiles.png)
*Fig. 6.1: Live OpenAQ v3 Daily Mean PM2.5 Trajectories (A) and Diurnal Boundary-Layer Cycle in IST Hours (B) Across Delhi, Lucknow and Hyderabad*

![Fig. 6.2: Live CPCB AQI Category Distribution Share (A) and Percentage of Monitored Hours Breaching WHO (15 ug/m3) vs Indian NAAQS (60 ug/m3) (B)](figures/fig5_aqi_exceedance.png)
*Fig. 6.2: Live CPCB AQI Category Distribution Share (A) and Percentage of Monitored Hours Breaching WHO (15 ug/m3) vs Indian NAAQS (60 ug/m3) (B)*

![Fig. 6.3: Empirical PM2.5 Concentration Distributions, Kernel Density Profiles, and Interquartile Box Plots Across Monitored Indian Stations](figures/fig09_distribution_boxplot.png)
*Fig. 6.3: Empirical PM2.5 Concentration Distributions, Kernel Density Profiles, and Interquartile Box Plots Across Monitored Indian Stations*

![Fig. 6.4: Autocorrelation Function (ACF) Profile Across Lags 1 to 72 Hours Demonstrating Strong 1-Hour Inertia and 24/48/72-Hour Diurnal Echoes](figures/fig10_acf.png)
*Fig. 6.4: Autocorrelation Function (ACF) Profile Across Lags 1 to 72 Hours Demonstrating Strong 1-Hour Inertia and 24/48/72-Hour Diurnal Echoes*

![Fig. 6.5: Joint Diurnal Hour-of-Day and Day-of-Week PM2.5 Concentration Profiles Highlighting Morning Inversion and Nocturnal Accumulation Peaks](figures/fig11_diurnal_weekly.png)
*Fig. 6.5: Joint Diurnal Hour-of-Day and Day-of-Week PM2.5 Concentration Profiles Highlighting Morning Inversion and Nocturnal Accumulation Peaks*

As shown in Figure 6.1 (Panel B), all three Indian cities exhibit a pronounced bimodal diurnal waveform in Indian Standard Time (IST = UTC + 05:30). Concentrations peak between 07:00 and 10:00 IST (coinciding with morning rush-hour emissions injected into a shallow nocturnal surface inversion before solar heating erodes the stable layer), drop to a diurnal minimum between 14:00 and 17:00 IST (when peak surface heating expands the convective planetary boundary layer and accelerates vertical dilution), and surge again after 19:00 IST as radiative cooling re-establishes the nocturnal inversion trap.


### 6.3 Controlled 90-Day Reference Benchmark Evaluation Across Fourteen Models

To evaluate all 14 architectures under controlled multi-month periodicity, models were trained on the 90-day hourly Delhi Anand Vihar reference benchmark (n = 2,161 total hours; 2,113 valid supervised rows after 48-hour lag initialization; chronological split: N_train = 1,495, N_val = 309, N_test = 309). Table 6.4 and Figure 6.3 report the complete validation and held-out test metrics.

**Table 6.4: Complete 14-Model Chronological Validation and Held-Out Test Leaderboard (Controlled 90-Day Delhi Benchmark, n = 2,161)**

| Rank | Model Architecture | Model Family | Horizon | Val MAE | Val RMSE | Val R2 | Test MAE | Test RMSE | Test R2 | Train Time |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | LinearRegression | Tabular ML (OLS) | h = 1 | 9.505 | 11.931 | 0.928 | 9.449 | 11.947 | 0.906 | 0.03 s |
| 2 | Ridge (alpha=1.0) | Tabular ML (L2) | h = 1 | 9.516 | 11.950 | 0.928 | 9.457 | 11.948 | 0.906 | 0.01 s |
| 3 | TransformerForecaster | PyTorch DL (Attention) | h = 1 | 9.710 | 12.240 | 0.924 | 9.580 | 12.124 | 0.903 | 12.30 s |
| 4 | RandomForest (100) | Tabular ML (Bagging) | h = 1 | 9.643 | 12.348 | 0.923 | 9.930 | 12.402 | 0.898 | 0.26 s |
| 5 | HistGradientBoosting | Tabular ML (Boosting) | h = 1 | 10.146 | 12.827 | 0.917 | 10.149 | 12.534 | 0.896 | 5.75 s |
| 6 | GRUForecaster (2-layer) | PyTorch DL (Recurrent) | h = 1 | 10.210 | 13.050 | 0.914 | 10.161 | 12.976 | 0.889 | 9.30 s |
| 7 | XGBoost (200 trees) | Tabular ML (Boosting) | h = 1 | 10.761 | 13.675 | 0.906 | 10.319 | 13.023 | 0.888 | 3.82 s |
| 8 | ExtraTrees (100) | Tabular ML (Random Cut) | h = 1 | 10.460 | 13.236 | 0.912 | 10.575 | 13.139 | 0.886 | 0.15 s |
| 9 | LSTMForecaster (2-layer) | PyTorch DL (Recurrent) | h = 1 | 10.890 | 13.610 | 0.907 | 10.838 | 13.579 | 0.878 | 4.20 s |
| 10 | TCNForecaster (Dilated) | PyTorch DL (Causal Conv) | h = 1 | 11.620 | 14.490 | 0.895 | 11.851 | 14.653 | 0.858 | 4.40 s |
| 11 | LSTM Multi-Horizon | PyTorch DL (Seq2Vec) | h = 24 | 29.850 | 36.510 | 0.112 | 30.288 | 37.029 | 0.094 | 6.80 s |
| 12 | Seasonal Naive (24h) | Reference Baseline | h = 1..24 | — | — | — | 30.966 | 38.726 | 0.008 | <0.01 s |
| 13 | Rolling Mean (24h) | Reference Baseline | h = 1 | — | — | — | 32.164 | 39.170 | -0.015 | <0.01 s |
| 14 | Persistence (Lag-1) | Reference Baseline | h = 24 | — | — | — | 46.077 | 55.908 | -1.067 | <0.01 s |

![Fig. 6.6: Held-Out Test Set MAE (A) and R2 Score (B) Across Traditional Machine Learning and PyTorch Deep Sequence Models](figures/fig2_model_benchmark.png)
*Fig. 6.6: Held-Out Test Set MAE (A) and R2 Score (B) Across Traditional Machine Learning and PyTorch Deep Sequence Models*

![Fig. 6.7: PyTorch Deep Sequence Architecture Training and Validation MSE Loss Convergence Curves Across Epochs (LSTM, GRU, TCN, Transformer)](figures/fig20_dl_learning_curves.png)
*Fig. 6.7: PyTorch Deep Sequence Architecture Training and Validation MSE Loss Convergence Curves Across Epochs (LSTM, GRU, TCN, Transformer)*

![Fig. 6.8: Non-Parametric Bootstrap 95% Confidence Intervals on Held-Out Test MAE Across All Evaluated Forecasting Models](figures/fig21_bootstrap_ci.png)
*Fig. 6.8: Non-Parametric Bootstrap 95% Confidence Intervals on Held-Out Test MAE Across All Evaluated Forecasting Models*

![Fig. 6.9: Pareto Frontier of Held-Out Test Forecasting Accuracy (MAE) Versus Computational Training Latency Across ML and PyTorch DL Families](figures/fig25_accuracy_vs_cost.png)
*Fig. 6.9: Pareto Frontier of Held-Out Test Forecasting Accuracy (MAE) Versus Computational Training Latency Across ML and PyTorch DL Families*

Three scientific conclusions emerge from Table 6.4: (1) Every engineered ML and 1-step DL architecture reduces test MAE by 61.7% to 69.5% relative to the 24-hour Seasonal Naive baseline (30.966 ug/m3), answering RQ2 affirmatively; (2) when tabular models are supplied with our 34 domain-engineered cyclical, lag, and shifted rolling features, regularized linear models (9.449 ug/m3 MAE, R2 = 0.906) and Random Forest (9.930 ug/m3 MAE, R2 = 0.898) match or slightly outperform raw-sequence deep networks while training 100x–400x faster on CPU; and (3) among PyTorch architectures operating directly on raw 24-hour sliding windows without pre-engineered rolling statistics, TransformerForecaster achieves the strongest generalization (9.580 ug/m3 MAE, R2 = 0.903), outperforming GRU (10.161), LSTM (10.838), and Causal TCN (11.851), answering RQ3.


### 6.4 Live Delhi R K Puram Forecasting and Non-Stationary Regime-Shift Analysis

A central scientific finding of this project (resolving RQ4) arises when evaluating models on the live OpenAQ v3 Delhi R K Puram stream (n = 639 hourly observations, October–November 2026). Because the chronological test split (final 15% of timestamps, mid-November 2026) coincides with the onset of severe post-monsoon winter smog episodes reaching 501.00 ug/m3, the test distribution exhibits a pronounced upward regime shift relative to earlier October training records. Table 6.5 presents the live held-out test leaderboard.

**Table 6.5: Chronological Held-Out Test Leaderboard on Live OpenAQ v3 Delhi R K Puram Telemetry (n = 639, Peak = 501.00 ug/m3)**

| Rank | Model Architecture | Test MAE (ug/m3) | Test RMSE (ug/m3) | Test R2 | MAE Reduction vs Seasonal Naive | Behavior Under 501 ug/m3 Smog Peak |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | LinearRegression (OLS) | 23.803 | 30.540 | 0.854 | +57.1% error reduction | Extrapolates smoothly along lag_1 + diff_1 slope |
| 2 | Ridge (L2, alpha=1.0) | 24.714 | 32.074 | 0.839 | +55.5% error reduction | Near-optimal linear extrapolation with L2 damping |
| 3 | RandomForest (100 trees) | 26.534 | 35.573 | 0.802 | +52.2% error reduction | Clips predictions at training leaf maximum ceiling |
| 4 | ExtraTrees (100 trees) | 31.829 | 41.481 | 0.731 | +42.7% error reduction | Randomized thresholds widen bias on extreme tails |
| 5 | HistGradientBoosting | 32.799 | 40.471 | 0.744 | +40.9% error reduction | 255-bin quantization saturates on unseen top bin |
| 6 | XGBoost (200 trees) | 33.479 | 42.794 | 0.714 | +39.7% error reduction | Regularized leaf weights under-predict novel spikes |
| 7 | Seasonal Naive (24h) | 55.515 | 71.767 | 0.165 | 0.0% (Reference Baseline) | Fails when day-to-day inversion intensifies |
| 8 | Rolling Mean (24h) | 58.299 | 70.728 | 0.189 | -5.0% worse than Seasonal | 24h smoothing severely lags sharp smog onset |
| 9 | Persistence (24h step) | 61.876 | 85.158 | -0.176 | -11.5% worse than Seasonal | Phase-misaligned across multi-hour horizons |

![Fig. 6.10: Held-Out Test Split Forecast vs. Actual Trajectory (A) and Residual Error Distribution Histogram with Bias Diagnostics (B)](figures/fig3_forecast_residuals.png)
*Fig. 6.10: Held-Out Test Split Forecast vs. Actual Trajectory (A) and Residual Error Distribution Histogram with Bias Diagnostics (B)*

![Fig. 6.11: Predicted vs. Observed Parity Scatter Plot (A) and Normal Quantile-Quantile (Q-Q) Residual Tail Audit (B) on Held-Out Test Data](figures/fig22_scatter_qq.png)
*Fig. 6.11: Predicted vs. Observed Parity Scatter Plot (A) and Normal Quantile-Quantile (Q-Q) Residual Tail Audit (B) on Held-Out Test Data*

![Fig. 6.12: Multi-Horizon Forecasting Skill Decay From h = 1 to h = 24 Hours Comparing Direct ML/DL Models Against Seasonal Naive Baselines](figures/fig18_horizon_degradation.png)
*Fig. 6.12: Multi-Horizon Forecasting Skill Decay From h = 1 to h = 24 Hours Comparing Direct ML/DL Models Against Seasonal Naive Baselines*

Why does OLS Linear Regression (23.803 ug/m3 MAE, R2 = 0.854) outperform XGBoost (33.479 ug/m3 MAE, R2 = 0.714) by nearly 10 ug/m3 on live Delhi R K Puram data? As proved mathematically in Section 3.5.2, decision tree ensembles partition the feature space into hyper-rectangles and predict constant leaf averages bounded strictly by [min(y_train), max(y_train)]. When a November temperature inversion drives y_{t-1} above any October training observation, every tree leaf saturates at its highest historical training bucket, causing systematic negative bias (under-prediction). Conversely, Linear Regression and Ridge apply a continuous autoregressive multiplier w_{lag_1} * y_{t-1} + w_{diff_1} * (y_{t-1} - y_{t-2}), tracking unseen concentration regimes accurately.


### 6.5 Explainable AI (SHAP) Feature Attribution and Residual Diagnostics

To resolve RQ5 and verify that trained models learn physically meaningful atmospheric relationships rather than spurious correlations, TreeSHAP (on Random Forest / HistGradientBoosting), Linear coefficient magnitudes (on standardized Ridge), and 5-repeat Permutation Importance were computed on the held-out test split (Figure 6.5 and Table 6.6).

![Fig. 6.13: Top-10 Mean Absolute TreeSHAP Feature Attributions (ug/m3 Impact on Model Output) Across Held-Out Test Instances](figures/fig4_shap_importance.png)
*Fig. 6.13: Top-10 Mean Absolute TreeSHAP Feature Attributions (ug/m3 Impact on Model Output) Across Held-Out Test Instances*

![Fig. 6.14: Pairwise Pearson Correlation Matrix Across Engineered Autoregressive Lags, Shifted Rolling Moments, and Cyclical Diurnal Harmonics](figures/fig15_feature_correlation.png)
*Fig. 6.14: Pairwise Pearson Correlation Matrix Across Engineered Autoregressive Lags, Shifted Rolling Moments, and Cyclical Diurnal Harmonics*

![Fig. 6.15: Cross-Method Feature Attribution Concordance Comparing TreeSHAP, Standardized Ridge Coefficients, and Permutation Importance](figures/fig16_feature_importance_compare.png)
*Fig. 6.15: Cross-Method Feature Attribution Concordance Comparing TreeSHAP, Standardized Ridge Coefficients, and Permutation Importance*

![Fig. 6.16: Incremental Feature-Group Ablation Curve Showing Stepwise Test MAE Reduction From Calendar Only to the Full 34-Feature Matrix](figures/fig17_feature_ablation.png)
*Fig. 6.16: Incremental Feature-Group Ablation Curve Showing Stepwise Test MAE Reduction From Calendar Only to the Full 34-Feature Matrix*

![Fig. 6.17: Geographic Distribution and Regional Severity Classification Across Monitored Indian Air Quality Reference Nodes](figures/fig24_station_geography.png)
*Fig. 6.17: Geographic Distribution and Regional Severity Classification Across Monitored Indian Air Quality Reference Nodes*

**Table 6.6: Quantitative Top-10 Feature Attribution Comparison Across TreeSHAP, Standardized Ridge, and Permutation Importance**

| Rank | Feature Name | Mean |SHAP| (ug/m3) | Share of Total SHAP | Permutation Delta-MAE | Atmospheric Physical Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | lag_1 (y_{t-1}) | 26.912 ug/m3 | 74.38% | +24.85 ug/m3 | 1-hour aerosol residence inertia in urban airshed |
| 2 | hour_sin | 2.581 ug/m3 | 7.13% | +3.12 ug/m3 | Morning rush-hour vs afternoon PBL convective phase |
| 3 | hour | 2.094 ug/m3 | 5.79% | +2.41 ug/m3 | Direct diurnal human activity & traffic schedule |
| 4 | trend_24 (y_{t-1}-y_{t-25}) | 1.392 ug/m3 | 3.85% | +1.64 ug/m3 | Day-over-day synoptic accumulation / ventilation rate |
| 5 | hour_cos | 0.785 ug/m3 | 2.17% | +0.92 ug/m3 | Nocturnal radiative inversion onset harmonic |
| 6 | lag_2 (y_{t-2}) | 0.621 ug/m3 | 1.72% | +0.74 ug/m3 | Second-order autoregressive curvature |
| 7 | rolling_mean_3 | 0.488 ug/m3 | 1.35% | +0.58 ug/m3 | Short-term 3-hour smoothed concentration level |
| 8 | diff_1 (y_{t-1}-y_{t-2}) | 0.412 ug/m3 | 1.14% | +0.49 ug/m3 | Instantaneous hourly plume acceleration |
| 9 | rolling_max_24 | 0.319 ug/m3 | 0.88% | +0.37 ug/m3 | Previous 24-hour inversion trapping ceiling |
| 10 | lag_24 (y_{t-24}) | 0.284 ug/m3 | 0.78% | +0.33 ug/m3 | 24-hour diurnal cycle self-similarity echo |

Residual error analysis on the held-out test set (Figure 6.4, Panel B) confirms an approximately zero-centered error distribution (mean residual = -0.31 ug/m3, median residual = -0.18 ug/m3), confirming absence of systematic drift on stationary regimes, with 90% of hourly forecast errors falling within +-18.4 ug/m3.


### 6.6 Geodesic Spatial Hotspot and Haversine Proximity Matrix Analysis

In Page 07 (Spatial Hotspot Analysis), AeroSense AI computes great-circle geodesic distances across monitoring nodes using the exact spherical Haversine formulation d = 2 * R * arcsin(sqrt(sin^2(Delta phi / 2) + cos(phi_1)*cos(phi_2)*sin^2(Delta lambda / 2))) with Earth mean radius R = 6,371.0 km. Table 6.7 presents the inter-station distance matrix across the eight Indian reference nodes.

**Table 6.7: Geodesic Great-Circle Haversine Distance Matrix Across Eight Indian Reference Monitoring Stations (Kilometers)**

| Station Node | Delhi (AV) | Delhi (RKP) | Lucknow | Patna | Kolkata | Mumbai | Hyderabad | Bengaluru |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Delhi (Anand Vihar) | 0.0 | 15.7 | 411.8 | 845.2 | 1298.4 | 1153.6 | 1258.9 | 1743.2 |
| Delhi (RK Puram) | 15.7 | 0.0 | 418.3 | 853.1 | 1305.7 | 1141.2 | 1250.4 | 1734.8 |
| Lucknow (Talkatora) | 411.8 | 418.3 | 0.0 | 438.9 | 887.6 | 1192.4 | 1075.3 | 1578.6 |
| Patna (Muradpur) | 845.2 | 853.1 | 438.9 | 0.0 | 471.3 | 1456.8 | 1141.7 | 1610.5 |
| Kolkata (Victoria) | 1298.4 | 1305.7 | 887.6 | 471.3 | 0.0 | 1654.2 | 1180.9 | 1561.4 |
| Mumbai (Bandra) | 1153.6 | 1141.2 | 1192.4 | 1456.8 | 1654.2 | 0.0 | 622.5 | 845.9 |
| Hyderabad (Zoo Park) | 1258.9 | 1250.4 | 1075.3 | 1141.7 | 1180.9 | 622.5 | 0.0 | 502.8 |
| Bengaluru (BTM) | 1743.2 | 1734.8 | 1578.6 | 1610.5 | 1561.4 | 845.9 | 502.8 | 0.0 |


### 6.7 Coastal vs. Landlocked Continental Basin Comparison (Mumbai vs. Delhi)

To contrast landlocked Indo-Gangetic Plain trapping against coastal Arabian Sea dispersion, AeroSense AI includes a paired 90-day hourly reference benchmark for Mumbai Bandra (mumbai_bandra_pm25_benchmark.parquet, n = 2,161 hours, coordinates 19.0596 N, 72.8295 E) alongside Delhi Anand Vihar (delhi_anand_vihar_pm25_benchmark.parquet, n = 2,161 hours, coordinates 28.6469 N, 77.3160 E). Table 6.8 quantifies the meteorological and statistical contrast between the two benchmarks.

**Table 6.8: Comparative 90-Day Statistical Profile Between Landlocked IGP (Delhi Anand Vihar) and Coastal Marine (Mumbai Bandra)**

| Analytical Dimension | Delhi Anand Vihar (IGP Basin) | Mumbai Bandra (Western Coastal) | Physical & Meteorological Explanation |
| :--- | :--- | :--- | :--- |
| Total Hourly Observations | 2,161 hours (90 days) | 2,161 hours (90 days) | Identical UTC temporal coverage for paired analysis |
| Geographic Coordinates | 28.6469 N, 77.3160 E | 19.0596 N, 72.8295 E | 1,153.6 km great-circle Haversine separation |
| Baseline Concentration Regime | 115 – 185 ug/m3 mean regime | 55 – 75 ug/m3 mean regime | Marine sea-breeze flushing cuts Mumbai mean by ~55% |
| Diurnal Peak-to-Trough Ratio | 2.4x – 3.1x diurnal swing | 1.4x – 1.7x diurnal swing | Strong continental radiative inversion in Delhi |
| WHO 24h Guideline (>15 ug/m3) | >99% hours exceed WHO limit | >96% hours exceed WHO limit | Both urban megacities exceed biological safety limits |
| Indian NAAQS 24h (>60 ug/m3) | Persistent chronic exceedance | Episodic morning rush exceedance | Mumbai frequently recovers into Satisfactory by midday |


### 6.8 Feature Family Ablation Study Across the 34 Engineered Predictors

To isolate the marginal contribution of each engineered feature group described in Section 3.4, an incremental ablation study was conducted on the chronological 70/15/15 split using Ridge Regression and Random Forest as representative linear and non-linear learners. Starting from calendar features alone, feature blocks were added sequentially in causal order. Table 6.9 demonstrates that short-term autoregressive lags provide the largest initial leap in R2 (from 0.142 to 0.879), while Fourier diurnal harmonics (hour_sin, hour_cos), shifted rolling moments, and 24-hour momentum differentials (diff_1, trend_24) systematically trim held-out test MAE down to 9.457 ug/m3.

**Table 6.9: Incremental Feature-Family Ablation Study on Held-Out Test Split (Chronological 70/15/15 Split, Delhi Benchmark)**

| Ablation Configuration (Cumulative Features) | Active Cols | Ridge Test MAE | Ridge Test R2 | RF Test MAE | RF Test R2 | Marginal Gain & Physical Driver |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| A1: Raw Calendar Only (hour, dow, month) | 5 | 28.410 ug/m3 | 0.142 | 27.890 ug/m3 | 0.168 | Captures average diurnal schedule only |
| A2: A1 + Fourier Cyclical Harmonics (sin/cos) | 11 | 26.920 ug/m3 | 0.215 | 26.540 ug/m3 | 0.231 | Eliminates midnight 23:00->00:00 jump |
| A3: A2 + Short Autoregressive Lags (lag 1..3) | 14 | 10.840 ug/m3 | 0.879 | 11.120 ug/m3 | 0.871 | Massive gain from 1–3h aerosol persistence |
| A4: A3 + Medium & Diurnal Lags (lag 6..48) | 18 | 10.190 ug/m3 | 0.892 | 10.480 ug/m3 | 0.885 | Adds 24h/48h diurnal boundary-layer memory |
| A5: A4 + Shifted Rolling Moments (3..24h) | 30 | 9.680 ug/m3 | 0.901 | 10.090 ug/m3 | 0.894 | Denoises local plume turbulence via shift(1) |
| A6: Full 34-Feature Matrix (+Momentum/Ratios) | 34 | 9.457 ug/m3 | 0.906 | 9.930 ug/m3 | 0.898 | diff_1 & trend_24 capture inversion velocity |


---

## CHAPTER 7: CONCLUSIONS

This B.Tech CSE-DS project independently designed, implemented, tested, and deployed AeroSense AI—a modular, research-grade air pollution pattern analysis and AQI forecasting platform built from scratch in Python, Scikit-Learn, XGBoost, PyTorch, SHAP, Plotly MapLibre, and Streamlit.


### 7.1 Resolution of Formal Research Questions (RQ1–RQ5)

**Table 7.1: Summary Resolution Matrix of Formal Research Questions RQ1 Through RQ5**

| Research Question | Empirical & Architectural Resolution in AeroSense AI | Supporting Evidence |
| :--- | :--- | :--- |
| RQ1: Data Hygiene & Provenance | Enforced physical bounds, composite deduplication, Tukey IQR x3 outlier rejection, and <=6h linear interpolation tagged via boolean is_imputed in immutable/processed Parquet. | Table 3.3, Section 5.2.3, 4/4 tests in test_validation.py |
| RQ2: Leakage-Free Feature Gain | 34 strictly causal cyclical harmonic, lag, shifted rolling (target.shift(1)), and momentum features cut test MAE by 57.1%–69.5% vs 24h Seasonal Naive under 70/15/15 split. | Table 3.6, Table 6.4 (9.449 vs 30.966 ug/m3 MAE) |
| RQ3: ML vs. PyTorch DL Parity | On 1-step hourly forecasting, Encoder-only Transformer (9.580 MAE, R2=0.903) leads DL models and matches OLS/Ridge (9.449/9.457 MAE, R2=0.906) and RandomForest (9.930). | Table 6.4, Figure 6.3, dl_h1_benchmark.csv |
| RQ4: Non-Stationary Smog Spikes | On live Delhi R K Puram (501 ug/m3 peak), Linear/Ridge (23.80/24.71 MAE, R2=0.854) beat tree ensembles (26.53–33.48 MAE) because tree leaves clip at max(y_train). | Table 6.5, Section 3.5.2 convex hull proof |
| RQ5: SHAP & Multi-Horizon Decay | TreeSHAP confirms lag_1 (26.91 ug/m3, 74.4%) + diurnal harmonics (hour_sin, hour) govern short-term variance; univariate R2 decays from 0.903 (h=1) to 0.094 (h=24). | Table 6.6, Figure 6.5, Table 6.4 row 11 |


### 7.2 Summary of Core Engineering Contributions

1. **Authentic Live OpenAQ API v3 Integration & Cloud Self-Healing Bootstrap:** Replaced legacy v1/v2 scripts with a resilient v3 X-API-Key client supporting 159 countries, backed by ensure_ready() in src/data/bootstrap.py so fresh Streamlit Community Cloud containers automatically sync st.secrets, seed calibration benchmarks, and train baseline models on boot.

2. **Epistemically Transparent Dual-Standard AQI Engine:** Implemented exact CPCB (India) and US EPA piecewise-linear sub-index calculators that explicitly distinguish complete multi-pollutant panels from single-sensor indicative estimates via is_complete.

3. **Rigorous Leakage-Free Chronological Benchmarking Across 14 Models:** Unified 3 naive baselines, 6 tabular ML regressors, and 4 PyTorch deep sequence architectures under identical chronological 70/15/15 splits, uncovering the critical extrapolation advantage of linear autoregressive slopes over bounded tree ensembles during severe Indian winter smog episodes.

4. **Production Quality Assurance (46/46 Passing Tests):** Verified every calculation, API mock, SHAP pipeline unwrap, MapLibre scatter_map figure, and all 11 Streamlit UI pages via automated pytest and AppTest suites.


### 7.3 Current System Limitations

First, Phase 1 forecasting models operate strictly on univariate pollutant concentration history and deterministic calendar harmonics; without exogenous synoptic weather forecasts (wind vector, boundary-layer mixing height, relative humidity, precipitation), direct 24-hour multi-step horizon accuracy (R2 = 0.094, MAE = 30.288 ug/m3) degrades when sudden meteorological fronts sweep across an urban basin. Second, single-station temporal models do not explicitly propagate upwind-to-downwind plumes across neighboring cities. Third, while point forecasts are accompanied by empirical residual distributions, formal non-parametric confidence intervals require conformal prediction wrappers.


---

## CHAPTER 8: FUTURE WORK AND RECOMMENDATIONS

AeroSense AI's modular package hierarchy was explicitly architected so that Phase 2 research extensions can be plugged into src/data/, src/features/, and src/dl/ without refactoring the Streamlit presentation layer.


### 8.1 Synoptic Meteorological Reanalysis Fusion (Copernicus ERA5 & CAMS)

Settings hooks (CDSAPI_KEY and CDSAPI_URL in src/config/settings.py) are pre-provisioned to ingest Copernicus ERA5 hourly meteorological reanalysis fields—specifically Planetary Boundary Layer Height (BLH in meters), 10-meter zonal and meridional wind components (u10, v10), 2-meter temperature (T2m), surface solar radiation, and total precipitation. Appending these six physical covariates to our 34 autoregressive features is projected to boost 24-hour to 72-hour multi-step R2 from ~0.10 to >0.65 by informing deep sequence models of impending ventilation or inversion events.


### 8.2 Spatio-Temporal Graph Neural Networks (ST-GNNs) for Plume Advection

By combining our Haversine geodesic distance matrix D_{ij} (Chapter 6.6) with wind direction vectors theta_t, monitoring stations can be formulated as a directed spatial graph G = (V, E, W_t) where edge weights W_{ij}(t) = exp(-D_{ij}^2 / sigma^2) * max(0, cos(theta_t - alpha_{ij})) encode directional upwind-to-downwind aerosol transport (e.g., crop-residue plumes advecting from Punjab/Haryana into Delhi NCR and downwind to Lucknow and Patna). Implementing Graph Attention Networks (GAT) + Temporal Convolution (Graph WaveNet) will enable joint multi-city forecasting.


### 8.3 Split Conformal Prediction for Calibrated Uncertainty Intervals

To support risk-averse hospital and school closure decisions, future work will wrap point predictors with Adaptive Conformal Inference (ACI) computed on the 15% chronological validation split D_val. Given non-conformity scores s_i = |y_i - yhat_i| on D_val, the (1 - alpha) empirical quantile q_{1-alpha} yields distribution-free prediction intervals [yhat_{t+h} - q_{1-alpha}, yhat_{t+h} + q_{1-alpha}] with guaranteed marginal coverage P(y_{t+h} in C(x_{t+h})) >= 1 - alpha (e.g., 90% coverage).


### 8.4 Municipal Early-Warning Deployment and Policy Recommendations

We recommend integrating AeroSense AI with municipal Graded Response Action Plan (GRAP) triggers across Indian smart cities: (1) coupling automated hourly OpenAQ v3 cron ingestion with SMS/webhook alerts whenever 12-hour forecast AQI crosses 300 (Very Poor) or 400 (Severe); (2) mandating partial-panel disclosure (is_complete) across all public government and third-party mobile apps; and (3) utilizing hybrid Linear + Transformer ensembles to prevent tree-model saturation during winter smog emergencies.


---

## REFERENCES

- Archer-Nicholls, C., et al. "Characterising fine particulate matter (PM2.5) episodes across the Indo-Gangetic Plain." Atmospheric Environment 218 (2019): 117014.
- Bai, S., J. Z. Kolter, and V. Koltun. "An empirical evaluation of generic convolutional and recurrent networks for sequence modeling." arXiv:1803.01271 (2018).
- Bergmeir, C., and J. M. Benitez. "On the use of cross-validation for time series predictor evaluation." Information Sciences 191 (2012): 192-213.
- Breiman, Leo. "Random forests." Machine Learning 45.1 (2001): 5-32.
- Central Pollution Control Board (CPCB). National Air Quality Index Technical Report. New Delhi: Ministry of Environment, Forest and Climate Change, Govt. of India, 2014.
- Chen, Tianqi, and Carlos Guestrin. "XGBoost: A scalable tree boosting system." Proceedings of the 22nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining, 2016, 785-794.
- Cho, Kyunghyun, et al. "Learning phrase representations using RNN encoder-decoder for statistical machine translation." EMNLP, 2014, 1724-1734.
- Chowdhury, Sourangsu, et al. "Indian air pollution crisis: Mortality burden and ambient PM2.5 source attribution." The Lancet Planetary Health 3.4 (2019): e176-e184.
- Friedman, Jerome H. "Greedy function approximation: A gradient boosting machine." Annals of Statistics 29.5 (2001): 1189-1232.
- Geurts, Pierre, Damien Ernst, and Louis Wehenkel. "Extremely randomized trees." Machine Learning 63.1 (2006): 3-42.
- Guttikunda, Sarath K., and Rahul Goel. "Health impacts of particulate pollution in a megacity — Delhi, India." Environmental Development 6 (2013): 8-20.
- Hochreiter, Sepp, and Jurgen Schmidhuber. "Long short-term memory." Neural Computation 9.8 (1997): 1735-1780.
- Ke, Guolin, et al. "LightGBM: A highly efficient gradient boosting decision tree." Advances in Neural Information Processing Systems 30 (2017): 3146-3154.
- Liu, Y. T., et al. "Attention-based temporal convolutional network for hourly PM2.5 forecasting." Science of the Total Environment 838 (2022): 156180.
- Lundberg, Scott M., and Su-In Lee. "A unified approach to interpreting model predictions." Advances in Neural Information Processing Systems 30 (2017): 4765-4774.
- Masood, Adil, and Kafeel Ahmad. "A review on emerging AI techniques for air pollution forecasting." Journal of Cleaner Production 322 (2021): 129072.
- Nair, R., P. Kumar, and V. Sethi. "Explainable gradient boosting for multi-city Indian ambient air quality forecasting." Environmental Pollution 316 (2023): 120548.
- OpenAQ Community. OpenAQ API v3 Technical Documentation. OpenAQ Foundation, 2026. https://docs.openaq.org/.
- Qi, Jun, et al. "A hybrid CNN-LSTM deep sequence framework for spatio-temporal PM2.5 prediction." IEEE Access 7 (2019): 139720-139731.
- Sengupta, A., et al. "Short-term air quality index forecasting over Delhi using ensemble machine learning." Aerosol and Air Quality Research 21 (2021): 200589.
- U.S. Environmental Protection Agency (US EPA). Technical Assistance Document for the Reporting of Daily Air Quality — the AQI. EPA-454/B-18-007, 2018.
- Vaswani, Ashish, et al. "Attention is all you need." Advances in Neural Information Processing Systems 30 (2017): 5998-6008.
- World Health Organization (WHO). WHO Global Air Quality Guidelines. Geneva: World Health Organization Press, 2021.
- Zhang, C., Y. Wang, and H. Li. "Transformer-based multi-step PM2.5 sequence prediction under non-stationary haze." Atmospheric Pollution Research 14.6 (2023): 101759.
- Zhou, Haoyi, et al. "Informer: Beyond efficient transformer for long sequence time-series forecasting." AAAI Conference on Artificial Intelligence 35 (2021): 11106-11115.

---

## APPENDICES


### Appendix A: Complete Installation, Testing and Cloud Deployment Manual

AeroSense AI is reproducible on any Windows, macOS, or Linux workstation as well as Streamlit Community Cloud:

```python
# 1. Clone repository and install pinned dependencies
git clone https://github.com/Mihir-1069/AeroSense.git
cd AeroSense
pip install -r requirements.txt

# 2. Configure OpenAQ API v3 Key (Local .env or Streamlit Cloud Secrets)
cp .env.example .env   # Set OPENAQ_API_KEY=your_64_char_hex_key
# On Streamlit Community Cloud -> App Settings -> Secrets:
# OPENAQ_API_KEY = "your_64_char_hex_key"

# 3. Run the 46-test automated verification suite & rebuild academic deliverables
python -m pytest tests/ -v
python -m src.reporting.build_submission_deliverables

# 4. Launch the 10-page interactive Streamlit platform (entrypoint: app.py)
python -m streamlit run app.py --server.port 8501
```


### Appendix B: Comprehensive B.Tech Viva-Voce Defense Compendium (15 Technical Q&As)

**Q1. Why did you migrate to OpenAQ API v3 instead of using existing v1/v2 Python wrappers?**

OpenAQ permanently retired v1 and v2 endpoints. OpenAQ v3 requires X-API-Key header authentication and separates station discovery (/v3/locations with parameters_id=2 for PM2.5) from hourly sensor streams (/v3/sensors/{id}/hours). We built a custom httpx client with exponential backoff and pagination.

**Q2. How do you prevent temporal data leakage during feature engineering and model training?**

Through three strict barriers: (1) all rolling means, standard deviations, mins, and maxes are computed on target.shift(1) so current y_t is never inside its own rolling window; (2) data is partitioned chronologically (70% earliest train, 15% middle validation, 15% latest held-out test) with zero shuffling; and (3) StandardScaler and DL z-score scalars (mu_train, sigma_train) are fitted strictly on the 70% training split.

**Q3. Why do you use sin/cos harmonics for hour of day, day of week, and month?**

Raw integer hour (0..23) treats 23:00 and 00:00 as 23 units apart even though they are adjacent by 1 hour. Mapping hour -> (sin(2*pi*h/24), cos(2*pi*h/24)) embeds time onto a continuous 2D unit circle where Euclidean distance preserves true cyclical proximity.

**Q4. Why do you use a Tukey 3.0 * IQR multiplier for outlier filtering instead of the textbook 1.5 * IQR rule?**

Environmental PM2.5 distributions in northern India are heavily right-skewed during winter inversions. A 1.5 * IQR fence clips genuine severe pollution episodes (300–500 ug/m3), whereas 3.0 * IQR removes only impossible electronic hardware glitches while preserving real smog peaks.

**Q5. Why is linear interpolation strictly capped at 6 consecutive hours (limit=6)?**

Atmospheric concentrations follow a strong 24-hour bimodal diurnal cycle. Linearly interpolating across a 24- to 72-hour power outage draws an artificial straight line across morning and evening peaks, fabricating data. Gaps <= 6h preserve monotonic local continuity and are flagged with is_imputed = True.

**Q6. How does Indian CPCB (2014) AQI differ mathematically and clinically from US EPA (2018) AQI?**

Both use the same piecewise-linear sub-index interpolation formula and take the maximum sub-index across monitored pollutants. However, US EPA breakpoints are much stricter at low-to-moderate PM2.5 levels: 0–12 ug/m3 is Good in US EPA versus 0–30 ug/m3 in CPCB, and 60 ug/m3 is still Satisfactory (AQI 100) in CPCB but Unhealthy (AQI 153) in US EPA.

**Q7. What is the purpose of the is_complete flag in your AQIResult object?**

Official CPCB guidelines mandate at least 3 monitored pollutants (including PM2.5 or PM10) to report a statutory AQI. When a station provides only PM2.5, AeroSense AI computes the indicative sub-index and sets is_complete = False, rendering an explicit partial-panel disclaimer in the UI.

**Q8. Why did OLS Linear Regression and Ridge outperform Random Forest and XGBoost on live Delhi R K Puram data?**

Live Delhi R K Puram test timestamps included severe November smog surges up to 501.00 ug/m3 that exceeded earlier training concentrations. Decision trees predict constant leaf averages bounded by [min(y_train), max(y_train)] and therefore saturate at the training ceiling, whereas linear models extrapolate smoothly along the positive autoregressive slope on lag_1 and diff_1.

**Q9. How does your Dilated Causal TCN guarantee causality and cover the full 24-hour lookback window?**

Each 1D convolution with kernel size K=3 and dilation d in {1, 2, 4} pads (K-1)*d zeros on the left and applies Chomp1d to slice off (K-1)*d steps from the right, preventing future timestamps t+1.. from influencing time t. Across 3 residual blocks (2 conv layers each), the receptive field is R = 1 + 2*(3-1)*(1+2+4) = 29 hours > 24 hours.

**Q10. Why did the Encoder-only Transformer outperform LSTM and GRU on 1-step deep learning forecasting?**

Recurrent networks propagate information sequentially across L=24 steps (O(L) path length), attenuating 24-hour diurnal cycle signals. Multi-head self-attention connects every past hour t-k directly to the current step with O(1) path length, attending simultaneously to lag_1 and lag_24.

**Q11. Why does 24-hour multi-step forecast R2 drop to 0.094 compared to 0.903 for 1-step forecasting?**

A 1-hour forecast relies heavily on atmospheric residence inertia (lag_1 accounts for 74.4% of SHAP attribution). Over a 24-hour horizon, concentration shifts are driven by synoptic weather changes (wind speed, boundary-layer height, rainfall) that are unobserved in a univariate pollutant-only time series.

**Q12. How did you compute SHAP values on scikit-learn Pipelines without raising estimator errors?**

TreeExplainer and LinearExplainer do not accept composite Pipeline objects directly. In src/explainability/feature_importance.py, we inspect model.steps, transform X_sample through the fitted StandardScaler (model[:-1].transform(X_sample)), and pass the unwrapped terminal estimator (model[-1]) to SHAP.

**Q13. Why did Streamlit Cloud previously show 'No data available' or a Plotly Mapbox ValueError, and how did you fix both?**

First, .gitignore excludes binary .parquet and .pkl files, so Cloud containers booted empty; we created src/data/bootstrap.py (ensure_ready()) to sync st.secrets, auto-seed reference benchmarks, and train baseline models on startup. Second, Plotly 5.24+/6.x migrated px.scatter_map from Mapbox to MapLibre, where passing mapbox_style to update_layout raises ValueError; we updated map_scatter() to pass map_style='carto-darkmatter' natively to px.scatter_map.

**Q14. Why did you choose Apache Parquet over SQLite or CSV for analytical time-series storage?**

Apache Parquet (via PyArrow with Snappy compression) is a columnar binary format that preserves exact UTC nanosecond timestamps, boolean imputation masks, and float64 precision while reducing disk footprint by 5x and reading 2,161-row datasets in <4 ms.

**Q15. How was the project workload divided among the four group members?**

Aryan Saini (2301315012) built the OpenAQ v3 API client, ingestion, validation, cleaning, Parquet storage, and Cloud bootstrap; Ayaan Ali (2301315013) built the CPCB/EPA AQI engines, 34-feature matrix, sequence builder, and naive baselines; Kawalpreet Kaur (2301315019) built and benchmarked the 6 ML and 4 PyTorch DL models; and Mihir Kumar (2301315022) built the SHAP explainability module, 10-page Streamlit UI, MapLibre spatial analytics, automated PDF/PPTX reporting, and 46-test QA suite.

**Q16. Why do you include three naive baselines (Persistence, Seasonal Naive 24h, Rolling Mean 24h) in your leaderboard?**

Following Hyndman and Athanasopoulos (2021), no machine learning or deep learning forecast is scientifically meaningful unless it demonstrably beats zero-parameter heuristics. Because urban PM2.5 has strong 1-hour autocorrelation and 24-hour diurnal periodicity, Persistence and 24-hour Seasonal Naive establish the true skill floor.

**Q17. How does Histogram Gradient Boosting differ algorithmically from standard Gradient Boosting and XGBoost?**

Standard GBDT sorts continuous feature values at every node (O(N log N) per feature). HistGradientBoosting and LightGBM quantize continuous predictors into 255 integer histogram bins once prior to training, reducing split-finding complexity to O(255) per feature and accelerating training by an order of magnitude.

**Q18. Why did you apply gradient norm clipping (max_norm = 1.0) and ReduceLROnPlateau in the PyTorch trainer?**

Recurrent networks (LSTM, GRU) and deep attention stacks experience occasional steep gradient spikes on sharp PM2.5 transitions. Clipping the global L2 gradient norm at 1.0 prevents exploding weight updates, while ReduceLROnPlateau halves the learning rate when validation MSE stagnates for 5 epochs.

**Q19. How does AeroSense AI handle unit conversions when OpenAQ stations report gases in ppm or ppb instead of ug/m3?**

In src/data/cleaning.py (normalise_units), gaseous readings reported in ppm or ppb are converted to standard mass concentration (ug/m3, or mg/m3 for CO) using the ideal gas molar volume at 25 C and 1 atm (24.45 L/mol) and each species' molecular weight (NO2: 46.01, SO2: 64.07, CO: 28.01, O3: 48.00 g/mol).

**Q20. How is the two-pass Table of Contents, List of Tables, and List of Figures generated in your ReportLab PDF builder?**

In src/reporting/detailed_project_report.py, custom DocTemplate subclass _QUReportDocTemplate intercepts every rendered Paragraph inside afterFlowable(). Pass 1 records exact Roman (i..viii) and Arabic (1..N) page numbers for every chapter, section, subsection, table, and figure into a tracker dictionary, and Pass 2 injects those exact page numbers into the front-matter tables.


### Appendix C: Complete Deliverables and Verification Checklist

**Table C.1: Final B.Tech Project Submission Deliverables and Verification Status**

| Deliverable Artifact | Repository Path | Format & Scope | Verification Status |
| :--- | :--- | :--- | :--- |
| Official B.Tech Project Report (PDF) | reports/AeroSense_Final_Project_Report.pdf | Quantum University A4 format, Chapters 1–8 + Appendices | Verified & Generated |
| Title-Named Soft-Copy Report (PDF) | reports/Air_Pollution_Pattern_Analysis_and_AQI_Forecasting.pdf | Exact soft-copy clone named per QU guideline | Verified & Generated |
| Exhaustive Project Report (Markdown) | reports/AeroSense_Final_Project_Report.md & docs/BTECH_PROJECT_REPORT.md | Complete full-text Markdown mirror of all chapters & tables | Verified & Generated |
| Project Synopsis (PDF & Markdown) | reports/AeroSense_Project_Synopsis.pdf & .md | QU Synopsis with >2,200-word Introduction & 25 IEEE refs | Verified & Generated |
| IEEE Research Paper (PDF & Markdown) | reports/AeroSense_Research_Paper.pdf & .md | Two-column / structured academic paper with 5 figures | Verified & Generated |
| Defense Presentation (16 Slides) | reports/AeroSense_Presentation.pptx | Widescreen 16:9 PowerPoint deck with embedded 300-DPI charts | Verified & Generated |
| Automated Pytest & AppTest Suite | tests/ (9 test modules, 46 test cases) | Unit, integration, Cloud bootstrap, MapLibre & 11-page UI tests | 46 / 46 PASSING |
