from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db

from backend.app.core import crud
from backend.app.features.freight_forecast.schema import ForecastRequestSchema
from backend.app.features.freight_forecast.service import generate_forecast, market_entry_signal
from backend.app.features.utils.validation import validate_origin, validate_destination, validate_vessel_type, validate_cargo_quantity

router = APIRouter()


@router.post("/forecast")
def forecast(payload: ForecastRequestSchema, db: Session = Depends(get_db)):
    validate_origin(payload.origin)
    validate_destination(payload.destination)
    validate_vessel_type(payload.vessel_type)
    validate_cargo_quantity(payload.cargo_quantity)

    vessel_type = payload.vessel_type if payload.vessel_type != "automatic" else "Supramax"
    result = generate_forecast(vessel_type, payload.forecast_horizon)
    entry = market_entry_signal(result)

    req = crud.save_forecast_request(db, payload.model_dump())
    crud.save_forecast_result(db, req.id, result)

    return {**result, "market_entry": entry}