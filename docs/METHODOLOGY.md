# 📐 Mathematical & Modeling Methodology

## 1. Air Quality Index (AQI) Formulation

Both the Indian **CPCB (2014)** and **US EPA** AQI calculations compute a sub-index $I_p$ for each measured pollutant $p$ using piecewise-linear interpolation between regulatory concentration breakpoints $[BP_{lo}, BP_{hi}]$ and corresponding index bounds $[I_{lo}, I_{hi}]$:

$$I_p = \text{round}\left( \frac{I_{hi} - I_{lo}}{BP_{hi} - BP_{lo}} \cdot (C_p - BP_{lo}) + I_{lo} \right)$$

Where $C_p$ is the time-averaged observed concentration. The composite AQI is determined by the **dominant pollutant** rule:

$$\text{AQI} = \max_{p \in P_{\text{avail}}} I_p$$

- **Incomplete Panel Disclosure**: When fewer than the regulatory minimum pollutants are present at a monitoring station, AeroSense explicitly computes `is_complete = False` and displays an indicative partial-AQI notice alongside the list of missing pollutants.

---

## 2. Data Cleaning & Outlier Filtering

1. **Physical Bounds Validation**: Concentrations outside sensor-plausible physical limits (e.g., $\text{PM}_{2.5} \notin [0, 1000]\ \mu g/m^3$) are rejected during ingestion validation.
2. **Interquartile Range (IQR) Outlier Filter**: Within each `(location_id, parameter)` group, extreme sensor glitches outside $[Q_1 - 3 \cdot \text{IQR},\ Q_3 + 3 \cdot \text{IQR}]$ are filtered.
3. **Bounded Temporal Interpolation**: Short telemetry dropouts up to `max_gap_hours = 6` hours are interpolated linearly in time and explicitly flagged (`is_imputed = True`). Longer outages are preserved as gaps to avoid fabricating multi-day trends.

---

## 3. Feature Engineering for Time-Series Forecasting

To transform univariate/station air pollution series into tabular supervised learning features without lookahead leakage:

### 3.1 Cyclical Temporal Harmonics
Discrete calendar indices wrap discontinuously (e.g., hour 23 to hour 0). AeroSense maps periodic indices onto the unit circle:
$$\text{hour\_sin} = \sin\left(\frac{2\pi \cdot h}{24}\right), \quad \text{hour\_cos} = \cos\left(\frac{2\pi \cdot h}{24}\right)$$
Similarly applied to day-of-week ($\text{period} = 7$) and month ($\text{period} = 12$).

### 3.2 Autoregressive Lags & Rolling Windows
- **Lag Features**: $y_{t-1}, y_{t-3}, y_{t-6}, y_{t-12}, y_{t-24}$
- **Rolling Window Statistics**: Computed exclusively on shifted past series $y_{t-1}$ (`shift(1)`) over windows $w \in \{3, 6, 12, 24\}$ hours (mean, standard deviation, minimum, maximum) to strictly prevent target leakage.
- **Short-Term Momentum**: $\text{trend}_{24} = y_{t-1} - y_{t-24}$.

---

## 4. Forecasting Model Formulations

### 4.1 Chronological Validation Strategy
Random k-fold cross-validation breaks temporal autocorrelation and leaks future seasonal regimes into training. All AeroSense pipelines strictly partition sorted timestamps chronologically:
- **Train Split**: First $70\%$
- **Validation Split**: Next $15\%$ (early stopping & LR scheduling)
- **Held-Out Test Split**: Final $15\%$ (unseen evaluation metrics)

### 4.2 Deep Learning Sequence Architectures (`src/dl/models.py`)
1. **LSTM (`LSTMForecaster`)**: Multi-layer Long Short-Term Memory network capturing non-linear temporal dependencies via gated cell states, projecting the final hidden state to the multi-step forecast horizon.
2. **GRU (`GRUForecaster`)**: Gated Recurrent Unit architecture with fewer parameters (reset & update gates), optimizing convergence speed on smaller station series.
3. **TCN (`TCNForecaster`)**: Dilated causal 1-D convolutions (`dilation = 2^i`) with right-side zero-padding removal (`chomp`) ensuring strict causality (prediction at $t$ depends only on $\le t$) and exponentially growing receptive fields.
4. **Transformer (`TransformerForecaster`)**: Linear input projection + learned positional embeddings (`nn.Embedding`) followed by stacked multi-head self-attention `TransformerEncoderLayer` blocks.

---

## 5. Evaluation Metrics

All models are evaluated on held-out test predictions $\hat{y}_i$ against observed measurements $y_i$:

$$\text{MAE} = \frac{1}{N} \sum_{i=1}^{N} |y_i - \hat{y}_i|$$

$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (y_i - \hat{y}_i)^2}$$

$$R^2 = 1 - \frac{\sum_{i=1}^{N} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{N} (y_i - \bar{y})^2}$$
