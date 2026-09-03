from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

VesselChoice = Literal["automatic", "Handysize", "Supramax", "Panamax", "Capesize"]
ContractChoice = Literal["automatic", "spot", "short-term", "medium-term"]


class ForecastRequestSchema(BaseModel):
    origin: str = Field(..., description="Loading origin country/region")
    origin_port: Optional[str] = Field(None, description="Specific loading port if known")
    destination: str = Field(..., description="Destination India East Coast port")
    cargo_type: str = Field(..., description="e.g. Coal, Iron ore")
    cargo_quantity: float = Field(..., gt=0, description="Cargo quantity in tonnes")
    vessel_type: VesselChoice = "automatic"
    forecast_horizon: int = Field(30, ge=1, le=90)

    @field_validator("cargo_quantity")
    @classmethod
    def quantity_reasonable(cls, v: float) -> float:
        if v > 400000:
            raise ValueError("cargo_quantity exceeds realistic single-parcel size (max 400,000 t)")
        return v


class HorizonPoint(BaseModel):
    days: int
    expected_rate: float
    lower_bound: float
    upper_bound: float


class ForecastResponseSchema(BaseModel):
    vessel_type: str
    current_rate: float
    forecast_rate: float
    trend: Literal["increasing", "decreasing", "stable"]
    confidence: float
    volatility: Literal["LOW", "MEDIUM", "HIGH"]
    model_used: str
    is_fallback: bool
    horizons: list[HorizonPoint]
    data_source_label: str


class MarketEntrySchema(BaseModel):
    signal: Literal["BOOK NOW", "WAIT", "PARTIALLY BOOK", "LOCK-IN CONTRACT", "MONITOR MARKET"]
    reasons: list[str]
