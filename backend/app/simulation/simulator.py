import time
import random
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

from app.schemas.machine import Machine
from app.schemas.sensor import SensorState, SensorReading
from app.simulation.injection import injection_manager

SENSOR_PROFILES = {
    "temperature": {"baseline": 65.0, "std": 1.5, "unit": "°C", "min": 20.0, "max": 150.0},
    "vibration": {"baseline": 2.5, "std": 0.2, "unit": "mm/s", "min": 0.0, "max": 50.0},
    "pressure": {"baseline": 6.0, "std": 0.3, "unit": "bar", "min": 0.0, "max": 30.0},
    "rpm": {"baseline": 1750.0, "std": 15.0, "unit": "RPM", "min": 0.0, "max": 3500.0},
    "current": {"baseline": 24.0, "std": 0.8, "unit": "A", "min": 0.0, "max": 100.0},
}

INITIAL_MACHINES_CONFIG = [
    {"id": "MACHINE-01", "name": "Main Steam Turbine Generator", "type": "Steam Turbine", "location": "Power House - Bay A", "criticality": "HIGH"},
    {"id": "MACHINE-02", "name": "Boiler Feedwater Pump 1A", "type": "Centrifugal Pump", "location": "Boiler Room - Sector 1", "criticality": "HIGH"},
    {"id": "MACHINE-03", "name": "Primary Air Compressor Alpha", "type": "Rotary Screw Compressor", "location": "Utility Hall", "criticality": "MEDIUM"},
    {"id": "MACHINE-04", "name": "Hydraulic Stamping Press 04", "type": "Hydraulic Press", "location": "Heavy Fabrication Shop", "criticality": "HIGH"},
    {"id": "MACHINE-05", "name": "Industrial Cooling Tower Fan 02", "type": "Axial Fan", "location": "Cooling Yard", "criticality": "MEDIUM"},
    {"id": "MACHINE-06", "name": "Line 3 Main Conveyor Drive", "type": "Induction Motor", "location": "Packaging Line 3", "criticality": "LOW"},
    {"id": "MACHINE-07", "name": "CNC Multi-Axis Milling Center", "type": "Machining Center", "location": "Precision Machining Bay", "criticality": "MEDIUM"},
    {"id": "MACHINE-08", "name": "Main Substation Transformer T1", "type": "Power Transformer", "location": "Substation Yard", "criticality": "HIGH"},
    {"id": "MACHINE-09", "name": "Process Exhaust Blower 09", "type": "Exhaust Fan", "location": "Ducting Deck", "criticality": "LOW"},
    {"id": "MACHINE-10", "name": "Chemical Reactor Agitator Pump", "type": "Dosing Pump", "location": "Chemical Plant Bay C", "criticality": "MEDIUM"},
]

class StreamingSimulator:
    """
    Simulates streaming sensor readings for 10 industrial machines across 5 sensors.
    Maintains history windows, controls state, and applies injection rules.
    """
    def __init__(self, history_max_len: int = 100):
        self.history_max_len = history_max_len
        self.is_running: bool = True
        self.is_paused: bool = False
        self.step_count: int = 0
        self.machines: Dict[str, Machine] = {}
        # History map: (machine_id, sensor_type) -> List[Optional[float]]
        self.history: Dict[Tuple[str, str], List[Optional[float]]] = {}
        
        self.reset()

    def reset(self):
        """
        Reset simulator state, clear active injections, initialize machines and pre-seed warm-up history.
        """
        self.is_running = True
        self.is_paused = False
        self.step_count = 0
        self.machines.clear()
        self.history.clear()
        injection_manager.clear_all()

        now_str = datetime.now(timezone.utc).isoformat()

        # Build 10 machines with 5 sensors each
        for cfg in INITIAL_MACHINES_CONFIG:
            m_id = cfg["id"]
            sensors_dict = {}
            for s_type, prof in SENSOR_PROFILES.items():
                sensors_dict[s_type] = SensorState(
                    sensor_type=s_type,
                    unit=prof["unit"],
                    baseline_value=prof["baseline"],
                    current_value=prof["baseline"],
                    min_value=prof["min"],
                    max_value=prof["max"],
                    last_update=now_str,
                    status="NORMAL"
                )

            machine = Machine(
                machine_id=m_id,
                machine_name=cfg["name"],
                machine_type=cfg["type"],
                location=cfg["location"],
                criticality=cfg["criticality"],
                health_score=100.0,
                status="HEALTHY",
                last_update=now_str,
                sensors=sensors_dict
            )
            self.machines[m_id] = machine

        # Pre-seed warm-up history (30 steps of clean normal baseline data)
        self._warmup_history(steps=30)

    def _warmup_history(self, steps: int = 30):
        """
        Pre-fill sensor history with clean baseline values + tiny noise
        so detector starts with warm normal statistics.
        """
        np.random.seed(123)
        for m_id, machine in self.machines.items():
            for s_type, prof in SENSOR_PROFILES.items():
                key = (m_id, s_type)
                self.history[key] = []
                base = prof["baseline"]
                std = prof["std"]
                for _ in range(steps):
                    val = float(np.random.normal(base, std * 0.3))
                    self.history[key].append(val)
                # Update current_value in sensor state
                machine.sensors[s_type].current_value = round(self.history[key][-1], 2)

    def step() -> List[SensorReading]:
        """
        Execute one simulation tick. Generates new sensor readings for all machines & sensors.
        """
        pass

    def step_simulation(self) -> List[SensorReading]:
        if not self.is_running or self.is_paused:
            return []

        self.step_count += 1
        now_str = datetime.now(timezone.utc).isoformat()
        new_readings: List[SensorReading] = []

        for m_id, machine in self.machines.items():
            machine.last_update = now_str
            for s_type, prof in SENSOR_PROFILES.items():
                base = prof["baseline"]
                std = prof["std"]

                # 1. Normal stochastic signal (baseline + noise)
                raw_noise = float(np.random.normal(0, std * 0.4))
                raw_value = round(base + raw_noise, 3)

                # 2. Apply active anomaly injections if present
                final_val, is_injected = injection_manager.modify_reading(
                    machine_id=m_id,
                    sensor_type=s_type,
                    raw_value=raw_value,
                    step_count=self.step_count
                )

                if final_val is not None:
                    final_val = round(final_val, 2)

                # 3. Update history window
                key = (m_id, s_type)
                if key not in self.history:
                    self.history[key] = []

                self.history[key].append(final_val)
                if len(self.history[key]) > self.history_max_len:
                    self.history[key].pop(0)

                # Update machine sensor state
                machine.sensors[s_type].current_value = final_val
                machine.sensors[s_type].last_update = now_str

                # Create SensorReading payload
                reading = SensorReading(
                    timestamp=now_str,
                    machine_id=m_id,
                    sensor_type=s_type,
                    value=final_val,
                    unit=prof["unit"],
                    is_missing=(final_val is None)
                )
                new_readings.append(reading)

        return new_readings

    def start(self):
        self.is_running = True
        self.is_paused = False

    def pause(self):
        self.is_paused = True

    def stop(self):
        self.is_running = False
        self.is_paused = False

simulator = StreamingSimulator()
