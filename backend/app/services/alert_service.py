import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.schemas.anomaly import Alert, Anomaly

class AlertService:
    """
    Manages alert creation, deduplication/cooldown, grouping, and acknowledgement/resolution lifecycle.
    """
    def __init__(self):
        # Key: alert_id -> Alert
        self.alerts: Dict[str, Alert] = {}
        # Mapping: (machine_id, sensor_type) -> active alert_id
        self.active_alert_map: Dict[tuple, str] = {}

    def process_anomaly(self, anomaly: Anomaly) -> Optional[Alert]:
        """
        Route anomaly to Alert system if severity is MONITOR or URGENT.
        Applies deduplication cooldown so active anomalies update existing alerts.
        """
        if anomaly.severity == "IGNORE" or anomaly.anomaly_type == "NONE":
            return None

        key = (anomaly.machine_id, anomaly.sensor_type)
        existing_alert_id = self.active_alert_map.get(key)

        now_str = datetime.now(timezone.utc).isoformat()

        if existing_alert_id and existing_alert_id in self.alerts:
            alert = self.alerts[existing_alert_id]
            if alert.status != "RESOLVED":
                # Update existing alert (cooldown / deduplication)
                alert.severity = anomaly.severity
                alert.severity_score = anomaly.severity_score
                alert.timestamp = now_str
                alert.message = (
                    f"Active {anomaly.severity} {anomaly.anomaly_type} detected on "
                    f"{anomaly.machine_id} [{anomaly.sensor_type}]. {anomaly.possible_cause}"
                )
                return alert

        # Create new Alert
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        alert = Alert(
            alert_id=alert_id,
            anomaly_id=anomaly.anomaly_id,
            machine_id=anomaly.machine_id,
            sensor_type=anomaly.sensor_type,
            severity=anomaly.severity,
            severity_score=anomaly.severity_score,
            timestamp=now_str,
            status="ACTIVE",
            message=(
                f"{anomaly.severity} alert: {anomaly.anomaly_type} detected on "
                f"{anomaly.machine_id} [{anomaly.sensor_type}]. {anomaly.possible_cause}"
            )
        )
        self.alerts[alert_id] = alert
        self.active_alert_map[key] = alert_id
        return alert

    def acknowledge_alert(self, alert_id: str) -> Optional[Alert]:
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = "ACKNOWLEDGED"
        return alert

    def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        alert = self.alerts.get(alert_id)
        if alert:
            alert.status = "RESOLVED"
            key = (alert.machine_id, alert.sensor_type)
            if self.active_alert_map.get(key) == alert_id:
                del self.active_alert_map[key]
        return alert

    def get_alerts(
        self,
        machine_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Alert]:
        result = list(self.alerts.values())
        if machine_id:
            result = [a for a in result if a.machine_id == machine_id]
        if severity:
            result = [a for a in result if a.severity.upper() == severity.upper()]
        if status:
            result = [a for a in result if a.status.upper() == status.upper()]
        # Sort by timestamp descending
        result.sort(key=lambda a: a.timestamp, reverse=True)
        return result

    def clear_all(self):
        self.alerts.clear()
        self.active_alert_map.clear()

alert_service = AlertService()
