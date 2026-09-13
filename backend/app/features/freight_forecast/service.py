"""
Freight forecasting service.

Contract:
    - If a trained CatBoost model exists at models/catboost_freight_model.cbm,
      it is loaded via CatBoostRegressor.load_model() and used for prediction,
      via the recursive lag1/lag7/lag30 method (adapted from the training
      notebook), scoped to the specific vessel_type + source + destination
      route requested.
    - Historical data is ALWAYS the real dataset (see `_load_historical_dataframe`
      below) — nothing is synthesized. If no history exists at all for the
      requested route, a ValueError is raised so the API layer can return a
      clean 404/422 instead of fabricating numbers.
    - If the trained model file is missing/corrupt, OR the route has fewer than
      30 historical points (not enough for lag30), the service falls back to
      exponential smoothing computed on that SAME real historical series, and
      labels the result `is_fallback=True`, `model_used="Fallback: Exponential
      Smoothing"`.
    - The frontend/API must never claim a fallback result is an ML prediction.
    - Response SHAPE is unchanged from the previous version of this module —
      only the data source (real vs synthetic) and the model backend
      (CatBoost vs the old sklearn/joblib model) have changed.

NOTE ON `_load_historical_dataframe`:
    I don't know where your real freight history actually lives (a CSV, a
    DB table, a data warehouse query, etc.), so this defaults to reading a
    CSV at `data/freight_history.csv` with columns
    [date, vessel_type, source, destination, price]. Point
    HISTORICAL_DATA_PATH at your real file, or replace the body of
    `_load_historical_dataframe()` with your actual DB/query call — the rest
    of the module only depends on it returning a DataFrame with those columns.
"""

from __future__ import annotations

import math
from datetime import date as _date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import traceback

DATA_SOURCE_LABEL = "Synthetic"
PROJECT_ROOT = Path(__file__).resolve().parents[4]
MODELS_DIR = PROJECT_ROOT / "ml" / "model"
FREIGHT_MODEL_PATH = MODELS_DIR / "catboost_freight_model.cbm"

# Real historical freight dataset path for this project.
HISTORICAL_DATA_PATH = PROJECT_ROOT / "data" / "freight_history.csv"

HORIZONS = [7, 15, 30, 60, 90]

# Column order the model was trained on (matches the notebook: date features
# first, then the three lags), after dropping the raw "date" column itself.
FEATURE_ORDER = [
    "vessel_type", "source", "destination",
    "month", "weekday", "quarter", "day_of_year",
    "lag1", "lag7", "lag30",
]


def _load_historical_dataframe() -> pd.DataFrame:
    """
    Load the REAL historical freight dataset.

    Expected columns: date, vessel_type, source, destination, price.
    Replace this body with your actual data source if it isn't a CSV at
    HISTORICAL_DATA_PATH.
    """
    if not HISTORICAL_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Historical freight data not found at {HISTORICAL_DATA_PATH}. "
            "Update HISTORICAL_DATA_PATH or _load_historical_dataframe() to "
            "point at your real dataset."
        )
    df = pd.read_csv(HISTORICAL_DATA_PATH, parse_dates=["date"])
    return df


class FreightForecastModel:
    """Thin wrapper that hides whether we're using the trained CatBoost model or fallback."""

    def __init__(self) -> None:
        self._model = None
        self._is_loaded = False
        self._try_load()

    def _try_load(self) -> None:
        if FREIGHT_MODEL_PATH.exists():
            try:
                from catboost import CatBoostRegressor
                model = CatBoostRegressor()
                model.load_model(str(FREIGHT_MODEL_PATH))
                self._model = model
                self._is_loaded = True
            except Exception as e:
                print(f"[FreightForecastModel] load_model failed: {e!r}")
                traceback.print_exc()
                self._model = None
                self._is_loaded = False
        else:
            print(f"[FreightForecastModel] model file not found at {FREIGHT_MODEL_PATH}")

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def predict_recursive(
        self,
        route_history: pd.DataFrame,
        vessel_type: str,
        source: str,
        destination: str,
        start_date: str,
        horizon: int,
    ) -> Optional[pd.DataFrame]:
        """
        Recursive multi-day forecast using lag1/lag7/lag30 features, same logic
        as `predict_freight` in the training notebook. Returns None (caller
        should fall back) if there's no model or not enough route history.
        """
        if not self._is_loaded or self._model is None:
            return None
        if len(route_history) < 30:
            # Not enough history for lag30 -> trained model isn't usable here
            return None

        try:
            last_history = route_history.sort_values("date").iloc[-30:]
            lag1 = float(last_history.iloc[-1]["price"])
            lag7 = float(last_history.iloc[-7]["price"])
            lag30 = float(last_history.iloc[-30]["price"])

            future_dates = pd.date_range(start=start_date, periods=horizon, freq="D")
            preds = []
            for d in future_dates:
                row = {
                    "vessel_type": vessel_type,
                    "source": source,
                    "destination": destination,
                    "month": d.month,
                    "weekday": d.weekday(),
                    "quarter": d.quarter,
                    "day_of_year": d.dayofyear,
                    "lag1": lag1,
                    "lag7": lag7,
                    "lag30": lag30,
                }
                features = pd.DataFrame([row], columns=FEATURE_ORDER)
                pred = float(self._model.predict(features)[0])
                preds.append(pred)

                # shift lags forward for the next recursive step
                lag30 = lag7
                lag7 = lag1
                lag1 = pred

            return pd.DataFrame({"date": future_dates, "predicted_price": preds})
        except Exception as e:
            print(f"[predict_recursive] failed for route "
                  f"{vessel_type}/{source}/{destination}: {e!r}")
            traceback.print_exc()
            return None


