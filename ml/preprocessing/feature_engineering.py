"""
Feature engineering for freight-rate time series.

Used by ml/training/train_freight_model.py. Kept separate from the backend
so the training pipeline can evolve independently of the serving code.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

VESSEL_TYPES=['Handysize','Supramax','Panamax','Capesize']
def add_lag_features(df: pd.DataFrame, col: str = "freight_rate", lags=(1, 7, 14, 30)) -> pd.DataFrame:
    df = df.copy()
    for lag in lags:
        df[f"lag_{lag}"] = df[col].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, col: str = "freight_rate", windows=(7, 14, 30)) -> pd.DataFrame:
    df = df.copy()
    for w in windows:
        df[f"rolling_mean_{w}"] = df[col].shift(1).rolling(w).mean()
        df[f"rolling_std_{w}"] = df[col].shift(1).rolling(w).std()
    return df


def add_momentum_features(df: pd.DataFrame, col: str = "freight_rate") -> pd.DataFrame:
    df = df.copy()
    df["momentum_7"] = df[col].shift(1) - df[col].shift(8)
    df["momentum_30"] = df[col].shift(1) - df[col].shift(31)
    return df


def add_calendar_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    df = df.copy()
    dt = pd.to_datetime(df[date_col])
    df["day_of_week"] = dt.dt.dayofweek
    df["month"] = dt.dt.month
    df["quarter"] = dt.dt.quarter
    df["season"] = (dt.dt.month % 12 + 3) // 3  # 1=winter .. 4=autumn (approx, N. hemisphere)
    return df


# Canonical feature column order — shared by the training pipeline (this file)
# and the serving code (backend/services/forecasting_service.py) so a model
# trained here can actually be loaded and called at inference time. If you
# change this list, retrain the model — the serving code builds features in
# this exact order via `build_inference_features()` below.
FEATURE_COLS = [
    "lag_1", "lag_7", "lag_14", "lag_30",
    "rolling_mean_7", "rolling_std_7",
    "rolling_mean_14", "rolling_std_14",
    "rolling_mean_30", "rolling_std_30",
    "momentum_7", "momentum_30",
    "day_of_week", "month", "quarter", "season",
]


def build_feature_matrix(df: pd.DataFrame, target_col: str = "freight_rate") -> tuple[pd.DataFrame, pd.Series]:
    """
    Full feature pipeline. Expects df sorted chronologically with columns:
    date, freight_rate, vessel_type (categorical, already one-hot or label-encoded upstream).
    Drops rows with NaN introduced by lag/rolling windows (no leakage — all
    features only look backward from shift(1) onward).
    """
    df = add_lag_features(df, target_col)
    df = add_rolling_features(df, target_col)
    df = add_momentum_features(df, target_col)
    df = add_calendar_features(df)

    df = df.dropna(subset=FEATURE_COLS + [target_col])
    return df[FEATURE_COLS], df[target_col]


def build_inference_features(history: list[float],vessel_type:str, as_of_date=None) -> list[float]:
    """
    Build a single feature row for prediction "as of" the latest point in
    `history`, in the exact column order of FEATURE_COLS. Used by
    backend/services/forecasting_service.py so training and serving stay in
    sync — change this alongside FEATURE_COLS/build_feature_matrix.
    """
    s = pd.Series(history)
    as_of_date = as_of_date or pd.Timestamp.today()

    def _roll_mean(w):
        return float(s.tail(w).mean())

    def _roll_std(w):
        return float(s.tail(w).std()) if len(s) >= 2 else 0.0

    row = {
        "lag_1": s.iloc[-1],
        "lag_7": s.iloc[-7],
        "lag_14": s.iloc[-14],
        "lag_30": s.iloc[-30],
        "rolling_mean_7": _roll_mean(7),
        "rolling_std_7": _roll_std(7),
        "rolling_mean_14": _roll_mean(14),
        "rolling_std_14": _roll_std(14),
        "rolling_mean_30": _roll_mean(30),
        "rolling_std_30": _roll_std(30),
        "momentum_7": s.iloc[-1] - s.iloc[-8],
        "momentum_30": s.iloc[-1] - s.iloc[-31],
        "day_of_week": as_of_date.dayofweek,
        "month": as_of_date.month,
        "quarter": as_of_date.quarter,
        "season": (as_of_date.month % 12 + 3) // 3,
    }
    for vt in VESSEL_TYPES:
        row[f'vt_{vt.lower()}'] =1 if vt==vessel_type else 0
    return [row[c] for c in FEATURE_COLS]


def chronological_split(df: pd.DataFrame, train_frac: float = 0.7, val_frac: float = 0.15):
    """Chronological (never random) train/val/test split — avoids time-series leakage."""
    n = len(df)
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]
