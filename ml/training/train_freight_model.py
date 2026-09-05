"""
Train the freight forecasting model.

Usage:
    python -m ml.training.train_freight_model

Behaviour:
    - If ml/data/freight_rates_history.csv exists, trains on it.
    - Otherwise generates a synthetic demo dataset (clearly labeled) so the
      pipeline is runnable end-to-end before real historical data exists.
    - Splits CHRONOLOGICALLY (never randomly) into train/val/test.
    - Trains a naive baseline, a moving-average baseline, and a
      RandomForest / GradientBoosting regressor; picks the best on
      validation MAPE.
    - Saves the winning model + scaler to models/freight_forecasting_model.pkl
      and models/scaler.pkl so backend/services/forecasting_service.py can
      load it automatically (no code changes needed there).
"""

from __future__ import annotations

import math
import os
import random
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from ml.preprocessing.feature_engineering import build_feature_matrix, chronological_split  # noqa: E402
from ml.evaluation.evaluate import evaluate_all  # noqa: E402

DATA_PATH = ROOT / "ml" / "data" / "freight_rates_history.csv"
MODELS_DIR = ROOT / "models"
SAVED_MODELS_DIR = ROOT / "ml" / "saved_models"


def load_or_generate_data(vessel_type: str = "Supramax", days: int = 900, seed: int = 42) -> pd.DataFrame:
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH, parse_dates=["date"])
        return df[df["vessel_type"] == vessel_type].sort_values("date").reset_index(drop=True)

    print(f"[train_freight_model] No historical data found at {DATA_PATH} — generating DEMO/SIMULATED dataset.")
    rng = random.Random(seed)
    base = 21.0
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days, freq="D")
    rates = [base]
    for day in range(1, days):
        seasonal = 0.6 * math.sin(2 * math.pi * day / 90)
        noise = rng.gauss(0, base * 0.015)
        drift = rng.uniform(-0.02, 0.02)
        next_val = rates[-1] * (1 + drift * 0.02) + seasonal * 0.05 + noise
        rates.append(max(next_val, base * 0.4))

    return pd.DataFrame({"date": dates, "vessel_type": vessel_type, "freight_rate": rates})


def naive_forecast(y_val: pd.Series, y_train_last: float) -> np.ndarray:
    return np.full(len(y_val), y_train_last)


def moving_average_forecast(history: pd.Series, y_val: pd.Series, window: int = 7) -> np.ndarray:
    ma = history.tail(window).mean()
    return np.full(len(y_val), ma)


def main():
    MODELS_DIR.mkdir(exist_ok=True)
    SAVED_MODELS_DIR.mkdir(exist_ok=True)

    df = load_or_generate_data()
    X, y = build_feature_matrix(df, target_col="freight_rate")

    X_train, X_val, X_test = chronological_split(X)
    y_train, y_val, y_test = chronological_split(y)

    print(f"Train/Val/Test sizes: {len(X_train)}/{len(X_val)}/{len(X_test)}")

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    results = {}

    # --- Baselines ---
    results["naive"] = evaluate_all(y_val, naive_forecast(y_val, y_train.iloc[-1]))
    results["moving_average"] = evaluate_all(
        y_val, moving_average_forecast(pd.concat([y_train]), y_val, window=7)
    )

    # --- ML models ---
    rf = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42)
    rf.fit(X_train_s, y_train)
    results["random_forest"] = evaluate_all(y_val, rf.predict(X_val_s))

    gbr = GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42)
    gbr.fit(X_train_s, y_train)
    results["gradient_boosting"] = evaluate_all(y_val, gbr.predict(X_val_s))

    print("\nValidation metrics (lower MAPE is better):")
    for name, metrics in results.items():
        print(f"  {name:18s} {metrics}")

    ml_candidates = {"random_forest": rf, "gradient_boosting": gbr}
    best_name = min(ml_candidates, key=lambda n: results[n]["MAPE"])
    best_model = ml_candidates[best_name]

    baseline_best_mape = min(results["naive"]["MAPE"], results["moving_average"]["MAPE"])
    if results[best_name]["MAPE"] >= baseline_best_mape:
        print(f"\n[train_freight_model] ML model ({best_name}) did not beat the baseline on this "
              f"synthetic dataset — this is expected with limited/synthetic history. "
              f"Re-run against real historical data before relying on the ML model in production.")

    test_metrics = evaluate_all(y_test, best_model.predict(X_test_s))
    print(f"\nBest model: {best_name}")
    print(f"Test metrics: {test_metrics}")

    joblib.dump(best_model, MODELS_DIR / "freight_forecasting_model.pkl")
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    joblib.dump(best_model, SAVED_MODELS_DIR / f"freight_model_{best_name}.pkl")
    print(f"\nSaved best model to {MODELS_DIR / 'freight_forecasting_model.pkl'}")


if __name__ == "__main__":
    main()
