from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LiveVesselResponse(BaseModel):
    vessel_name: str
    mmsi: str
    port: str
    latitude: float
    longitude: float
    status: str
    last_updated: datetime

    class Config:
        from_attributes = True