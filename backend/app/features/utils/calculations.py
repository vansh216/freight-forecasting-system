"""Pure calculation helpers — voyage economics, distances, scoring.

No business/decision logic here — that lives in backend/services/*.
Keeping this module side-effect free makes it independently testable.
"""

from __future__ import annotations

from data.reference_data import (
    ORIGIN_PORTS,
    BUNKER_PRICE_USD_PER_TONNE,
    PORT_COST_USD_PER_DAY,
)


def get_distance_nm(origin: str, destination: str) -> float:
    """Great-circle-equivalent voyage distance in nautical miles (demo lookup table)."""
    origin_data = ORIGIN_PORTS.get(origin)
    if not origin_data:
        raise ValueError(f"Unknown origin: {origin}")
    distance = origin_data["base_distance_nm"].get(destination)
    if distance is None:
        raise ValueError(f"No distance data for {origin} -> {destination}")
    return float(distance)


def sailing_time_days(distance_nm: float, speed_knots: float) -> float:
    if speed_knots <= 0:
        raise ValueError("speed_knots must be positive")
    return distance_nm / (speed_knots * 24.0)


def port_time_days(cargo_quantity_t: float, cargo_handling_rate_tpd: float, waiting_days: float = 0.0) -> float:
    if cargo_handling_rate_tpd <= 0:
        raise ValueError("cargo_handling_rate_tpd must be positive")
    handling_days = cargo_quantity_t / cargo_handling_rate_tpd
    return handling_days + waiting_days


def voyage_duration_days(
    sailing_days: float,
    loading_days: float,
    discharge_days: float,
    waiting_days: float = 0.0,
) -> float:
    return sailing_days + loading_days + discharge_days + waiting_days


def voyage_economics(
    *,
    cargo_quantity_t: float,
    freight_rate_usd_per_mt: float,
    distance_nm: float,
    speed_knots: float,
    fuel_consumption_tpd: float,
    cargo_handling_rate_tpd: float,
    destination_congestion: str,
    bunker_price: float = BUNKER_PRICE_USD_PER_TONNE,
    waiting_days: float = 0.0,
    canal_cost: float = 0.0,
) -> dict:
    """Compute end-to-end voyage economics for a single voyage."""
    sailing_days = sailing_time_days(distance_nm, speed_knots)
    loading_days = port_time_days(cargo_quantity_t, cargo_handling_rate_tpd)
    discharge_days = loading_days  # symmetric assumption for demo purposes
    duration_days = voyage_duration_days(sailing_days, loading_days, discharge_days, waiting_days)

    freight_cost = cargo_quantity_t * freight_rate_usd_per_mt
    fuel_cost = sailing_days * fuel_consumption_tpd * bunker_price
    port_cost = (loading_days + discharge_days) * PORT_COST_USD_PER_DAY.get(destination_congestion, 9000) / 2
    waiting_cost = waiting_days * PORT_COST_USD_PER_DAY.get(destination_congestion, 9000)

    total_cost = freight_cost + fuel_cost + port_cost + waiting_cost + canal_cost
    cost_per_tonne = total_cost / cargo_quantity_t if cargo_quantity_t else 0.0

    return {
        "sailing_days": round(sailing_days, 2),
        "loading_days": round(loading_days, 2),
        "discharge_days": round(discharge_days, 2),
        "waiting_days": round(waiting_days, 2),
        "voyage_duration_days": round(duration_days, 2),
        "freight_cost_usd": round(freight_cost, 2),
        "fuel_cost_usd": round(fuel_cost, 2),
        "port_cost_usd": round(port_cost, 2),
        "waiting_cost_usd": round(waiting_cost, 2),
        "canal_cost_usd": round(canal_cost, 2),
        "total_voyage_cost_usd": round(total_cost, 2),
        "cost_per_tonne_usd": round(cost_per_tonne, 2),
    }


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def pct_change(old: float, new: float) -> float:
    if old == 0:
        return 0.0
    return (new - old) / old * 100.0
