"""
Spot vs Short-Term vs Medium-Term multiple-voyage contract comparison.

Contract premiums/discounts are demo assumptions (documented inline) —
in production these would come from broker-quoted term rates.
"""

from __future__ import annotations

from backend.app.features.freight_forecast.service import generate_forecast
from backend.app.services.voyage_service import compute_voyage_economics

# Demo assumptions: term contracts typically trade at a discount to the
# expected average spot rate, in exchange for the owner/charterer giving up
# some flexibility. Short-term carries a smaller discount than medium-term
# because there is less exposure to be priced in, but medium-term protects
# better against volatility.
SHORT_TERM_DISCOUNT = 0.04   # 4% below expected average spot
MEDIUM_TERM_DISCOUNT = 0.07  # 7% below expected average spot
SHORT_TERM_RISK_LOAD = 0.015  # narrows volatility exposure priced as a small premium in HIGH vol
MEDIUM_TERM_RISK_LOAD = 0.01


def compare_strategies(origin: str, destination: str, cargo_type: str, cargo_quantity: float,
                        vessel_type: str, number_of_voyages: int, contract_duration_months: int) -> dict:
    forecast = generate_forecast(vessel_type, forecast_horizon=min(90, contract_duration_months * 30))
    expected_spot_rate = (forecast["current_rate"] + forecast["forecast_rate"]) / 2
    volatility = forecast["volatility"]

    vol_adj = {"LOW": 0.0, "MEDIUM": 0.01, "HIGH": 0.025}.get(volatility, 0.01)

    # SPOT: pay expected spot rate each voyage, full exposure to volatility
    spot_rate_per_voyage = expected_spot_rate * (1 + vol_adj)
    spot_econ = compute_voyage_economics(origin, destination, vessel_type, cargo_quantity, spot_rate_per_voyage)
    spot_total = spot_econ["total_voyage_cost_usd"] * number_of_voyages

    # SHORT-TERM: discounted fixed rate, small risk load
    st_rate = expected_spot_rate * (1 - SHORT_TERM_DISCOUNT) * (1 + SHORT_TERM_RISK_LOAD * (vol_adj > 0))
    st_econ = compute_voyage_economics(origin, destination, vessel_type, cargo_quantity, st_rate)
    st_total = st_econ["total_voyage_cost_usd"] * number_of_voyages

    # MEDIUM-TERM: deeper discount, best volatility protection, some idle-time efficiency assumed
    mt_rate = expected_spot_rate * (1 - MEDIUM_TERM_DISCOUNT) * (1 + MEDIUM_TERM_RISK_LOAD * (vol_adj > 0))
    mt_econ = compute_voyage_economics(origin, destination, vessel_type, cargo_quantity, mt_rate)
    mt_total = mt_econ["total_voyage_cost_usd"] * number_of_voyages

    options = [
        {"strategy": "SPOT", "total_cost": round(spot_total, 2),
         "cost_per_voyage": round(spot_total / number_of_voyages, 2), "risk": "HIGH", "flexibility": "HIGH"},
        {"strategy": "SHORT-TERM MULTIPLE VOYAGE", "total_cost": round(st_total, 2),
         "cost_per_voyage": round(st_total / number_of_voyages, 2), "risk": "MEDIUM", "flexibility": "MEDIUM"},
        {"strategy": "MEDIUM-TERM MULTIPLE VOYAGE", "total_cost": round(mt_total, 2),
         "cost_per_voyage": round(mt_total / number_of_voyages, 2), "risk": "LOW", "flexibility": "LOW"},
    ]

    cheapest = min(options, key=lambda o: o["total_cost"])
    spot_cost = options[0]["total_cost"]
    savings_abs = round(spot_cost - cheapest["total_cost"], 2)
    savings_pct = round((savings_abs / spot_cost * 100) if spot_cost else 0, 1)

    reasons = []
    if cheapest["strategy"] == "SPOT":
        reasons.append("Spot market pricing is currently favourable relative to term contract discounts.")
        reasons.append("Low number of voyages reduces the benefit of a term commitment.")
    else:
        reasons.append(f"{cheapest['strategy'].title()} contract offers a locked-in discount vs. expected spot exposure.")
        if volatility in ("MEDIUM", "HIGH"):
            reasons.append(f"Freight volatility is currently {volatility}, favouring a fixed-rate term contract to reduce risk.")
        reasons.append(f"Across {number_of_voyages} voyages, the discount compounds into a meaningful total saving.")
    reasons.append(f"Estimated savings vs. spot: {savings_pct}% (${savings_abs:,.0f}).")

    if number_of_voyages <= 2:
        overall_risk = "MEDIUM"
    elif volatility == "HIGH":
        overall_risk = "MEDIUM" if cheapest["strategy"] != "SPOT" else "HIGH"
    else:
        overall_risk = cheapest["risk"]

    return {
        "options": options,
        "recommended_strategy": cheapest["strategy"],
        "expected_savings_abs": savings_abs,
        "expected_savings_pct": savings_pct,
        "risk": overall_risk,
        "reasons": reasons,
        "spot_cost": options[0]["total_cost"],
        "short_term_cost": options[1]["total_cost"],
        "medium_term_cost": options[2]["total_cost"],
    }
