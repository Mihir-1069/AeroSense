"""Generate the additional publication figures used by the detailed project report.

All plots are drawn from stored datasets and the experiments/results/ext_*.csv files; nothing is hand-entered.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch
from PIL import Image

from src.aqi.cpcb import CPCB_BREAKPOINTS, CPCB_COLORS
from src.aqi.us_epa import EPA_BREAKPOINTS
from src.config import settings
from src.data.storage import load_processed
from src.features.feature_engineering import FEATURE_COLUMNS, build_feature_matrix

FIG_DIR = settings.REPORTS_DIR / "figures"
RES = settings.PROJECT_ROOT / "experiments" / "results"
SCREEN_DIR = settings.REPORTS_DIR / "screens"
IST = pd.Timedelta(hours=5, minutes=30)
STATION_LABELS = {17: "R K Puram, Delhi", 2456: "Talkatora, Lucknow", 407: "Zoo Park, Hyderabad"}
COLORS = ["#0284C7", "#EA580C", "#16A34A", "#7C3AED"]

plt.rcParams.update({"font.family": "sans-serif", "font.size": 9.5, "axes.edgecolor": "#CBD5E1",
                     "axes.linewidth": 0.8, "axes.grid": True, "grid.alpha": 0.25})


def _save(fig, name: str) -> Path:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    p = FIG_DIR / name
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def _live() -> pd.DataFrame:
    live = load_processed("IN_pm25_live_openaq")
    live["datetime_utc"] = pd.to_datetime(live["datetime_utc"], utc=True)
    live["label"] = live["location_id"].map(STATION_LABELS)
    return live


def fig_pipeline_flow() -> Path:
    stages = [
        ("1. Discover", "GET /v3/locations\n(ISO country, parameter)"),
        ("2. Extract", "GET /v3/sensors/{id}/hours\npaginated + backoff"),
        ("3. Validate", "schema, UTC, bounds,\nde-duplicate"),
        ("4. Clean", "IQR x 3 filter,\n<= 6 h interpolation"),
        ("5. Store", "Parquet raw/\nprocessed/ + CSV"),
        ("6. Features", "35 leakage-free\nlag/rolling/calendar"),
        ("7. Model", "3 baselines, 6 ML,\n4 PyTorch DL"),
        ("8. Explain", "SHAP, permutation,\nresiduals"),
        ("9. Deliver", "10 Streamlit pages,\nPDF/HTML/ZIP reports"),
    ]
    fig, ax = plt.subplots(figsize=(13, 3.6))
    ax.axis("off")
    ax.set_xlim(0, len(stages) * 1.45)
    ax.set_ylim(0, 3)
    palette = ["#0369A1", "#0369A1", "#0F766E", "#0F766E", "#B45309", "#7C3AED", "#7C3AED", "#BE185D", "#15803D"]
    for i, (title, body) in enumerate(stages):
        x = i * 1.45 + 0.05
        ax.add_patch(FancyBboxPatch((x, 0.9), 1.25, 1.5, boxstyle="round,pad=0.03", fc=palette[i], ec="none"))
        ax.text(x + 0.625, 2.12, title, ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")
        ax.text(x + 0.625, 1.45, body, ha="center", va="center", color="white", fontsize=7.4)
        if i < len(stages) - 1:
            ax.annotate("", xy=(x + 1.42, 1.65), xytext=(x + 1.27, 1.65),
                        arrowprops=dict(arrowstyle="->", color="#334155", lw=1.4))
    ax.text(len(stages) * 1.45 / 2, 0.35, "AeroSense AI end-to-end pipeline (provider: OpenAQ API v3, storage: local-first Parquet)",
            ha="center", fontsize=9.5, color="#334155")
    return _save(fig, "fig07_pipeline_flow.png")


def fig_layer_architecture() -> Path:
    layers = [
        ("Presentation layer", "app.py + pages/01 ... pages/10 (Streamlit, Plotly dark theme)", "#0369A1"),
        ("Reporting & export layer", "src/reporting: Markdown, HTML, ReportLab PDF, python-pptx, ZIP bundles", "#7C3AED"),
        ("Explainability layer", "src/explainability: native importance, permutation, SHAP, residuals", "#BE185D"),
        ("Modelling layer", "src/ml (baselines, 6 sklearn/XGBoost regressors)  |  src/dl (LSTM, GRU, TCN, Transformer)", "#B45309"),
        ("Feature layer", "src/features: calendar harmonics, lags, shifted rolling stats, trend, sliding windows", "#0F766E"),
        ("AQI layer", "src/aqi: CPCB 2014 and US EPA breakpoint calculators with is_complete disclosure", "#15803D"),
        ("Data layer", "src/data: ingestion, validation, cleaning, storage, bootstrap, seed_benchmark", "#475569"),
        ("Integration layer", "src/api/openaq_client.py: X-API-Key auth, retry/backoff, pagination, status mapping", "#0F172A"),
    ]
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, len(layers) * 1.1)
    for i, (name, body, col) in enumerate(layers):
        y = (len(layers) - 1 - i) * 1.1
        ax.add_patch(FancyBboxPatch((0.1, y + 0.08), 9.8, 0.9, boxstyle="round,pad=0.02", fc=col, ec="none"))
        ax.text(0.35, y + 0.64, name, color="white", fontsize=10.5, fontweight="bold", va="center")
        ax.text(0.35, y + 0.32, body, color="white", fontsize=8.2, va="center")
    return _save(fig, "fig08_layer_architecture.png")


def fig_distribution(live: pd.DataFrame) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.4))
    labels, data = [], []
    for i, (lid, lab) in enumerate(STATION_LABELS.items()):
        v = live.loc[live["location_id"] == lid, "value"].dropna()
        ax1.hist(v, bins=40, alpha=0.55, color=COLORS[i], label=f"{lab} (n={len(v)})")
        labels.append(lab.split(",")[0])
        data.append(v.values)
    ax1.axvline(60, color="#DC2626", ls="--", lw=1.2, label="NAAQS 60")
    ax1.axvline(15, color="#64748B", ls=":", lw=1.2, label="WHO 15")
    ax1.set_title("A. PM2.5 value distribution per station", fontweight="bold")
    ax1.set_xlabel("PM2.5 (ug/m3)")
    ax1.set_ylabel("Hourly readings")
    ax1.legend(fontsize=7.5)
    bp = ax2.boxplot(data, tick_labels=labels, patch_artist=True, showfliers=True)
    for patch, c in zip(bp["boxes"], COLORS):
        patch.set_facecolor(c)
        patch.set_alpha(0.6)
    ax2.axhline(60, color="#DC2626", ls="--", lw=1.2)
    ax2.set_title("B. Spread, quartiles and extremes", fontweight="bold")
    ax2.set_ylabel("PM2.5 (ug/m3)")
    fig.tight_layout()
    return _save(fig, "fig09_distribution_boxplot.png")


def fig_acf() -> Path:
    acf = pd.read_csv(RES / "ext_acf.csv")
    fig, ax = plt.subplots(figsize=(11, 4.2))
    cols = [c for c in acf.columns if c != "lag_h"]
    for i, c in enumerate(cols):
        ax.plot(acf["lag_h"], acf[c], lw=1.7, color=COLORS[i % 4], label=c)
    ax.axvline(24, color="#64748B", ls=":", lw=1.1)
    ax.axvline(48, color="#64748B", ls=":", lw=1.1)
    ax.axvline(72, color="#64748B", ls=":", lw=1.1)
    ax.set_xlabel("Lag (hours)")
    ax.set_ylabel("Autocorrelation")
    ax.set_title("Autocorrelation of hourly PM2.5 (dotted lines mark 24 / 48 / 72 h)", fontweight="bold")
    ax.legend(fontsize=8)
    return _save(fig, "fig10_acf.png")


def fig_hour_heatmap() -> Path:
    h = pd.read_csv(RES / "ext_hourly_profile.csv").set_index("hour_ist")
    norm = (h - h.min()) / (h.max() - h.min())
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 5.6), gridspec_kw={"height_ratios": [1.1, 1]})
    im = ax1.imshow(norm.T.values, aspect="auto", cmap="YlOrRd")
    ax1.set_yticks(range(len(h.columns)))
    ax1.set_yticklabels(h.columns, fontsize=8.5)
    ax1.set_xticks(range(0, 24, 2))
    ax1.set_xticklabels(range(0, 24, 2))
    ax1.set_xlabel("Hour of day (IST)")
    ax1.grid(False)
    ax1.set_title("A. Min-max normalised diurnal intensity (darker = higher relative PM2.5)", fontweight="bold")
    fig.colorbar(im, ax=ax1, fraction=0.025, pad=0.01)
    d = pd.read_csv(RES / "ext_weekday_profile.csv")
    names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    w = 0.26
    for i, c in enumerate([c for c in d.columns if c != "dow_ist"]):
        ax2.bar(d["dow_ist"] + (i - 1) * w, d[c], width=w, color=COLORS[i], label=c)
    ax2.set_xticks(range(7))
    ax2.set_xticklabels(names)
    ax2.set_ylabel("Mean PM2.5 (ug/m3)")
    ax2.set_title("B. Day-of-week mean (IST calendar)", fontweight="bold")
    ax2.legend(fontsize=8)
    fig.tight_layout()
    return _save(fig, "fig11_diurnal_weekly.png")


def fig_missingness(live: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(11, 3.6))
    t0 = live["datetime_utc"].min()
    for row, (lid, lab) in enumerate(STATION_LABELS.items()):
        g = live[live["location_id"] == lid].sort_values("datetime_utc")
        x = (g["datetime_utc"] - t0).dt.total_seconds() / 3600
        state = np.where(g["value"].isna(), 2, np.where(g["is_imputed"], 1, 0))
        for code, col in ((0, "#16A34A"), (1, "#F59E0B"), (2, "#DC2626")):
            sel = state == code
            ax.scatter(x[sel], np.full(sel.sum(), row), s=9, marker="|", color=col, linewidths=1.3)
    ax.set_yticks(range(3))
    ax.set_yticklabels(list(STATION_LABELS.values()))
    ax.set_xlabel("Hours since first record (2026-10-17 05:00 UTC)")
    ax.set_title("Data completeness: observed / interpolated (<= 6 h) / unfilled gap", fontweight="bold")
    ax.legend(handles=[Patch(color="#16A34A", label="Observed"), Patch(color="#F59E0B", label="Interpolated (is_imputed)"),
                       Patch(color="#DC2626", label="Unfilled gap (NaN)")], ncol=3, fontsize=8, loc="upper center",
              bbox_to_anchor=(0.5, -0.22))
    return _save(fig, "fig12_missingness_timeline.png")


def fig_aqi_curves() -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.4))
    for ax, table, title, lim in (
        (ax1, CPCB_BREAKPOINTS["pm25"], "A. CPCB (India, 2014) PM2.5 sub-index", 260),
        (ax2, EPA_BREAKPOINTS["pm25"], "B. US EPA (2018) PM2.5 sub-index", 260),
    ):
        for lo, hi, ilo, ihi in table:
            ax.plot([lo, hi], [ilo, ihi], lw=2.2, color="#0284C7")
            ax.axvspan(lo, hi, alpha=0.08, color="#0284C7" if table is CPCB_BREAKPOINTS["pm25"] else "#7C3AED")
        ax.set_xlim(0, lim)
        ax.set_ylim(0, 410)
        ax.set_xlabel("PM2.5 24 h concentration (ug/m3)")
        ax.set_ylabel("Sub-index")
        ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "fig13_aqi_breakpoint_curves.png")


def fig_cpcb_stack() -> Path:
    s = pd.read_csv(RES / "ext_station_stats.csv")
    cats = ["good", "satisfactory", "moderate", "poor", "very_poor", "severe"]
    names = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    fig, ax = plt.subplots(figsize=(10.5, 3.4))
    left = np.zeros(len(s))
    for c, n in zip(cats, names):
        vals = s[f"cpcb_{c}_pct"].values
        ax.barh(s["station"], vals, left=left, color=CPCB_COLORS[n], edgecolor="white", label=n)
        for i, v in enumerate(vals):
            if v >= 4:
                ax.text(left[i] + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=8,
                        color="black" if n in ("Good", "Satisfactory", "Moderate") else "white")
        left += vals
    ax.set_xlim(0, 100)
    ax.set_xlabel("Share of valid hourly readings (%)")
    ax.set_title("CPCB category share per station (hourly PM2.5 treated as indicative single-pollutant AQI)", fontweight="bold")
    ax.legend(ncol=6, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    return _save(fig, "fig14_cpcb_category_stack.png")


def fig_feature_corr(live: pd.DataFrame) -> Path:
    g = live[live["location_id"] == 17].dropna(subset=["value"]).sort_values("datetime_utc")
    feat = build_feature_matrix(g)
    cols = ["value", "lag_1", "lag_3", "lag_6", "lag_12", "lag_24", "roll_mean_3", "roll_mean_24", "roll_std_24",
            "roll_max_24", "trend_24", "hour_sin", "hour_cos", "dow_sin", "is_weekend"]
    corr = feat[cols].corr()
    fig, ax = plt.subplots(figsize=(8.4, 7.2))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=60, ha="right", fontsize=8)
    ax.set_yticklabels(cols, fontsize=8)
    ax.grid(False)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=6.2,
                    color="white" if abs(corr.values[i, j]) > 0.6 else "black")
    fig.colorbar(im, ax=ax, fraction=0.04)
    ax.set_title("Pearson correlation of target and engineered features (live R K Puram)", fontweight="bold", fontsize=10)
    return _save(fig, "fig15_feature_correlation.png")


def fig_feature_importance() -> Path:
    fi = pd.read_csv(RES / "ext_feature_importance.csv")
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.4))
    for r, ds in enumerate(["Live R K Puram, Delhi", "Benchmark Delhi Anand Vihar"]):
        d = fi[fi["dataset"] == ds]
        top = d.nlargest(10, "rf_importance").iloc[::-1]
        axes[r, 0].barh(top["feature"], top["rf_importance"], color="#0284C7")
        axes[r, 0].set_title(f"RandomForest importance - {ds}", fontsize=9.5, fontweight="bold")
        top2 = d.nlargest(10, "linear_abs_std_coef").iloc[::-1]
        axes[r, 1].barh(top2["feature"], top2["linear_abs_std_coef"], color="#7C3AED")
        axes[r, 1].set_title(f"|Standardised coefficient| LinearRegression - {ds}", fontsize=9.5, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "fig16_feature_importance_compare.png")


def fig_ablation() -> Path:
    ab = pd.read_csv(RES / "ext_ablation.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=False)
    for ax, ds in zip(axes, ["Live R K Puram, Delhi", "Benchmark Delhi Anand Vihar"]):
        d = ab[ab["dataset"] == ds]
        groups = list(dict.fromkeys(d["feature_group"]))
        x = np.arange(len(groups))
        for i, m in enumerate(["LinearRegression", "RandomForest"]):
            vals = [d[(d["feature_group"] == g) & (d["model"] == m)]["test_MAE"].values[0] for g in groups]
            ax.bar(x + (i - 0.5) * 0.38, vals, width=0.38, color=COLORS[i], label=m)
        ax.set_xticks(x)
        ax.set_xticklabels(groups, rotation=28, ha="right", fontsize=8)
        ax.set_ylabel("Test MAE (ug/m3)")
        ax.set_title(ds, fontweight="bold", fontsize=10)
        ax.legend(fontsize=8)
    fig.suptitle("Feature-group ablation (chronological 70/15/15, 1-step ahead)", fontweight="bold")
    fig.tight_layout()
    return _save(fig, "fig17_feature_ablation.png")


def fig_horizon() -> Path:
    hz = pd.read_csv(RES / "ext_horizon_study.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4))
    for ax, ds in zip(axes, ["Live R K Puram, Delhi", "Benchmark Delhi Anand Vihar"]):
        d = hz[hz["dataset"] == ds]
        for i, m in enumerate(["LinearRegression", "RandomForest", "Persistence (lag_1)", "Seasonal naive (lag_24)"]):
            dd = d[d["model"] == m].sort_values("horizon_h")
            ax.plot(dd["horizon_h"], dd["test_MAE"], marker="o", lw=1.9, color=COLORS[i], label=m)
        ax.set_xlabel("Forecast horizon h (hours ahead of the feature timestamp)")
        ax.set_ylabel("Test MAE (ug/m3)")
        ax.set_title(ds, fontweight="bold", fontsize=10)
        ax.set_xticks([1, 3, 6, 12, 24])
        ax.legend(fontsize=8)
    fig.suptitle("Direct multi-horizon degradation of tabular forecasters", fontweight="bold")
    fig.tight_layout()
    return _save(fig, "fig18_horizon_degradation.png")


def fig_error_hour_level() -> Path:
    eh = pd.read_csv(RES / "ext_error_by_hour.csv")
    el = pd.read_csv(RES / "ext_error_by_level.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.4))
    ax1.bar(eh["hour_ist"], eh["MAE"], color="#0284C7", label="LinearRegression MAE")
    ax1b = ax1.twinx()
    ax1b.plot(eh["hour_ist"], eh["mean_actual"], color="#EA580C", marker="o", ms=3.5, label="Mean actual PM2.5")
    ax1b.grid(False)
    ax1.set_xlabel("Hour of day (IST)")
    ax1.set_ylabel("Test MAE (ug/m3)")
    ax1b.set_ylabel("Mean actual PM2.5 (ug/m3)")
    ax1.set_title("A. Error by hour of day (live R K Puram test split)", fontweight="bold", fontsize=10)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax1b.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
    ax2.bar(el["level"].astype(str), el["MAE"], color="#7C3AED", label="MAE")
    ax2.plot(el["level"].astype(str), el["mean_residual"], color="#DC2626", marker="s", label="Mean residual (pred - actual)")
    ax2.axhline(0, color="black", lw=0.8)
    for i, n in enumerate(el["n"]):
        ax2.text(i, 1, f"n={n}", ha="center", va="bottom", fontsize=8, color="white")
    ax2.set_xlabel("Actual PM2.5 level bin (ug/m3)")
    ax2.set_ylabel("ug/m3")
    ax2.set_title("B. Error and bias by pollution level", fontweight="bold", fontsize=10)
    ax2.legend(fontsize=8)
    fig.tight_layout()
    return _save(fig, "fig19_error_hour_level.png")


def fig_dl_curves() -> Path | None:
    h = pd.read_csv(RES / "ext_dl_history.csv")
    h = h[h["epoch"] > 0]
    if h.empty:
        return None
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    for name, g in h.groupby("checkpoint"):
        ax.plot(g["epoch"], g["train_loss"], lw=1.8, color="#0284C7", label=f"{name} train MSE (scaled)")
        ax.plot(g["epoch"], g["val_loss"], lw=1.8, color="#EA580C", label=f"{name} validation MSE (scaled)")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE on MinMax-scaled target")
    ax.set_title("LSTM learning curves from the persisted checkpoint (early stopping + ReduceLROnPlateau)",
                 fontweight="bold", fontsize=10)
    ax.legend(fontsize=7.5)
    return _save(fig, "fig20_dl_learning_curves.png")


def fig_bootstrap() -> Path:
    b = pd.read_csv(RES / "ext_bootstrap_ci.csv")
    b = b[b["model"] != "Persistence (lag_1)"].copy()
    labels = [f"{d.replace('Live ', '').replace('Benchmark ', 'Bench. ')}\n{m}" for d, m in zip(b["dataset"], b["model"])]
    fig, ax = plt.subplots(figsize=(11.5, 4.4))
    x = np.arange(len(b))
    err = [b["test_MAE"] - b["ci95_low"], b["ci95_high"] - b["test_MAE"]]
    ax.bar(x, b["test_MAE"], yerr=err, capsize=4, color=[COLORS[0] if m == "LinearRegression" else COLORS[1] for m in b["model"]])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.4, rotation=20, ha="right")
    ax.set_ylabel("Test MAE (ug/m3)")
    ax.set_title("Test MAE with 95% moving-block bootstrap interval (block = 24 h, 1000 resamples)", fontweight="bold", fontsize=10)
    return _save(fig, "fig21_bootstrap_ci.png")


def fig_scatter_qq(live: pd.DataFrame) -> Path:
    from scipy import stats
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    g = live[live["location_id"] == 17].dropna(subset=["value"]).sort_values("datetime_utc")
    feat = build_feature_matrix(g)
    X, y = feat[FEATURE_COLUMNS].values, feat["value"].values
    n_tr, n_va = int(len(X) * 0.7), int(len(X) * 0.15)
    m = Pipeline([("s", StandardScaler()), ("m", LinearRegression())]).fit(X[:n_tr], y[:n_tr])
    pred = m.predict(X[n_tr + n_va:])
    act = y[n_tr + n_va:]
    res = pred - act
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))
    ax1.scatter(act, pred, s=14, alpha=0.65, color="#0284C7")
    lim = [0, max(act.max(), pred.max()) * 1.05]
    ax1.plot(lim, lim, color="#DC2626", lw=1.3, ls="--", label="Perfect forecast")
    ax1.set_xlabel("Actual PM2.5 (ug/m3)")
    ax1.set_ylabel("Predicted PM2.5 (ug/m3)")
    ax1.set_title("A. Predicted vs actual (LinearRegression, test split)", fontweight="bold", fontsize=10)
    ax1.legend(fontsize=8)
    (osm, osr), (slope, intercept, r) = stats.probplot(res, dist="norm")
    ax2.scatter(osm, osr, s=12, alpha=0.7, color="#7C3AED")
    ax2.plot(osm, slope * np.array(osm) + intercept, color="#DC2626", lw=1.3)
    ax2.set_xlabel("Theoretical normal quantiles")
    ax2.set_ylabel("Residual quantiles (ug/m3)")
    ax2.set_title(f"B. Residual Q-Q plot (r = {r:.3f})", fontweight="bold", fontsize=10)
    fig.tight_layout()
    return _save(fig, "fig22_scatter_qq.png")


def fig_benchmark_vs_live() -> Path:
    live = _live()
    bench = load_processed("delhi_anand_vihar_pm25_benchmark")
    bench["datetime_utc"] = pd.to_datetime(bench["datetime_utc"], utc=True)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    b = bench.assign(h=(bench["datetime_utc"] + IST).dt.hour).groupby("h")["value"].mean()
    r = live[live["location_id"] == 17].assign(h=lambda d: (d["datetime_utc"] + IST).dt.hour).groupby("h")["value"].mean()
    ax.plot(b.index, (b - b.mean()) / b.std(), lw=2, color="#0284C7", marker="o", ms=3.5, label="Calibration benchmark (synthetic, Anand Vihar profile)")
    ax.plot(r.index, (r - r.mean()) / r.std(), lw=2, color="#EA580C", marker="s", ms=3.5, label="Live OpenAQ R K Puram (measured)")
    ax.set_xlabel("Hour of day (IST)")
    ax.set_ylabel("z-scored diurnal mean")
    ax.set_title("Diurnal shape: calibration benchmark vs live measurements (z-scored)", fontweight="bold", fontsize=10)
    ax.legend(fontsize=8)
    return _save(fig, "fig23_benchmark_vs_live_diurnal.png")


def fig_station_map(live: pd.DataFrame) -> Path:
    s = pd.read_csv(RES / "ext_station_stats.csv")
    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    sc = ax.scatter(s["longitude"], s["latitude"], c=s["mean"], s=s["mean"] * 4 + 120, cmap="YlOrRd",
                    edgecolor="black", linewidth=0.8, vmin=0, vmax=200)
    for _, r in s.iterrows():
        ax.annotate(f"{r['station']}\nmean {r['mean']:.1f}", (r["longitude"], r["latitude"]),
                    textcoords="offset points", xytext=(8, 8), fontsize=8.4)
    ax.set_xlim(75, 85)
    ax.set_ylim(15.5, 30)
    ax.set_xlabel("Longitude (deg E)")
    ax.set_ylabel("Latitude (deg N)")
    ax.set_title("Live OpenAQ v3 stations (marker size and colour = mean PM2.5)", fontweight="bold", fontsize=10)
    fig.colorbar(sc, ax=ax, label="Mean PM2.5 (ug/m3)", fraction=0.04)
    return _save(fig, "fig24_station_geography.png")


def fig_model_time_vs_error() -> Path:
    ml = pd.read_csv(RES / "ml_benchmark_results.csv")
    dl = pd.read_csv(RES / "dl_h1_benchmark.csv")
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    ax.scatter(ml["train_time_s"] + 0.01, ml["test_MAE"], s=90, color="#0284C7", label="Traditional ML")
    ax.scatter(dl["train_time_s"], dl["MAE"], s=90, color="#7C3AED", marker="D", label="PyTorch DL (h=1)")
    for _, r in ml.iterrows():
        ax.annotate(r["model"], (r["train_time_s"] + 0.01, r["test_MAE"]), textcoords="offset points", xytext=(5, 4), fontsize=7.8)
    for _, r in dl.iterrows():
        ax.annotate(r["model"], (r["train_time_s"], r["MAE"]), textcoords="offset points", xytext=(5, 4), fontsize=7.8)
    ax.set_xscale("log")
    ax.set_xlabel("Training time (s, log scale)")
    ax.set_ylabel("Test MAE (ug/m3)")
    ax.set_title("Accuracy-cost trade-off on the controlled benchmark", fontweight="bold", fontsize=10)
    ax.legend(fontsize=8)
    return _save(fig, "fig25_accuracy_vs_cost.png")


def crop_screenshots() -> list[Path]:
    """Trim the Streamlit top bar and trailing blank background from raw page captures."""
    out_dir = SCREEN_DIR / "cropped"
    out_dir.mkdir(parents=True, exist_ok=True)
    outs = []
    for p in sorted(SCREEN_DIR.glob("scr*.png")):
        im = Image.open(p).convert("RGB")
        arr = np.asarray(im).astype(int)
        bg = arr[-1, -1]
        diff = np.abs(arr - bg).sum(axis=2) > 18
        rows = np.where(diff[:, 330:].any(axis=1))[0]
        bottom = min(im.height, (rows.max() + 40) if len(rows) else im.height)
        cropped = im.crop((0, 62, im.width, bottom))
        dest = out_dir / p.name
        cropped.save(dest, optimize=True)
        outs.append(dest)
    return outs


def generate_all() -> list[Path]:
    live = _live()
    made = [
        fig_pipeline_flow(), fig_layer_architecture(), fig_distribution(live), fig_acf(), fig_hour_heatmap(),
        fig_missingness(live), fig_aqi_curves(), fig_cpcb_stack(), fig_feature_corr(live), fig_feature_importance(),
        fig_ablation(), fig_horizon(), fig_error_hour_level(), fig_dl_curves(), fig_bootstrap(),
        fig_scatter_qq(live), fig_benchmark_vs_live(), fig_station_map(live), fig_model_time_vs_error(),
    ]
    made = [m for m in made if m]
    made += crop_screenshots()
    for m in made:
        print("figure:", m.name)
    return made


if __name__ == "__main__":
    generate_all()
