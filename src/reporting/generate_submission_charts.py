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

    paths["qu_logo"] = generate_qu_logo()
    paths["fig6_uml"] = generate_uml_dfd_diagram()
    return paths


def generate_qu_logo() -> Path:
    """Render high-DPI Quantum University Roorkee emblem & wordmark for cover pages."""
    from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

    fig, ax = plt.subplots(figsize=(4.4, 2.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.8)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Iconic magenta/purple QU square badge at top-right of 'Quantum'
    magenta = "#D81B60"
    purple = "#6A1B7A"
    charcoal = "#2D2D2D"

    ax.add_patch(FancyBboxPatch((4.95, 3.65), 1.45, 1.45, boxstyle="round,pad=0.05,rounding_size=0.08", facecolor=magenta, edgecolor="none"))
    ax.add_patch(Rectangle((5.22, 4.10), 0.90, 0.98, facecolor="white", edgecolor="none"))
    ax.add_patch(Rectangle((5.42, 4.30), 0.50, 0.78, facecolor=magenta, edgecolor="none"))
    ax.add_patch(Rectangle((5.61, 4.65), 0.14, 0.45, facecolor="white", edgecolor="none"))

    # Cleanly spaced Q + uantum wordmark
    ax.text(2.42, 2.68, "Q", fontsize=44, fontweight="bold", color=purple, ha="center", va="center", fontfamily="DejaVu Sans")
    ax.text(3.28, 2.54, "uantum", fontsize=30, fontweight="bold", color=charcoal, ha="left", va="center", fontfamily="DejaVu Sans")
    tail = Polygon([[2.35, 2.15], [2.95, 1.94], [3.55, 1.94], [2.78, 2.28]], closed=True, facecolor=magenta, edgecolor="none")
    ax.add_patch(tail)

    ax.text(5.40, 1.50, "UNIVERSITY", fontsize=17.5, fontweight="bold", fontstyle="italic", color=charcoal, ha="center", va="center", fontfamily="DejaVu Sans")
    ax.text(5.40, 0.92, "ROORKEE, INDIA", fontsize=10.5, fontweight="bold", color="#475569", ha="center", va="center", fontfamily="DejaVu Sans")

    out_path = FIG_DIR / "qu_logo.png"
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)
    return out_path


