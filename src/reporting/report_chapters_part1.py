"""Detailed Chapters 1 to 4 for the Quantum University B.Tech Project Report."""
from __future__ import annotations

import html
from pathlib import Path
from typing import Callable, List

from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer


def append_chapters_1_to_4(
    el: list,
    qstyles: dict,
    fig_dir: Path,
    team_members: list,
    meta: dict,
    chapter_block: Callable,
    sec: Callable,
    subsec: Callable,
    add_table_block: Callable,
    add_figure: Callable,
    code_block: Callable,
) -> None:
    """Append exhaustive Chapters 1, 2, 3, and 4 to the ReportLab story list."""

    # =========================================================================
    # CHAPTER 1  INTRODUCTION
    # =========================================================================
    chapter_block(el, 1, "INTRODUCTION", qstyles, is_first=True)
    el.append(Paragraph(
        "Ambient air pollution constitutes one of the most severe environmental, epidemiological, and computational challenges "
        "of the twenty-first century. Rapid industrialization, high-density vehicular corridors, seasonal agricultural residue "
        "burning, and topographic boundary-layer trapping subject billions of urban residents—particularly across South Asia and "
        "the Indo-Gangetic Plain (IGP)—to hazardous concentrations of fine particulate matter and reactive trace gases. This "
        "opening chapter establishes the atmospheric physical foundations, public health urgency, regulatory divergence, failure "
        "modes of conventional environmental portals, formal research questions, and engineering scope of the AeroSense AI platform.",
        qstyles["BodyNoIndent"],
    ))

    el.append(sec("1.1 Atmospheric Background, Particulate Micro-Physics and Public Health Burden", qstyles))
    el.append(Paragraph(
        "Atmospheric pollutants are broadly classified into particulate aerosols and gaseous species. Among regulated criteria "
        "pollutants—fine particulate matter (PM2.5), respirable coarse particulate matter (PM10), nitrogen dioxide (NO2), sulfur "
        "dioxide (SO2), carbon monoxide (CO), and ground-level ozone (O3)—PM2.5 (suspended solid and liquid droplets with aerodynamic "
        "diameter d_a <= 2.5 micrometers) exerts the highest attributable human mortality. Whereas coarse particles (2.5 < d_a <= 10 "
        "micrometers) are predominantly intercepted by mucociliary clearance in the nasopharyngeal tract, PM2.5 aerosols bypass upper "
        "airway filtration, penetrate deep into terminal bronchioles and pulmonary alveoli, and translocate across the alveolar-capillary "
        "membrane directly into systemic arterial circulation.",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "Once inside the vascular system, transition metals, polycyclic aromatic hydrocarbons (PAHs), black carbon, and secondary "
        "inorganic sulfate/nitrate salts adsorbed onto PM2.5 surfaces induce oxidative stress, endothelial dysfunction, systemic "
        "inflammation, and prothrombotic cascades. Long-term cohort syntheses by the World Health Organization (WHO Global Air Quality "
        "Guidelines, 2021) and the Global Burden of Disease (GBD) study establish causal links between chronic and acute PM2.5 exposure "
        "and ischemic heart disease, cerebrovascular stroke, chronic obstructive pulmonary disease (COPD), acute lower respiratory "
        "infections, lung adenocarcinoma, adverse birth outcomes, and pediatric neurodevelopmental impairment.",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "To guide public health interventions, national and international bodies promulgate ambient concentration thresholds. In September "
        "2021, the WHO halved its annual mean PM2.5 guideline from 10 ug/m3 to 5 ug/m3 and reduced its 24-hour mean guideline from "
        "25 ug/m3 to 15 ug/m3. Conversely, India's National Ambient Air Quality Standards (NAAQS), notified by the Central Pollution "
        "Control Board (CPCB, 2009), define an annual PM2.5 limit of 40 ug/m3 and a 24-hour limit of 60 ug/m3—reflecting a four-fold "
        "to eight-fold regulatory divergence from WHO biological safety thresholds. Similarly, the United States Environmental Protection "
        "Agency (US EPA, revised 2024) enforces an annual primary PM2.5 standard of 9.0 ug/m3 and a 24-hour standard of 35 ug/m3. "
        "Table 1.1 summarizes these multi-pollutant regulatory benchmarks enforced across the AeroSense AI compliance engine.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "1.1", "Multi-Pollutant Ambient Regulatory Standards Across WHO (2021), Indian CPCB NAAQS (2009), and US EPA (2024)",
        [
            ["Pollutant", "Averaging Period", "WHO 2021 Guideline", "Indian CPCB NAAQS", "US EPA NAAQS", "Primary Anthropogenic Sources"],
            ["PM2.5", "24-Hour Mean", "15.0 ug/m3", "60.0 ug/m3", "35.0 ug/m3", "Combustion, vehicular exhaust, secondary aerosols"],
            ["PM2.5", "Annual Mean", "5.0 ug/m3", "40.0 ug/m3", "9.0 ug/m3", "Industrial plumes, biomass burning, power plants"],
            ["PM10", "24-Hour Mean", "45.0 ug/m3", "100.0 ug/m3", "150.0 ug/m3", "Road resuspension dust, construction, crustal soil"],
            ["PM10", "Annual Mean", "15.0 ug/m3", "60.0 ug/m3", "Discontinued", "Quarrying, unpaved transport corridors, brick kilns"],
            ["NO2", "24-Hour / 1-Hour", "25.0 ug/m3 (24h)", "80.0 ug/m3 (24h)", "100 ppb (1h)", "High-temperature diesel/petrol engine combustion"],
            ["SO2", "24-Hour / 1-Hour", "40.0 ug/m3 (24h)", "80.0 ug/m3 (24h)", "75 ppb (1h)", "Coal thermal power stations, high-sulfur fuel oil"],
            ["CO", "8-Hour Mean", "4.0 mg/m3", "2.0 mg/m3", "9.0 ppm (~10 mg/m3)", "Incomplete hydrocarbon and residential fuel burn"],
            ["O3", "8-Hour Peak", "100.0 ug/m3", "100.0 ug/m3", "0.070 ppm (~137 ug/m3)", "Photochemical NOx + VOC reaction under solar UV"],
        ],
        [1.8 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2.4 * cm, 3.8 * cm],
        qstyles, font_pt=8.4,
    )

    el.append(sec("1.2 Meteorology and Topography of the Indo-Gangetic Plain vs Peninsular India", qstyles))
    el.append(Paragraph(
        "Air pollutant concentration at ground level is governed not solely by emission flux, but critically by atmospheric dispersion "
        "volume. Across northern India, the Indo-Gangetic Plain forms a vast alluvial trough bounded to the north and northeast by the "
        "Himalayan mountain arc. During post-monsoon and winter months (October through February), synoptic wind speeds drop, solar "
        "insolation weakens, and rapid nocturnal longwave radiative cooling chills the ground surface relative to aloft air layers. "
        "This creates a strong surface temperature inversion that suppresses vertical convective mixing and collapses the Planetary "
        "Boundary Layer (PBL) from summer daytime heights exceeding 1,800 meters down to nocturnal winter depths below 100–150 meters.",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "When continuous urban emissions (vehicular tailpipes, diesel generators, domestic solid-fuel heating, and regional Kharif "
        "paddy residue burning) inject particulates into a compressed 120-meter mixing column, ground-level PM2.5 surges non-linearly "
        "from baseline levels (~60 ug/m3) to hazardous smog episodes exceeding 400–500 ug/m3 within 12 to 24 hours. By contrast, coastal "
        "and Deccan plateau cities (such as Mumbai, Chennai, and Hyderabad) benefit from marine land-sea breeze circulation and deeper "
        "convective boundary layers, yielding substantially lower mean concentrations and muted diurnal amplitude.",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "To anchor our research in real-world atmospheric behavior rather than synthetic assumptions, AeroSense AI extracted 30 days "
        "of continuous hourly telemetry (October–November 2026, n = 2,157 raw records, 1,907 validated clean records) directly from the "
        "live OpenAQ API v3 across three representative Indian government reference stations summarized in Table 1.2.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "1.2", "Live OpenAQ v3 Telemetry Baseline Snapshot Across Three Indian Geographies (Oct–Nov 2026)",
        [
            ["Monitoring Station & Agency", "OpenAQ ID", "Physiographic Zone", "Valid Hrs", "Mean +- Std (ug/m3)", "Min–Max (ug/m3)", "WHO >15", "NAAQS >60"],
            ["R K Puram, Delhi (DPCC)", "17", "Indo-Gangetic Plain (North)", "639", "177.81 +- 95.74", "1.00 – 501.00", "98.6%", "92.3%"],
            ["Talkatora, Lucknow (CPCB)", "407", "Central Indo-Gangetic Basin", "641", "85.64 +- 50.82", "4.34 – 265.00", "92.2%", "68.3%"],
            ["Zoo Park, Hyderabad (TSPCB)", "2456", "Deccan Peninsular Plateau", "627", "52.71 +- 19.43", "9.50 – 87.00", "97.4%", "36.0%"],
        ],
        [3.3 * cm, 1.3 * cm, 2.7 * cm, 1.3 * cm, 2.2 * cm, 1.9 * cm, 1.1 * cm, 1.1 * cm],
        qstyles, font_pt=8.2,
    )

    el.append(sec("1.3 Critical Engineering Deficiencies in Existing Air Quality Portals", qstyles))
    el.append(Paragraph(
        "A rigorous audit of existing academic prototypes, open-source repositories, and public air quality dashboards reveals five "
        "pervasive methodological and software engineering failures that compromise their scientific validity:",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "1. <b>Reliance on Retired APIs or Fabricated Demo Data:</b> Following OpenAQ's retirement of legacy v1 and v2 REST endpoints "
        "and mandatory enforcement of v3 X-API-Key authentication, numerous existing tools fail at runtime or silently substitute random "
        "number generators in place of real sensor observations.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "2. <b>Unbounded Interpolation Across Multi-Day Telemetry Blackouts:</b> Environmental monitoring stations frequently suffer power "
        "or calibration outages lasting 24 to 72 hours. Naive pipelines call pandas.DataFrame.interpolate() across the entire series "
        "without a gap ceiling, fabricating synthetic straight lines across multi-day diurnal cycles and corrupting downstream training.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "3. <b>Temporal Look-Ahead Leakage in Feature Engineering and Cross-Validation:</b> Two subtle forms of data leakage pervade "
        "published student notebooks: (a) using randomized k-fold cross-validation or train_test_split(shuffle=True) on autocorrelated "
        "time series, allowing future observations at t+1 to train models predicting t; and (b) computing rolling averages via "
        "df['value'].rolling(w).mean() without shifting onto y_{t-1}, thereby leaking y_t / w directly into the input vector X_t.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "4. <b>Silent Partial-Panel AQI Misrepresentation:</b> Official CPCB (2014) AQI computation requires at least three monitored "
        "pollutants including PM2.5 or PM10. Most single-sensor dashboards compute a PM2.5 sub-index and display it as an unqualified "
        "official AQI without disclosing missing co-pollutants.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "5. <b>Opaque Black-Box Predictions and Unexamined Regime Shifts:</b> Deep neural networks and tree ensembles are frequently "
        "deployed without game-theoretic attribution (SHAP) or analysis of why decision trees fail to extrapolate beyond training "
        "bounds during extreme winter smog surges.",
        qstyles["Bullet"],
    ))

    el.append(sec("1.4 Formal Problem Statement and Research Questions", qstyles))
    el.append(Paragraph(
        "The core problem addressed by this B.Tech project is the design, implementation, and empirical validation of a modular, "
        "leakage-free, explainable air quality analytics and forecasting platform (AeroSense AI) capable of ingesting live global "
        "OpenAQ API v3 telemetry, enforcing bounded data hygiene, computing epistemically transparent CPCB and US EPA AQI ratings, "
        "and benchmarking classical machine learning against deep sequence neural architectures under stationary and non-stationary "
        "Indian atmospheric regimes. This investigation is structured around five formal research questions:",
        qstyles["Body"],
    ))
    el.append(Paragraph("• <b>RQ1 (Data Hygiene & Provenance):</b> How can live OpenAQ v3 sensor streams be validated, filtered for hardware glitches, and imputed across brief drop-outs (<= 6h) while preserving strict provenance between observed and imputed records?", qstyles["Bullet"]))
    el.append(Paragraph("• <b>RQ2 (Leakage-Free Feature Synthesis):</b> How much predictive gain do 34 strictly causal cyclical harmonic, autoregressive lag, shifted rolling moment, and momentum features provide over Persistence and 24-hour Seasonal Naive baselines under a 70/15/15 chronological split?", qstyles["Bullet"]))
    el.append(Paragraph("• <b>RQ3 (ML vs. Deep Learning Parity):</b> On 1-step hourly PM2.5 forecasting, how do four PyTorch sequence architectures (LSTM, GRU, Dilated Causal TCN, Encoder-only Transformer) compare against six tabular ML models (Linear Regression, Ridge, Random Forest, Extra Trees, HistGradientBoosting, XGBoost)?", qstyles["Bullet"]))
    el.append(Paragraph("• <b>RQ4 (Non-Stationary Extrapolation Under Smog Spikes):</b> Why do regularized linear autoregressive models outperform bounded decision-tree ensembles when live Delhi R K Puram concentrations surge to unseen November peaks (501.00 ug/m3)?", qstyles["Bullet"]))
    el.append(Paragraph("• <b>RQ5 (Game-Theoretic Explainability & Horizon Decay):</b> Do TreeSHAP and LinearSHAP attributions align with atmospheric boundary-layer physics, and how rapidly does univariate forecast skill decay from horizon h = 1 to h = 24 hours?", qstyles["Bullet"]))

    el.append(sec("1.5 Project Objectives and Team Engineering Ownership", qstyles))
    el.append(Paragraph(
        "To resolve RQ1–RQ5, the four-member CSE-DS project team divided the AeroSense AI architecture into four cohesive engineering "
        "workstreams under the supervision of Mr. Abhishek Kumar (QU0125261068), as documented in Table 1.3.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "1.3", "B.Tech CSE-DS Project Team Roster, Roll Numbers, and Modular Engineering Ownership",
        [
            ["Student Name", "Student ID", "University Roll No.", "Batch / Sem / Branch", "Owned Subsystems & Core Deliverables"],
            ["Aryan Saini", "23030173", "2301315012", "2023-2027 | Sem 7 | CSE-DS", "OpenAQ API v3 client, rate-limit backoff, ingestion, schema validation, IQR x3 cleaning, <=6h interpolation, Apache Parquet storage & Cloud bootstrap"],
            ["Ayaan Ali", "23030175", "2301315013", "2023-2027 | Sem 7 | CSE-DS", "Dual CPCB (2014) & US EPA (2018) AQI engines, partial-panel disclosure logic, 34 leakage-free cyclical/lag/rolling features, sliding-window tensors & 3 naive baselines"],
            ["Kawalpreet Kaur", "23030255", "2301315019", "2023-2027 | Sem 7 | CSE-DS", "6 scikit-learn/XGBoost ML pipelines, 4 PyTorch DL models (LSTM, GRU, Causal TCN, Transformer), chronological 70/15/15 trainer, early stopping & empirical benchmarking"],
            ["Mihir Kumar", "23030268", "2301315022", "2023-2027 | Sem 7 | CSE-DS", "Tree/Linear SHAP & permutation explainability, 10-page Streamlit UI, Plotly MapLibre spatial maps, Haversine distance engine, automated PDF/PPTX reporting & 46-test QA suite"],
        ],
        [2.5 * cm, 1.8 * cm, 2.2 * cm, 2.4 * cm, 6.0 * cm],
        qstyles, font_pt=8.3,
    )

    el.append(sec("1.6 Scope, Geographical Phasing Strategy, and Report Organization", qstyles))
    el.append(Paragraph(
        "AeroSense AI follows a disciplined two-phase geographical strategy. Phase 1 delivers deep calibration, regulatory compliance, "
        "and live sensor validation across India (ISO code IN, primary pollutant PM2.5, with multi-pollutant support for PM10, NO2, SO2, "
        "CO, and O3). Phase 2 scales globally without code modification by parameterizing station discovery across all 159 OpenAQ v3 "
        "countries. The remainder of this report is organized as follows: Chapter 2 surveys 25 peer-reviewed papers; Chapter 3 derives "
        "the complete mathematical formulations of data hygiene, AQI, 34 features, 14 models, and SHAP; Chapter 4 presents software/hardware "
        "design, DFDs, UML diagrams, and Parquet schemas; Chapter 5 documents production Python code templates and the 10-page Streamlit UI; "
        "Chapter 6 analyzes the 46 automated test cases, live Indian telemetry, and 14-model benchmarks; Chapter 7 summarizes conclusions "
        "and limitations; and Chapter 8 outlines Phase 2 extensions, followed by References and Appendices A–B.",
        qstyles["Body"],
    ))
    el.append(PageBreak())

    # =========================================================================
    # CHAPTER 2  LITERATURE SURVEY
    # =========================================================================
    chapter_block(el, 2, "LITERATURE SURVEY", qstyles)
    el.append(Paragraph(
        "A systematic review of twenty-five peer-reviewed journal articles, conference proceedings, and regulatory technical monographs "
        "spanning 1970 to 2024 was conducted to ground AeroSense AI in established atmospheric science, statistical learning theory, "
        "deep sequence modeling, and game-theoretic explainability.",
        qstyles["BodyNoIndent"],
    ))

    el.append(sec("2.1 Taxonomic Evolution of Air Quality Modeling Paradigms", qstyles))
    el.append(Paragraph(
        "Computational air pollution forecasting has evolved across four distinct generations. First-generation deterministic Chemical "
        "Transport Models (CTMs) such as WRF-Chem and CMAQ numerically solve coupled 3D advection-diffusion-reaction partial differential "
        "equations over Eulerian grids. While physically comprehensive, CTMs require supercomputing clusters and high-resolution emission "
        "inventories that lag rapidly changing urban traffic and biomass burning. Second-generation classical statistical models—most "
        "notably Box-Jenkins ARIMA, SARIMAX, and Vector Autoregression (Box et al., 2015)—exploit temporal autocorrelation efficiently "
        "on single-station series but assume linear stationarity and struggle with complex non-linear diurnal boundary-layer interactions.",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "Third-generation non-linear tabular machine learning ensembles—Random Forests (Breiman, 2001), Extra Trees (Geurts et al., 2006), "
        "Gradient Boosted Decision Trees (Friedman, 2001), XGBoost (Chen & Guestrin, 2016), and LightGBM (Ke et al., 2017)—achieve high "
        "accuracy on engineered lag and rolling features with sub-second CPU training. Fourth-generation deep sequence networks—LSTM "
        "(Hochreiter & Schmidhuber, 1997), GRU (Cho et al., 2014), Dilated Causal TCN (Bai et al., 2018), and self-attention Transformers "
        "(Vaswani et al., 2017; Zhou et al., 2021)—learn hierarchical representations directly from raw sliding-window tensors.",
        qstyles["Body"],
    ))

    el.append(sec("2.2 Thematic Critical Review of Twenty-Five Foundational and Contemporary Works", qstyles))
    el.append(subsec("2.2.1 Epidemiological Burden, Source Apportionment and Regulatory Indexing", qstyles))
    el.append(Paragraph(
        "Apte et al. (2018) quantified ambient PM2.5-attributable life-expectancy loss globally using non-linear integrated exposure-response "
        "curves, demonstrating that South Asian urban populations lose 1.5 to 3.0 years of life expectancy due to winter particulate peaks, "
        "and proving that marginal reductions even at high baseline concentrations (>100 ug/m3) yield substantial mortality benefits. "
        "Guttikunda and Gurjar (2012) modeled multi-season dispersion across Delhi NCR, establishing that winter morning (06:00–09:00 IST) "
        "and nocturnal (20:00–01:00 IST) PM2.5 peaks are driven by planetary boundary-layer compression rather than emission spikes alone. "
        "Pant et al. (2019) synthesized Indian receptor-modeling studies, motivating why AeroSense AI incorporates multi-scale rolling "
        "windows (3h, 6h, 12h, 24h) and seasonal harmonics. Regulatory frameworks by CPCB (2014), US EPA (2018), and WHO (2021) define "
        "the mathematical piecewise-linear sub-index equations and health thresholds codified in src/aqi/.",
        qstyles["Body"],
    ))

    el.append(subsec("2.2.2 Classical Autoregression, L2 Regularization and Decision Tree Ensembles", qstyles))
    el.append(Paragraph(
        "Box et al. (2015) formalized autoregressive integrated moving average processes, demonstrating that differencing (Delta y_t = y_t - y_{t-1}) "
        "and seasonal lags (y_{t-24}) stabilize non-stationary environmental series. Hoerl and Kennard (1970) introduced Ridge Regression "
        "(L2 penalty alpha ||w||_2^2) to resolve severe multicollinearity among correlated predictors—a crucial foundation for AeroSense AI, "
        "where lag_1, rolling_mean_3, and rolling_mean_6 exhibit correlation r > 0.92. Breiman (2001) proved that Random Forests reduce "
        "variance via bootstrap aggregation and random feature subspacing, while Geurts et al. (2006) showed that Extremely Randomized "
        "Trees (Extra Trees) further reduce variance by randomizing split thresholds. Friedman (2001), Chen and Guestrin (2016), and "
        "Ke et al. (2017) developed second-order and histogram-binned gradient boosting (XGBoost and HistGradientBoosting), which we "
        "benchmark systematically across stationary and non-stationary PM2.5 regimes.",
        qstyles["Body"],
    ))

    el.append(subsec("2.2.3 Applied Machine Learning Studies on Indian Urban PM2.5", qstyles))
    el.append(Paragraph(
        "Masood and Ahmad (2021) evaluated SVM and ANN models on 2016–2018 Delhi CPCB data, confirming PM2.5 dominance while highlighting "
        "missing-data sensitivity. Sengupta et al. (2021) documented multi-city Indian spatial-temporal trends during 2019–2020, motivating "
        "our Haversine spatial hotspot module. Kumar and Pande (2023) benchmarked tree ensembles across Indian cities and identified black-box "
        "opacity as a primary barrier to regulatory adoption. Nair et al. (2023) applied XGBoost with SHAP to Indian monitoring stations, "
        "confirming 1-hour and 24-hour lags as dominant predictors, though without benchmarking against deep sequence Transformers or TCNs.",
        qstyles["Body"],
    ))

    el.append(subsec("2.2.4 Deep Sequence Networks: LSTM, GRU, Dilated Causal TCN and Transformers", qstyles))
    el.append(Paragraph(
        "Hochreiter and Schmidhuber (1997) solved vanishing recurrent gradients via multiplicative forget, input, and output gates in LSTM "
        "networks. Cho et al. (2014) simplified gated recurrence into the 2-gate GRU cell, reducing parameter count by 25%—an advantage on "
        "medium-sized environmental datasets (n ~ 2,000). Bai et al. (2018) proved that Dilated Causal Temporal Convolutional Networks (TCNs) "
        "with exponential dilation d = 2^l, residual connections, and weight normalization match or exceed recurrent networks while training "
        "in parallel. Vaswani et al. (2017) introduced multi-head scaled dot-product self-attention, eliminating sequential path length O(L) "
        "to O(1). Qi et al. (2019), Zhou et al. (2021), Liu et al. (2022), and Zhang et al. (2023) extended deep sequence and Transformer "
        "architectures to PM2.5 forecasting, motivating our unified PyTorch comparison.",
        qstyles["Body"],
    ))

    el.append(subsec("2.2.5 Chronological Validation Theory and Game-Theoretic Explainability", qstyles))
    el.append(Paragraph(
        "Bergmeir and Benitez (2012) and Hyndman and Athanasopoulos (2021) proved that randomized k-fold cross-validation on autocorrelated "
        "series induces severe optimistic bias via look-ahead leakage, mandating strict chronological train/validation/test partitioning and "
        "Seasonal Naive benchmarking. Finally, Lundberg and Lee (2017) unified local feature attribution under cooperative game-theoretic "
        "Shapley values (SHAP), providing the theoretical basis for our TreeSHAP and LinearSHAP diagnostic engine.",
        qstyles["Body"],
    ))

    el.append(sec("2.3 Comprehensive Twenty-Five Paper Literature Synthesis Matrix", qstyles))
    add_table_block(
        el, "2.1", "Exhaustive Synthesis Matrix of Twenty-Five Peer-Reviewed References Anchoring AeroSense AI",
        [
            ["#", "Author(s) & Year", "Core Method / Focus", "Primary Finding & Contribution", "Identified Limitation / Gap Addressed"],
            ["1", "Apte et al. (2018)", "Global PM2.5 Life-Table", "South Asia loses 1.5–3.0 yrs life expectancy from PM2.5", "Macro-epidemiology; no real-time forecasting UI"],
            ["2", "Bai et al. (2018)", "Dilated Causal TCN", "Exponential dilation d=2^l beats RNNs with parallelism", "Requires strict Chomp1d causal slicing on hourly lags"],
            ["3", "Bergmeir & Benitez (2012)", "Time-Series CV Theory", "Random k-fold CV leaks future autocorrelation", "Frequently violated in applied air quality notebooks"],
            ["4", "Box et al. (2015)", "ARIMA / SARIMAX", "Differencing & seasonal lag-24 stabilize trends", "Linear stationarity assumption fails on complex features"],
            ["5", "Breiman (2001)", "Random Forests", "Bagging + feature subspacing reduces variance", "Tree leaves bounded by [min(y_train), max(y_train)]"],
            ["6", "Chen & Guestrin (2016)", "XGBoost GBDT", "2nd-order Taylor loss + L1/L2 tree regularization", "Under-predicts unseen non-stationary smog spikes"],
            ["7", "Cho et al. (2014)", "GRU Recurrent Cell", "2-gate recurrence cuts parameters by 25% vs LSTM", "Sequential step unrolling limits GPU parallelism"],
            ["8", "CPCB India (2014)", "National AQI Standard", "6-category piecewise breakpoints; >=3 pollutant rule", "Public portals rarely flag single-sensor partial AQI"],
            ["9", "Friedman (2001)", "Gradient Boosting", "Stagewise additive trees on pseudo-residuals", "Prone to overfitting without shrinkage & early stop"],
            ["10", "Geurts et al. (2006)", "Extra Trees", "Randomized cut-points reduce variance further", "Same convex-hull extrapolation bound as Random Forest"],
            ["11", "Guttikunda & Gurjar (2012)", "Delhi Dispersion Audit", "Winter PBL compression drives 2x–3x PM2.5 surges", "Offline emissions inventory; no live API pipeline"],
            ["12", "Hochreiter & Schmidhuber (1997)", "LSTM Architecture", "Constant error carousel preserves long-term state", "Higher parameter overhead on ~2,000-row datasets"],
            ["13", "Hoerl & Kennard (1970)", "Ridge Regression (L2)", "Stabilizes multicollinear autoregressive lag matrices", "Requires standardized pipelines & cyclical features"],
            ["14", "Hyndman & Athanasopoulos (2021)", "Forecasting Principles", "Seasonal Naive & MASE/MAE benchmark standards", "Many ML papers omit naive baseline comparisons"],
            ["15", "Ke et al. (2017)", "LightGBM / HistGBDT", "256-bin histogram quantization speeds GBDT 10x", "Piecewise-constant leaf outputs clip extreme peaks"],
            ["16", "Kumar & Pande (2023)", "Indian City ML Survey", "Ensembles excel on stationary Indian CPCB datasets", "Lack of SHAP transparency & live v3 API ingestion"],
            ["17", "Liu et al. (2022)", "Attention-TCN PM2.5", "Receptive field >=24h critical for diurnal cycles", "Evaluated offline without regulatory AQI integration"],
            ["18", "Lundberg & Lee (2017)", "SHAP Attribution", "Unique additive game-theoretic local explanations", "Needs pipeline unwrap for scaled linear/tree models"],
            ["19", "Masood & Ahmad (2021)", "Delhi SVM & ANN", "Confirmed PM2.5 dominance across Delhi stations", "Sensitive to uncleaned sensor spikes & long gaps"],
            ["20", "Nair et al. (2023)", "XGBoost + SHAP India", "lag_1 and lag_24 dominate urban PM2.5 variance", "Did not compare against Transformers or Causal TCNs"],
            ["21", "Pant et al. (2019)", "India PM2.5 Review", "Synthesized IGP winter inversion & biomass drivers", "Called for open reproducible Indian analytics tools"],
            ["22", "Qi et al. (2019)", "Hybrid Deep PM2.5", "Spatial-temporal features boost 1–12h accuracy", "High compute cost; lacks lightweight local storage"],
            ["23", "US EPA (2018)", "US EPA AQI Technical", "Tighter PM2.5 breakpoints (Good <=12 ug/m3)", "Diverges from Indian CPCB categories on moderate air"],
            ["24", "Vaswani et al. (2017)", "Transformer Attention", "O(1) path length multi-head self-attention", "Requires positional encoding & dropout on short series"],
            ["25", "WHO (2021) & Zhang (2023)", "WHO Guidelines & Trans.", "24h PM2.5 limit 15 ug/m3; attention captures haze", "Integrated end-to-end in AeroSense AI health engine"],
        ],
        [0.7 * cm, 3.0 * cm, 2.6 * cm, 4.3 * cm, 4.3 * cm],
        qstyles, font_pt=7.8,
    )

    el.append(sec("2.4 Comparative Gap Analysis and Architectural Positioning", qstyles))
    add_table_block(
        el, "2.2", "Methodological Capability Comparison Between Prior Works and AeroSense AI",
        [
            ["Capability / Methodological Dimension", "Typical Academic Notebooks", "Public AQI Dashboards", "AeroSense AI (This Project)"],
            ["Live OpenAQ API v3 Authenticated Ingestion", "Rare (mostly static CSVs)", "Yes (backend hidden)", "Yes (X-API-Key, backoff, sensor hours)"],
            ["Bounded Imputation (<= 6h) & Provenance Mask", "No (blind full-series fill)", "Undisclosed", "Yes (IQR x3 + <=6h linear + is_imputed)"],
            ["Dual CPCB (India) & US EPA + Partial Flag", "Single standard or none", "Single standard, silent partial", "Dual standard + explicit is_complete flag"],
            ["Strict Chronological 70/15/15 Split & Shifted Rolls", "Often random k-fold (leaky)", "Not applicable", "Strict chronological + target.shift(1)"],
            ["Unified 14-Model ML + PyTorch DL + Baselines", "1–3 models only", "None or proprietary", "3 Baselines + 6 ML + 4 PyTorch DL models"],
            ["Non-Stationary Smog Extrapolation Audit", "Unexamined", "Not available", "Proven on live Delhi 501 ug/m3 peak"],
            ["Game-Theoretic SHAP + 46 Automated Tests", "Rare", "No", "TreeSHAP, LinearSHAP, Permutation + 46 tests"],
        ],
        [4.2 * cm, 3.3 * cm, 3.2 * cm, 4.2 * cm],
        qstyles, font_pt=8.3,
    )
    el.append(PageBreak())

    # =========================================================================
    # CHAPTER 3  METHODOLOGY AND MATHEMATICAL FORMULATION
    # =========================================================================
    chapter_block(el, 3, "METHODOLOGY AND MATHEMATICAL FORMULATION", qstyles)
    el.append(Paragraph(
        "AeroSense AI implements a deterministic seven-stage data science and deep learning methodology: (1) authenticated OpenAQ API v3 "
        "extraction; (2) physical bounds validation, Tukey IQR outlier rejection, and bounded <= 6-hour temporal interpolation; "
        "(3) dual-standard CPCB and US EPA piecewise-linear AQI computation; (4) leakage-free 34-feature synthesis and 3D tensor "
        "windowing; (5) chronological 70/15/15 model training across 14 architectures; (6) game-theoretic SHAP attribution; and "
        "(7) automated publication reporting. Table 3.1 specifies the verified software and hardware stack.",
        qstyles["BodyNoIndent"],
    ))
    add_table_block(
        el, "3.1", "Verified Software Stack, Library Versions, and Compute Governance",
        [
            ["Subsystem Layer", "Packages & Verified Versions", "Architectural Purpose in AeroSense AI"],
            ["Core Runtime", "Python 3.12–3.14 (Verified on 3.14.4)", "Type-annotated execution across Windows local & Linux Cloud"],
            ["HTTP & Config", "httpx >= 0.27.0, python-dotenv >= 1.0.0", "Synchronous TLS 1.3 OpenAQ v3 client, .env & st.secrets sync"],
            ["Data & Storage", "pandas >= 2.1.0, numpy >= 1.26.0, pyarrow >= 14.0", "Vectorized time-series transforms & Snappy Parquet I/O"],
            ["Tabular ML", "scikit-learn >= 1.4.0, xgboost >= 2.0.0, joblib", "StandardScaler pipelines, 6 regressors, .pkl serialization"],
            ["Deep Learning", "torch >= 2.2.0 (PyTorch CPU / CUDA)", "LSTM, GRU, Dilated Causal TCN, Encoder-only Transformer"],
            ["Explainability", "shap >= 0.45.0, scipy >= 1.12.0, statsmodels", "TreeExplainer, LinearExplainer, permutation & residual stats"],
            ["UI & Maps", "streamlit >= 1.35.0, plotly >= 5.20 (MapLibre 6.9)", "10-page dark-themed studio & carto-darkmatter scatter_map"],
            ["Reporting & QA", "reportlab >= 4.0, python-pptx, matplotlib, pytest", "300-DPI charts, QU-format PDF, 16-slide PPTX & 46 unit/UI tests"],
        ],
        [3.1 * cm, 4.8 * cm, 7.0 * cm],
        qstyles, font_pt=8.4,
    )

    el.append(sec("3.1 Authenticated OpenAQ API v3 Ingestion and Rate-Limit Governance", qstyles))
    el.append(Paragraph(
        "Unlike retired OpenAQ v1/v2 endpoints that allowed unauthenticated flat queries, OpenAQ API v3 enforces a hierarchical resource "
        "topology (Countries -> Locations -> Sensors -> Hours) protected by an HTTP X-API-Key header. AeroSense AI implements a two-phase "
        "discovery and extraction protocol in src/api/openaq_client.py and src/data/ingestion.py. In Phase A (Station Discovery), the client "
        "queries GET https://api.openaq.org/v3/locations with query parameters iso={COUNTRY_ISO}, parameters_id={PARAM_ID} (where PM2.5 maps "
        "to parameter ID 2), and limit=200. For each returned monitoring location, the parser extracts geographic coordinates (latitude, "
        "longitude), station metadata, and builds a JSON sensors_map mapping each normalized pollutant code to its unique integer sensor_id.",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "In Phase B (Hourly Sensor Stream Extraction), the client queries GET https://api.openaq.org/v3/sensors/{sensor_id}/hours with "
        "datetime_from, datetime_to, limit=1000, and page=p (up to OPENAQ_MAX_PAGES = 20). Because v3 hourly payloads nest timestamps inside "
        "period.datetimeTo.utc (or period.datetimeFrom.utc), our parser extracts the exact interval-ending UTC timestamp alongside the "
        "floating-point concentration. Transient rate limits (HTTP 429) and server faults (HTTP 500/502/503/504) are handled via deterministic "
        "exponential backoff:",
        qstyles["Body"],
    ))
    el.append(Paragraph("t_sleep(k) = t_0 * (b ^ (k - 1)),    where t_0 = 1.5 s,  b = 1.5,  k in {1, 2, 3}", qstyles["Formula"]))
    add_table_block(
        el, "3.2", "OpenAQ API v3 HTTP Status Code Governance and Exception Handling Matrix",
        [
            ["HTTP Status / Fault", "Client Exception Raised", "Retry Policy", "Diagnostic Action & User Feedback"],
            ["200 OK", "None (Valid JSON)", "0 retries", "Update _last_success UTC timestamp; parse results array"],
            ["401 Unauthorized", "OpenAQAuthError", "Immediate abort", "Invalid or missing X-API-Key; prompt System Diagnostics key setup"],
            ["403 Forbidden", "OpenAQAuthError", "Immediate abort", "Key lacks resource scope; log masked key prefix/suffix"],
            ["404 Not Found", "OpenAQNotFoundError", "Immediate abort", "Station or sensor ID retired; skip station cleanly in loop"],
            ["429 Too Many Requests", "OpenAQRateLimitError", "Up to 3 backoff retries", "Sleep 3.0s * k; raise controlled warning if quota exhausted"],
            ["500 / 502 / 503 / 504", "OpenAQServerError", "Up to 3 backoff retries", "Sleep 1.5 * 1.5^(k-1) s; fall back to cached/stored Parquet"],
            ["Timeout / DNS Error", "OpenAQConnectionError", "Up to 3 backoff retries", "30s socket timeout guard; preserve offline studio operation"],
        ],
        [3.1 * cm, 3.3 * cm, 2.8 * cm, 5.7 * cm],
        qstyles, font_pt=8.3,
    )

    el.append(sec("3.2 Deterministic Schema Validation, Tukey IQR Filtering and Bounded Imputation", qstyles))
    el.append(Paragraph(
        "Raw environmental sensor feeds frequently contain negative drift voltages, zero-calibration spikes, duplicate transmission "
        "packets, and power-outage gaps. AeroSense AI separates validation (src/data/validation.py) from cleaning (src/data/cleaning.py) "
        "and never overwrites raw Parquet snapshots stored in data/raw/. First, unit normalization converts parts-per-million (ppm) or "
        "parts-per-billion (ppb) gaseous readings into standard mass concentration (ug/m3 or mg/m3 for CO) at 25 C and 1 atm using "
        "molecular weight factors M_w / 24.45. Second, physical domain bounds (Table 3.3) reject impossible sensor glitches.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "3.3", "Criteria Pollutant Physical Validation Bounds, Standard Units, and Averaging Windows",
        [
            ["Pollutant Code", "Chemical Species", "OpenAQ Parameter ID", "Canonical Unit", "Valid Physical Range", "Regulatory Averaging Window"],
            ["pm25", "Fine Particulate Matter (<=2.5 um)", "2", "ug/m3", "[0.0, 2000.0]", "24-Hour Rolling / Daily Mean"],
            ["pm10", "Coarse Particulate Matter (<=10 um)", "1", "ug/m3", "[0.0, 5000.0]", "24-Hour Rolling / Daily Mean"],
            ["no2", "Nitrogen Dioxide", "5", "ug/m3", "[0.0, 2000.0]", "24-Hour (CPCB) / 1-Hour (EPA)"],
            ["so2", "Sulfur Dioxide", "6", "ug/m3", "[0.0, 2000.0]", "24-Hour (CPCB) / 1-Hour (EPA)"],
            ["co", "Carbon Monoxide", "4", "mg/m3 (or ug/m3)", "[0.0, 100.0] mg/m3", "8-Hour Rolling Mean"],
            ["o3", "Ground-Level Ozone", "3", "ug/m3", "[0.0, 1000.0]", "8-Hour Rolling Mean"],
        ],
        [2.0 * cm, 3.8 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.5 * cm],
        qstyles, font_pt=8.2,
    )
    el.append(Paragraph(
        "Third, records are sorted chronologically and deduplicated on the composite primary key (location_id, parameter, datetime_utc). "
        "Fourth, per-station statistical anomaly screening computes the 25th percentile (Q1), 75th percentile (Q3), and interquartile range "
        "IQR = Q3 - Q1. Unlike standard 1.5 * IQR fences that mistakenly clip legitimate winter smog episodes, AeroSense AI uses an "
        "extreme outer Tukey multiplier of k = 3.0, retaining real severe pollution while rejecting isolated electronic surges:",
        qstyles["Body"],
    ))
    el.append(Paragraph("Valid Concentration Domain:   y_t in [ max(0, Q_1 - 3.0 * IQR),   Q_3 + 3.0 * IQR ]", qstyles["Formula"]))
    el.append(Paragraph(
        "Fifth, each station stream is reindexed onto a complete hourly UTC grid. Missing timestamps are imputed via piecewise linear "
        "interpolation strictly when the contiguous gap length Delta t <= 6 hours (limit=6). Every interpolated timestamp is tagged with "
        "is_imputed = True, whereas contiguous outages exceeding 6 hours remain NaN (and are subsequently dropped during supervised window "
        "construction) so the platform never fabricates diurnal pollution cycles.",
        qstyles["Body"],
    ))

    el.append(sec("3.3 Dual-Standard Regulatory AQI Mathematical Formulation (CPCB vs. US EPA)", qstyles))
    el.append(Paragraph(
        "To translate multi-pollutant physical concentrations into actionable public health indices, AeroSense AI implements both the "
        "Indian Central Pollution Control Board National AQI (CPCB, 2014) in src/aqi/cpcb.py and the United States EPA AQI (US EPA, 2018) "
        "in src/aqi/us_epa.py. For each monitored pollutant p with concentration C_p falling within breakpoint bracket [BP_lo, BP_hi] "
        "corresponding to index interval [I_lo, I_hi], the sub-index I_p is computed via piecewise linear interpolation:",
        qstyles["Body"],
    ))
    el.append(Paragraph("I_p = round( ((I_hi - I_lo) / (BP_hi - BP_lo)) * (C_p - BP_lo) + I_lo ),      AQI = max_{p in P} ( I_p )", qstyles["Formula"]))
    el.append(Paragraph(
        "Crucially, official CPCB rules require a minimum of three monitored pollutants (one of which must be PM2.5 or PM10) to issue "
        "a statutory AQI. AeroSense AI sets result.is_complete = (len(sub_indices) >= 3 and any(p in {'pm25','pm10'} for p in calculated)) "
        "and displays an explicit partial-panel warning banner whenever single-pollutant streams are evaluated. Tables 3.4 and 3.5 document "
        "the complete breakpoint matrices verified by our 12 automated test cases in tests/test_aqi.py.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "3.4", "Official Indian CPCB (2014) AQI Breakpoint Matrix and Health Impact Categories",
        [
            ["AQI Category (Index Range)", "PM2.5 24h (ug/m3)", "PM10 24h (ug/m3)", "NO2 24h (ug/m3)", "SO2 24h (ug/m3)", "CO 8h (mg/m3)", "O3 8h (ug/m3)"],
            ["Good (0 – 50)", "0 – 30", "0 – 50", "0 – 40", "0 – 40", "0.0 – 1.0", "0 – 50"],
            ["Satisfactory (51 – 100)", "31 – 60", "51 – 100", "41 – 80", "41 – 80", "1.1 – 2.0", "51 – 100"],
            ["Moderate (101 – 200)", "61 – 90", "101 – 250", "81 – 180", "81 – 380", "2.1 – 10.0", "101 – 168"],
            ["Poor (201 – 300)", "91 – 120", "251 – 350", "181 – 280", "381 – 800", "10.1 – 17.0", "169 – 208"],
            ["Very Poor (301 – 400)", "121 – 250", "351 – 430", "281 – 400", "801 – 1600", "17.1 – 34.0", "209 – 748"],
            ["Severe (401 – 500)", "251 – 500+", "431 – 600+", "401 – 550+", "1601 – 2100+", "34.1 – 50.0+", "749 – 1000+"],
        ],
        [3.3 * cm, 2.0 * cm, 2.0 * cm, 1.9 * cm, 2.0 * cm, 1.9 * cm, 1.8 * cm],
        qstyles, font_pt=8.2,
    )
    add_table_block(
        el, "3.5", "Official US EPA AQI Breakpoint Matrix and Severity Comparison Against Indian CPCB",
        [
            ["US EPA Category (Index Range)", "PM2.5 24h (ug/m3)", "PM10 24h (ug/m3)", "O3 8h (ppm)", "CO 8h (ppm)", "Key Divergence from Indian CPCB"],
            ["Good (0 – 50)", "0.0 – 12.0", "0 – 54", "0.000 – 0.054", "0.0 – 4.4", "EPA Good ceiling (12.0) is 2.5x stricter than CPCB (30)"],
            ["Moderate (51 – 100)", "12.1 – 35.4", "55 – 154", "0.055 – 0.070", "4.5 – 9.4", "60 ug/m3 is Satisfactory in CPCB but Unhealthy in EPA"],
            ["Unhealthy for Sensitive (101 – 150)", "35.5 – 55.4", "155 – 254", "0.071 – 0.085", "9.5 – 12.4", "Triggers pediatric/asthmatic advisory at 35.5 ug/m3"],
            ["Unhealthy (151 – 200)", "55.5 – 150.4", "255 – 354", "0.086 – 0.105", "12.5 – 15.4", "Spans CPCB Satisfactory through Very Poor range"],
            ["Very Unhealthy (201 – 300)", "150.5 – 250.4", "355 – 424", "0.106 – 0.200", "15.5 – 30.4", "Converges with CPCB Very Poor upper bound (250 ug/m3)"],
            ["Hazardous (301 – 500)", "250.5 – 500.4", "425 – 604", "0.201 – 0.604", "30.5 – 50.4", "Matches CPCB Severe threshold above 250.5 ug/m3"],
        ],
        [3.5 * cm, 2.1 * cm, 2.0 * cm, 1.9 * cm, 1.8 * cm, 3.6 * cm],
        qstyles, font_pt=8.1,
    )
    add_figure(
        el, fig_dir, "fig13_aqi_breakpoint_curves.png", "Fig. 3.1",
        "Piecewise-Linear Sub-Index Transfer Curves Comparing Indian CPCB (2014) and US EPA (2018) PM2.5 Breakpoint Schedules",
        qstyles, width_cm=14.4,
    )

    el.append(sec("3.4 Leakage-Free 34-Feature Engineering Mathematical Specification", qstyles))
    el.append(Paragraph(
        "To transform an hourly univariate series {(t, y_t)} into a rich tabular design matrix X in R^{N x 34} without temporal look-ahead "
        "leakage, src/features/feature_engineering.py constructs four orthogonal feature families:",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "1. <b>Calendar & Fourier Cyclical Harmonics (11 features):</b> Raw integer calendar fields (hour in [0,23], day_of_week in [0,6], "
        "day_of_month in [1,31], month in [1,12], is_weekend in {0,1}) exhibit artificial metric discontinuities at period boundaries "
        "(e.g., 23:00 is 1 hour from 00:00, yet |23 - 0| = 23). We project each periodic variable onto a 2D unit circle via orthogonal "
        "sine and cosine harmonics:",
        qstyles["Bullet"],
    ))
    el.append(Paragraph("hour_sin = sin(2*pi*h / 24),   hour_cos = cos(2*pi*h / 24),   dow_sin = sin(2*pi*d / 7),   month_sin = sin(2*pi*m / 12)", qstyles["Formula"]))
    el.append(Paragraph(
        "2. <b>Strictly Causal Autoregressive Lags (7 features):</b> Past concentrations y_{t-k} for k in {1, 2, 3, 6, 12, 24, 48} hours "
        "capture immediate persistence (k=1..3), half-day boundary-layer transitions (k=6, 12), and 24-hour/48-hour diurnal cycle memory.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "3. <b>Shifted Rolling Window Moments (12 features — Zero-Leakage Guarantee):</b> If a rolling mean over window w is computed naively "
        "on y_t, then r_t = (1/w)*(y_t + y_{t-1} + ... + y_{t-w+1}) contains the target y_t itself with weight 1/w, allowing a linear model "
        "to reconstruct y_t trivially! AeroSense AI computes all rolling moments exclusively on the shifted series s_t = y_{t-1} = target.shift(1):",
        qstyles["Bullet"],
    ))
    el.append(Paragraph("mu_{t,w} = (1/w) * sum_{j=1}^{w} y_{t-j},      sigma_{t,w} = sqrt( (1/(w-1)) * sum_{j=1}^{w} (y_{t-j} - mu_{t,w})^2 ),      w in {3, 6, 12, 24}", qstyles["Formula"]))
    el.append(Paragraph(
        "4. <b>First-Order & Diurnal Momentum Differentials (4 features):</b> Rate-of-change predictors capture whether the atmospheric "
        "column is actively accumulating or flushing aerosols prior to timestamp t: diff_1 = y_{t-1} - y_{t-2}, trend_24 = y_{t-1} - y_{t-25}, "
        "pct_change_1 = (y_{t-1} - y_{t-2}) / (y_{t-2} + epsilon), and ratio_to_rolling_24 = y_{t-1} / (mu_{t,24} + epsilon). Table 3.6 "
        "catalogs all 34 features.",
        qstyles["Bullet"],
    ))
    add_table_block(
        el, "3.6", "Complete 34-Feature Engineering Catalog, Mathematical Formulas, and Atmospheric Roles",
        [
            ["Feature Group", "Feature Names (Count)", "Exact Mathematical Definition", "Physical & Predictive Role"],
            ["Raw Calendar", "hour, day_of_week, day_of_month, month, is_weekend (5)", "UTC timestamp calendar extraction; is_weekend = I(dow >= 5)", "Captures weekday commuter vs weekend emission drop"],
            ["Diurnal Harmonics", "hour_sin, hour_cos (2)", "sin(2*pi*hour/24), cos(2*pi*hour/24)", "Continuous encoding of PBL morning/evening cycle"],
            ["Weekly Harmonics", "dow_sin, dow_cos (2)", "sin(2*pi*dow/7), cos(2*pi*dow/7)", "Smooth weekly industrial activity periodicity"],
            ["Annual Harmonics", "month_sin, month_cos (2)", "sin(2*pi*month/12), cos(2*pi*month/12)", "Seasonal monsoon wash-out vs winter inversion phase"],
            ["Short Lags", "lag_1, lag_2, lag_3 (3)", "y_{t-1}, y_{t-2}, y_{t-3}", "Immediate atmospheric residence & inertia"],
            ["Medium/Diurnal Lags", "lag_6, lag_12, lag_24, lag_48 (4)", "y_{t-6}, y_{t-12}, y_{t-24}, y_{t-48}", "Half-day mixing transition & 1–2 day diurnal echo"],
            ["Rolling Means", "rolling_mean_3, _6, _12, _24 (4)", "(1/w) * sum_{j=1..w} y_{t-j}  (shifted onto y_{t-1})", "Smoothed local concentration baseline over window w"],
            ["Rolling Volatility", "rolling_std_3, _6, _12, _24 (4)", "std(y_{t-1}, ..., y_{t-w})", "Measures plume turbulence & onset of smog spikes"],
            ["Rolling Extrema", "rolling_min_3..24, rolling_max_3..24 (4)", "min_{j=1..w} y_{t-j}, max_{j=1..w} y_{t-j}", "Local floor (ventilation) & ceiling (peak accumulation)"],
            ["Momentum / Ratios", "diff_1, trend_24, pct_change_1, ratio_to_roll24 (4)", "y_{t-1}-y_{t-2}; y_{t-1}-y_{t-25}; y_{t-1}/mu_{t,24}", "Velocity of aerosol buildup / boundary-layer collapse"],
        ],
        [2.8 * cm, 3.8 * cm, 4.3 * cm, 4.0 * cm],
        qstyles, font_pt=8.0,
    )

    el.append(sec("3.5 Mathematical Formulations of All Fourteen Forecasting Architectures", qstyles))
    el.append(Paragraph(
        "All models are trained and evaluated under a strict chronological split: the earliest 70% of ordered timestamps form D_train, "
        "the middle 15% form D_val (used for early stopping and hyperparameter verification), and the final 15% form the unseen held-out "
        "test set D_test. No shuffling is ever permitted.",
        qstyles["Body"],
    ))
    el.append(subsec("3.5.1 Naive Baselines and Regularized Linear Models (5 Models)", qstyles))
    el.append(Paragraph(
        "Three parameter-free baselines establish lower bounds on acceptable skill: (1) Persistence predicts yhat_t = y_{t-1}; "
        "(2) Seasonal Naive (24h) predicts yhat_t = y_{t-24}; and (3) Rolling Mean (24h) predicts yhat_t = (1/24)*sum_{j=1}^{24} y_{t-j}. "
        "Ordinary Least Squares (LinearRegression) and L2-Penalized Ridge Regression wrap a StandardScaler (z = (x - mu_train)/sigma_train) "
        "inside a scikit-learn Pipeline and minimize the Tikhonov objective:",
        qstyles["Body"],
    ))
    el.append(Paragraph("J_Ridge(w, b) = sum_{i=1}^{N_train} (y_i - (w^T z_i + b))^2 + alpha * ||w||_2^2,      w* = (Z^T Z + alpha * I)^{-1} Z^T y", qstyles["Formula"]))
    el.append(Paragraph(
        "Because yhat = w^T z + b is an unbounded affine hyperplane, Linear and Ridge models possess a critical physical property: when "
        "y_{t-1} and diff_1 surge above the highest concentration observed in D_train, the linear predictor extrapolates proportionally "
        "along the learned autoregressive slope w_{lag_1} > 0.",
        qstyles["Body"],
    ))

    el.append(subsec("3.5.2 Bagging and Gradient Boosted Decision Tree Ensembles (4 Models)", qstyles))
    el.append(Paragraph(
        "Random Forest (B = 100 trees) and Extra Trees (B = 100 trees) average predictions across bootstrap-aggregated regression trees "
        "T_b(x). Crucially, every leaf node R_{b,m} in a regression tree outputs the arithmetic mean of training targets falling into that "
        "region. Consequently, for any arbitrary test vector x_test, a tree ensemble is mathematically constrained by the convex hull of "
        "training targets:",
        qstyles["Body"],
    ))
    el.append(Paragraph("yhat_Tree(x_test) = (1/B) * sum_{b=1}^{B} T_b(x_test)  in  [ min(y_train),  max(y_train) ]", qstyles["Formula"]))
    el.append(Paragraph(
        "Histogram Gradient Boosting (HistGradientBoostingRegressor) and XGBoost (XGBRegressor) construct stagewise additive ensembles "
        "yhat_i^{(M)} = sum_{m=1}^{M} eta * f_m(x_i) by minimizing a second-order Taylor expansion of the squared-error loss with leaf-weight "
        "L2 penalty lambda and tree-complexity penalty gamma:",
        qstyles["Body"],
    ))
    el.append(Paragraph("L^{(m)} = sum_{i=1}^{N} [ g_i * f_m(x_i) + (1/2) * h_i * f_m(x_i)^2 ] + gamma * T + (1/2) * lambda * sum_{j=1}^{T} w_j^2", qstyles["Formula"]))

    el.append(subsec("3.5.3 PyTorch Deep Sequence Architectures: LSTM, GRU, Causal TCN and Transformer (4 Models)", qstyles))
    el.append(Paragraph(
        "For deep sequence modeling (src/dl/models.py and src/dl/trainer.py), the training series is z-score normalized using strictly "
        "training-split statistics (mu_train, sigma_train) and segmented into 3D sliding-window tensors X_seq in R^{N x L x 1} (lookback "
        "L = 24 hours) predicting target vector Y_seq in R^{N x H} (horizon H = 1 or H = 24 hours). All four PyTorch architectures are "
        "trained with AdamW (lr = 10^{-3}, weight_decay = 10^{-4}), Huber/MSE loss, gradient norm clipping (max_norm = 1.0), "
        "ReduceLROnPlateau, and validation early stopping (patience = 10 epochs):",
        qstyles["Body"],
    ))
    el.append(Paragraph(
        "• <b>LSTMForecaster (2-layer stacked LSTM, hidden_size = 64):</b> Maintains separate cell state c_t and hidden state h_t governed by "
        "forget gate f_t = sigma(W_f [h_{t-1}, x_t] + b_f), input gate i_t = sigma(W_i [h_{t-1}, x_t] + b_i), candidate c~_t = tanh(W_c [h_{t-1}, x_t] + b_c), "
        "and update c_t = f_t * c_{t-1} + i_t * c~_t, projecting final step h_L through a Linear(64 -> H) head.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "• <b>GRUForecaster (2-layer stacked GRU, hidden_size = 64):</b> Couples forget and input gates into a single update gate "
        "z_t = sigma(W_z [h_{t-1}, x_t]) and reset gate r_t = sigma(W_r [h_{t-1}, x_t]), updating h_t = (1 - z_t) * h_{t-1} + z_t * h~_t "
        "with 25% fewer parameters than LSTM.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "• <b>TCNForecaster (3-block Dilated Causal Temporal Convolutional Network):</b> Applies 1D causal convolutions with kernel size "
        "K = 3 and exponential dilation factors d_l in {1, 2, 4}. Left-padding of (K - 1)*d_l followed by a Chomp1d module slices off "
        "future right-side padding so output at time t depends strictly on x_{<=t}. Across L_blocks = 3 residual blocks (2 conv layers each), "
        "the receptive field is R = 1 + sum_{l=0}^{2} 2*(3 - 1)*2^l = 1 + 4*(1 + 2 + 4) = 29 hours > 24-hour lookback.",
        qstyles["Bullet"],
    ))
    el.append(Paragraph(
        "• <b>TransformerForecaster (2-layer Encoder-only Transformer, d_model = 64, nhead = 4):</b> Projects scalar inputs via Linear(1 -> 64), "
        "adds deterministic sinusoidal positional encodings PE_{(pos, 2i)} = sin(pos / 10000^{2i/d_model}), applies 4-head scaled dot-product "
        "self-attention Attention(Q,K,V) = softmax(Q K^T / sqrt(d_k)) V with pre-norm residual layers, and maps the terminal token to R^H.",
        qstyles["Bullet"],
    ))
    add_table_block(
        el, "3.7", "Complete Architecture, Hyperparameter, and Regularization Specification Across All 14 Models",
        [
            ["Model Name", "Family", "Input Representation", "Core Hyperparameters & Regularization", "Extrapolation Capability"],
            ["Persistence", "Naive Baseline", "Scalar y_{t-1}", "Parameter-free identity lag_1", "Bounded to last observed value"],
            ["Seasonal Naive (24h)", "Naive Baseline", "Scalar y_{t-24}", "Parameter-free 24h diurnal cycle echo", "Bounded to previous day profile"],
            ["Rolling Mean (24h)", "Naive Baseline", "Window y_{t-24..t-1}", "Unweighted 24-hour moving average", "Lags rapid inflection points"],
            ["LinearRegression", "Tabular ML", "34 Features (Scaled)", "StandardScaler + exact OLS normal equation", "Unbounded linear slope extrapolation"],
            ["Ridge", "Tabular ML", "34 Features (Scaled)", "StandardScaler + L2 penalty alpha = 1.0", "Unbounded L2-damped extrapolation"],
            ["RandomForest", "Tabular ML", "34 Features", "n_estimators=100, max_depth=None, random_state=42", "Convex hull bounded [min, max]"],
            ["ExtraTrees", "Tabular ML", "34 Features", "n_estimators=100, randomized cut-points, seed=42", "Convex hull bounded [min, max]"],
            ["HistGradientBoosting", "Tabular ML", "34 Features", "max_iter=200, lr=0.05, max_bins=255, L2=1.0", "Piecewise-constant leaf bounded"],
            ["XGBoost", "Tabular ML", "34 Features", "n_estimators=200, lr=0.05, max_depth=6, subsample=0.8", "Piecewise-constant leaf bounded"],
            ["LSTMForecaster", "PyTorch DL", "Tensor (N, 24, 1)", "2 layers, hidden=64, dropout=0.2, AdamW lr=1e-3", "Tanh/linear readout semi-bounded"],
            ["GRUForecaster", "PyTorch DL", "Tensor (N, 24, 1)", "2 layers, hidden=64, dropout=0.2, grad_clip=1.0", "Sigmoid/tanh gated readout"],
            ["TCNForecaster", "PyTorch DL", "Tensor (N, 24, 1)", "Channels [64,64,64], k=3, dilations [1,2,4], Chomp1d", "ReLU + linear head extrapolation"],
            ["TransformerForecaster", "PyTorch DL", "Tensor (N, 24, 1)", "d_model=64, nhead=4, layers=2, FFN=128, dropout=0.1", "Attention + linear projection"],
        ],
        [3.1 * cm, 2.2 * cm, 2.7 * cm, 4.1 * cm, 2.8 * cm],
        qstyles, font_pt=7.9,
    )

    el.append(sec("3.6 Game-Theoretic Explainable AI (SHAP) and Evaluation Metrics", qstyles))
    el.append(Paragraph(
        "To audit model decisions, src/explainability/feature_importance.py computes exact Shapley Additive exPlanations (Lundberg & Lee, 2017). "
        "For feature j among F predictors, the Shapley attribution phi_j(f, x) averages the marginal contribution of feature j across all "
        "coalitions S subseteq F \\ {j}:",
        qstyles["Body"],
    ))
    el.append(Paragraph("phi_j(f, x) = sum_{S subseteq F \\ {j}} ( |S|! * (|F| - |S| - 1)! / |F|! ) * [ f_{S union {j}}(x_{S union {j}}) - f_S(x_S) ]", qstyles["Formula"]))
    el.append(Paragraph(
        "Our implementation automatically unwraps scikit-learn Pipelines (applying StandardScaler.transform(X_sample) prior to passing "
        "the estimator to shap.TreeExplainer for tree models or shap.LinearExplainer for linear models), and complements SHAP with "
        "5-repeat Permutation Importance on D_test.",
        qstyles["Body"],
    ))

    el.append(sec("3.7 Residual Diagnostics and Computational Complexity Analysis", qstyles))
    el.append(Paragraph(
        "Beyond scalar error aggregates (MAE, RMSE, R2), AeroSense AI audits model residuals e_t = y_t - yhat_t for systematic bias "
        "(mean residual mu_e = (1/N_test)*sum e_t), asymmetry (sample skewness gamma_1), tail heaviness (excess kurtosis gamma_2), and "
        "heteroscedasticity across concentration deciles. Table 3.8 summarizes the asymptotic time and space complexity of every stage "
        "in our seven-stage pipeline, proving that the entire tabular ML training and inference workflow executes in O(N * F) to "
        "O(B * F * N log N) time on standard multi-core CPU hardware without requiring dedicated GPU clusters.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "3.8", "Asymptotic Time and Space Complexity Across AeroSense AI Pipeline Stages",
        [
            ["Pipeline Stage / Algorithm", "Time Complexity (Training / Execution)", "Inference Complexity (Per Step)", "Memory Footprint"],
            ["OpenAQ v3 Paginated Ingestion", "O(P * M) across P pages of M=1000 rows", "O(1) cached Parquet read (<4 ms)", "O(N) DataFrame buffer"],
            ["Schema Validation & IQR x3 Clean", "O(N log N) chronological sort & group quantiles", "O(N) single-pass vector filter", "O(N) Arrow column arrays"],
            ["34-Feature Matrix Synthesis", "O(N * W) where max rolling window W = 24", "O(F) with F = 34 features", "O(34 * N) float64 matrix"],
            ["OLS / Ridge Regression (F=34)", "O(N * F^2 + F^3) normal matrix inversion", "O(F) inner product (<0.01 ms)", "O(F^2) covariance matrix"],
            ["RandomForest / ExtraTrees (B=100)", "O(B * F * N log N) recursive partitioning", "O(B * D_max) tree traversal", "O(B * N_leaves) pointers"],
            ["HistGradientBoosting / XGBoost", "O(M_trees * F * N_bins) with N_bins = 255", "O(M_trees * D_max) leaf lookup", "O(F * N_bins + M * 2^D)"],
            ["PyTorch LSTM / GRU (L=24, H_d=64)", "O(E * N * L * H_d^2) sequential BPTT", "O(L * H_d^2) recurrent unroll", "O(L * H_d) hidden states"],
            ["PyTorch Dilated Causal TCN (K=3)", "O(E * N * L * K * C^2) parallel 1D conv", "O(L * K * C^2) parallel conv", "O(B_batch * C * L) activations"],
            ["PyTorch Transformer (L=24, d=64)", "O(E * N * (L^2 * d + L * d^2)) attention", "O(L^2 * d + L * d^2) forward", "O(nhead * L^2) attention map"],
            ["TreeSHAP / LinearSHAP Attribution", "O(N_s * B * D_max^2) / O(N_s * F) exact", "O(B * D_max^2) per explanation", "O(N_s * F) Shapley matrix"],
        ],
        [3.8 * cm, 4.3 * cm, 3.8 * cm, 3.0 * cm],
        qstyles, font_pt=7.9,
    )
    el.append(PageBreak())

    # =========================================================================
    # CHAPTER 4  SOFTWARE AND HARDWARE DESIGN
    # =========================================================================
    chapter_block(el, 4, "SOFTWARE AND HARDWARE DESIGN", qstyles)
    el.append(Paragraph(
        "AeroSense AI is engineered as a six-layer modular software system separating configuration, external data acquisition, "
        "domain mathematics, machine/deep learning training, explainability/reporting, and interactive presentation. This clean "
        "decoupling ensures that every algorithmic component can be unit-tested headlessly via Pytest and scaled from India to "
        "international monitoring networks without UI code modification.",
        qstyles["BodyNoIndent"],
    ))

    el.append(sec("4.1 Six-Layer Modular Software Architecture and Repository Audit", qstyles))
    add_table_block(
        el, "4.1", "Complete Repository Module Inventory, Architectural Layer, and Functional Responsibilities",
        [
            ["Architectural Layer", "Repository File Path", "Key Classes / Functions", "Engineering Responsibility"],
            ["1. Config & Logging", "src/config/settings.py", "PROJECT_ROOT, api_key_configured, masked_api_key", "Centralized paths, constants, .env loader & secret masking"],
            ["1. Config & Logging", "src/utils/logging_config.py", "setup_logging, get_logger", "Idempotent rotating 5 MB file + color console logger"],
            ["2. API & Data Pipeline", "src/api/openaq_client.py", "OpenAQClient, OpenAQError hierarchy", "Authenticated v3 REST client, pagination, backoff retry"],
            ["2. API & Data Pipeline", "src/data/ingestion.py", "DataIngestion.fetch_locations / measurements", "Two-phase station discovery & sensor hours extraction"],
            ["2. API & Data Pipeline", "src/data/validation.py", "validate_measurements, ValidationReport", "Schema enforcement, numeric coercion & physical bounds"],
            ["2. API & Data Pipeline", "src/data/cleaning.py", "clean_measurements, normalise_units", "Composite deduplication, IQR x3 filter & <=6h interpolation"],
            ["2. API & Data Pipeline", "src/data/storage.py", "save_raw, save_processed, load_processed", "Immutable raw & processed Snappy Apache Parquet persistence"],
            ["2. API & Data Pipeline", "src/data/seed_benchmark.py", "generate_delhi_benchmark, seed_all_benchmarks", "Reference 90-day Delhi & Mumbai calibration benchmarks"],
            ["2. API & Data Pipeline", "src/data/bootstrap.py", "ensure_ready, sync_streamlit_secrets", "Self-healing Streamlit Cloud secret sync & auto-seeding"],
            ["3. Domain & Features", "src/aqi/cpcb.py & us_epa.py", "calculate_cpcb_aqi, calculate_epa_aqi", "Dual-standard piecewise linear AQI & is_complete flag"],
            ["3. Domain & Features", "src/features/feature_engineering.py", "build_feature_matrix, build_sequences", "34 leakage-free tabular features & 3D (N,24,1) DL tensors"],
            ["4. ML / DL Modeling", "src/ml/baselines.py & train.py", "evaluate_baselines, train_models, predict", "3 naive baselines + 6 ML pipelines with 70/15/15 split"],
            ["4. ML / DL Modeling", "src/dl/models.py & trainer.py", "LSTM/GRU/TCN/TransformerForecaster, train_dl_model", "4 PyTorch sequence models, AdamW, early stop & checkpointing"],
            ["5. XAI & Reporting", "src/explainability/feature_importance.py", "get_feature_importance, shap_values, residual_analysis", "Pipeline-aware Tree/Linear SHAP, permutation & error stats"],
            ["5. XAI & Reporting", "src/reporting/*.py", "build_detailed_project_report, build_synopsis", "Automated QU Report, IEEE Paper, Synopsis, PPTX & ZIP"],
            ["6. Presentation & QA", "app.py, pages/01..10, src/visualization/", "apply_theme, map_scatter, forecast_chart", "11-entrypoint Streamlit dark UI, MapLibre & 46 Pytest cases"],
        ],
        [2.7 * cm, 3.8 * cm, 3.8 * cm, 4.6 * cm],
        qstyles, font_pt=7.8,
    )

    el.append(sec("4.2 Data Flow Diagrams (Context Level-0 and Detailed Level-1 DFD)", qstyles))
    el.append(Paragraph(
        "At Context Level-0, external entities comprise the OpenAQ API v3 Cloud Server, the Environmental Researcher / End User, and "
        "the Local/Cloud File System. At Level-1 (Figure 4.1, Panel A), authenticated HTTPS JSON responses flow into Process 1.0 "
        "(Ingestion & Raw Preservation), writing immutable snapshots to D1 (data/raw/*.parquet). Process 2.0 (Validation & IQR/<=6h "
        "Cleaning) filters anomalies and writes clean analytical tables with is_imputed flags to D2 (data/processed/*.parquet). "
        "Process 3.0 (34-Feature & 3D Tensor Builder) and Process 4.0 (Dual CPCB/EPA AQI Engine) feed Process 5.0 (Chronological "
        "70/15/15 ML/DL Trainer), persisting model binaries to D3 (models/ml/*.pkl, models/dl/*.pt) and evaluation ledgers to D4 "
        "(experiments/results/*.csv), which drive Process 6.0 (SHAP Explainability & 10-Page Streamlit UI).",
        qstyles["Body"],
    ))

    el.append(sec("4.3 UML Class, Sequence, Control Flow and Use-Case Diagrams", qstyles))
    el.append(Paragraph(
        "Figure 4.1 illustrates the four formal software design views of AeroSense AI: (A) Level-1 Data Flow Diagram; (B) UML Class "
        "Diagram showing composition and inheritance across OpenAQClient, DataIngestion, AQICalculator, FeatureBuilder, MLTrainer, "
        "and PyTorch nn.Module subclasses; (C) End-to-End UML Sequence Diagram tracing synchronous method calls from user trigger to "
        "rendered Plotly chart; and (D) Runtime Control Flow & Use-Case Governance.",
        qstyles["Body"],
    ))
    add_figure(
        el, fig_dir, "fig6_uml_system_design.png", "Fig. 4.1",
        "AeroSense AI Level-1 DFD (A), UML Class Architecture (B), Execution Sequence Diagram (C) and Control Flow / Use-Case Design (D)",
        qstyles, width_cm=14.6,
    )
    add_figure(
        el, fig_dir, "fig07_pipeline_flow.png", "Fig. 4.2",
        "End-to-End Seven-Stage AeroSense AI Data Engineering, Feature Synthesis, Chronological Split, and Model Deployment Pipeline",
        qstyles, width_cm=14.5,
    )
    add_figure(
        el, fig_dir, "fig08_layer_architecture.png", "Fig. 4.3",
        "Six-Layer Modular Software Architecture Depicting Package Boundaries Across Config, Data, Domain, ML/DL, XAI, and Streamlit UI",
        qstyles, width_cm=14.5,
    )

    el.append(sec("4.4 Persistent Storage Architecture and Apache Parquet Schemas", qstyles))
    el.append(Paragraph(
        "Rather than requiring an external database daemon that complicates academic portability and Streamlit Community Cloud hosting, "
        "AeroSense AI adopts a local-first analytical lakehouse architecture backed by Snappy-compressed Apache Parquet files. Columnar "
        "Parquet storage preserves strict Arrow data types (UTC nanosecond timestamps, int64 IDs, float64 concentrations, boolean flags) "
        "and achieves 4x–6x compression over CSV while loading 2,161-row time series in under 4 milliseconds. Tables 4.2 and 4.3 define "
        "the exact schemas for processed datasets and serialized model checkpoints.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "4.2", "Processed Analytical Dataset Schema (data/processed/*.parquet)",
        [
            ["Field Name", "Apache Arrow / Pandas Dtype", "Nullability", "Provenance & Analytical Role"],
            ["datetime_utc", "datetime64[ns, UTC]", "NOT NULL", "Monotonic hourly UTC key governing 70/15/15 chronological split"],
            ["location_id", "int64", "NOT NULL", "Unique OpenAQ v3 monitoring station identifier (e.g., 17, 407, 2456)"],
            ["location_name", "string", "NOT NULL", "Human-readable CPCB/DPCC/TSPCB reference monitor name"],
            ["city / country", "string", "NOT NULL", "City label (with location_name fallback) and ISO-3166 alpha-2 code (IN)"],
            ["latitude / longitude", "float64", "NULLABLE", "WGS-84 decimal degrees driving MapLibre scatter_map & Haversine matrix"],
            ["sensor_id / parameter", "int64 / string", "NOT NULL", "OpenAQ v3 sensor primary key and pollutant code (pm25, pm10, etc.)"],
            ["unit / value", "string / float64", "NOT NULL", "Normalized mass unit (ug/m3) and validated concentration reading"],
            ["is_imputed", "bool", "NOT NULL", "False for raw sensor observation; True for <= 6h linear interpolation"],
            ["source_provider / api_endpoint", "string", "NOT NULL", "Audit trail ('OpenAQ API v3' vs 'AeroSense Reference Benchmark')"],
            ["retrieved_at", "string (ISO-8601 UTC)", "NOT NULL", "Exact extraction timestamp ensuring full data lineage"],
        ],
        [3.3 * cm, 3.2 * cm, 1.9 * cm, 6.5 * cm],
        qstyles, font_pt=8.1,
    )
    add_table_block(
        el, "4.3", "Serialized ML (.pkl) and PyTorch DL (.pt) Model Artifact Dictionary Schema",
        [
            ["Artifact Key", "Value Type", "Persisted Content & Runtime Role"],
            ["model / model_state", "sklearn Pipeline / OrderedDict", "Fitted StandardScaler+Estimator or PyTorch state_dict weights"],
            ["features / lookback, horizon", "list[str] / int, int", "Exact ordered 34 feature names or (L=24, H=1/24) tensor dimensions"],
            ["val_metrics / test_metrics", "dict[str, float]", "Chronological validation & held-out test {'MAE', 'RMSE', 'R2'} scores"],
            ["train_time_s / pred_time_s", "float", "Wall-clock training and inference latency in seconds"],
            ["n_features / train_rows", "int", "Dimensionality verification (34 features, 1,495 training instances)"],
            ["mean / std (DL only)", "float", "Training-split z-score normalization scalars preventing test leakage"],
        ],
        [3.8 * cm, 3.5 * cm, 7.6 * cm],
        qstyles, font_pt=8.2,
    )

    el.append(sec("4.5 Self-Healing Cloud Bootstrap and Geodesic Spatial Architecture", qstyles))
    el.append(Paragraph(
        "When deployed to ephemeral cloud containers (such as Streamlit Community Cloud), git-ignored binary directories (data/processed/, "
        "models/ml/) start empty and environment variables reside in st.secrets rather than .env. Our bootstrap module (src/data/bootstrap.py) "
        "executes ensure_ready() at the top of app.py and every page (pages/01..10): it synchronizes st.secrets['OPENAQ_API_KEY'] into "
        "os.environ and settings.OPENAQ_API_KEY, seeds reference Delhi and Mumbai benchmarks if data/processed/ is empty, and trains "
        "five baseline scikit-learn models in < 0.8 seconds if models/ml/*.pkl is absent, while preserving tracked experiment CSVs.",
        qstyles["Body"],
    ))

    el.append(sec("4.6 Security, Secret Isolation and Fault-Tolerant Threat Model", qstyles))
    el.append(Paragraph(
        "Because AeroSense AI interfaces with external authenticated REST endpoints and executes interactive model training in a web "
        "browser environment, defense-in-depth controls are enforced across credential storage, network resilience, input sanitization, "
        "and UI compatibility. Table 4.4 documents the system threat model and verified mitigations.",
        qstyles["Body"],
    ))
    add_table_block(
        el, "4.4", "System Threat Model, Failure Modes, and Verified Engineering Mitigations",
        [
            ["Risk / Failure Mode", "Attack Vector or Operational Trigger", "Engineering Mitigation in AeroSense AI", "Verification Test"],
            ["API Key Exposure in Git / UI", "Committing .env or printing raw key in UI", ".gitignore blocks .env; masked_api_key() hides middle chars; st.text_input(type='password')", "test_bootstrap.py & git status audit"],
            ["OpenAQ Rate Limit (HTTP 429)", "Burst station/sensor queries exceeding quota", "Exponential backoff (1.5s * 1.5^k, max 3 retries); graceful fallback to cached Parquet", "test_api_and_explainability.py"],
            ["Ephemeral Cloud Cold Start", "Streamlit Cloud boots with empty data/ & models/", "ensure_ready() syncs st.secrets, seeds Delhi/Mumbai Parquet & trains 5 baseline ML models", "test_bootstrap_seeds_empty_workspace"],
            ["Blank City Strings in OpenAQ v3", "OpenAQ v3 returns city='' on Indian stations", "Page 02 checks non-whitespace city strings and falls back cleanly to location_name", "AppTest IN_pm25_live_openaq check"],
            ["Plotly Mapbox Deprecation Crash", "Plotly >=5.24 scatter_map rejects mapbox_style", "map_scatter() passes map_style='carto-darkmatter' natively to px.scatter_map", "test_charts.py (2/2 PASS)"],
            ["Insufficient Sample Size (<50)", "User selects short 1-day series for ML/DL fit", "Pre-flight guard checks len(df) >= 50 (ML) and >= 100 (DL) with actionable error alert", "04_Forecasting_Studio.py guard"],
            ["Corrupted / Extreme Sensor Spike", "Hardware fault transmits -999 or 99,999 ug/m3", "Physical bounds filter [0, 2000] + Tukey IQR x 3 fence before feature synthesis", "test_validation.py (4/4 PASS)"],
        ],
        [3.2 * cm, 3.6 * cm, 5.2 * cm, 2.9 * cm],
        qstyles, font_pt=7.9,
    )
    el.append(PageBreak())
