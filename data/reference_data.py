"""
Static / seed reference data: ports, vessel classes, origin regions.

This is DEMO / SIMULATED data built for prototype purposes so the
application is fully runnable before real AIS / port-authority /
Baltic-index feeds are integrated. Every record below is clearly a
placeholder for a future real data source (see docs/architecture.md).

Nothing here should be presented to an end user as live operational data.
"""

from __future__ import annotations

DATA_SOURCE_LABEL = "Demo / Simulated Data"

# ---------------------------------------------------------------------------
# Destination ports — India East Coast
# ---------------------------------------------------------------------------
# max_loa (m), max_beam (m), max_draft (m), channel_depth (m), berth_depth (m)
# cargo_handling_rate (tonnes/day), max_vessel_dwt, congestion_level (LOW/MEDIUM/HIGH)
DESTINATION_PORTS = {
    "Paradip": {
        "port_name": "Paradip",
        "country": "India",
        "max_loa": 300.0,
        "max_beam": 45.0,
        "max_draft": 18.1,
        "channel_depth": 19.0,
        "berth_depth": 18.5,
        "cargo_handling_rate": 45000,
        "max_vessel_dwt": 180000,
        "congestion_level": "MEDIUM",
        "berthing_restriction": "Deep-draft berth available for Capesize; tidal window for larger vessels",
    },
    "Visakhapatnam": {
        "port_name": "Visakhapatnam",
        "country": "India",
        "max_loa": 280.0,
        "max_beam": 43.0,
        "max_draft": 17.0,
        "channel_depth": 18.0,
        "berth_depth": 17.5,
        "cargo_handling_rate": 40000,
        "max_vessel_dwt": 150000,
        "congestion_level": "MEDIUM",
        "berthing_restriction": "Outer harbour handles Capesize; inner harbour limited to Panamax",
    },
    "Gangavaram": {
        "port_name": "Gangavaram",
        "country": "India",
        "max_loa": 300.0,
        "max_beam": 48.0,
        "max_draft": 18.5,
        "channel_depth": 20.0,
        "berth_depth": 19.0,
        "cargo_handling_rate": 50000,
        "max_vessel_dwt": 200000,
        "congestion_level": "LOW",
        "berthing_restriction": "Deepest all-weather port on the east coast; minimal restriction",
    },
    "Gopalpur": {
        "port_name": "Gopalpur",
        "country": "India",
        "max_loa": 230.0,
        "max_beam": 36.0,
        "max_draft": 14.0,
        "channel_depth": 14.5,
        "berth_depth": 14.2,
        "cargo_handling_rate": 22000,
        "max_vessel_dwt": 80000,
        "congestion_level": "LOW",
        "berthing_restriction": "Shallow-draft port; no Panamax/Capesize berthing",
    },
    "Dhamra": {
        "port_name": "Dhamra",
        "country": "India",
        "max_loa": 290.0,
        "max_beam": 45.0,
        "max_draft": 18.0,
        "channel_depth": 19.0,
        "berth_depth": 18.2,
        "cargo_handling_rate": 42000,
        "max_vessel_dwt": 180000,
        "congestion_level": "LOW",
        "berthing_restriction": "Deep-water port, low congestion, suitable for large bulkers",
    },
    "Sagar/Sandheads": {
        "port_name": "Sagar/Sandheads",
        "country": "India",
        "max_loa": 250.0,
        "max_beam": 40.0,
        "max_draft": 12.5,
        "channel_depth": 13.0,
        "berth_depth": 12.5,
        "cargo_handling_rate": 18000,
        "max_vessel_dwt": 70000,
        "congestion_level": "HIGH",
        "berthing_restriction": "Anchorage / lightering point; requires transhipment for larger parcels",
    },
    "Haldia": {
        "port_name": "Haldia",
        "country": "India",
        "max_loa": 225.0,
        "max_beam": 32.5,
        "max_draft": 11.5,
        "channel_depth": 12.0,
        "berth_depth": 11.8,
        "cargo_handling_rate": 20000,
        "max_vessel_dwt": 55000,
        "congestion_level": "HIGH",
        "berthing_restriction": "River port with tidal and draft restriction; Handysize/Supramax only",
    },
}

