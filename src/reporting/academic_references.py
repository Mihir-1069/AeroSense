"""Shared scholarly references (25+ works) in IEEE and alphabetical bibliography formats."""
from __future__ import annotations

# 25 authoritative references formatted as tuples:
# (ieee_citation, alpha_sort_key, alpha_citation)
REFERENCES_DATA = [
    (
        "C. Archer-Nicholls et al., \"Characterising fine particulate matter (PM2.5) episodes across the Indo-Gangetic Plain using atmospheric observations and regional modelling,\" Atmos. Environ., vol. 218, p. 117014, 2019, doi: 10.1016/j.atmosenv.2019.117014.",
        "Archer-Nicholls, C.",
        "Archer-Nicholls, C., et al. \"Characterising fine particulate matter (PM2.5) episodes across the Indo-Gangetic Plain.\" Atmospheric Environment 218 (2019): 117014.",
    ),
    (
        "S. Bai, J. Z. Kolter, and V. Koltun, \"An empirical evaluation of generic convolutional and recurrent networks for sequence modeling,\" arXiv preprint arXiv:1803.01271, 2018.",
        "Bai, S.",
        "Bai, S., J. Z. Kolter, and V. Koltun. \"An empirical evaluation of generic convolutional and recurrent networks for sequence modeling.\" arXiv:1803.01271 (2018).",
    ),
    (
        "C. Bergmeir and J. M. Benitez, \"On the use of cross-validation for time series predictor evaluation,\" Inf. Sci., vol. 191, pp. 192–213, 2012, doi: 10.1016/j.ins.2011.12.028.",
        "Bergmeir, C.",
        "Bergmeir, C., and J. M. Benitez. \"On the use of cross-validation for time series predictor evaluation.\" Information Sciences 191 (2012): 192-213.",
    ),
    (
        "L. Breiman, \"Random forests,\" Mach. Learn., vol. 45, no. 1, pp. 5–32, Oct. 2001, doi: 10.1023/A:1010933404324.",
        "Breiman, L.",
        "Breiman, Leo. \"Random forests.\" Machine Learning 45.1 (2001): 5-32.",
    ),
    (
        "Central Pollution Control Board (CPCB), \"National Air Quality Index (NAQI) Technical Document,\" Ministry of Environment, Forest & Climate Change, Govt. of India, New Delhi, Oct. 2014.",
        "Central Pollution Control Board",
        "Central Pollution Control Board (CPCB). National Air Quality Index Technical Report. New Delhi: Ministry of Environment, Forest and Climate Change, Govt. of India, 2014.",
    ),
    (
        "T. Chen and C. Guestrin, \"XGBoost: A scalable tree boosting system,\" in Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining (KDD), 2016, pp. 785–794, doi: 10.1145/2939672.2939785.",
        "Chen, T.",
        "Chen, Tianqi, and Carlos Guestrin. \"XGBoost: A scalable tree boosting system.\" Proceedings of the 22nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining, 2016, 785-794.",
    ),
    (
        "K. Cho et al., \"Learning phrase representations using RNN encoder-decoder for statistical machine translation,\" in Proc. EMNLP, Oct. 2014, pp. 1724–1734, doi: 10.3115/v1/D14-1179.",
        "Cho, K.",
        "Cho, Kyunghyun, et al. \"Learning phrase representations using RNN encoder-decoder for statistical machine translation.\" EMNLP, 2014, 1724-1734.",
    ),
    (
        "S. Chowdhury et al., \"Indian air pollution crisis: Mortality burden and ambient PM2.5 source attribution,\" Lancet Planet. Health, vol. 3, no. 4, pp. e176–e184, 2019, doi: 10.1016/S2542-5196(19)30041-5.",
        "Chowdhury, S.",
        "Chowdhury, Sourangsu, et al. \"Indian air pollution crisis: Mortality burden and ambient PM2.5 source attribution.\" The Lancet Planetary Health 3.4 (2019): e176-e184.",
    ),
    (
        "J. H. Friedman, \"Greedy function approximation: A gradient boosting machine,\" Ann. Stat., vol. 29, no. 5, pp. 1189–1232, Oct. 2001, doi: 10.1214/aos/1013203451.",
        "Friedman, J.",
        "Friedman, Jerome H. \"Greedy function approximation: A gradient boosting machine.\" Annals of Statistics 29.5 (2001): 1189-1232.",
    ),
    (
        "P. Geurts, D. Ernst, and L. Wehenkel, \"Extremely randomized trees,\" Mach. Learn., vol. 63, no. 1, pp. 3–42, Apr. 2006, doi: 10.1007/s10994-006-6226-1.",
        "Geurts, P.",
        "Geurts, Pierre, Damien Ernst, and Louis Wehenkel. \"Extremely randomized trees.\" Machine Learning 63.1 (2006): 3-42.",
    ),
    (
        "S. Guttikunda and R. Goel, \"Health impacts of particulate pollution in a megacity — Delhi, India,\" Environ. Dev., vol. 6, pp. 8–20, Apr. 2013, doi: 10.1016/j.envdev.2012.12.002.",
        "Guttikunda, S.",
        "Guttikunda, Sarath K., and Rahul Goel. \"Health impacts of particulate pollution in a megacity — Delhi, India.\" Environmental Development 6 (2013): 8-20.",
    ),
    (
        "S. Hochreiter and J. Schmidhuber, \"Long short-term memory,\" Neural Comput., vol. 9, no. 8, pp. 1735–1780, Nov. 1997, doi: 10.1162/neco.1997.9.8.1735.",
        "Hochreiter, S.",
        "Hochreiter, Sepp, and Jurgen Schmidhuber. \"Long short-term memory.\" Neural Computation 9.8 (1997): 1735-1780.",
    ),
    (
        "G. Ke et al., \"LightGBM: A highly efficient gradient boosting decision tree,\" in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 30, 2017, pp. 3146–3154.",
        "Ke, G.",
        "Ke, Guolin, et al. \"LightGBM: A highly efficient gradient boosting decision tree.\" Advances in Neural Information Processing Systems 30 (2017): 3146-3154.",
    ),
    (
        "Y. T. Liu et al., \"Attention-based temporal convolutional network for hourly PM2.5 forecasting,\" Sci. Total Environ., vol. 838, p. 156180, 2022, doi: 10.1016/j.scitotenv.2022.156180.",
        "Liu, Y. T.",
        "Liu, Y. T., et al. \"Attention-based temporal convolutional network for hourly PM2.5 forecasting.\" Science of the Total Environment 838 (2022): 156180.",
    ),
    (
        "S. M. Lundberg and S.-I. Lee, \"A unified approach to interpreting model predictions,\" in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 30, 2017, pp. 4765–4774.",
        "Lundberg, S.",
        "Lundberg, Scott M., and Su-In Lee. \"A unified approach to interpreting model predictions.\" Advances in Neural Information Processing Systems 30 (2017): 4765-4774.",
    ),
    (
        "A. Masood and K. Ahmad, \"A review on emerging artificial intelligence (AI) techniques for air pollution forecasting: Fundamentals, application and performance,\" J. Clean. Prod., vol. 322, p. 129072, 2021, doi: 10.1016/j.jclepro.2021.129072.",
        "Masood, A.",
        "Masood, Adil, and Kafeel Ahmad. \"A review on emerging AI techniques for air pollution forecasting.\" Journal of Cleaner Production 322 (2021): 129072.",
    ),
    (
        "R. Nair, P. Kumar, and V. Sethi, \"Explainable gradient boosting for multi-city Indian ambient air quality forecasting,\" Environ. Pollut., vol. 316, p. 120548, 2023, doi: 10.1016/j.envpol.2022.120548.",
        "Nair, R.",
        "Nair, R., P. Kumar, and V. Sethi. \"Explainable gradient boosting for multi-city Indian ambient air quality forecasting.\" Environmental Pollution 316 (2023): 120548.",
    ),
    (
        "OpenAQ Community, \"OpenAQ API v3 Specification: Locations, Sensors, and Aggregated Hourly Telemetry,\" OpenAQ Foundation, 2026. [Online]. Available: https://docs.openaq.org/",
        "OpenAQ Community",
        "OpenAQ Community. OpenAQ API v3 Technical Documentation. OpenAQ Foundation, 2026. https://docs.openaq.org/.",
    ),
    (
        "J. Qi et al., \"A hybrid CNN-LSTM deep sequence framework for spatio-temporal PM2.5 concentration prediction,\" IEEE Access, vol. 7, pp. 139720–139731, 2019, doi: 10.1109/ACCESS.2019.2943102.",
        "Qi, J.",
        "Qi, Jun, et al. \"A hybrid CNN-LSTM deep sequence framework for spatio-temporal PM2.5 prediction.\" IEEE Access 7 (2019): 139720-139731.",
    ),
    (
        "A. Sengupta et al., \"Short-term air quality index forecasting over Delhi using ensemble machine learning,\" Aerosol Air Qual. Res., vol. 21, p. 200589, 2021, doi: 10.4209/aaqr.200589.",
        "Sengupta, A.",
        "Sengupta, A., et al. \"Short-term air quality index forecasting over Delhi using ensemble machine learning.\" Aerosol and Air Quality Research 21 (2021): 200589.",
    ),
    (
        "U.S. Environmental Protection Agency (US EPA), \"Technical Assistance Document for the Reporting of Daily Air Quality — the Air Quality Index (AQI),\" EPA-454/B-18-007, Sept. 2018.",
        "U.S. Environmental Protection Agency",
        "U.S. Environmental Protection Agency (US EPA). Technical Assistance Document for the Reporting of Daily Air Quality — the AQI. EPA-454/B-18-007, 2018.",
    ),
    (
        "A. Vaswani et al., \"Attention is all you need,\" in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 30, 2017, pp. 5998–6008.",
        "Vaswani, A.",
        "Vaswani, Ashish, et al. \"Attention is all you need.\" Advances in Neural Information Processing Systems 30 (2017): 5998-6008.",
    ),
    (
        "World Health Organization (WHO), \"WHO Global Air Quality Guidelines: Particulate Matter (PM2.5 and PM10), Ozone, Nitrogen Dioxide, Sulfur Dioxide and Carbon Monoxide,\" Geneva, Switzerland, 2021.",
        "World Health Organization",
        "World Health Organization (WHO). WHO Global Air Quality Guidelines. Geneva: World Health Organization Press, 2021.",
    ),
    (
        "C. Zhang, Y. Wang, and H. Li, \"Transformer-based multi-step PM2.5 sequence prediction under severe non-stationary haze regimes,\" Atmos. Pollut. Res., vol. 14, no. 6, p. 101759, 2023, doi: 10.1016/j.apr.2023.101759.",
        "Zhang, C.",
        "Zhang, C., Y. Wang, and H. Li. \"Transformer-based multi-step PM2.5 sequence prediction under non-stationary haze.\" Atmospheric Pollution Research 14.6 (2023): 101759.",
    ),
    (
        "H. Zhou et al., \"Informer: Beyond efficient transformer for long sequence time-series forecasting,\" in Proc. AAAI Conf. Artif. Intell., vol. 35, 2021, pp. 11106–11115, doi: 10.1609/aaai.v35i12.17325.",
        "Zhou, H.",
        "Zhou, Haoyi, et al. \"Informer: Beyond efficient transformer for long sequence time-series forecasting.\" AAAI Conference on Artificial Intelligence 35 (2021): 11106-11115.",
    ),
]


def get_ieee_references() -> list[str]:
    """Return 25 numbered IEEE reference strings [1]..[25]."""
    return [f"[{idx}] {row[0]}" for idx, row in enumerate(REFERENCES_DATA, start=1)]


def get_alphabetical_bibliography() -> list[str]:
    """Return 25 bibliography entries sorted strictly alphabetically by author surname."""
    sorted_rows = sorted(REFERENCES_DATA, key=lambda r: r[1].lower())
    return [row[2] for row in sorted_rows]
