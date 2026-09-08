from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class CharterRequestSchema(BaseModel):
    origin: str
    destination: str
    cargo_type: str
    cargo_quantity: float = Field(..., gt=0)
    vessel_type: str
    number_of_voyages: int = Field(1, ge=1, le=60)
    contract_duration_months: int = Field(6, ge=1, le=60)
    min_acceptable_rate: float | None = None
    max_acceptable_rate: float | None = None


class StrategyOption(BaseModel):
    strategy: Literal["SPOT", "SHORT-TERM MULTIPLE VOYAGE", "MEDIUM-TERM MULTIPLE VOYAGE"]
    total_cost: float
    cost_per_voyage: float
    risk: Literal["LOW", "MEDIUM", "HIGH"]
    flexibility: Literal["LOW", "MEDIUM", "HIGH"]


class CharterRecommendationSchema(BaseModel):
    options: list[StrategyOption]
    recommended_strategy: str
    expected_savings_abs: float
    expected_savings_pct: float
    risk: Literal["LOW", "MEDIUM", "HIGH"]
    reasons: list[str]
