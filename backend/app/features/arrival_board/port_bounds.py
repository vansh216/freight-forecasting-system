# Used ONLY for classifying which port a ship is near, after receiving its position.
PORT_CLASSIFICATION_BOXES = {
    "Paradip":    {"lat_min": -10.912, "lat_max": 5.632, "lon_min": 105.296, "lon_max": 115.052},
    "Visakhapatnam":      {"lat_min": -10.326, "lat_max": 10.046, "lon_min": 90.919, "lon_max": 120.675},
    "Gangavaram": {"lat_min": -10.257, "lat_max": 17.977, "lon_min": 70.858, "lon_max": 90.614},
    "Gopalpur":   {"lat_min": -10.924, "lat_max": 25.644, "lon_min": 60.570, "lon_max": 108.334},
    "Dhamra":     {"lat_min": -10.472, "lat_max": 34.192, "lon_min": 120.599, "lon_max": 130.371},
    "Haldia":     {"lat_min": -1.665, "lat_max": 44.385, "lon_min": 70.697, "lon_max": 100.474},
}

# Used for the actual aisstream.io SUBSCRIPTION — one wide box, proven to return ships.
SUBSCRIPTION_BOX = {"lat_min": -10, "lat_max": 40, "lon_min": 40, "lon_max": 120.0}


def get_port_for_coordinates(lat, lon):
    for port_name, box in PORT_CLASSIFICATION_BOXES.items():
        if box["lat_min"] <= lat <= box["lat_max"] and box["lon_min"] <= lon <= box["lon_max"]:
            return port_name
    return None