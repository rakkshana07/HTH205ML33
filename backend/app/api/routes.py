from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
import asyncio
import json

from app.config import settings
from app.simulation.simulator import simulator
from app.simulation.injection import injection_manager
from app.services.simulation_service import simulation_service
from app.services.anomaly_service import anomaly_service
from app.services.alert_service import alert_service
from app.schemas.anomaly import InjectionRequest

router = APIRouter()

# ----------------------------------------------------
# HEALTH ENDPOINT
# ----------------------------------------------------
@router.get("/health")
def get_health():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION
    }

# ----------------------------------------------------
# MACHINES API
# ----------------------------------------------------
@router.get("/machines")
def get_machines():
    return list(simulator.machines.values())

@router.get("/machines/{machine_id}")
def get_machine(machine_id: str):
    machine = simulator.machines.get(machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine '{machine_id}' not found.")
    return machine

# ----------------------------------------------------
# SENSORS & LIVE DATA API
# ----------------------------------------------------
@router.get("/sensors")
def get_sensors():
    all_sensors = []
    for m_id, machine in simulator.machines.items():
        for s_type, s_state in machine.sensors.items():
            all_sensors.append({
                "machine_id": m_id,
                "machine_name": machine.machine_name,
                "sensor_type": s_type,
                "unit": s_state.unit,
                "baseline_value": s_state.baseline_value,
                "current_value": s_state.current_value,
                "status": s_state.status,
                "last_update": s_state.last_update
            })
    return all_sensors

@router.get("/live-data")
def get_live_data():
    """
    Returns current live state of all machines, sensors, and active anomalies.
    Enables polling fallback for frontend dashboards.
    """
    res = simulation_service.tick()
    return {
        "timestamp": res["readings"][0].timestamp if res["readings"] else None,
        "machines": list(simulator.machines.values()),
        "active_anomalies": anomaly_service.get_active_anomalies(),
        "readings": res["readings"]
    }

# ----------------------------------------------------
# ANOMALIES API
# ----------------------------------------------------
@router.get("/anomalies")
def get_anomalies(
    machine_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    return anomaly_service.get_anomalies(machine_id=machine_id, severity=severity, status=status)

@router.get("/anomalies/{anomaly_id}")
def get_anomaly(anomaly_id: str):
    anom = anomaly_service.anomalies.get(anomaly_id)
    if not anom:
        raise HTTPException(status_code=404, detail=f"Anomaly '{anomaly_id}' not found.")
    return anom

# ----------------------------------------------------
# ALERTS API
# ----------------------------------------------------
@router.get("/alerts")
def get_alerts(
    machine_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    return alert_service.get_alerts(machine_id=machine_id, severity=severity, status=status)

@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str):
    alert = alert_service.acknowledge_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")
    return alert

@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    alert = alert_service.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")
    return alert

# ----------------------------------------------------
# ANALYTICS API
# ----------------------------------------------------
@router.get("/analytics")
def get_analytics():
    return simulation_service.get_analytics()

# ----------------------------------------------------
# SIMULATION CONTROL API
# ----------------------------------------------------
@router.post("/simulation/start")
def start_simulation():
    simulator.start()
    return {"status": "started", "message": "Simulation streaming started."}

@router.post("/simulation/pause")
def pause_simulation():
    simulator.pause()
    return {"status": "paused", "message": "Simulation streaming paused."}

@router.post("/simulation/stop")
def stop_simulation():
    simulator.stop()
    return {"status": "stopped", "message": "Simulation streaming stopped."}

@router.post("/simulation/reset")
def reset_simulation():
    simulation_service.reset_all()
    return {"status": "reset", "message": "Simulation reset to baseline clean operational state."}

# ----------------------------------------------------
# ANOMALY INJECTION API
# ----------------------------------------------------
@router.post("/simulation/inject/spike")
def inject_spike(req: InjectionRequest):
    if req.machine_id not in simulator.machines:
        raise HTTPException(status_code=404, detail=f"Machine '{req.machine_id}' not found.")
    inj = injection_manager.inject(
        machine_id=req.machine_id,
        sensor_type=req.sensor_type,
        injection_type="SPIKE",
        magnitude=req.magnitude,
        duration_steps=req.duration_steps or 30
    )
    return {
        "status": "injected",
        "injection_type": "SPIKE",
        "machine_id": req.machine_id,
        "sensor_type": req.sensor_type,
        "magnitude": inj.magnitude
    }

@router.post("/simulation/inject/drift")
def inject_drift(req: InjectionRequest):
    if req.machine_id not in simulator.machines:
        raise HTTPException(status_code=404, detail=f"Machine '{req.machine_id}' not found.")
    inj = injection_manager.inject(
        machine_id=req.machine_id,
        sensor_type=req.sensor_type,
        injection_type="DRIFT",
        magnitude=req.magnitude or 2.0,
        duration_steps=req.duration_steps or 40
    )
    return {
        "status": "injected",
        "injection_type": "DRIFT",
        "machine_id": req.machine_id,
        "sensor_type": req.sensor_type,
        "rate": inj.magnitude
    }

@router.post("/simulation/inject/dropout")
def inject_dropout(req: InjectionRequest):
    if req.machine_id not in simulator.machines:
        raise HTTPException(status_code=404, detail=f"Machine '{req.machine_id}' not found.")
    inj = injection_manager.inject(
        machine_id=req.machine_id,
        sensor_type=req.sensor_type,
        injection_type="DROPOUT",
        duration_steps=req.duration_steps or 20
    )
    return {
        "status": "injected",
        "injection_type": "DROPOUT",
        "machine_id": req.machine_id,
        "sensor_type": req.sensor_type
    }

@router.post("/simulation/inject/stuck")
def inject_stuck(req: InjectionRequest):
    if req.machine_id not in simulator.machines:
        raise HTTPException(status_code=404, detail=f"Machine '{req.machine_id}' not found.")
    inj = injection_manager.inject(
        machine_id=req.machine_id,
        sensor_type=req.sensor_type,
        injection_type="STUCK",
        duration_steps=req.duration_steps or 40
    )
    return {
        "status": "injected",
        "injection_type": "STUCK",
        "machine_id": req.machine_id,
        "sensor_type": req.sensor_type
    }
