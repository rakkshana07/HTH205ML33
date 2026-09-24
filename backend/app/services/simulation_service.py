import asyncio
from typing import Dict, List, Any
from app.simulation.simulator import simulator
from app.simulation.injection import injection_manager
from app.services.anomaly_service import anomaly_service
from app.services.alert_service import alert_service

class SimulationService:
    """
    Service managing background streaming simulation, machine health score aggregation,
    and injection controls.
    """
    def __init__(self):
        self._loop_task: asyncio.Task = None

    def tick(self) -> Dict[str, Any]:
        """
        Execute one step of the simulation & anomaly detection pipeline.
        Returns latest readings and newly processed anomalies.
        """
        readings = simulator.step_simulation()
        detected_anomalies = []

        for reading in readings:
            anom = anomaly_service.process_reading(reading)
            if anom:
                detected_anomalies.append(anom)

        # Update machine health scores and statuses
        self._update_machine_health()

        return {
            "readings": readings,
            "anomalies": detected_anomalies,
            "active_anomaly_count": len(anomaly_service.get_active_anomalies())
        }

    def _update_machine_health(self):
        active_anoms = anomaly_service.get_active_anomalies()
        
        # Group active anomalies by machine_id
        machine_anoms: Dict[str, list] = {m_id: [] for m_id in simulator.machines.keys()}
        for a in active_anoms:
            if a.machine_id in machine_anoms:
                machine_anoms[a.machine_id].append(a)

        for m_id, machine in simulator.machines.items():
            anom_list = machine_anoms.get(m_id, [])
            if not anom_list:
                machine.health_score = 100.0
                machine.status = "HEALTHY"
            else:
                total_deduction = 0.0
                has_urgent = False
                has_monitor = False

                for a in anom_list:
                    if a.severity == "URGENT":
                        total_deduction += 35.0
                        has_urgent = True
                    elif a.severity == "MONITOR":
                        total_deduction += 15.0
                        has_monitor = True
                    else:
                        total_deduction += 5.0

                machine.health_score = round(max(0.0, 100.0 - total_deduction), 1)

                if has_urgent or machine.health_score < 50.0:
                    machine.status = "URGENT"
                elif has_monitor or machine.health_score < 80.0:
                    machine.status = "MONITORING"
                else:
                    machine.status = "HEALTHY"

    def reset_all(self):
        """
        Reset simulator, clear all anomalies, alerts, and active injections.
        """
        simulator.reset()
        anomaly_service.clear_all()
        alert_service.clear_all()

    def get_analytics(self) -> Dict[str, Any]:
        """
        Calculate aggregated system analytics.
        """
        machines = list(simulator.machines.values())
        total_machines = len(machines)
        healthy_count = sum(1 for m in machines if m.status == "HEALTHY")
        monitoring_count = sum(1 for m in machines if m.status == "MONITORING")
        urgent_count = sum(1 for m in machines if m.status == "URGENT")

        active_anoms = anomaly_service.get_active_anomalies()
        total_active_anomalies = len(active_anoms)

        anom_by_type = {"SPIKE": 0, "DRIFT": 0, "DROPOUT": 0, "STUCK_SENSOR": 0}
        anom_by_severity = {"IGNORE": 0, "MONITOR": 0, "URGENT": 0}
        sensor_anom_counts = {
            "temperature": 0, "vibration": 0, "pressure": 0, "rpm": 0, "current": 0
        }

        for a in active_anoms:
            if a.anomaly_type in anom_by_type:
                anom_by_type[a.anomaly_type] += 1
            if a.severity in anom_by_severity:
                anom_by_severity[a.severity] += 1
            s_lower = a.sensor_type.lower()
            if s_lower in sensor_anom_counts:
                sensor_anom_counts[s_lower] += 1

        return {
            "total_machines": total_machines,
            "healthy_machines": healthy_count,
            "machines_requiring_monitoring": monitoring_count,
            "urgent_machines": urgent_count,
            "active_anomalies": total_active_anomalies,
            "anomaly_counts_by_type": anom_by_type,
            "anomaly_counts_by_severity": anom_by_severity,
            "sensor_anomaly_counts": sensor_anom_counts
        }

simulation_service = SimulationService()
