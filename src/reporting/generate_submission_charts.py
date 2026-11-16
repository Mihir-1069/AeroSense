"""
AeroSense AI — Publication Figure Generator for Academic Reports & Presentation
Produces 300 DPI Matplotlib charts strictly from actual observed data and experiment CSVs.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config import settings
from src.data.storage import load_processed
from src.features.feature_engineering import build_feature_matrix
from src.ml.train import load_model
from src.explainability.feature_importance import shap_values
from src.aqi.cpcb import calculate_cpcb_aqi

FIG_DIR = settings.REPORTS_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": "#CBD5E1",
    "axes.linewidth": 0.8,
})

def generate_all_figures() -> dict[str, Path]:
    paths: dict[str, Path] = {}

    live = load_processed("IN_pm25_live_openaq")
    bench = load_processed("delhi_anand_vihar_pm25_benchmark")
    ml_csv = settings.PROJECT_ROOT / "experiments" / "results" / "ml_benchmark_results.csv"
    live_csv = settings.PROJECT_ROOT / "experiments" / "results" / "live_rkp_benchmark.csv"
    dl_csv = settings.PROJECT_ROOT / "experiments" / "results" / "dl_h1_benchmark.csv"

    # Fig 1: Live OpenAQ India Multi-Station Time Series & Diurnal Cycle
    if live is not None and not live.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5), dpi=300)
        colors = ["#0284C7", "#EA580C", "#16A34A"]
        live["datetime_utc"] = pd.to_datetime(live["datetime_utc"], utc=True)
        live["hour_ist"] = ((live["datetime_utc"].dt.hour + 5.5) % 24).astype(int)

        for idx, (st_name, grp) in enumerate(live.groupby("location_name")):
            short = st_name.split(",")[0]
            c = colors[idx % len(colors)]
            daily = grp.set_index("datetime_utc")["value"].resample("D").mean().dropna()
            ax1.plot(daily.index, daily.values, marker="o", markersize=3, linewidth=1.8, label=short, color=c)

            diurnal = grp.groupby("hour_ist")["value"].mean()
            ax2.plot(diurnal.index, diurnal.values, marker="s", markersize=3.5, linewidth=2.0, label=short, color=c)

        ax1.axhline(60, color="#DC2626", linestyle="--", linewidth=1.2, label="CPCB NAAQS 24h (60 µg/m³)")
        ax1.axhline(15, color="#64748B", linestyle=":", linewidth=1.2, label="WHO 24h (15 µg/m³)")
        ax1.set_title("A. Live OpenAQ v3 Daily Mean PM2.5 (Oct-Nov 2026)", fontweight="bold")
        ax1.set_ylabel("PM2.5 (µg/m³)")
        ax1.tick_params(axis="x", rotation=25)
        ax1.grid(alpha=0.25)
        ax1.legend(fontsize=8)

        ax2.set_title("B. Diurnal Boundary-Layer Cycle (IST Hours)", fontweight="bold")
        ax2.set_xlabel("Hour of Day (IST)")
        ax2.set_ylabel("Mean PM2.5 (µg/m³)")
        ax2.set_xticks(range(0, 24, 3))
        ax2.grid(alpha=0.25)
        ax2.legend(fontsize=8)

        plt.tight_layout()
        p1 = FIG_DIR / "fig1_live_station_profiles.png"
        fig.savefig(p1, bbox_inches="tight")
        plt.close(fig)
        paths["fig1"] = p1

    # Fig 2: Held-Out Test Benchmark Comparison (ML + DL 1-step & Live)
    if ml_csv.exists():
        ml_df = pd.read_csv(ml_csv)
        frames = [ml_df[["model", "test_MAE", "test_RMSE", "test_R2"]].assign(Family="ML (Tabular)")]
        if dl_csv.exists():
            dl_df = pd.read_csv(dl_csv).rename(columns={"MAE": "test_MAE", "RMSE": "test_RMSE", "R2": "test_R2"})
            dl_df["Family"] = "DL (PyTorch 1-step)"
            frames.append(dl_df[["model", "test_MAE", "test_RMSE", "test_R2", "Family"]])
        comb = pd.concat(frames, ignore_index=True).sort_values("test_MAE", ascending=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=300)
        bar_colors = ["#0284C7" if f.startswith("ML") else "#7C3AED" for f in comb["Family"]]

        bars1 = ax1.barh(comb["model"], comb["test_MAE"], color=bar_colors, edgecolor="#0F172A", linewidth=0.5)
        ax1.invert_yaxis()
        ax1.set_xlim(0, 14.2)
        ax1.set_title("A. Test MAE (µg/m³) — Lower is Better", fontweight="bold")
        ax1.set_xlabel("Mean Absolute Error (µg/m³)")
        ax1.grid(axis="x", alpha=0.25)
        for b in bars1:
            ax1.text(b.get_width() + 0.25, b.get_y() + b.get_height()/2, f"{b.get_width():.2f}", va="center", fontsize=8.5)

        bars2 = ax2.barh(comb["model"], comb["test_R2"], color=bar_colors, edgecolor="#0F172A", linewidth=0.5)
        ax2.invert_yaxis()
        ax2.set_title("B. Test R² Score — Higher is Better", fontweight="bold")
        ax2.set_xlabel("Coefficient of Determination (R²)")
        ax2.set_xlim(0, 1.08)
        ax2.grid(axis="x", alpha=0.25)
        for b in bars2:
            ax2.text(b.get_width() + 0.015, b.get_y() + b.get_height()/2, f"{b.get_width():.3f}", va="center", fontsize=8.5)

        from matplotlib.patches import Patch
        legend_handles = [Patch(color="#0284C7", label="Traditional ML"), Patch(color="#7C3AED", label="Deep Learning (PyTorch)")]
        fig.legend(handles=legend_handles, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.04), frameon=True, fontsize=9)

        plt.tight_layout(rect=[0, 0.04, 1, 1])
        p2 = FIG_DIR / "fig2_model_benchmark.png"
        fig.savefig(p2, bbox_inches="tight")
        plt.close(fig)
        paths["fig2"] = p2

    # Fig 3: Actual vs Forecast + Residual Diagnostics (Held-Out Test Split)
    if bench is not None and not bench.empty:
        feat_df = build_feature_matrix(bench)
        lr_dict = load_model("LinearRegression")
        rf_dict = load_model("RandomForest")
        if lr_dict and rf_dict:
            feats = lr_dict["features"]
            n = len(feat_df)
            n_test = int(n * 0.15)
            test_df = feat_df.iloc[-n_test:].copy()
            X_te = test_df[feats].values
            y_te = test_df["value"].values
            y_lr = lr_dict["model"].predict(X_te)
            y_rf = rf_dict["model"].predict(X_te)
            residuals = y_lr - y_te

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.3), dpi=300, gridspec_kw={"width_ratios": [2.2, 1]})
            tail = 140
            ax1.plot(test_df["datetime_utc"].iloc[-tail:], y_te[-tail:], color="#0F172A", linewidth=1.8, label="Observed Actual")
            ax1.plot(test_df["datetime_utc"].iloc[-tail:], y_lr[-tail:], color="#0284C7", linestyle="--", linewidth=1.6, label="LinearRegression Pred")
            ax1.plot(test_df["datetime_utc"].iloc[-tail:], y_rf[-tail:], color="#EA580C", linestyle=":", linewidth=1.5, label="RandomForest Pred")
            ax1.set_title("A. Chronological Held-Out Test Split Forecast (Last 140 Hours)", fontweight="bold")
            ax1.set_ylabel("PM2.5 (µg/m³)")
            ax1.tick_params(axis="x", rotation=25)
            ax1.grid(alpha=0.25)
            ax1.legend(fontsize=8.5)

            ax2.hist(residuals, bins=28, color="#0284C7", edgecolor="white", alpha=0.85)
            ax2.axvline(0, color="#DC2626", linestyle="--", linewidth=1.3)
            ax2.set_title(f"B. Test Residual Distribution\n(Mean={residuals.mean():.2f}, Std={residuals.std():.2f})", fontweight="bold")
            ax2.set_xlabel("Prediction Error (ŷ - y, µg/m³)")
            ax2.set_ylabel("Frequency")
            ax2.grid(alpha=0.25)

            plt.tight_layout()
            p3 = FIG_DIR / "fig3_forecast_residuals.png"
            fig.savefig(p3, bbox_inches="tight")
            plt.close(fig)
            paths["fig3"] = p3

            # Fig 4: SHAP Feature Attribution Bar Chart
            sv_res = shap_values(rf_dict, X_te, max_samples=min(120, len(X_te)))
            if sv_res is not None:
                sv, _ = sv_res
                shap_df = pd.DataFrame({
                    "feature": feats[:sv.shape[1]],
                    "mean_abs_shap": np.abs(sv).mean(axis=0),
                }).sort_values("mean_abs_shap", ascending=False).head(10)

                fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
                bars = ax.barh(shap_df["feature"], shap_df["mean_abs_shap"], color="#0D9488", edgecolor="#0F172A", linewidth=0.5)
                ax.invert_yaxis()
                ax.set_title("Explainable AI: Top-10 Mean |SHAP| Feature Attributions (RandomForest Test Set)", fontweight="bold")
                ax.set_xlabel("Mean |SHAP Value| (Impact on PM2.5 Prediction in µg/m³)")
                ax.grid(axis="x", alpha=0.25)
                for b in bars:
                    ax.text(b.get_width() + 0.3, b.get_y() + b.get_height()/2, f"{b.get_width():.2f}", va="center", fontsize=8.5)
                plt.tight_layout()
                p4 = FIG_DIR / "fig4_shap_importance.png"
                fig.savefig(p4, bbox_inches="tight")
                plt.close(fig)
                paths["fig4"] = p4

    # Fig 5: Live CPCB AQI Category Breakdown & WHO/NAAQS Breach Rates
    if live is not None and not live.empty:
        valid_live = live.dropna(subset=["value"]).copy()
        cats = [calculate_cpcb_aqi(v, "pm25").category for v in valid_live["value"]]
        valid_live["cpcb_category"] = cats
        cat_order = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
        cat_colors = ["#00B050", "#92D050", "#EAB308", "#F97316", "#EF4444", "#7E0023"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.3), dpi=300)

        counts = valid_live["cpcb_category"].value_counts().reindex(cat_order, fill_value=0)
        pcts = counts / counts.sum() * 100
        bars = ax1.bar(cat_order, pcts.values, color=cat_colors, edgecolor="#0F172A", linewidth=0.6)
        ax1.set_ylim(0, max(pcts.values) * 1.18)
        ax1.set_title("A. CPCB AQI Category Share Across Live Indian Stations (%)", fontweight="bold")
        ax1.set_ylabel("Share of Hourly Observations (%)")
        ax1.tick_params(axis="x", rotation=20)
        ax1.grid(axis="y", alpha=0.25)
        for b in bars:
            ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 0.6, f"{b.get_height():.1f}%", ha="center", fontsize=8.5)

        label_map = {
            "R K Puram, Delhi - DPCC": "Delhi\n(R K Puram)",
            "Talkatora District Industries Center, Lucknow - CPCB": "Lucknow\n(Talkatora)",
            "Zoo Park, Hyderabad - TSPCB": "Hyderabad\n(Zoo Park)",
        }
        stations = []
        who_rates = []
        naaqs_rates = []
        for s_name, grp in valid_live.groupby("location_name"):
            stations.append(label_map.get(s_name, s_name.split(",")[0]))
            who_rates.append((grp["value"] > 15.0).mean() * 100)
            naaqs_rates.append((grp["value"] > 60.0).mean() * 100)

        x = np.arange(len(stations))
        w = 0.35
        b1 = ax2.bar(x - w/2, who_rates, width=w, label="WHO 24h Breach (>15 µg/m³)", color="#0284C7")
        b2 = ax2.bar(x + w/2, naaqs_rates, width=w, label="Indian NAAQS Breach (>60 µg/m³)", color="#DC2626")
        ax2.set_xticks(x)
        ax2.set_xticklabels(stations)
        ax2.set_ylim(0, 126)
        ax2.set_title("B. Regulatory Threshold Exceedance Rate (%)", fontweight="bold")
        ax2.set_ylabel("Exceedance Percentage (%)")
        ax2.grid(axis="y", alpha=0.25)
        ax2.legend(loc="upper center", ncol=2, fontsize=7.8)
        for b in list(b1) + list(b2):
            ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 1.5, f"{b.get_height():.1f}%", ha="center", fontsize=8)

        plt.tight_layout()
        p5 = FIG_DIR / "fig5_aqi_exceedance.png"
        fig.savefig(p5, bbox_inches="tight")
        plt.close(fig)
        paths["fig5"] = p5

    return paths

if __name__ == "__main__":
    out = generate_all_figures()
    for k, v in out.items():
        print(f"Generated {k}: {v}")