def generate_uml_dfd_diagram() -> Path:
    """Render 4-panel software design diagram: DFD, UML Class, Sequence & Control Flow."""
    from matplotlib.patches import FancyBboxPatch

    fig, axes = plt.subplots(2, 2, figsize=(12.4, 8.6), dpi=300)
    fig.patch.set_facecolor("white")

    def _box(ax, x, y, w, h, text, fc="#F8FAFC", ec="#0F172A", tc="#0F172A", fs=7.8, bold=False):
        patch = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=fc, edgecolor=ec, linewidth=1.1,
        )
        ax.add_patch(patch)
        ax.text(
            x + w / 2, y + h / 2, text,
            ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal",
            color=tc, family="sans-serif",
        )

    def _arrow(ax, x1, y1, x2, y2, label="", col="#334155"):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1, shrinkA=2, shrinkB=2),
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(
                mx, my + (0.14 if abs(y2 - y1) < 0.3 else 0.0),
                label, ha="center", va="center", fontsize=6.8, color="#334155",
                bbox=dict(fc="white", ec="none", pad=1.0),
            )

    # Panel A: Level-1 Data Flow Diagram (DFD)
    ax = axes[0, 0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("A. Level-1 Data Flow Diagram (DFD)", fontweight="bold", fontsize=10.5, pad=6)
    _box(ax, 0.3, 4.9, 2.2, 1.1, "OpenAQ API v3\nExternal Source", "#E0F2FE", "#0369A1", fs=7.5, bold=True)
    _box(ax, 3.6, 4.9, 2.7, 1.1, "1.0 Ingestion &\nValidation Engine", "#F1F5F9", "#0F172A", fs=7.5, bold=True)
    _box(ax, 7.2, 4.9, 2.4, 1.1, "Parquet Store\nraw/ & processed/", "#FEF3C7", "#B45309", fs=7.5, bold=True)
    _box(ax, 3.6, 2.6, 2.7, 1.1, "2.0 Feature Matrix\n& Dual AQI Calc", "#F1F5F9", "#0F172A", fs=7.5, bold=True)
    _box(ax, 7.2, 2.6, 2.4, 1.1, "Model Artifacts\n.pkl & .pt Files", "#EDE9FE", "#6D28D9", fs=7.5, bold=True)
    _box(ax, 3.6, 0.4, 2.7, 1.1, "3.0 ML/DL Forecast\n& SHAP Engine", "#DCFCE7", "#15803D", fs=7.5, bold=True)
    _box(ax, 0.3, 0.4, 2.2, 1.1, "End User &\nStreamlit 10-Page UI", "#E0F2FE", "#0369A1", fs=7.5, bold=True)
    _arrow(ax, 2.5, 5.45, 3.6, 5.45, "JSON")
    _arrow(ax, 6.3, 5.45, 7.2, 5.45, "Clean")
    _arrow(ax, 4.95, 4.9, 4.95, 3.7, "DF")
    _arrow(ax, 4.95, 2.6, 4.95, 1.5, "X, y")
    _arrow(ax, 6.3, 0.95, 8.4, 2.6, "Save")
    _arrow(ax, 3.6, 0.95, 2.5, 0.95, "Charts/AQI")
    _arrow(ax, 1.4, 1.5, 3.6, 3.1, "Queries")

    # Panel B: UML Class Diagram
    ax = axes[0, 1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("B. UML Class Architecture", fontweight="bold", fontsize=10.5, pad=6)
    _box(ax, 0.15, 4.3, 2.75, 2.2, "OpenAQClient\n----------------\n- _api_key, _base_url\n----------------\n+ get_locations()\n+ get_sensor_hours()", "#EFF6FF", "#1D4ED8", fs=7.1)
    _box(ax, 3.65, 4.3, 2.8, 2.2, "DataIngestion\n----------------\n- client: OpenAQClient\n----------------\n+ fetch_locations()\n+ fetch_measurements()", "#F8FAFC", "#0F172A", fs=7.1)
    _box(ax, 7.05, 4.3, 2.8, 2.2, "AQICalculator\n----------------\n- CPCB / EPA tables\n----------------\n+ compute_subindex()\n+ calculate_aqi()", "#F8FAFC", "#0F172A", fs=7.1)
    _box(ax, 0.45, 0.7, 4.15, 2.4, "MLTrainer / ModelSuite\n----------------\n- models: Linear..XGBoost\n- ratios: 70 / 15 / 15 split\n----------------\n+ train_models(df)\n+ predict(model_dict, df)", "#F5F3FF", "#6D28D9", fs=7.1)
    _box(ax, 5.2, 0.7, 4.5, 2.4, "DLForecaster (nn.Module)\n----------------\n- LSTM / GRU / TCN / Trans.\n- lookback=24, horizon=h\n----------------\n+ forward(x_seq)\n+ train_dl_model(series)", "#F0FDF4", "#15803D", fs=7.1)
    _arrow(ax, 2.9, 5.4, 3.65, 5.4, "uses")
    _arrow(ax, 5.05, 4.3, 2.6, 3.1, "clean df")
    _arrow(ax, 5.05, 4.3, 7.2, 3.1, "series")

    # Panel C: UML Sequence Diagram
    ax = axes[1, 0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("C. UML Sequence Diagram (Forecast Workflow)", fontweight="bold", fontsize=10.5, pad=6)
    actors = [(1.1, "User"), (3.3, "Streamlit UI"), (5.6, "Pipeline"), (8.1, "ML/DL/XAI")]
    for x0, lbl in actors:
        _box(ax, x0 - 0.85, 5.8, 1.7, 0.75, lbl, "#0F172A", "#0F172A", "white", fs=7.6, bold=True)
        ax.plot([x0, x0], [0.6, 5.8], linestyle="--", color="#94A3B8", linewidth=1.0)
    _arrow(ax, 1.1, 5.1, 3.3, 5.1, "1: Select Dataset/Country")
    _arrow(ax, 3.3, 4.3, 5.6, 4.3, "2: validate & clean(df)")
    _arrow(ax, 5.6, 3.5, 8.1, 3.5, "3: build_features() + fit()")
    _arrow(ax, 8.1, 2.6, 5.6, 2.6, "4: MAE/RMSE/R² + SHAP")
    _arrow(ax, 5.6, 1.8, 3.3, 1.8, "5: Plotly Figs + AQI")
    _arrow(ax, 3.3, 1.0, 1.1, 1.0, "6: PDF/HTML/ZIP Report")

    # Panel D: Control Flow & Use-Case Architecture
    ax = axes[1, 1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("D. System Control Flow & Use-Case Governance", fontweight="bold", fontsize=10.5, pad=6)
    _box(ax, 0.4, 5.4, 2.7, 0.95, "Start: app.py\nensure_ready()", "#E0F2FE", "#0369A1", fs=7.4, bold=True)
    _box(ax, 3.6, 5.4, 2.8, 0.95, "API Key Present?\nYes->Live | No->Seed", "#FEF3C7", "#B45309", fs=7.4, bold=True)
    _box(ax, 7.0, 5.4, 2.6, 0.95, "Parquet Store\n>= 2,157 Records", "#F1F5F9", "#0F172A", fs=7.4)
    _box(ax, 0.4, 3.1, 4.3, 1.4, "Use Cases: Explore & Audit\n• Global Data Explorer  • Spatial Hotspots\n• Pollution Analytics   • Health Risk Audit", "#F8FAFC", "#0F172A", fs=7.3)
    _box(ax, 5.2, 3.1, 4.4, 1.4, "Use Cases: Intelligence & Forecasting\n• CPCB/EPA AQI Engine  • ML/DL Studio\n• Model Benchmarking   • SHAP XAI", "#F5F3FF", "#6D28D9", fs=7.3)
    _box(ax, 2.3, 0.8, 5.4, 1.15, "Len >= 50? -> Chronological Split (70/15/15)\nExport Research PDF / HTML / PPTX / ZIP", "#DCFCE7", "#15803D", fs=7.5, bold=True)
    _arrow(ax, 3.1, 5.88, 3.6, 5.88)
    _arrow(ax, 6.4, 5.88, 7.0, 5.88)
    _arrow(ax, 4.9, 5.4, 2.6, 4.5)
    _arrow(ax, 5.1, 5.4, 7.3, 4.5)
    _arrow(ax, 2.6, 3.1, 4.2, 1.95)
    _arrow(ax, 7.3, 3.1, 5.8, 1.95)

    plt.tight_layout(pad=1.2)
    out_path = FIG_DIR / "fig6_uml_system_design.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path

if __name__ == "__main__":
    out = generate_all_figures()
    for k, v in out.items():
        print(f"Generated {k}: {v}")
