from sqlalchemy.orm import Session
from backend.app.features.arrival_board.models import VesselArrival


def get_live_vessels(db: Session, port: str = None):
    query = db.query(VesselArrival).filter(
        VesselArrival.latitude.isnot(None),
        VesselArrival.longitude.isnot(None),
    )
    if port:
        query = query.filter(VesselArrival.port == port)
    return query.order_by(VesselArrival.last_updated.desc()).all()