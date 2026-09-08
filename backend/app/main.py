import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import Base, engine
from backend.app.shared.aisstream_client import stream_ais_data   # ADD THIS

from backend.app.features.arrival_board.models import VesselArrival
from backend.app.features.arrival_board.router import router as arrival_router
from backend.app.features.freight_forecast.router import router as freight_router
from backend.app.features.vessel_recomendation.router import router as vessel_recmdtion
from backend.app.api import vessel, charter,risk,ports,meta



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(stream_ais_data())    
    yield


app = FastAPI(
    title="Freight Forecasting & Vessel Recommendation API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Freight backend is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(arrival_router, prefix="/api", tags=["Arrival Board"])
app.include_router(freight_router,prefix='/api', tags=["freight_forecast"])
app.include_router(vessel_recmdtion,prefix='/api', tags=["vessel_recommedation"])

app.include_router(vessel.router)
app.include_router(charter.router)
app.include_router(risk.router)
app.include_router(ports.router)
app.include_router(meta.router)