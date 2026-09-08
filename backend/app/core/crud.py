"""CRUD helpers and one-time seeding from the static reference dataset."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.features.freight_forecast import models
from data.reference_data import DESTINATION_PORTS, VESSEL_CLASSES


def seed_reference_data(db: Session) -> None:
    """Populate ports/vessel_specs tables if empty. Idempotent."""
    if db.query(models.Port).count() == 0:
        for p in DESTINATION_PORTS.values():
            db.add(models.Port(**p))
    if db.query(models.VesselSpec).count() == 0:
        for v in VESSEL_CLASSES.values():
            db.add(
                models.VesselSpec(
                    vessel_type=v["vessel_type"],
                    typical_dwt=v["typical_dwt"],
                    loa=v["loa"],
                    beam=v["beam"],
                    draft=v["draft"],
                    speed_knots=v["speed_knots"],
                    fuel_consumption_tpd=v["fuel_consumption_tpd"],
                    cargo_handling_capable_rate=v["cargo_handling_capable_rate"],
                )
            )
    db.commit()


def get_port(db: Session, port_name: str) -> models.Port | None:
    return db.query(models.Port).filter(models.Port.port_name == port_name).first()


def get_all_ports(db: Session) -> list[models.Port]:
    return db.query(models.Port).all()


def save_forecast_request(db: Session, payload: dict) -> models.ForecastRequest:
    req = models.ForecastRequest(
        origin=payload["origin"],
        origin_port=payload.get("origin_port"),
        destination=payload["destination"],
        cargo_type=payload["cargo_type"],
        cargo_quantity=payload["cargo_quantity"],
        vessel_type=payload.get("vessel_type", "automatic"),
        forecast_horizon=payload.get("forecast_horizon", 30),
        request_payload=payload,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req



def save_forecast_result(db: Session, request_id: int | None, result: dict) -> models.ForecastResult:

    volatility_map = {"LOW": 0.1, "MEDIUM": 0.5, "HIGH": 0.9}
    row = models.ForecastResult(
        request_id=request_id,
        vessel_type=result["vessel_type"],
        current_rate=float(result["current_rate"]),
        forecast_rate=float(result["forecast_rate"]),
        trend=result["trend"],
        confidence=float(result["confidence"]),
        volatility=volatility_map.get(result["volatility"], None),
        model_used=result["model_used"],
        horizon_json=result.get("horizons"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_risk_alert(db: Session, request_id: int | None, category: str, level: str, message: str) -> models.RiskAlert:
    row = models.RiskAlert(request_id=request_id, category=category, level=level, message=message)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_charter_recommendation(db: Session, request_id: int | None, rec: dict) -> models.CharterRecommendation:
    row = models.CharterRecommendation(
        request_id=request_id,
        recommended_strategy=rec["recommended_strategy"],
        spot_cost=float(rec["spot_cost"]),
        short_term_cost=float(rec["short_term_cost"]),
        medium_term_cost=float(rec["medium_term_cost"]),
        expected_savings_pct=float(rec["expected_savings_pct"]),
        risk_level=rec["risk"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
