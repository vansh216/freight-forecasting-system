"""SQLAlchemy ORM models."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Column, Integer, Float, String, DateTime, JSON, ForeignKey, Text,
)
from sqlalchemy.orm import relationship

from backend.database.database import Base


class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    port_name = Column(String, unique=True, index=True, nullable=False)
    country = Column(String, nullable=False)
    max_loa = Column(Float, nullable=False)
    max_beam = Column(Float, nullable=False)
    max_draft = Column(Float, nullable=False)
    channel_depth = Column(Float, nullable=False)
    berth_depth = Column(Float, nullable=False)
    cargo_handling_rate = Column(Integer, nullable=False)
    max_vessel_dwt = Column(Integer, nullable=False)
    congestion_level = Column(String, nullable=False)
    berthing_restriction = Column(Text, nullable=True)


class VesselSpec(Base):
    __tablename__ = "vessel_specs"

    id = Column(Integer, primary_key=True, index=True)
    vessel_type = Column(String, unique=True, index=True, nullable=False)
    typical_dwt = Column(Integer, nullable=False)
    loa = Column(Float, nullable=False)
    beam = Column(Float, nullable=False)
    draft = Column(Float, nullable=False)
    speed_knots = Column(Float, nullable=False)
    fuel_consumption_tpd = Column(Float, nullable=False)
    cargo_handling_capable_rate = Column(Integer, nullable=False)


class ForecastRequest(Base):
    __tablename__ = "forecast_requests"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    origin = Column(String, nullable=False)
    origin_port = Column(String, nullable=True)
    destination = Column(String, nullable=False)
    cargo_type = Column(String, nullable=False)
    cargo_quantity = Column(Float, nullable=False)
    vessel_type = Column(String, nullable=False, default="automatic")
    forecast_horizon = Column(Integer, nullable=False, default=30)
    request_payload = Column(JSON, nullable=True)

    results = relationship("ForecastResult", back_populates="request")


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("forecast_requests.id"))
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    vessel_type = Column(String, nullable=False)
    current_rate = Column(Float, nullable=False)
    forecast_rate = Column(Float, nullable=False)
    trend = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    volatility = Column(String, nullable=False)
    model_used = Column(String, nullable=False)
    horizon_json = Column(JSON, nullable=True)

    request = relationship("ForecastRequest", back_populates="results")


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    request_id = Column(Integer, ForeignKey("forecast_requests.id"), nullable=True)
    category = Column(String, nullable=False)  # FREIGHT / PORT / VESSEL / MARKET
    level = Column(String, nullable=False)      # LOW / MEDIUM / HIGH
    message = Column(Text, nullable=False)


class CharterRecommendation(Base):
    __tablename__ = "charter_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    request_id = Column(Integer, ForeignKey("forecast_requests.id"), nullable=True)
    recommended_strategy = Column(String, nullable=False)
    spot_cost = Column(Float, nullable=False)
    short_term_cost = Column(Float, nullable=False)
    medium_term_cost = Column(Float, nullable=False)
    expected_savings_pct = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)


class HistoricalObservation(Base):
    __tablename__ = "historical_observations"

    id = Column(Integer, primary_key=True, index=True)
    observation_date = Column(DateTime, nullable=False, index=True)
    vessel_type = Column(String, nullable=False, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    freight_rate = Column(Float, nullable=False)
    is_demo_data = Column(Integer, default=1)  # 1 = simulated, 0 = real
