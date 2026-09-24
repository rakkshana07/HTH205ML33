from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ActiveInjection:
    machine_id: str
    sensor_type: str
    injection_type: str # SPIKE, DRIFT, DROPOUT, STUCK
    magnitude: float
    start_step: int
    duration_steps: int = 50 # steps duration
    stuck_value: Optional[float] = None

class InjectionManager:
    """
    Manages stateful anomaly injection rules for machines and sensors.
    """
    def __init__(self):
        # Key: (machine_id, sensor_type) -> ActiveInjection
        self.injections: Dict[Tuple[str, str], ActiveInjection] = {}

    def inject(
        self,
        machine_id: str,
        sensor_type: str,
        injection_type: str,
        magnitude: Optional[float] = None,
        duration_steps: int = 50
    ) -> ActiveInjection:
        """
        Register an active injection rule on machine_id & sensor_type.
        """
        # Default magnitudes based on sensor type if not provided
        if magnitude is None:
            default_mags = {
                "temperature": 40.0,
                "vibration": 15.0,
                "pressure": 25.0,
                "rpm": 800.0,
                "current": 35.0
            }
            magnitude = default_mags.get(sensor_type.lower(), 20.0)

        inj = ActiveInjection(
            machine_id=machine_id,
            sensor_type=sensor_type,
            injection_type=injection_type.upper(),
            magnitude=magnitude,
            start_step=0,
            duration_steps=duration_steps
        )
        self.injections[(machine_id, sensor_type)] = inj
        return inj

    def clear_injection(self, machine_id: str, sensor_type: str):
        key = (machine_id, sensor_type)
        if key in self.injections:
            del self.injections[key]

    def clear_all(self):
        self.injections.clear()

    def modify_reading(
        self,
        machine_id: str,
        sensor_type: str,
        raw_value: float,
        step_count: int
    ) -> Tuple[Optional[float], bool]:
        """
        Apply active injection rules to raw sensor output.
        Returns: (modified_value, is_injected)
        """
        key = (machine_id, sensor_type)
        if key not in self.injections:
            return raw_value, False

        inj = self.injections[key]
        if inj.start_step == 0:
            inj.start_step = step_count

        elapsed = step_count - inj.start_step

        if inj.duration_steps > 0 and elapsed > inj.duration_steps:
            # Injection expired
            del self.injections[key]
            return raw_value, False

        itype = inj.injection_type
        if itype == "SPIKE":
            # Sudden large offset
            return raw_value + inj.magnitude, True

        elif itype == "DRIFT":
            # Gradual sustained movement away from baseline
            # Rate per step = magnitude / 10.0
            drift_offset = (inj.magnitude / 10.0) * (elapsed + 1)
            return raw_value + drift_offset, True

        elif itype == "DROPOUT":
            # Missing / Null / NaN value
            return None, True

        elif itype == "STUCK":
            # Output repeated identical value with zero noise
            if inj.stuck_value is None:
                inj.stuck_value = raw_value
            return inj.stuck_value, True

        return raw_value, False

injection_manager = InjectionManager()
