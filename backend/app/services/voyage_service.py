"""Voyage economics service — orchestrates calculations.py for a full request."""

from __future__ import annotations

from data.reference_data import DESTINATION_PORTS, VESSEL_CLASSES
from backend.app.features.utils.calculations import get_distance_nm, voyage_economics


def compute_voyage_economics(origin: str, destination: str, vessel_type: str,
                              cargo_quantity: float, freight_rate: float,
                              waiting_days: float = 0.0) -> dict:
    vessel = VESSEL_CLASSES[vessel_type]
    port = DESTINATION_PORTS[destination]
    distance_nm = get_distance_nm(origin, destination)

    economics = voyage_economics(
        cargo_quantity_t=cargo_quantity,
        freight_rate_usd_per_mt=freight_rate,
        distance_nm=distance_nm,
        speed_knots=vessel["speed_knots"],
        fuel_consumption_tpd=vessel["fuel_consumption_tpd"],
        cargo_handling_rate_tpd=min(vessel["cargo_handling_capable_rate"], port["cargo_handling_rate"]),
        destination_congestion=port["congestion_level"],
        waiting_days=waiting_days,
    )
    economics["distance_nm"] = distance_nm
    economics["vessel_type"] = vessel_type
    return economics
