from __future__ import annotations

from fastapi import APIRouter

from backend.app.features.vessel_recomendation.schema import VesselRequestSchema
from backend.app.features.vessel_recomendation.service import recommend_vessel
from backend.app.features.utils.validation import validate_origin, validate_destination, validate_cargo_quantity, validate_vessel_type

router = APIRouter(prefix="/api/vessel", tags=["vessel"])


@router.post("/recommend")
def vessel_recommend(payload: VesselRequestSchema):
    validate_origin(payload.origin)
    validate_destination(payload.destination)
    validate_cargo_quantity(payload.cargo_quantity)
    validate_vessel_type(payload.vessel_preference)

    return recommend_vessel(
        payload.origin, payload.destination, payload.cargo_type,
        payload.cargo_quantity, payload.vessel_preference,
    )
