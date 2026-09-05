# ML Data

Place real historical CSVs here to switch the training pipeline off demo/synthetic data:

- `freight_rates_history.csv` — columns: date, vessel_type, freight_rate (+ optional market/port features)
- `vessel_fixtures_history.csv` — historical fixture outcomes for vessel-model training
- `risk_history.csv` — labeled historical risk outcomes for risk-model training

Until these exist, `ml/training/*.py` either generates a clearly-labeled synthetic
dataset (freight model) or exits without training (vessel/risk models, which
still rely on the rule-based engines in `backend/services/`).
