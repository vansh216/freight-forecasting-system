import asyncio
import json
import websockets
from datetime import datetime

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.features.arrival_board.models import VesselArrival
from backend.app.features.arrival_board.port_bounds import get_port_for_coordinates, PORT_BOUNDING_BOXES


async def stream_ais_data():
    """
    Connects to aisstream.io, filters ships near our 3 India ports,
    and writes their latest position/status into PostgreSQL.
    Run this as a background task when the app starts.
    """
    url = "wss://stream.aisstream.io/v0/stream"

    # Combine all 3 port bounding boxes into one subscription area
    bounding_boxes = [[
        [box["lat_min"], box["lon_min"]],
        [box["lat_max"], box["lon_max"]]
    ] for box in PORT_BOUNDING_BOXES.values()]

    subscribe_message = {
        "APIKey": settings.aisstream_api_key,
        "BoundingBoxes": bounding_boxes,
    }

    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(subscribe_message))

        async for message_json in websocket:
            message = json.loads(message_json)

            if message.get("MessageType") == "PositionReport":
                report = message["Message"]["PositionReport"]
                meta = message.get("MetaData", {})

                lat = report.get("Latitude")
                lon = report.get("Longitude")
                mmsi = str(meta.get("MMSI", ""))
                vessel_name = meta.get("ShipName", "Unknown").strip()

                port = get_port_for_coordinates(lat, lon)
                if port is None:
                    continue  # not near any of our tracked ports, skip

                save_vessel_update(mmsi, vessel_name, port, lat, lon)




async def stream_ais_data():
    url = "wss://stream.aisstream.io/v0/stream"

    bounding_boxes = [[
        [box["lat_min"], box["lon_min"]],
        [box["lat_max"], box["lon_max"]]
    ] for box in PORT_BOUNDING_BOXES.values()]

    subscribe_message = {
        "APIKey": settings.aisstream_api_key,
        "BoundingBoxes": bounding_boxes,
    }

    print(">>> Connecting to aisstream.io...")
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(subscribe_message))
        print(">>> Subscribed. Waiting for messages...")

        async for message_json in websocket:
            message = json.loads(message_json)
            print(">>> Received message type:", message.get("MessageType"))  # ADD THIS

            if message.get("MessageType") == "PositionReport":
                report = message["Message"]["PositionReport"]
                meta = message.get("MetaData", {})

                lat = report.get("Latitude")
                lon = report.get("Longitude")
                mmsi = str(meta.get("MMSI", ""))
                vessel_name = meta.get("ShipName", "Unknown").strip()

                port = get_port_for_coordinates(lat, lon)
                print(f">>> Ship {vessel_name} at ({lat},{lon}) -> matched port: {port}")  # ADD THIS

                if port is None:
                    continue

                save_vessel_update(mmsi, vessel_name, port, lat, lon)


def save_vessel_update(mmsi, vessel_name, port, lat, lon):
    db = SessionLocal()
    try:
        vessel = db.query(VesselArrival).filter_by(mmsi=mmsi).first()
        if vessel:
            vessel.port = port
            vessel.latitude = lat
            vessel.longitude = lon
            vessel.last_updated = datetime.utcnow()
        else:
            vessel = VesselArrival(
                vessel_name=vessel_name,
                mmsi=mmsi,
                port=port,
                latitude=lat,
                longitude=lon,
                status="en_route",
                last_updated=datetime.utcnow(),
            )
            db.add(vessel)
        db.commit()
        print(f">>> SAVED: {vessel_name} ({mmsi}) at {port}")   
    except Exception as e:
        print(f">>> ERROR saving vessel: {e}")
    finally:
        db.close()