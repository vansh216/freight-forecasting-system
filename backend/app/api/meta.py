from __future__ import annotations

from fastapi import APIRouter

from data.reference_data import ORIGIN_PORTS, DESTINATION_PORTS, VESSEL_CLASSES, DATA_SOURCE_LABEL

router = APIRouter(prefix="/api/meta", tags=["meta"])


@router.get("/origins")
def origins():
    return {name: {"ports": data["ports"], "typical_cargo": data["typical_cargo"]} for name, data in ORIGIN_PORTS.items()}


@router.get("/destinations")
def destinations():
    return list(DESTINATION_PORTS.keys())


@router.get("/vessel-classes")
def vessel_classes():
    return VESSEL_CLASSES


@router.get("/data-source-label")
def data_source_label():
    return {"label": DATA_SOURCE_LABEL}
