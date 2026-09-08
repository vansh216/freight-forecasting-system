"""
Freight forecasting service.

Contract:
    - If a trained model exists at models/freight_forecasting_model.pkl (+ scaler),
      it is loaded via joblib and used for prediction.
    - If it does not exist (fresh clone, before ml/training has been run),
      the service transparently falls back to a statistical method
      (exponential smoothing over a synthetic/demo historical series) and
      labels the result `is_fallback=True`, `model_used="Fallback: Exponential Smoothing"`.
    - The frontend/API must never claim a fallback result is an ML prediction.

This keeps the interface stable: swap in a real trained model later without
touching the API or frontend contract.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import numpy as np

from data.reference_data import BASE_FREIGHT_RATES, DATA_SOURCE_LABEL
from ml.preprocessing.feature_engineering import build_inference_features

MODELS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "ml" / "model"
# backend\app\features\freight_forecast\service.py
FREIGHT_MODEL_PATH = MODELS_DIR / "freight_forecasting_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

HORIZONS = [7, 15, 30, 60, 90]


class FreightForecastModel:
    """Thin wrapper that hides whether we're using a trained model or fallback."""

    def __init__(self) -> None:
        self._model = None
        self._scaler = None
        self._is_loaded = False
        self._try_load()

    def _try_load(self) -> None:
        if FREIGHT_MODEL_PATH.exists():
            try:
                import joblib
                self._model = joblib.load(FREIGHT_MODEL_PATH)
                if SCALER_PATH.exists():
                    self._scaler = joblib.load(SCALER_PATH)
                self._is_loaded = True
            except Exception:
                # Corrupt/incompatible model file -> fall back, never crash the app
                self._model = None
                self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def predict(self, history: list[float], vessel_type) -> Optional[dict]:
        """Return None if no trained model is available (caller should fall back)."""
        if not self._is_loaded or self._model is None:
            return None
        try:
            import pandas as pd
            from ml.preprocessing.feature_engineering import FEATURE_COLS
            row = build_inference_features(history,vessel_type)
            x = pd.DataFrame([row], columns=FEATURE_COLS)
            if self._scaler is not None:
                x = self._scaler.transform(x)
            pred = float(self._model.predict(x)[0])
            return {"predicted_rate": pred}
        except Exception:
            return None


_freight_model = FreightForecastModel()


def _synthetic_history(vessel_type: str, days: int = 180, seed: Optional[int] = None) -> list[float]:
    """Generate a plausible demo freight-rate history (random walk + seasonality)."""
    base = BASE_FREIGHT_RATES.get(vessel_type, 20.0)
    rng = random.Random(seed or hash(vessel_type) % (2**31))
    series = [base]
    for day in range(1, days):
        seasonal = 0.6 * math.sin(2 * math.pi * day / 90)
        noise = rng.gauss(0, base * 0.015)
        drift = rng.uniform(-0.02, 0.02)
        next_val = series[-1] * (1 + drift * 0.02) + seasonal * 0.05 + noise
        series.append(max(next_val, base * 0.4))
    return series


def _exponential_smoothing_forecast(history: list[float], horizon_days: int, alpha: float = 0.3) -> dict:
    """Simple/robust fallback: exponential smoothing + volatility-based confidence band."""
    level = history[0]
    for val in history[1:]:
        level = alpha * val + (1 - alpha) * level

    recent = history[-30:] if len(history) >= 30 else history
    volatility = float(np.std(recent))
    mean_recent = float(np.mean(recent))
    cv = volatility / mean_recent if mean_recent else 0

    # slight trend estimate from last 30 vs previous 30
    if len(history) >= 60:
        trend_slope = (np.mean(history[-30:]) - np.mean(history[-60:-30])) / 30
    else:
        trend_slope = 0.0

    forecast_rate = level + trend_slope * horizon_days
    band = volatility * math.sqrt(horizon_days / 7.0) * 1.28  # ~80% band, widens with horizon

    if cv < 0.03:
        vol_label = "LOW"
    elif cv < 0.07:
        vol_label = "MEDIUM"
    else:
        vol_label = "HIGH"

    confidence = max(0.35, min(0.9, 1 - cv * 4 - (horizon_days / 500)))

    return {
        "expected_rate": round(forecast_rate, 2),
        "lower_bound": round(max(forecast_rate - band, 0), 2),
        "upper_bound": round(forecast_rate + band, 2),
        "volatility_label": vol_label,
        "confidence": round(confidence, 2),
        "current_level": round(history[-1], 2),
    }


