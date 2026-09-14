import json
import asyncio
from datetime import datetime

import websockets

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.features.arrival_board.models import VesselArrival
from backend.app.features.arrival_board.port_bounds import (
    SUBSCRIPTION_BOX,
    get_port_for_coordinates,
)

# In-memory buffer — collects updates, flushed to DB periodically instead of per-message
_vessel_buffer = {}
_buffer_lock = asyncio.Lock()


async def stream_ais_data():
    url = "wss://stream.aisstream.io/v0/stream"

    bounding_boxes = [[
        [SUBSCRIPTION_BOX["lat_min"], SUBSCRIPTION_BOX["lon_min"]],
        [SUBSCRIPTION_BOX["lat_max"], SUBSCRIPTION_BOX["lon_max"]],
    ]]

    subscribe_message = {
        "APIKey": settings.aisstream_api_key,
        "BoundingBoxes": bounding_boxes,
    }

    # Start the periodic flush task alongside the listener
    asyncio.create_task(periodic_flush())

    while True:
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(json.dumps(subscribe_message))
                print(">>> Subscribed. Waiting for messages...")

                async for message_json in websocket:
                    message = json.loads(message_json)

                    if message.get("MessageType") == "PositionReport":
                        report = message["Message"]["PositionReport"]
                        meta = message.get("MetaData", {})

                        lat = report.get("Latitude")
                        lon = report.get("Longitude")
                        mmsi = str(meta.get("MMSI", ""))
                        vessel_name = meta.get("ShipName", "Unknown").strip()

                        if not mmsi or lat is None or lon is None:
                            continue

                        port = get_port_for_coordinates(lat, lon) or "Unclassified"

                        # Just update the in-memory buffer — no DB call here
                        async with _buffer_lock:
                            _vessel_buffer[mmsi] = {
                                "vessel_name": vessel_name,
                                "port": port,
                                "latitude": lat,
                                "longitude": lon,
                                "status": "en_route",
                                "last_updated": datetime.utcnow(),
                            }

        except Exception as e:
            print(f">>> AIS stream error: {e}, reconnecting in 5s...")
            await asyncio.sleep(5)


async def periodic_flush(interval_seconds: int = 10):
    """Flush the in-memory buffer to Postgres every N seconds in one batch, not per-message."""
    while True:
        await asyncio.sleep(interval_seconds)
        await flush_buffer_to_db()


async def flush_buffer_to_db():
    async with _buffer_lock:
        if not _vessel_buffer:
            return
        batch = dict(_vessel_buffer)
        _vessel_buffer.clear()

    db = SessionLocal()
    try:
        mmsis = list(batch.keys())
        existing = {
            v.mmsi: v
            for v in db.query(VesselArrival).filter(VesselArrival.mmsi.in_(mmsis)).all()
        }

        new_rows = []
        for mmsi, data in batch.items():
            if mmsi in existing:
                vessel = existing[mmsi]
                vessel.vessel_name = data["vessel_name"]
                vessel.port = data["port"]
                vessel.latitude = data["latitude"]
                vessel.longitude = data["longitude"]
                vessel.status = data["status"]
                vessel.last_updated = data["last_updated"]
            else:
                new_rows.append(VesselArrival(mmsi=mmsi, **data))

        if new_rows:
            db.bulk_save_objects(new_rows)

        db.commit()
        print(f">>> Flushed {len(batch)} vessel updates to DB "
              f"({len(new_rows)} new, {len(batch) - len(new_rows)} updated)")
    except Exception as e:
        db.rollback()
        print(f">>> Error flushing buffer: {e}")
    finally:
        db.close()