import uuid
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

from app.schemas.sensor import SensorReading
from app.schemas.anomaly import Anomaly
from app.ml.features import extract_features
from app.ml.detector import detector
from app.ml.classification import classify_anomaly
from app.ml.severity import calculate_severity_and_confidence
from app.ml.explanation import generate_explanation_and_action
from app.simulation.simulator import simulator, SENSOR_PROFILES
from app.services.alert_service import alert_service

class AnomalyService:
    """
    Core engine running feature extraction, ML detection, classification,
    severity calculation, explanation, and anomaly state tracking.
    """
    def __init__(self):
        # All detected anomalies (history list)
        self.anomalies: Dict[str, Anomaly] = {}
        # Active anomaly map: (machine_id, sensor_type) -> Anomaly
        self.active_anomalies: Dict[Tuple[str, str], Anomaly] = {}

    def process_reading(self, reading: SensorReading) -> Optional[Anomaly]:
        m_id = reading.machine_id
        s_type = reading.sensor_type
        key = (m_id, s_type)

        machine = simulator.machines.get(m_id)
        machine_criticality = machine.criticality if machine else "MEDIUM"

        prof = SENSOR_PROFILES.get(s_type, {"baseline": 50.0, "std": 1.0})
        baseline_val = prof["baseline"]
        std_baseline = prof["std"]

        # Fetch history for feature extraction
        history_seq = simulator.history.get(key, [])
        features = extract_features(
            history=history_seq,
            baseline_value=baseline_val,
            current_value=reading.value
        )

        # Step 1: ML Isolation Forest Detection
        is_ml_anom, ml_score = detector.predict(s_type, features)

        # Step 2: Anomaly Classification
        anom_type = classify_anomaly(
            features=features,
            is_ml_anomaly=is_ml_anom,
            anomaly_score=ml_score,
            std_baseline=std_baseline
        )

        now_str = datetime.now(timezone.utc).isoformat()

        # Step 3: Handle Normal Behavior (CLEAR ACTIVE ANOMALY)
        if anom_type == "NONE":
            if key in self.active_anomalies:
                active_anom = self.active_anomalies[key]
                active_anom.status = "RESOLVED"
                del self.active_anomalies[key]
                if machine:
                    machine.sensors[s_type].status = "NORMAL"
            return None

        # Determine duration steps if anomaly already active
        existing = self.active_anomalies.get(key)
        duration_steps = (existing.duration + 1) if existing else 1

        # Step 4: Calculate Severity and Confidence
        sev_score, sev_level, confidence = calculate_severity_and_confidence(
            anomaly_type=anom_type,
            features=features,
            ml_anomaly_score=ml_score,
            machine_criticality=machine_criticality,
            sensor_type=s_type,
            std_baseline=std_baseline,
            duration_steps=duration_steps
        )

        # Step 5: Root-Cause Hint & Recommended Action
        cause, action = generate_explanation_and_action(
            sensor_type=s_type,
            anomaly_type=anom_type,
            severity=sev_level
        )

        # Deviation calculation
        dev = features["baseline_deviation"]

        # Step 6: Create / Update Anomaly Object
        if existing and existing.status != "RESOLVED":
            existing.anomaly_type = anom_type
            existing.severity = sev_level
            existing.severity_score = sev_score
            existing.confidence = confidence
            existing.current_value = reading.value
            existing.deviation = round(dev, 2)
            existing.duration = duration_steps
            existing.timestamp = now_str
            existing.possible_cause = cause
            existing.recommended_action = action
            anomaly_obj = existing
        else:
            anom_id = f"ANM-{uuid.uuid4().hex[:8].upper()}"
            anomaly_obj = Anomaly(
                anomaly_id=anom_id,
                machine_id=m_id,
                sensor_type=s_type,
                anomaly_type=anom_type,
                severity=sev_level,
                severity_score=sev_score,
                confidence=confidence,
                current_value=reading.value,
                baseline_value=baseline_val,
                deviation=round(dev, 2),
                timestamp=now_str,
                duration=1,
                possible_cause=cause,
                recommended_action=action,
                status="ACTIVE"
            )
            self.anomalies[anom_id] = anomaly_obj
            self.active_anomalies[key] = anomaly_obj

        if machine:
            machine.sensors[s_type].status = "ANOMALOUS"

        # Step 7: Route to Alert Service
        alert_service.process_anomaly(anomaly_obj)

        return anomaly_obj

    def get_anomalies(
        self,
        machine_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Anomaly]:
        result = list(self.anomalies.values())
        if machine_id:
            result = [a for a in result if a.machine_id == machine_id]
        if severity:
            result = [a for a in result if a.severity.upper() == severity.upper()]
        if status:
            result = [a for a in result if a.status.upper() == status.upper()]
        result.sort(key=lambda a: a.timestamp, reverse=True)
        return result

    def get_active_anomalies(self) -> List[Anomaly]:
        return list(self.active_anomalies.values())

    def clear_all(self):
        self.anomalies.clear()
        self.active_anomalies.clear()

anomaly_service = AnomalyService()
