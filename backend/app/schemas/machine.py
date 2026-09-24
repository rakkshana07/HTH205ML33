from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from app.schemas.sensor import SensorState

class CriticalityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class MachineStatus(str, Enum):
    HEALTHY = "HEALTHY"
    MONITORING = "MONITORING"
    URGENT = "URGENT"

class Machine(BaseModel):
    machine_id: str
    machine_name: str
    machine_type: str
    location: str
    criticality: str
    health_score: float = 100.0
    status: str = "HEALTHY"
    last_update: str
    sensors: Dict[str, SensorState] = {}
