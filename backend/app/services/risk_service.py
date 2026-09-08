"""Risk management engine + idle-vessel management module."""

from __future__ import annotations

from data.reference_data import DESTINATION_PORTS


_LEVEL_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def _worse(a: str, b: str) -> str:
    return a if _LEVEL_ORDER[a] >= _LEVEL_ORDER[b] else b


def freight_risk(forecast: dict) -> dict:
    volatility = forecast["volatility"]
    confidence = forecast["confidence"]

    if volatility == "HIGH" or confidence < 0.5:
        level = "HIGH"
    elif volatility == "MEDIUM" or confidence < 0.7:
        level = "MEDIUM"
    else:
        level = "LOW"

    reasons = [f"Freight volatility: {volatility}", f"Forecast confidence: {confidence*100:.0f}%"]
    return {"category": "FREIGHT", "level": level, "reasons": reasons}


def port_risk(destination: str) -> dict:
    port = DESTINATION_PORTS[destination]
    congestion = port["congestion_level"]
    level = congestion  # LOW/MEDIUM/HIGH map directly in this demo model
    reasons = [f"{destination} congestion level: {congestion}"]
    if port["berthing_restriction"]:
        reasons.append(port["berthing_restriction"])
    return {"category": "PORT", "level": level, "reasons": reasons}


def vessel_risk(vessel_candidate: dict | None) -> dict:
    if vessel_candidate is None:
        return {"category": "VESSEL", "level": "HIGH", "reasons": ["No feasible vessel found for this route."]}
    if not vessel_candidate["feasible"]:
        return {"category": "VESSEL", "level": "HIGH", "reasons": [vessel_candidate["infeasibility_reason"]]}
    score = vessel_candidate["port_compatibility_score"]
    if score >= 70:
        level = "LOW"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "HIGH"
    return {"category": "VESSEL", "level": level, "reasons": [f"Port compatibility score: {score:.0f}%"]}


def market_risk(forecast: dict, cargo_type: str) -> dict:
    change_pct = forecast.get("change_pct", 0)
    volatility = forecast["volatility"]

    if abs(change_pct) >= 10 and volatility == "HIGH":
        level = "HIGH"
    elif abs(change_pct) >= 5 or volatility == "MEDIUM":
        level = "MEDIUM"
    else:
        level = "LOW"

    reasons = [
        f"Expected rate movement: {change_pct:+.1f}% over forecast horizon.",
        f"Commodity: {cargo_type} — demand/supply and seasonal patterns factored via forecast volatility.",
    ]
    return {"category": "MARKET", "level": level, "reasons": reasons}


def overall_risk(risks: list[dict]) -> str:
    level = "LOW"
    for r in risks:
        level = _worse(level, r["level"])
    return level


def generate_alerts(risks: list[dict], forecast: dict, destination: str) -> list[dict]:
    alerts = []
    for r in risks:
        if r["level"] == "HIGH":
            if r["category"] == "FREIGHT":
                alerts.append({"level": "HIGH", "message": "HIGH FREIGHT VOLATILITY"})
            elif r["category"] == "PORT":
                alerts.append({"level": "HIGH", "message": f"PORT CONGESTION EXPECTED AT {destination.upper()}"})
            elif r["category"] == "VESSEL":
                alerts.append({"level": "HIGH", "message": "DRAFT/PORT LIMITATION DETECTED"})
            elif r["category"] == "MARKET":
                direction = "INCREASE" if forecast.get("change_pct", 0) > 0 else "DECREASE"
                alerts.append({"level": "HIGH", "message": f"RATE {direction} EXPECTED"})
    if not alerts:
        alerts.append({"level": "LOW", "message": "NO ELEVATED RISK ALERTS AT THIS TIME"})
    return alerts


def idle_vessel_analysis(destination: str, forecast: dict) -> dict:
    """Estimate expected idle time and give a repositioning/employment recommendation."""
    port = DESTINATION_PORTS[destination]
    congestion = port["congestion_level"]
    volatility = forecast["volatility"]

    congestion_days = {"LOW": 0.5, "MEDIUM": 1.8, "HIGH": 3.5}[congestion]
    demand_softness_days = {"LOW": 0.2, "MEDIUM": 1.0, "HIGH": 2.2}[volatility]
    expected_idle_days = round(congestion_days + demand_softness_days, 1)

    if expected_idle_days >= 4:
        risk = "HIGH"
    elif expected_idle_days >= 1.5:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    recommendations = []
    if risk == "HIGH":
        recommendations.append("Reposition vessel toward a lower-congestion region while awaiting the next fixture.")
        recommendations.append("Seek short-term alternative cargo to avoid extended idle time.")
    elif risk == "MEDIUM":
        recommendations.append("Monitor berth allocation closely; consider a short-haul interim fixture if idle window exceeds 2 days.")
    else:
        recommendations.append("Wait at current position — idle time is within normal operating range.")

    return {
        "expected_idle_days": expected_idle_days,
        "risk": risk,
        "recommendations": recommendations,
        "reasons": [
            f"Destination congestion level: {congestion}",
            f"Freight-market volatility: {volatility}",
        ],
    }


def full_risk_analysis(destination: str, cargo_type: str, forecast: dict, vessel_candidate: dict | None) -> dict:
    risks = [
        freight_risk(forecast),
        port_risk(destination),
        vessel_risk(vessel_candidate),
        market_risk(forecast, cargo_type),
    ]
    return {
        "risks": risks,
        "overall_risk": overall_risk(risks),
        "alerts": generate_alerts(risks, forecast, destination),
        "idle_vessel": idle_vessel_analysis(destination, forecast),
    }
