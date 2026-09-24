from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum

class AnomalyType(str, Enum):
    SPIKE = "SPIKE"
    DRIFT = "DRIFT"
    DROPOUT = "DROPOUT"
    STUCK_SENSOR = "STUCK_SENSOR"
    NONE = "NONE"

class SeverityLevel(str, Enum):
    IGNORE = "IGNORE"
    MONITOR = "MONITOR"
    URGENT = "URGENT"

class AnomalyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"

class Anomaly(BaseModel):
    anomaly_id: str
    machine_id: str
    sensor_type: str
    anomaly_type: str
    severity: str
    severity_score: float
    confidence: float
    current_value: Optional[float] = None
    baseline_value: float
    deviation: float
    timestamp: str
    duration: float = 0.0
    possible_cause: str
    recommended_action: str
    status: str = "ACTIVE"

class Alert(BaseModel):
    alert_id: str
    anomaly_id: str
    machine_id: str
    sensor_type: str
    severity: str
    severity_score: float
    timestamp: str
    status: str = "ACTIVE"
    message: str

class InjectionRequest(BaseModel):
    machine_id: str
    sensor_type: str
    magnitude: Optional[float] = None
    rate: Optional[float] = None
    duration_steps: Optional[int] = 30
