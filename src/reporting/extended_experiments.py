"""Extended, reproducible experiments that feed the detailed project report.

Every number written to experiments/results/ext_*.csv is computed from the stored
datasets and the project's own pipeline (no hand-typed metrics).
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.aqi.cpcb import calculate_cpcb_aqi
from src.config import settings
from src.data.storage import load_processed
from src.features.feature_engineering import FEATURE_COLUMNS, build_feature_matrix
from src.ml.train import compute_metrics

OUT_DIR = settings.PROJECT_ROOT / "experiments" / "results"
LIVE_NAME = "IN_pm25_live_openaq"
BENCH_NAME = "delhi_anand_vihar_pm25_benchmark"
STATIONS = {17: "R K Puram, Delhi", 2456: "Talkatora, Lucknow", 407: "Zoo Park, Hyderabad"}
IST = pd.Timedelta(hours=5, minutes=30)

FEATURE_GROUPS = {
    "Temporal calendar only": [c for c in FEATURE_COLUMNS if c in (
        "hour", "day_of_week", "day_of_month", "month", "quarter", "is_weekend",
        "hour_sin", "hour_cos", "month_sin", "month_cos", "dow_sin", "dow_cos", "season")],
    "Lags only": [c for c in FEATURE_COLUMNS if c.startswith("lag_")],
    "Rolling statistics only": [c for c in FEATURE_COLUMNS if c.startswith("roll_")],
    "Lags + trend": [c for c in FEATURE_COLUMNS if c.startswith("lag_")] + ["trend_24"],
    "Lags + rolling + trend": [c for c in FEATURE_COLUMNS if c.startswith(("lag_", "roll_"))] + ["trend_24"],
    "All 35 features": list(FEATURE_COLUMNS),
}


def _load_series() -> dict[str, pd.DataFrame]:
    """Return named single-station DataFrames used throughout the experiments."""
    out: dict[str, pd.DataFrame] = {}
    live = load_processed(LIVE_NAME)
    if live is not None:
        live["datetime_utc"] = pd.to_datetime(live["datetime_utc"], utc=True)
        for lid, label in STATIONS.items():
            g = live[live["location_id"] == lid].dropna(subset=["value"]).sort_values("datetime_utc")
            if not g.empty:
                out[f"Live {label}"] = g.reset_index(drop=True)
    bench = load_processed(BENCH_NAME)
    if bench is not None:
        bench["datetime_utc"] = pd.to_datetime(bench["datetime_utc"], utc=True)
        out["Benchmark Delhi Anand Vihar"] = bench.sort_values("datetime_utc").reset_index(drop=True)
    return out


def _split(X: np.ndarray, y: np.ndarray):
    n = len(X)
    n_tr, n_va = int(n * settings.TRAIN_RATIO), int(n * settings.VAL_RATIO)
    return (X[:n_tr], y[:n_tr]), (X[n_tr:n_tr + n_va], y[n_tr:n_tr + n_va]), (X[n_tr + n_va:], y[n_tr + n_va:])


def _make(name: str):
    if name == "LinearRegression":
        return Pipeline([("scaler", StandardScaler()), ("model", LinearRegression())])
    if name == "Ridge":
        return Pipeline([("scaler", StandardScaler()), ("model", Ridge(alpha=1.0))])
    return RandomForestRegressor(n_estimators=100, random_state=settings.ML_RANDOM_STATE, n_jobs=-1)


def station_statistics(series: dict[str, pd.DataFrame]) -> pd.DataFrame:
    live = load_processed(LIVE_NAME)
    live["datetime_utc"] = pd.to_datetime(live["datetime_utc"], utc=True)
    rows = []
    for lid, label in STATIONS.items():
        g = live[live["location_id"] == lid].sort_values("datetime_utc")
        v = g["value"].dropna()
        nan_rows = int(g["value"].isna().sum())
        imputed = int(g["is_imputed"].sum())
        cats = v.apply(lambda x: calculate_cpcb_aqi(float(x)).category).value_counts()
        row = {
            "station": label, "location_id": lid, "rows": len(g), "valid_hours": len(v),
            "unfilled_gap_hours": nan_rows, "imputed_hours": imputed,
            "observed_hours": len(v) - imputed,
            "mean": v.mean(), "median": v.median(), "std": v.std(), "min": v.min(), "max": v.max(),
            "p25": v.quantile(.25), "p75": v.quantile(.75), "p90": v.quantile(.90), "p95": v.quantile(.95),
            "skew": v.skew(), "kurtosis": v.kurt(),
            "who_exceed_pct": 100 * (v > 15).mean(), "naaqs_exceed_pct": 100 * (v > 60).mean(),
            "latitude": g["latitude"].iloc[0], "longitude": g["longitude"].iloc[0],
            "sensor_id": int(g["sensor_id"].dropna().iloc[0]),
        }
        for c in ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]:
            row[f"cpcb_{c.replace(' ', '_').lower()}_pct"] = 100 * cats.get(c, 0) / len(v)
        hourly = g.set_index("datetime_utc")["value"].resample("h").mean()
        row["acf_lag1"] = hourly.autocorr(1)
        row["acf_lag24"] = hourly.autocorr(24)
        row["acf_lag168"] = hourly.autocorr(168) if len(hourly) > 200 else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def hourly_profile() -> pd.DataFrame:
    live = load_processed(LIVE_NAME)
    live["datetime_utc"] = pd.to_datetime(live["datetime_utc"], utc=True)
    live["hour_ist"] = (live["datetime_utc"] + IST).dt.hour
    live["dow_ist"] = (live["datetime_utc"] + IST).dt.dayofweek
    h = live.pivot_table(index="hour_ist", columns="location_id", values="value", aggfunc="mean")
    h.columns = [STATIONS[c] for c in h.columns]
    h.index.name = "hour_ist"
    return h.reset_index()


def weekday_profile() -> pd.DataFrame:
    live = load_processed(LIVE_NAME)
    live["datetime_utc"] = pd.to_datetime(live["datetime_utc"], utc=True)
    live["dow_ist"] = (live["datetime_utc"] + IST).dt.dayofweek
    d = live.pivot_table(index="dow_ist", columns="location_id", values="value", aggfunc="mean")
    d.columns = [STATIONS[c] for c in d.columns]
    d.index.name = "dow_ist"
    return d.reset_index()


def _feature_split(df: pd.DataFrame, horizon: int = 1):
    feat = build_feature_matrix(df)
    y = feat["value"].shift(-(horizon - 1)) if horizon > 1 else feat["value"]
    keep = y.notna()
    feat, y = feat[keep].reset_index(drop=True), y[keep].values
    return feat, y


def ablation(series: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for ds_name in ("Live R K Puram, Delhi", "Benchmark Delhi Anand Vihar"):
        if ds_name not in series:
            continue
        feat, y = _feature_split(series[ds_name])
        for grp, cols in FEATURE_GROUPS.items():
            cols = [c for c in cols if c in feat.columns]
            X = feat[cols].values
            (Xtr, ytr), _, (Xte, yte) = _split(X, y)
            for mname in ("LinearRegression", "RandomForest"):
                mdl = _make(mname).fit(Xtr, ytr)
                m = compute_metrics(yte, mdl.predict(Xte))
                rows.append({"dataset": ds_name, "feature_group": grp, "n_features": len(cols),
                             "model": mname, **{f"test_{k}": v for k, v in m.items()}})
    return pd.DataFrame(rows)


def horizon_study(series: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for ds_name in ("Live R K Puram, Delhi", "Benchmark Delhi Anand Vihar"):
        if ds_name not in series:
            continue
        for h in (1, 3, 6, 12, 24):
            feat, y = _feature_split(series[ds_name], horizon=h)
            X = feat[FEATURE_COLUMNS].values
            (Xtr, ytr), _, (Xte, yte) = _split(X, y)
            for mname in ("LinearRegression", "RandomForest"):
                mdl = _make(mname).fit(Xtr, ytr)
                m = compute_metrics(yte, mdl.predict(Xte))
                rows.append({"dataset": ds_name, "horizon_h": h, "model": mname,
                             **{f"test_{k}": v for k, v in m.items()}})
            # naive references using the same chronological test rows
            n_tr, n_va = int(len(X) * settings.TRAIN_RATIO), int(len(X) * settings.VAL_RATIO)
            te_idx = slice(n_tr + n_va, None)
            for lag_col, label in (("lag_1", "Persistence (lag_1)"), ("lag_24", "Seasonal naive (lag_24)")):
                pred = feat[lag_col].values[te_idx]
                m = compute_metrics(yte, pred)
                rows.append({"dataset": ds_name, "horizon_h": h, "model": label,
                             **{f"test_{k}": v for k, v in m.items()}})
    return pd.DataFrame(rows)


def block_bootstrap_ci(series: dict[str, pd.DataFrame], n_boot: int = 1000, block: int = 24) -> pd.DataFrame:
    rng = np.random.default_rng(settings.ML_RANDOM_STATE)
    rows = []
    for ds_name in ("Live R K Puram, Delhi", "Live Talkatora, Lucknow", "Live Zoo Park, Hyderabad",
                    "Benchmark Delhi Anand Vihar"):
        if ds_name not in series:
            continue
        feat, y = _feature_split(series[ds_name])
        X = feat[FEATURE_COLUMNS].values
        (Xtr, ytr), _, (Xte, yte) = _split(X, y)
        n_tr, n_va = int(len(X) * settings.TRAIN_RATIO), int(len(X) * settings.VAL_RATIO)
        for mname in ("LinearRegression", "RandomForest"):
            pred = _make(mname).fit(Xtr, ytr).predict(Xte)
            err = np.abs(yte - pred)
            n = len(err)
            n_blocks = int(np.ceil(n / block))
            maes = []
            for _ in range(n_boot):
                starts = rng.integers(0, max(1, n - block + 1), size=n_blocks)
                sample = np.concatenate([err[s:s + block] for s in starts])[:n]
                maes.append(sample.mean())
            rows.append({"dataset": ds_name, "model": mname, "n_test": n,
                         "test_MAE": err.mean(), "ci95_low": np.percentile(maes, 2.5),
                         "ci95_high": np.percentile(maes, 97.5)})
        persist = np.abs(yte - feat["lag_1"].values[n_tr + n_va:])
        rows.append({"dataset": ds_name, "model": "Persistence (lag_1)", "n_test": len(persist),
                     "test_MAE": persist.mean(), "ci95_low": np.nan, "ci95_high": np.nan})
    return pd.DataFrame(rows)


def error_analysis(series: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ds_name = "Live R K Puram, Delhi"
    feat, y = _feature_split(series[ds_name])
    X = feat[FEATURE_COLUMNS].values
    (Xtr, ytr), _, (Xte, yte) = _split(X, y)
    n_tr, n_va = int(len(X) * settings.TRAIN_RATIO), int(len(X) * settings.VAL_RATIO)
    te = feat.iloc[n_tr + n_va:].reset_index(drop=True)
    pred = _make("LinearRegression").fit(Xtr, ytr).predict(Xte)
    res = pred - yte
    te_dt = pd.to_datetime(te["datetime_utc"], utc=True) + IST
    by_hour = (pd.DataFrame({"hour_ist": te_dt.dt.hour.values, "abs_err": np.abs(res), "actual": yte})
               .groupby("hour_ist").agg(MAE=("abs_err", "mean"), mean_actual=("actual", "mean"),
                                         n=("abs_err", "size")).reset_index())
    bins = pd.cut(yte, bins=[0, 100, 200, 300, 600], labels=["0-100", "100-200", "200-300", ">300"])
    by_level = (pd.DataFrame({"level": bins, "abs_err": np.abs(res), "res": res})
                .groupby("level", observed=True).agg(MAE=("abs_err", "mean"), mean_residual=("res", "mean"),
                                                      n=("abs_err", "size")).reset_index())
    rs = pd.Series(res)
    stats = pd.DataFrame([{
        "dataset": ds_name, "model": "LinearRegression", "n_test": len(res),
        "mean_residual": rs.mean(), "std_residual": rs.std(), "skew": rs.skew(), "kurtosis": rs.kurt(),
        "residual_acf_lag1": rs.autocorr(1), "max_abs_error": np.abs(res).max(),
        "p50_abs_error": np.percentile(np.abs(res), 50), "p90_abs_error": np.percentile(np.abs(res), 90),
        "p95_abs_error": np.percentile(np.abs(res), 95),
    }])
    return by_hour, by_level, stats


def feature_importance(series: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for ds_name in ("Live R K Puram, Delhi", "Benchmark Delhi Anand Vihar"):
        feat, y = _feature_split(series[ds_name])
        X = feat[FEATURE_COLUMNS].values
        (Xtr, ytr), _, _ = _split(X, y)
        rf = _make("RandomForest").fit(Xtr, ytr)
        lin = _make("LinearRegression").fit(Xtr, ytr)
        coef = np.abs(lin.named_steps["model"].coef_)
        for i, f in enumerate(FEATURE_COLUMNS):
            rows.append({"dataset": ds_name, "feature": f,
                         "rf_importance": rf.feature_importances_[i],
                         "linear_abs_std_coef": coef[i]})
    return pd.DataFrame(rows)


def acf_table(series: dict[str, pd.DataFrame], max_lag: int = 72) -> pd.DataFrame:
    rows = {}
    for name, df in series.items():
        s = df.set_index("datetime_utc")["value"].resample("h").mean()
        rows[name] = [s.autocorr(k) for k in range(1, max_lag + 1)]
    out = pd.DataFrame(rows)
    out.insert(0, "lag_h", range(1, max_lag + 1))
    return out


def dl_history() -> pd.DataFrame:
    rows = []
    for p in sorted(settings.DL_MODELS_DIR.glob("*.pt")):
        try:
            import torch
            ck = torch.load(p, map_location="cpu", weights_only=False)
            h = ck.get("history", {})
            for e, (tl, vl) in enumerate(zip(h.get("train_loss", []), h.get("val_loss", [])), start=1):
                rows.append({"checkpoint": p.name, "epoch": e, "train_loss": tl, "val_loss": vl})
            rows.append({"checkpoint": p.name, "epoch": -1, "train_loss": np.nan, "val_loss": np.nan,
                         **{f"metric_{k}": v for k, v in ck.get("metrics", {}).items()},
                         "lookback": ck.get("lookback"), "horizon": ck.get("horizon")})
        except Exception:
            continue
    return pd.DataFrame(rows)


def aqi_worked_examples() -> pd.DataFrame:
    from src.aqi.us_epa import calculate_epa_aqi
    cases = [
        ("PM2.5 only, 25 ug/m3", {"pm25": 25.0}),
        ("PM2.5 only, 75 ug/m3", {"pm25": 75.0}),
        ("PM2.5 only, 177.8 ug/m3 (R K Puram mean)", {"pm25": 177.8}),
        ("PM2.5 only, 345 ug/m3", {"pm25": 345.0}),
        ("PM2.5 only, 501 ug/m3 (observed max)", {"pm25": 501.0}),
        ("PM2.5 130 + PM10 210 + NO2 90 + SO2 25", {"pm25": 130.0, "pm10": 210.0, "no2": 90.0, "so2": 25.0}),
        ("Full panel PM2.5 65, PM10 110, NO2 42, SO2 18, CO 1.1, O3 48",
         {"pm25": 65.0, "pm10": 110.0, "no2": 42.0, "so2": 18.0, "co": 1.1, "o3": 48.0}),
    ]
    rows = []
    for label, meas in cases:
        c = calculate_cpcb_aqi(meas)
        e = calculate_epa_aqi({k: v for k, v in meas.items() if k in ("pm25", "pm10")}) \
            if set(meas) <= {"pm25", "pm10"} else None
        rows.append({"case": label, "cpcb_aqi": c.aqi, "cpcb_category": c.category,
                     "cpcb_dominant": c.dominant_pollutant, "cpcb_is_complete": c.is_complete,
                     "epa_aqi": e.aqi if e else np.nan, "epa_category": e.category if e else ""})
    return pd.DataFrame(rows)


def run_all() -> dict[str, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    series = _load_series()
    outputs: dict[str, pd.DataFrame] = {}
    outputs["ext_station_stats"] = station_statistics(series)
    outputs["ext_hourly_profile"] = hourly_profile()
    outputs["ext_weekday_profile"] = weekday_profile()
    outputs["ext_ablation"] = ablation(series)
    outputs["ext_horizon_study"] = horizon_study(series)
    outputs["ext_bootstrap_ci"] = block_bootstrap_ci(series)
    by_hour, by_level, rstats = error_analysis(series)
    outputs["ext_error_by_hour"], outputs["ext_error_by_level"], outputs["ext_residual_stats"] = by_hour, by_level, rstats
    outputs["ext_feature_importance"] = feature_importance(series)
    outputs["ext_acf"] = acf_table(series)
    outputs["ext_dl_history"] = dl_history()
    outputs["ext_aqi_examples"] = aqi_worked_examples()
    paths = {}
    for name, df in outputs.items():
        p = OUT_DIR / f"{name}.csv"
        df.to_csv(p, index=False)
        paths[name] = p
        print(f"wrote {p.name}: {len(df)} rows")
    meta = {"datasets": {k: {"rows": len(v)} for k, v in series.items()}}
    (OUT_DIR / "ext_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return paths


if __name__ == "__main__":
    run_all()
