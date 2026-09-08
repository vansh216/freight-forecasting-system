from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core import crud
from backend.app.schemas.charter_schema import CharterRequestSchema
from backend.app.services.charter_service import compare_strategies
from backend.app.features.utils.validation import validate_origin, validate_destination, validate_cargo_quantity, validate_vessel_type

router = APIRouter(prefix="/api/charter", tags=["charter"])


@router.post("/recommend")
def charter_recommend(payload: CharterRequestSchema, db: Session = Depends(get_db)):
    validate_origin(payload.origin)
    validate_destination(payload.destination)
    validate_cargo_quantity(payload.cargo_quantity)
    validate_vessel_type(payload.vessel_type)

    result = compare_strategies(
        payload.origin, payload.destination, payload.cargo_type, payload.cargo_quantity,
        payload.vessel_type, payload.number_of_voyages, payload.contract_duration_months,
    )
    crud.save_charter_recommendation(db, None, result)
    return result
