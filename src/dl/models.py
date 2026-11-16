"""
AeroSense AI — Deep Learning Models (PyTorch)
LSTM, GRU, TCN, and Transformer architectures for air quality forecasting.
"""
from __future__ import annotations

import logging
from typing import Optional

import torch
import torch.nn as nn

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LSTM
# ---------------------------------------------------------------------------
class LSTMForecaster(nn.Module):
    """Stacked LSTM for sequence-to-sequence pollution forecasting."""

    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = 1,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0.0,
        )
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


# ---------------------------------------------------------------------------
# GRU
# ---------------------------------------------------------------------------
class GRUForecaster(nn.Module):
    """Stacked GRU for sequence-to-sequence pollution forecasting."""

    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,
        num_layers: int = 2,
        output_size: int = 1,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        self.gru = nn.GRU(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0.0,
        )
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.gru(x)
        return self.fc(out[:, -1, :])


# ---------------------------------------------------------------------------
# TCN — Temporal Convolutional Network
# ---------------------------------------------------------------------------
class _CausalConv1d(nn.Module):
    """Causal dilated 1-D convolution with optional residual connection."""

    def __init__(self, in_ch: int, out_ch: int, kernel: int, dilation: int) -> None:
        super().__init__()
        self.padding = (kernel - 1) * dilation
        self.conv = nn.Conv1d(in_ch, out_ch, kernel,
                              padding=self.padding, dilation=dilation)
        self.chomp = lambda x: x[:, :, : -self.padding] if self.padding else x
        self.relu  = nn.ReLU()
        self.bn    = nn.BatchNorm1d(out_ch)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.bn(self.relu(self.chomp(self.conv(x))))


class TCNForecaster(nn.Module):
    """Temporal Convolutional Network for time-series forecasting."""

    def __init__(
        self,
        input_size: int = 1,
        num_channels: int = 32,
        num_levels: int = 4,
        kernel_size: int = 3,
        output_size: int = 1,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        layers = []
        for i in range(num_levels):
            dil = 2 ** i
            in_ch  = input_size if i == 0 else num_channels
            layers.append(_CausalConv1d(in_ch, num_channels, kernel_size, dil))
            layers.append(nn.Dropout(dropout))
        self.network = nn.Sequential(*layers)
        self.fc = nn.Linear(num_channels, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq, features) → (batch, features, seq)
        x = x.permute(0, 2, 1)
        out = self.network(x)
        return self.fc(out[:, :, -1])


# ---------------------------------------------------------------------------
# Transformer
# ---------------------------------------------------------------------------
class TransformerForecaster(nn.Module):
    """Encoder-only Transformer for time-series forecasting."""

    def __init__(
        self,
        input_size: int = 1,
        d_model: int = 64,
        nhead: int = 4,
        num_encoder_layers: int = 2,
        dim_feedforward: int = 128,
        output_size: int = 1,
        dropout: float = 0.1,
        max_seq_len: int = 512,
    ) -> None:
        super().__init__()
        self.input_proj = nn.Linear(input_size, d_model)
        self.pos_emb    = nn.Embedding(max_seq_len, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_feedforward, dropout, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_encoder_layers)
        self.fc      = nn.Linear(d_model, output_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq, features)
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0)
        x = self.input_proj(x) + self.pos_emb(positions)
        enc = self.encoder(x)
        return self.fc(enc[:, -1, :])


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------
MODEL_REGISTRY = {
    "LSTM": LSTMForecaster,
    "GRU":  GRUForecaster,
    "TCN":  TCNForecaster,
    "Transformer": TransformerForecaster,
}


def build_model(
    name: str,
    input_size: int = 1,
    output_size: int = 1,
    **kwargs,
) -> nn.Module:
    cls = MODEL_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown DL model: {name}. Choose from {list(MODEL_REGISTRY)}")
    return cls(input_size=input_size, output_size=output_size, **kwargs)
