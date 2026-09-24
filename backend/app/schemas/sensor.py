from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    VIBRATION = "vibration"
    PRESSURE = "pressure"
    RPM = "rpm"
    CURRENT = "current"

class SensorReading(BaseModel):
    timestamp: str
    machine_id: str
    sensor_type: str
    value: Optional[float] = None
    unit: str
    is_missing: bool = False

class SensorState(BaseModel):
    sensor_type: str
    unit: str
    baseline_value: float
    current_value: Optional[float] = None
    min_value: float
    max_value: float
    last_update: str
    status: str = "NORMAL" # NORMAL, ANOMALOUS
