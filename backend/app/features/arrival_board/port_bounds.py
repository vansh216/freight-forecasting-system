# Rough bounding boxes (lat_min, lat_max, lon_min, lon_max) around each port
PORT_BOUNDING_BOXES = {
    "GlobalTest": {"lat_min": -60.0, "lat_max": 70.0, "lon_min": -180.0, "lon_max": 180.0},
}



def get_port_for_coordinates(lat: float, lon: float):
    for port_name, box in PORT_BOUNDING_BOXES.items():
        if box["lat_min"] <= lat <= box["lat_max"] and box["lon_min"] <= lon <= box["lon_max"]:
            return port_name
    return None