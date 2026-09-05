from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ArrivalResponse(BaseModel):
    vessel_name: str
    mmsi: str
    port: str
    status: str
    last_updated: datetime

    class Config:
        from_attributes = True