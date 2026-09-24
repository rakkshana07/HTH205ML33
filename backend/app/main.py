import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Set

from app.config import settings
from app.api.routes import router as api_router
from app.services.simulation_service import simulation_service
from app.simulation.simulator import simulator

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"Severity-Aware Streaming Anomaly Detector for Industrial Sensors. {settings.TAGLINE}",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for future React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Active WebSocket connections pool
active_websockets: Set[WebSocket] = set()

@app.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        while True:
            # Send live updates every interval
            await asyncio.sleep(settings.SIMULATION_INTERVAL_SEC)
            if simulator.is_running and not simulator.is_paused:
                res = simulation_service.tick()
                payload = {
                    "event": "live_update",
                    "readings": [r.model_dump() for r in res["readings"]],
                    "anomalies": [a.model_dump() for a in res["anomalies"]],
                    "active_anomaly_count": res["active_anomaly_count"]
                }
                await websocket.send_text(json_dumps(payload))
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

def json_dumps(obj):
    import json
    return json.dumps(obj, default=str)

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
