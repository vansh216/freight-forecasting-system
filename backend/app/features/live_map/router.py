from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.app.core.database import get_db
from backend.app.features.live_map.schema import LiveVesselResponse
from backend.app.features.live_map.service import get_live_vessels

router = APIRouter(prefix="/api/live-vessels", tags=["Live Map"])


@router.get("", response_model=List[LiveVesselResponse])
def get_live_vessels_endpoint(port: Optional[str] = None, db: Session = Depends(get_db)):
    return get_live_vessels(db, port=port)