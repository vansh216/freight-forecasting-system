from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from backend.app.core.database import Base


class VesselArrival(Base):
    __tablename__ = "vessel_arrivals"

    id = Column(Integer, primary_key=True, index=True)
    vessel_name = Column(String, nullable=False)
    mmsi = Column(String, index=True, nullable=False)   # unique vessel ID from AIS
    port = Column(String, nullable=False)                # Paradip / Vizag / Gangavaram
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String, default="en_route")           # en_route / arrived / departed
    last_updated = Column(DateTime, default=datetime.utcnow)