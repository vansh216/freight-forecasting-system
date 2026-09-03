"""Domain-level input validation helpers, raising HTTPException on failure."""

from __future__ import annotations

from fastapi import HTTPException

from backend.database.reference_data import (
    DESTINATION_PORTS, ORIGIN_PORTS, VESSEL_CLASSES,
)


def validate_origin(origin: str) -> None:
    if origin not in ORIGIN_PORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown origin '{origin}'. Valid options: {list(ORIGIN_PORTS.keys())}",
        )


def validate_destination(destination: str) -> None:
    if destination not in DESTINATION_PORTS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown destination port '{destination}'. Valid options: {list(DESTINATION_PORTS.keys())}",
        )


def validate_vessel_type(vessel_type: str) -> None:
    if vessel_type not in VESSEL_CLASSES and vessel_type != "automatic":
        raise HTTPException(
            status_code=400,
            detail=f"Unknown vessel type '{vessel_type}'. Valid options: automatic, {list(VESSEL_CLASSES.keys())}",
        )


def validate_cargo_quantity(quantity: float) -> None:
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="cargo_quantity must be greater than 0")
    if quantity > 400000:
        raise HTTPException(status_code=400, detail="cargo_quantity exceeds realistic single-parcel size")
