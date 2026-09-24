import sys
import os
import time
from fastapi.testclient import TestClient

# Ensure UTF-8 stdout encoding on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.main import app
from app.simulation.simulator import simulator
from app.services.simulation_service import simulation_service
from app.services.anomaly_service import anomaly_service

client = TestClient(app)

def print_banner(title):
    print("\n" + "=" * 60)
    print(f" TEST: {title}")
    print("=" * 60)

def test_1_health_endpoint():
    print_banner("1. Health Endpoint")
    response = client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "ok", f"Expected status 'ok', got {data['status']}"
    assert "INDUSTRIALGUARD AI" in data["app"]
    print("[PASS] Health endpoint returned 200 OK with valid payload:", data)

def test_2_exactly_10_machines():
    print_banner("2. Exactly 10 Machines")
    response = client.get("/api/machines")
    assert response.status_code == 200
    machines = response.json()
    assert len(machines) == 10, f"Expected 10 machines, got {len(machines)}"
    machine_ids = [m["machine_id"] for m in machines]
    expected_ids = [f"MACHINE-{i:02d}" for i in range(1, 11)]
    assert sorted(machine_ids) == sorted(expected_ids), f"Machine IDs mismatch: {machine_ids}"
    print(f"[PASS] Found exactly 10 machines: {machine_ids}")

def test_3_exactly_5_sensors_per_machine():
    print_banner("3. Exactly 5 Sensors per Machine")
    response = client.get("/api/machines/MACHINE-01")
    assert response.status_code == 200
    machine = response.json()
    sensors = machine["sensors"]
    assert len(sensors) == 5, f"Expected 5 sensors, got {len(sensors)}"
    expected_sensors = {"temperature", "vibration", "pressure", "rpm", "current"}
    assert set(sensors.keys()) == expected_sensors, f"Sensor types mismatch: {sensors.keys()}"
    print(f"[PASS] Machine-01 has exactly 5 sensor types: {list(sensors.keys())}")

def test_4_normal_startup_zero_anomalies():
    print_banner("4. Normal Startup (Zero Active Anomalies)")
    # Reset simulator to baseline
    client.post("/api/simulation/reset")
    
    # Run 10 normal simulation steps
    for _ in range(10):
        res = simulation_service.tick()
        assert res["active_anomaly_count"] == 0, f"False anomaly during normal startup! Active count: {res['active_anomaly_count']}"

    response = client.get("/api/anomalies")
    assert response.status_code == 200
    anomalies = response.json()
    active_anomalies = [a for a in anomalies if a["status"] == "ACTIVE"]
    assert len(active_anomalies) == 0, f"Expected 0 active anomalies on normal startup, found {len(active_anomalies)}"
    print("[PASS] Normal startup produced zero false anomalies across 10 steps.")

def test_5_spike_injection_detection():
    print_banner("5. SPIKE Injection Detection")
    client.post("/api/simulation/reset")
    
    # Inject SPIKE on MACHINE-01 temperature
    target_m = "MACHINE-01"
    target_s = "temperature"
    inj_res = client.post("/api/simulation/inject/spike", json={
        "machine_id": target_m,
        "sensor_type": target_s,
        "magnitude": 45.0
    })
    assert inj_res.status_code == 200

    # Step simulation to trigger spike detection
    detected = None
    for _ in range(5):
        simulation_service.tick()
        anoms = anomaly_service.get_active_anomalies()
        for a in anoms:
            if a.machine_id == target_m and a.sensor_type == target_s:
                detected = a
                break
        if detected:
            break

    assert detected is not None, f"SPIKE on {target_m} {target_s} was not detected!"
    assert detected.anomaly_type == "SPIKE", f"Expected anomaly_type 'SPIKE', got '{detected.anomaly_type}'"
    assert 0.0 <= detected.severity_score <= 100.0
    assert "Possible" in detected.possible_cause
    print(f"[PASS] SPIKE injection correctly detected!")
    print(f"  Type: {detected.anomaly_type}, Severity: {detected.severity} (Score: {detected.severity_score}), Cause: {detected.possible_cause}")

def test_6_drift_injection_detection():
    print_banner("6. DRIFT Injection Detection")
    client.post("/api/simulation/reset")
    
    target_m = "MACHINE-03"
    target_s = "pressure"
    inj_res = client.post("/api/simulation/inject/drift", json={
        "machine_id": target_m,
        "sensor_type": target_s,
        "rate": 3.0
    })
    assert inj_res.status_code == 200

    detected = None
    for _ in range(8):
        simulation_service.tick()
        anoms = anomaly_service.get_active_anomalies()
        for a in anoms:
            if a.machine_id == target_m and a.sensor_type == target_s:
                detected = a
                break
        if detected:
            break

    assert detected is not None, f"DRIFT on {target_m} {target_s} was not detected!"
    assert detected.anomaly_type == "DRIFT", f"Expected anomaly_type 'DRIFT', got '{detected.anomaly_type}'"
    assert 0.0 <= detected.severity_score <= 100.0
    print(f"[PASS] DRIFT injection correctly detected!")
    print(f"  Type: {detected.anomaly_type}, Severity: {detected.severity} (Score: {detected.severity_score}), Cause: {detected.possible_cause}")