def generate_forecast(vessel_type: str, forecast_horizon: int = 30) -> dict:
    """
    Main entry point used by the API layer.

    Returns a dict matching ForecastResponseSchema fields (minus request-specific ones).
    """
    history = _synthetic_history(vessel_type)
    current_rate = round(history[-1], 2)

    # Attempt trained-model prediction first (feature schema shared with ml/training via
    # ml/preprocessing/feature_engineering.py so a trained model is actually usable here)
    model_pred = _freight_model.predict(history,vessel_type)

    horizons = []
    for h in HORIZONS:
        stat = _exponential_smoothing_forecast(history, h)
        horizons.append({
            "days": h,
            "expected_rate": stat["expected_rate"],
            "lower_bound": stat["lower_bound"],
            "upper_bound": stat["upper_bound"],
        })

    primary_horizon_stat = _exponential_smoothing_forecast(history, forecast_horizon)

    is_fallback = model_pred is None
    if is_fallback:
        forecast_rate = primary_horizon_stat["expected_rate"]
        model_used = "Fallback: Exponential Smoothing (Demo Data)"
    else:
     forecast_rate = round(model_pred["predicted_rate"], 2)
     model_used = "Trained Model: freight_forecasting_model.pkl"

    change_pct = ((forecast_rate - current_rate) / current_rate * 100) if current_rate else 0
    if change_pct > 2:
        trend = "increasing"
    elif change_pct < -2:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "vessel_type": vessel_type,
        "current_rate": current_rate,
        "forecast_rate": forecast_rate,
        "trend": trend,
        "confidence": primary_horizon_stat["confidence"],
        "volatility": primary_horizon_stat["volatility_label"],
        "model_used": model_used,
        "is_fallback": is_fallback,
        "horizons": horizons,
        "data_source_label": DATA_SOURCE_LABEL,
        "change_pct": round(change_pct, 2),
        "historical_average": round(float(np.mean(history)), 2),
    }


def market_entry_signal(forecast: dict, contract_duration_months: int = 6, requirement_days: int = 30) -> dict:
    """Decision engine: BOOK NOW / WAIT / PARTIALLY BOOK / LOCK-IN CONTRACT / MONITOR MARKET."""
    current = forecast["current_rate"]
    forecasted = forecast["forecast_rate"]
    change_pct = forecast["change_pct"]
    confidence = forecast["confidence"]
    volatility = forecast["volatility"]
    hist_avg = forecast["historical_average"]

    reasons = []
    vs_hist_pct = ((current - hist_avg) / hist_avg * 100) if hist_avg else 0

    if change_pct <= -8 and confidence >= 0.55:
        signal = "WAIT"
        reasons.append(f"Forecast indicates a potential {abs(change_pct):.1f}% decline in freight rates over the forecast horizon.")
    elif change_pct >= 8 and confidence >= 0.5:
        signal = "BOOK NOW"
        reasons.append(f"Forecast indicates increasing freight rates (+{change_pct:.1f}%) and {volatility.lower()} market volatility.")
    elif volatility == "HIGH" and confidence < 0.55:
        signal = "MONITOR MARKET"
        reasons.append("Forecast confidence is low and volatility is high — recommend close monitoring before committing.")
    elif contract_duration_months >= 6 and abs(change_pct) < 8:
        signal = "LOCK-IN CONTRACT"
        reasons.append("Rates are expected to stay range-bound; a medium-term contract locks in cost certainty.")
    elif -8 < change_pct < 0:
        signal = "PARTIALLY BOOK"
        reasons.append(f"Mild softening ({change_pct:.1f}%) expected — partial booking now hedges against a rebound while capturing further downside.")
    else:
        signal = "MONITOR MARKET"
        reasons.append("No strong directional signal detected; continue monitoring the market.")

    if abs(vs_hist_pct) >= 5:
        direction = "below" if vs_hist_pct < 0 else "above"
        reasons.append(f"Current rate is {abs(vs_hist_pct):.1f}% {direction} the historical average.")
    reasons.append(f"Forecast confidence: {confidence*100:.0f}%; volatility: {volatility}.")
    if requirement_days <= 15:
        reasons.append(f"Cargo requirement begins in {requirement_days} days, limiting the window to wait for better rates.")

    return {"signal": signal, "reasons": reasons}
