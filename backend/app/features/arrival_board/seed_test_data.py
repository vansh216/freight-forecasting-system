from datetime import datetime, timedelta
import random

from backend.app.core.database import SessionLocal, engine, Base
from backend.app.features.arrival_board.models import VesselArrival

# Port center coordinates (from your earlier lookups)
PORT_CENTERS = {
    "Paradip":    (20.2722, 86.6741),
    "Vizag":      (17.6859, 83.2975),
    "Gangavaram": (17.6169, 83.2361),
    "Gopalpur":   (19.2843, 84.9521),
    "Dhamra":     (20.8323, 86.9855),
    "Haldia":     (22.0247, 88.0857),
}

# Real ship names pulled from live AIS traffic (repurposed for demo realism)
DEMO_SHIP_NAMES = [
    "COSCO ARGENTINA", "GUANGZHOU HIGHWAY", "SOARER LAKE", "PACIFIC TRUST",
    "SEA SPARKLE", "MORNING STAR", "MERIDIAN STAR", "DIAMOND EXPRESS",
    "SUNNY SAIL NO.2", "SEA SPIRIT", "YUE HANG 307", "SHINING STAR",
    "SOLAR STAR", "SCT SHEKOU", "UNIVERSAL MK2004",
]

STATUSES = ["en_route", "arrived", "departed"]


def random_offset(center_lat, center_lon):
    """Small random jitter (~5-15km) so ships don't all stack on the exact port point."""
    return (
        center_lat + random.uniform(-0.08, 0.08),
        center_lon + random.uniform(-0.08, 0.08),
    )


def random_mmsi():
    return str(random.randint(200000000, 799999999))


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_count = db.query(VesselArrival).count()
        if existing_count > 0:
            print(f"Already have {existing_count} vessels — skipping seed. "
                  f"Delete rows first if you want to reseed.")
            return

        vessels = []
        name_pool = DEMO_SHIP_NAMES.copy()
        random.shuffle(name_pool)

        for port_name, (lat, lon) in PORT_CENTERS.items():
            # 2-3 ships per port for a realistic-looking board
            num_ships = random.randint(2, 3)
            for _ in range(num_ships):
                if not name_pool:
                    name_pool = DEMO_SHIP_NAMES.copy()
                    random.shuffle(name_pool)
                ship_name = name_pool.pop()

                ship_lat, ship_lon = random_offset(lat, lon)
                status = random.choice(STATUSES)
                minutes_ago = random.randint(1, 180)

                vessels.append(
                    VesselArrival(
                        vessel_name=ship_name,
                        mmsi=random_mmsi(),
                        port=port_name,
                        latitude=round(ship_lat, 6),
                        longitude=round(ship_lon, 6),
                        status=status,
                        last_updated=datetime.utcnow() - timedelta(minutes=minutes_ago),
                    )
                )

        db.add_all(vessels)
        db.commit()
        print(f"Seeded {len(vessels)} vessels across {len(PORT_CENTERS)} ports.")

        for v in vessels:
            print(f"  {v.vessel_name:<25} -> {v.port:<12} [{v.status}]")

    finally:
        db.close()


if __name__ == "__main__":
    seed()