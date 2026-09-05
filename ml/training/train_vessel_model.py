"""
Train the vessel optimization model.

The live application currently uses a rule-based feasibility + scoring
engine (backend/services/vessel_service.py) because no historical
fixture-outcome dataset exists yet. This script is the intended future
replacement: once a dataset of (cargo, route, vessel_type, port
constraints -> actual chosen vessel / voyage outcome) is available at
ml/data/vessel_fixtures_history.csv, train a classifier here and it will
be picked up automatically once saved as
models/vessel_optimization_model.pkl (see backend fallback pattern in
forecasting_service.py — apply the same load-or-fallback pattern for this
model when it's integrated).

Usage:
    python -m ml.training.train_vessel_model
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DATA_PATH = ROOT / "ml" / "data" / "vessel_fixtures_history.csv"
MODELS_DIR = ROOT / "models"
SAVED_MODELS_DIR = ROOT / "ml" / "saved_models"

FEATURE_COLS = [
    "cargo_quantity", "distance_nm", "vessel_dwt", "vessel_draft",
    "port_max_draft", "port_max_dwt", "port_congestion_score", "freight_rate",
]


def main():
    if not DATA_PATH.exists():
        print(f"[train_vessel_model] No historical fixture data found at {DATA_PATH}.")
        print("The rule-based engine in backend/services/vessel_service.py remains authoritative "
              "until a real fixture-outcome dataset is collected. Nothing to train yet — exiting.")
        return

    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLS]
    y = df["chosen_vessel_type"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    clf = RandomForestClassifier(n_estimators=300, max_depth=10, random_state=42)
    clf.fit(X_train_s, y_train)
    preds = clf.predict(X_test_s)

    print(f"Accuracy: {accuracy_score(y_test, preds):.4f}")
    print(f"F1 (weighted): {f1_score(y_test, preds, average='weighted'):.4f}")

    MODELS_DIR.mkdir(exist_ok=True)
    SAVED_MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(clf, MODELS_DIR / "vessel_optimization_model.pkl")
    joblib.dump(clf, SAVED_MODELS_DIR / "vessel_optimization_model.pkl")
    print(f"Saved model to {MODELS_DIR / 'vessel_optimization_model.pkl'}")


if __name__ == "__main__":
    main()