# ---------------------------------------------------------------------------
# Origin regions and representative loading ports
# ---------------------------------------------------------------------------
ORIGIN_PORTS = {
    "Australia": {
        "region": "Australia",
        "ports": ["Newcastle", "Port Hedland", "Gladstone", "Hay Point"],
        "typical_cargo": ["Coal", "Iron ore"],
        "base_distance_nm": {
            "Paradip": 4600, "Visakhapatnam": 4700, "Gangavaram": 4750,
            "Gopalpur": 4650, "Dhamra": 4600, "Sagar/Sandheads": 4550, "Haldia": 4600,
        },
    },
    "USA": {
        "region": "USA",
        "ports": ["Norfolk", "Baltimore", "New Orleans"],
        "typical_cargo": ["Coal", "Grain"],
        "base_distance_nm": {
            "Paradip": 10800, "Visakhapatnam": 10900, "Gangavaram": 10950,
            "Gopalpur": 10850, "Dhamra": 10800, "Sagar/Sandheads": 10750, "Haldia": 10800,
        },
    },
    "Mozambique": {
        "region": "Mozambique",
        "ports": ["Beira", "Nacala"],
        "typical_cargo": ["Coal"],
        "base_distance_nm": {
            "Paradip": 4300, "Visakhapatnam": 4200, "Gangavaram": 4150,
            "Gopalpur": 4250, "Dhamra": 4300, "Sagar/Sandheads": 4400, "Haldia": 4450,
        },
    },
    "Russia": {
        "region": "Russia",
        "ports": ["Vostochny", "Vanino"],
        "typical_cargo": ["Coal", "Iron ore"],
        "base_distance_nm": {
            "Paradip": 6200, "Visakhapatnam": 6300, "Gangavaram": 6350,
            "Gopalpur": 6250, "Dhamra": 6200, "Sagar/Sandheads": 6100, "Haldia": 6150,
        },
    },
    "Indonesia": {
        "region": "Indonesia",
        "ports": ["Tanjung Bara", "Samarinda", "Balikpapan"],
        "typical_cargo": ["Coal"],
        "base_distance_nm": {
            "Paradip": 2400, "Visakhapatnam": 2300, "Gangavaram": 2250,
            "Gopalpur": 2350, "Dhamra": 2400, "Sagar/Sandheads": 2500, "Haldia": 2550,
        },
    },
}

# ---------------------------------------------------------------------------
# Vessel classes
# ---------------------------------------------------------------------------
VESSEL_CLASSES = {
    "Handysize": {
        "vessel_type": "Handysize",
        "dwt_range": [10000, 40000],
        "typical_dwt": 32000,
        "loa": 180.0,
        "beam": 30.0,
        "draft": 10.5,
        "speed_knots": 13.5,
        "fuel_consumption_tpd": 18,
        "cargo_handling_capable_rate": 15000,
        "typical_use": "Smaller cargo parcels and ports with infrastructure constraints",
    },
    "Supramax": {
        "vessel_type": "Supramax",
        "dwt_range": [50000, 60000],
        "typical_dwt": 56000,
        "loa": 190.0,
        "beam": 32.3,
        "draft": 12.5,
        "speed_knots": 14.0,
        "fuel_consumption_tpd": 24,
        "cargo_handling_capable_rate": 25000,
        "typical_use": "Medium cargo parcels",
    },
    "Panamax": {
        "vessel_type": "Panamax",
        "dwt_range": [65000, 80000],
        "typical_dwt": 76000,
        "loa": 225.0,
        "beam": 32.3,
        "draft": 14.5,
        "speed_knots": 14.2,
        "fuel_consumption_tpd": 30,
        "cargo_handling_capable_rate": 35000,
        "typical_use": "Large cargo parcels and ports capable of handling larger vessels",
    },
    "Capesize": {
        "vessel_type": "Capesize",
        "dwt_range": [150000, 180000],
        "typical_dwt": 170000,
        "loa": 290.0,
        "beam": 45.0,
        "draft": 17.5,
        "speed_knots": 14.5,
        "fuel_consumption_tpd": 42,
        "cargo_handling_capable_rate": 50000,
        "typical_use": "Very large cargo parcels and ports with sufficient draft and infrastructure",
    },
}

# ---------------------------------------------------------------------------
# Baseline freight rates ($/MT) per vessel class — used to seed synthetic
# historical series and as the "current rate" anchor in demo mode.
# ---------------------------------------------------------------------------
BASE_FREIGHT_RATES = {
    "Handysize": 18.0,
    "Supramax": 21.0,
    "Panamax": 24.5,
    "Capesize": 14.0,  # $/MT is lower on Capesize due to economies of scale on huge parcels
}

BUNKER_PRICE_USD_PER_TONNE = 620.0
CANAL_COST_USD = 0.0  # not applicable for these India east-coast routes in demo scope
PORT_COST_USD_PER_DAY = {
    "LOW": 6000,
    "MEDIUM": 9000,
    "HIGH": 14000,
}
