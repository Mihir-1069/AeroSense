"""
AeroSense AI — Deep Learning Training Pipeline
Training loop with early stopping, LR scheduling, checkpointing.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader, TensorDataset

from src.config import settings
from src.dl.models import build_model
from src.features.sequence_builder import (
    build_sequences,
    chronological_split,
    fit_scaler,
)

log = logging.getLogger(__name__)

torch.manual_seed(settings.DL_RANDOM_SEED)
np.random.seed(settings.DL_RANDOM_SEED)

def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def _make_loader(X: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    dataset = TensorDataset(
        torch.tensor(X, dtype=torch.float32),
        torch.tensor(y, dtype=torch.float32),
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

def train_dl_model(
    series: np.ndarray,
    model_name: str = "LSTM",
    lookback: int = settings.DL_LOOKBACK_DEFAULT,
    horizon: int = settings.DL_FORECAST_DEFAULT,
    epochs: int = settings.DL_MAX_EPOCHS,
    batch_size: int = settings.DL_BATCH_SIZE,
    lr: float = settings.DL_LEARNING_RATE,
    patience: int = settings.DL_EARLY_STOP_PATIENCE,
    save_dir: Optional[Path] = None,
) -> Dict:
    """
    Train a DL model on a univariate time series.

    Args:
        series: 1-D numpy array of observations (sorted, regularly spaced).
        model_name: One of LSTM, GRU, TCN, Transformer.
        lookback: Input sequence length.
        horizon: Forecast horizon.

    Returns:
        dict with model, scaler, history, and evaluation metrics.
    """
    save_dir = save_dir or settings.DL_MODELS_DIR
    device = get_device()
    log.info("Training %s on %s (lookback=%d, horizon=%d).", model_name, device, lookback, horizon)

    # Scale on train portion only
    n = len(series)
    n_train = int(n * settings.TRAIN_RATIO)
    train_series = series[:n_train]
    scaled_train, scaler = fit_scaler(train_series)
    scaled_all = scaler.transform(series.reshape(-1, 1)).flatten().astype(np.float32)

    # Build sequences
    X, y = build_sequences(
        series=type("S", (), {"values": scaled_all})(),  # duck-type for reuse
        lookback=lookback, horizon=horizon,
    )
    # Workaround: build_sequences expects pd.Series-like; use directly
    values = scaled_all
    Xl, yl = [], []
    for i in range(len(values) - lookback - horizon + 1):
        Xl.append(values[i : i + lookback])
        yl.append(values[i + lookback : i + lookback + horizon])
    X = np.array(Xl, dtype=np.float32).reshape(-1, lookback, 1)
    y = np.array(yl, dtype=np.float32)

    if len(X) < 20:
        raise ValueError(
            f"Insufficient data for DL training: only {len(X)} sequences. "
            "Need at least 20. Collect more historical data."
        )

    (X_tr, y_tr), (X_vl, y_vl), (X_te, y_te) = chronological_split(
        X, y, settings.TRAIN_RATIO, settings.VAL_RATIO
    )

    train_loader = _make_loader(X_tr, y_tr, batch_size, shuffle=False)
    val_loader   = _make_loader(X_vl, y_vl, batch_size, shuffle=False)

    model = build_model(model_name, input_size=1, output_size=horizon).to(device)
    optimizer  = Adam(model.parameters(), lr=lr)
    scheduler  = ReduceLROnPlateau(optimizer, patience=patience // 2, factor=0.5)
    criterion  = nn.MSELoss()

    history = {"train_loss": [], "val_loss": []}
    best_val, best_state, no_improve = float("inf"), None, 0

    t0 = time.time()
    for epoch in range(1, epochs + 1):
        # Train
        model.train()
        train_losses = []
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_losses.append(loss.item())

        # Validate
        model.eval()
        val_losses = []
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                val_losses.append(criterion(model(xb), yb).item())

        tl = float(np.mean(train_losses))
        vl = float(np.mean(val_losses)) if val_losses else float("inf")
        history["train_loss"].append(tl)
        history["val_loss"].append(vl)
        scheduler.step(vl)

        if vl < best_val:
            best_val = vl
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
        else:
            no_improve += 1

        if epoch % 10 == 0:
            log.info("Epoch %3d | train=%.4f | val=%.4f", epoch, tl, vl)

        if no_improve >= patience:
            log.info("Early stopping at epoch %d.", epoch)
            break

    train_time = round(time.time() - t0, 1)
    if best_state:
        model.load_state_dict(best_state)

    # Test evaluation
    model.eval()
    with torch.no_grad():
        X_te_t = torch.tensor(X_te, dtype=torch.float32).to(device)
        preds   = model(X_te_t).cpu().numpy()

    preds_inv  = scaler.inverse_transform(preds.reshape(-1, 1)).flatten()
    actual_inv = scaler.inverse_transform(y_te.reshape(-1, 1)).flatten()
    mae  = float(np.mean(np.abs(preds_inv - actual_inv)))
    rmse = float(np.sqrt(np.mean((preds_inv - actual_inv) ** 2)))
    ss_res = float(np.sum((actual_inv - preds_inv) ** 2))
    ss_tot = float(np.sum((actual_inv - np.mean(actual_inv)) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    # Save checkpoint
    ckpt_path = save_dir / f"{model_name}_lookback{lookback}_h{horizon}.pt"
    torch.save({
        "model_state": best_state or model.state_dict(),
        "model_name": model_name,
        "lookback": lookback,
        "horizon": horizon,
        "scaler": scaler,
        "history": history,
        "metrics": {"MAE": round(mae, 3), "RMSE": round(rmse, 3), "R2": round(r2, 3)},
    }, ckpt_path)
    log.info(
        "%s trained in %.1fs | test MAE=%.3f RMSE=%.3f R²=%.3f | saved → %s",
        model_name, train_time, mae, rmse, r2, ckpt_path.name,
    )

    return {
        "model": model,
        "scaler": scaler,
        "history": history,
        "metrics": {"MAE": round(mae, 3), "RMSE": round(rmse, 3), "R2": round(r2, 3)},
        "train_time_s": train_time,
        "checkpoint": str(ckpt_path),
        "device": str(device),
    }

def load_dl_model(ckpt_path: Path, model_name: Optional[str] = None) -> Dict:
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    name  = model_name or ckpt["model_name"]
    lb    = ckpt["lookback"]
    h     = ckpt["horizon"]
    model = build_model(name, input_size=1, output_size=h)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return {"model": model, "scaler": ckpt["scaler"],
            "lookback": lb, "horizon": h, "metrics": ckpt.get("metrics", {})}

def predict_dl(
    model_dict: Dict,
    recent_values: np.ndarray,
) -> np.ndarray:
    """Run inference given the most recent observations."""
    model  = model_dict["model"]
    scaler = model_dict["scaler"]
    lb     = model_dict["lookback"]

    if len(recent_values) < lb:
        raise ValueError(f"Need at least {lb} observations; got {len(recent_values)}.")

    vals = recent_values[-lb:]
    scaled = scaler.transform(vals.reshape(-1, 1)).flatten().astype(np.float32)
    X = torch.tensor(scaled.reshape(1, lb, 1), dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        pred_scaled = model(X).numpy().flatten()
    return scaler.inverse_transform(pred_scaled.reshape(-1, 1)).flatten()
