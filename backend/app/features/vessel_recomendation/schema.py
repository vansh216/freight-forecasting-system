from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


class VesselRequestSchema(BaseModel):
    origin: str
    destination: str
    cargo_type: Optional[str] = None
    cargo_quantity: float = Field(..., gt=0)
    vessel_preference: str = "automatic"


class VesselCandidate(BaseModel):
    vessel_type: str
    feasible: bool
    infeasibility_reason: Optional[str] = None
    freight_rate: float
    estimated_voyage_cost: float
    port_compatibility_score: float
    score: float
    reasons: list[str]


class VesselRecommendationSchema(BaseModel):
    recommended_vessel: Optional[str]
    ranked_vessels: list[VesselCandidate]
    reasons: list[str]
    error: Optional[str] = None
