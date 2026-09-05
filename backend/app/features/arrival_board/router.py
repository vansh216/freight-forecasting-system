from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from backend.app.core.database import get_db
from backend.app.features.arrival_board.schema import ArrivalResponse
from backend.app.features.arrival_board.service import get_arrivals

router = APIRouter()


@router.get("/arrivals", response_model=List[ArrivalResponse])
def get_arrivals_endpoint(port: Optional[str] = None, db: Session = Depends(get_db)):
    return get_arrivals(db, port=port)