_freight_model = FreightForecastModel()


def _load_route_history(vessel_type: str, source: str, destination: str) -> list[float]:
    """
    Return the REAL price history for this exact route, oldest -> newest.
    Raises ValueError if no data exists for the route — never fabricated.
    """
    df = _load_historical_dataframe()
    route = df[
        (df["vessel_type"] == vessel_type)
        & (df["source"] == source)
        & (df["destination"] == destination)
    ].sort_values("date")

    if route.empty:
        raise ValueError(
            f"No historical freight data found for vessel_type='{vessel_type}', "
            f"source='{source}', destination='{destination}'."
        )
    return route["price"].astype(float).tolist()


def _exponential_smoothing_forecast(history: list[float], horizon_days: int, alpha: float = 0.3) -> dict:
    """Fallback: exponential smoothing + volatility-based confidence band, run on REAL history."""
    level = history[0]
    for val in history[1:]:
        level = alpha * val + (1 - alpha) * level

    recent = history[-30:] if len(history) >= 30 else history
    volatility = float(np.std(recent))
    mean_recent = float(np.mean(recent))
    cv = volatility / mean_recent if mean_recent else 0

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


def generate_forecast(
    vessel_type: str,
    source: str,
    destination: str,
    forecast_horizon: int = 30,
    start_date: Optional[str] = None,
) -> dict:
    """
    Main entry point used by the API layer.

    vessel_type / source / destination now fully determine which real route's
    history is used (previously source/destination were ignored and history
    was synthesized). Returns a dict matching ForecastResponseSchema fields —
    same shape as before this change.
    """
    start_date = start_date or _date.today().isoformat()

    df = _load_historical_dataframe()
    route_history_df = df[
        (df["vessel_type"] == vessel_type)
        & (df["source"] == source)
        & (df["destination"] == destination)
    ].sort_values("date")

    history = _load_route_history(vessel_type, source, destination)
    current_rate = round(history[-1], 2)

    model_forecast_df = _freight_model.predict_recursive(
        route_history_df, vessel_type, source, destination, start_date, max(HORIZONS)
    )
    ### to check if catboosting actually predicting or not
    print(model_forecast_df)
    is_fallback = model_forecast_df is None

    horizons = []
    for h in HORIZONS:
        stat = _exponential_smoothing_forecast(history, h)
        if not is_fallback:
            expected = round(float(model_forecast_df.iloc[h - 1]["predicted_price"]), 2)
            band = stat["upper_bound"] - stat["expected_rate"]
            horizons.append({
                "days": h,
                "expected_rate": expected,
                "lower_bound": round(max(expected - band, 0), 2),
                "upper_bound": round(expected + band, 2),
            })
        else:
            horizons.append({
                "days": h,
                "expected_rate": stat["expected_rate"],
                "lower_bound": stat["lower_bound"],
                "upper_bound": stat["upper_bound"],
            })

    primary_horizon_stat = _exponential_smoothing_forecast(history, forecast_horizon)

    if is_fallback:
        forecast_rate = primary_horizon_stat["expected_rate"]
        model_used = "Fallback: Exponential Smoothing"
    else:
        forecast_rate = round(float(model_forecast_df.iloc[forecast_horizon - 1]["predicted_price"]), 2)
        model_used = "Trained Model: catboost_freight_model.cbm"

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