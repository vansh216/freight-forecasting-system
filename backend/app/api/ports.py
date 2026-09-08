from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core import crud

router = APIRouter(prefix="/api/ports", tags=["ports"])


@router.get("")
def list_ports(db: Session = Depends(get_db)):
    ports = crud.get_all_ports(db)
    return [
        {
            "port_name": p.port_name, "country": p.country, "max_loa": p.max_loa,
            "max_beam": p.max_beam, "max_draft": p.max_draft, "channel_depth": p.channel_depth,
            "berth_depth": p.berth_depth, "cargo_handling_rate": p.cargo_handling_rate,
            "max_vessel_dwt": p.max_vessel_dwt, "congestion_level": p.congestion_level,
            "berthing_restriction": p.berthing_restriction,
        }
        for p in ports
    ]


@router.get("/{port_name}")
def get_port(port_name: str, db: Session = Depends(get_db)):
    p = crud.get_port(db, port_name)
    if not p:
        raise HTTPException(status_code=404, detail=f"Port '{port_name}' not found")
    return {
        "port_name": p.port_name, "country": p.country, "max_loa": p.max_loa,
        "max_beam": p.max_beam, "max_draft": p.max_draft, "channel_depth": p.channel_depth,
        "berth_depth": p.berth_depth, "cargo_handling_rate": p.cargo_handling_rate,
        "max_vessel_dwt": p.max_vessel_dwt, "congestion_level": p.congestion_level,
        "berthing_restriction": p.berthing_restriction,
    }
