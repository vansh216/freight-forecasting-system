"""
Vessel optimization module + port constraint engine.

Feasibility is NEVER based on cargo quantity alone — a vessel is only
feasible if it satisfies the destination (and, where known, origin) port's
draft / LOA / beam / DWT limits. See section 8-9 of the spec this
implements.
"""

from __future__ import annotations

from backend.database.reference_data import DESTINATION_PORTS, VESSEL_CLASSES
from backend.services.forecasting_service import generate_forecast
from backend.utils.calculations import get_distance_nm, voyage_economics, clamp


def check_port_compatibility(vessel_type: str, port_name: str) -> dict:
    vessel = VESSEL_CLASSES[vessel_type]
    port = DESTINATION_PORTS[port_name]

    checks = {
        "draft": vessel["draft"] <= port["max_draft"],
        "loa": vessel["loa"] <= port["max_loa"],
        "beam": vessel["beam"] <= port["max_beam"],
        "dwt": vessel["typical_dwt"] <= port["max_vessel_dwt"],
    }
    feasible = all(checks.values())

    failed = [k for k, ok in checks.items() if not ok]
    reason = None
    if not feasible:
        labels = {"draft": "draft", "loa": "LOA", "beam": "beam", "dwt": "DWT"}
        reason = f"Exceeds {port_name} maximum " + " & ".join(labels[f] for f in failed) + " limit"

    # compatibility score: how much headroom the vessel has vs. port limits (0-100)
    margins = [
        clamp(1 - vessel["draft"] / port["max_draft"], 0, 1),
        clamp(1 - vessel["loa"] / port["max_loa"], 0, 1),
        clamp(1 - vessel["beam"] / port["max_beam"], 0, 1),
        clamp(1 - vessel["typical_dwt"] / port["max_vessel_dwt"], 0, 1),
    ]
    score = round((sum(margins) / len(margins)) * 100, 1) if feasible else 0.0

    return {"feasible": feasible, "reason": reason, "score": score, "checks": checks}


def rank_vessels(origin: str, destination: str, cargo_type: str, cargo_quantity: float) -> list[dict]:
    port = DESTINATION_PORTS[destination]
    distance_nm = get_distance_nm(origin, destination)

    candidates = []
    for vessel_type, vessel in VESSEL_CLASSES.items():
        compat = check_port_compatibility(vessel_type, destination)
        forecast = generate_forecast(vessel_type, forecast_horizon=30)
        freight_rate = forecast["current_rate"]

        reasons = []
        if compat["feasible"]:
            economics = voyage_economics(
                cargo_quantity_t=cargo_quantity,
                freight_rate_usd_per_mt=freight_rate,
                distance_nm=distance_nm,
                speed_knots=vessel["speed_knots"],
                fuel_consumption_tpd=vessel["fuel_consumption_tpd"],
                cargo_handling_rate_tpd=min(vessel["cargo_handling_capable_rate"], port["cargo_handling_rate"]),
                destination_congestion=port["congestion_level"],
            )
            cost_per_tonne = economics["cost_per_tonne_usd"]

            # How well does vessel capacity match the parcel size? (closer to 1.0 utilisation = better)
            dwt_min, dwt_max = vessel["dwt_range"]
            utilisation = clamp(cargo_quantity / vessel["typical_dwt"], 0, 1.3)
            utilisation_score = 100 - abs(1.0 - utilisation) * 60

            cost_score = clamp(100 - (cost_per_tonne - 10) * 2, 0, 100)
            score = round(
                0.4 * compat["score"] + 0.35 * cost_score + 0.25 * utilisation_score, 1
            )

            reasons.append(f"Draft/LOA/beam/DWT within {destination} limits (port compatibility {compat['score']:.0f}%).")
            if dwt_min <= cargo_quantity <= dwt_max * 1.4:
                reasons.append(f"Cargo quantity ({cargo_quantity:,.0f} t) fits {vessel_type} capacity well.")
            else:
                reasons.append(f"Cargo quantity ({cargo_quantity:,.0f} t) is a suboptimal match for {vessel_type} typical capacity.")
            reasons.append(f"Estimated voyage cost: ${cost_per_tonne:.2f}/t.")
        else:
            economics = None
            cost_per_tonne = None
            score = 0.0
            reasons.append(compat["reason"])

        candidates.append({
            "vessel_type": vessel_type,
            "feasible": compat["feasible"],
            "infeasibility_reason": compat["reason"],
            "freight_rate": freight_rate,
            "estimated_voyage_cost": cost_per_tonne if cost_per_tonne is not None else 0.0,
            "port_compatibility_score": compat["score"],
            "score": score,
            "reasons": reasons,
            "economics": economics,
            "distance_nm": distance_nm,
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates


def recommend_vessel(origin: str, destination: str, cargo_type: str, cargo_quantity: float,
                      vessel_preference: str = "automatic") -> dict:
    ranked = rank_vessels(origin, destination, cargo_type, cargo_quantity)

    if vessel_preference != "automatic":
        chosen = next((c for c in ranked if c["vessel_type"] == vessel_preference), None)
        if chosen and not chosen["feasible"]:
            best_feasible = next((c for c in ranked if c["feasible"]), None)
            reasons = [f"{vessel_preference} is not feasible for this route: {chosen['infeasibility_reason']}."]
            if best_feasible:
                reasons.append(f"Automatically substituting {best_feasible['vessel_type']} as the nearest feasible alternative.")
            recommended = best_feasible["vessel_type"] if best_feasible else None
            return {"recommended_vessel": recommended, "ranked_vessels": ranked, "reasons": reasons}
        return {
            "recommended_vessel": vessel_preference,
            "ranked_vessels": ranked,
            "reasons": [f"User-specified vessel type: {vessel_preference}."] + (chosen["reasons"] if chosen else []),
        }

    feasible = [c for c in ranked if c["feasible"]]
    if not feasible:
        return {
            "recommended_vessel": None,
            "ranked_vessels": ranked,
            "reasons": ["No vessel class is feasible for this route's port constraints. Consider a different destination or lightering/transhipment."],
        }

    best = feasible[0]
    reasons = [f"Recommended Vessel: {best['vessel_type']}"] + best["reasons"]
    return {"recommended_vessel": best["vessel_type"], "ranked_vessels": ranked, "reasons": reasons}
