from __future__ import annotations

from fastapi import APIRouter, Body

from backend.app.features.freight_forecast.schema import ForecastRequestSchema
from backend.app.features.freight_forecast.service import generate_forecast
from backend.app.features.vessel_recomendation.service import rank_vessels
from backend.app.services.risk_service import full_risk_analysis
from backend.app.features.utils.validation import validate_origin, validate_destination, validate_cargo_quantity

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.post("/analyze")
def risk_analyze(payload: ForecastRequestSchema):
    validate_origin(payload.origin)
    validate_destination(payload.destination)
    validate_cargo_quantity(payload.cargo_quantity)

    vessel_type = payload.vessel_type if payload.vessel_type != "automatic" else "Supramax"
    forecast = generate_forecast(vessel_type, payload.forecast_horizon)

    ranked = rank_vessels(payload.origin, payload.destination, payload.cargo_type, payload.cargo_quantity)
    best_candidate = next((c for c in ranked if c["feasible"]), ranked[0] if ranked else None)

    return full_risk_analysis(payload.destination, payload.cargo_type, forecast, best_candidate)
