"""
Train the risk classification model.

Like train_vessel_model.py, this is a forward-looking script: the live
application currently uses the rule-based risk engine in
backend/services/risk_service.py. Once a labeled historical dataset of
(freight volatility, port congestion, vessel compatibility, market
indicators -> realized risk outcome) exists at
ml/data/risk_history.csv, train a classifier here and save it to
models/risk_model.pkl to have it picked up by a future model-aware
version of risk_service.py (apply the same load-or-fallback pattern used
in forecasting_service.py).

Usage:
    python -m ml.training.train_risk_model
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DATA_PATH = ROOT / "ml" / "data" / "risk_history.csv"
MODELS_DIR = ROOT / "models"
SAVED_MODELS_DIR = ROOT / "ml" / "saved_models"

FEATURE_COLS = [
    "freight_volatility_pct", "forecast_confidence", "port_congestion_score",
    "vessel_port_compat_score", "rate_change_pct",
]


def main():
    if not DATA_PATH.exists():
        print(f"[train_risk_model] No historical risk-outcome data found at {DATA_PATH}.")
        print("The rule-based engine in backend/services/risk_service.py remains authoritative "
              "until a real labeled dataset is collected. Nothing to train yet — exiting.")
        return

    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLS]
    y = df["risk_level"]  # LOW / MEDIUM / HIGH

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = GradientBoostingClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42)
    clf.fit(X_train_s, y_train)
    preds = clf.predict(X_test_s)

    print(classification_report(y_test, preds))

    MODELS_DIR.mkdir(exist_ok=True)
    SAVED_MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(clf, MODELS_DIR / "risk_model.pkl")
    joblib.dump(clf, SAVED_MODELS_DIR / "risk_model.pkl")
    print(f"Saved model to {MODELS_DIR / 'risk_model.pkl'}")


if __name__ == "__main__":
    main()
