"""SQLAlchemy models for freight forecasting (PostgreSQL)."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB   # Postgres-native JSON type
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    port_name = Column(String, unique=True, index=True, nullable=False)
    country = Column(String, nullable=False)
    port_type = Column(String, nullable=False)   # "loading" or "discharge"
    max_draft_m = Column(Float, nullable=False)
    max_loa_m = Column(Float, nullable=False)
    max_beam_m = Column(Float, nullable=False)
    cargo_handling_rate_tpd = Column(Float, nullable=True)


class VesselSpec(Base):
    __tablename__ = "vessel_specs"

    id = Column(Integer, primary_key=True, index=True)
    vessel_type = Column(String, unique=True, index=True, nullable=False)
    typical_dwt = Column(Float, nullable=False)
    loa = Column(Float, nullable=False)
    beam = Column(Float, nullable=False)
    draft = Column(Float, nullable=False)
    speed_knots = Column(Float, nullable=True)
    fuel_consumption_tpd = Column(Float, nullable=True)
    cargo_handling_capable_rate = Column(Float, nullable=True)


class ForecastRequest(Base):
    __tablename__ = "forecast_requests"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    origin_port = Column(String, nullable=True)
    destination = Column(String, nullable=False)
    cargo_type = Column(String, nullable=False)
    cargo_quantity = Column(Float, nullable=False)
    vessel_type = Column(String, default="automatic")
    forecast_horizon = Column(Integer, default=30)
    request_payload = Column(JSONB, nullable=True)     # stores the full raw dict
    created_at = Column(DateTime, default=datetime.utcnow)

    results = relationship("ForecastResult", back_populates="request")
    alerts = relationship("RiskAlert", back_populates="request")
    recommendations = relationship("CharterRecommendation", back_populates="request")


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("forecast_requests.id"), nullable=True)
    vessel_type = Column(String, nullable=False)
    current_rate = Column(Float, nullable=False)
    forecast_rate = Column(Float, nullable=False)
    trend = Column(String, nullable=False)          # "rising" / "falling" / "flat"
    confidence = Column(Float, nullable=False)
    volatility = Column(Float, nullable=True)
    model_used = Column(String, nullable=False)      # "prophet" / "sarima" etc.
    horizon_json = Column(JSONB, nullable=True)       # stores forecast points per horizon
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("ForecastRequest", back_populates="results")


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("forecast_requests.id"), nullable=True)
    category = Column(String, nullable=False)    # "market_volatility" / "port_congestion" / "weather"
    level = Column(String, nullable=False)        # "low" / "medium" / "high"
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("ForecastRequest", back_populates="alerts")


class CharterRecommendation(Base):
    __tablename__ = "charter_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("forecast_requests.id"), nullable=True)
    recommended_strategy = Column(String, nullable=False)   # "spot" / "short_term" / "medium_term"
    spot_cost = Column(Float, nullable=False)
    short_term_cost = Column(Float, nullable=False)
    medium_term_cost = Column(Float, nullable=False)
    expected_savings_pct = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("ForecastRequest", back_populates="recommendations")