import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import Base, engine
from backend.app.shared.aisstream_client import stream_ais_data   # ADD THIS

from backend.app.features.arrival_board.models import VesselArrival
from backend.app.features.arrival_board.router import router as arrival_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    asyncio.create_task(stream_ais_data())    # ADD THIS LINE
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