def test_7_dropout_injection_detection():
    print_banner("7. DROPOUT Injection Detection")
    client.post("/api/simulation/reset")
    
    target_m = "MACHINE-05"
    target_s = "vibration"
    inj_res = client.post("/api/simulation/inject/dropout", json={
        "machine_id": target_m,
        "sensor_type": target_s
    })
    assert inj_res.status_code == 200

    detected = None
    for _ in range(3):
        simulation_service.tick()
        anoms = anomaly_service.get_active_anomalies()
        for a in anoms:
            if a.machine_id == target_m and a.sensor_type == target_s:
                detected = a
                break
        if detected:
            break

    assert detected is not None, f"DROPOUT on {target_m} {target_s} was not detected!"
    assert detected.anomaly_type == "DROPOUT", f"Expected anomaly_type 'DROPOUT', got '{detected.anomaly_type}'"
    assert 0.0 <= detected.severity_score <= 100.0
    print(f"[PASS] DROPOUT injection correctly detected!")
    print(f"  Type: {detected.anomaly_type}, Severity: {detected.severity} (Score: {detected.severity_score}), Cause: {detected.possible_cause}")

def test_8_stuck_injection_detection():
    print_banner("8. STUCK Sensor Injection Detection")
    client.post("/api/simulation/reset")
    
    target_m = "MACHINE-07"
    target_s = "current"
    inj_res = client.post("/api/simulation/inject/stuck", json={
        "machine_id": target_m,
        "sensor_type": target_s
    })
    assert inj_res.status_code == 200

    detected = None
    for _ in range(6):
        simulation_service.tick()
        anoms = anomaly_service.get_active_anomalies()
        for a in anoms:
            if a.machine_id == target_m and a.sensor_type == target_s:
                detected = a
                break
        if detected:
            break

    assert detected is not None, f"STUCK on {target_m} {target_s} was not detected!"
    assert detected.anomaly_type == "STUCK_SENSOR", f"Expected anomaly_type 'STUCK_SENSOR', got '{detected.anomaly_type}'"
    assert 0.0 <= detected.severity_score <= 100.0
    print(f"[PASS] STUCK_SENSOR injection correctly detected!")
    print(f"  Type: {detected.anomaly_type}, Severity: {detected.severity} (Score: {detected.severity_score}), Cause: {detected.possible_cause}")

def test_9_severity_mapping_and_routing():
    print_banner("9. Severity Score Range & Alert Routing")
    client.post("/api/simulation/reset")

    # Inject large SPIKE (URGENT/MONITOR)
    client.post("/api/simulation/inject/spike", json={
        "machine_id": "MACHINE-01",
        "sensor_type": "temperature",
        "magnitude": 50.0
    })
    simulation_service.tick()
    
    anomalies_res = client.get("/api/anomalies")
    assert anomalies_res.status_code == 200
    anomalies = anomalies_res.json()
    assert len(anomalies) > 0
    anom = anomalies[0]
    
    assert 0.0 <= anom["severity_score"] <= 100.0, f"Severity score out of bounds: {anom['severity_score']}"
    assert anom["severity"] in ["IGNORE", "MONITOR", "URGENT"], f"Invalid severity level: {anom['severity']}"
    
    alerts_res = client.get("/api/alerts")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) >= 1, "Alert was not created for non-IGNORE severity!"
    alert = alerts[0]
    print(f"[PASS] Severity mapped ({anom['severity_score']:.1f} -> {anom['severity']}) and routed to Alert: {alert['alert_id']}")

def test_10_alert_lifecycle():
    print_banner("10. Alert Lifecycle (Acknowledge & Resolve)")
    alerts = client.get("/api/alerts").json()
    assert len(alerts) > 0
    alert_id = alerts[0]["alert_id"]

    # Acknowledge
    ack_res = client.post(f"/api/alerts/{alert_id}/acknowledge")
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # Resolve
    res_res = client.post(f"/api/alerts/{alert_id}/resolve")
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"
    print(f"[PASS] Alert lifecycle test passed for Alert ID: {alert_id}")

def test_11_analytics_endpoint():
    print_banner("11. Analytics Endpoint")
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_machines"] == 10
    assert "active_anomalies" in data
    assert "anomaly_counts_by_type" in data
    print(f"[PASS] Analytics returned accurate aggregated metrics: {data}")

def test_12_simulation_controls():
    print_banner("12. Simulation Controls (Start, Pause, Stop, Reset)")
    assert client.post("/api/simulation/pause").json()["status"] == "paused"
    assert client.post("/api/simulation/start").json()["status"] == "started"
    assert client.post("/api/simulation/stop").json()["status"] == "stopped"
    assert client.post("/api/simulation/reset").json()["status"] == "reset"
    print("[PASS] Simulation controls operating cleanly.")

if __name__ == "__main__":
    print("\n==================================================")
    print(" RUNNING INDUSTRIALGUARD AI BACKEND TEST SUITE")
    print("==================================================")
    test_1_health_endpoint()
    test_2_exactly_10_machines()
    test_3_exactly_5_sensors_per_machine()
    test_4_normal_startup_zero_anomalies()
    test_5_spike_injection_detection()
    test_6_drift_injection_detection()
    test_7_dropout_injection_detection()
    test_8_stuck_injection_detection()
    test_9_severity_mapping_and_routing()
    test_10_alert_lifecycle()
    test_11_analytics_endpoint()
    test_12_simulation_controls()
    print("\n==================================================")
    print(" ALL 12 TEST SUITE MODULES PASSED SUCCESSFULLY!")
    print("==================================================")
