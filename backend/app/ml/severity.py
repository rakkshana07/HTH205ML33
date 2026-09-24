from typing import Dict, Any, Tuple

CRITICALITY_WEIGHTS = {
    "HIGH": 1.3,
    "MEDIUM": 1.0,
    "LOW": 0.8
}

SENSOR_WEIGHTS = {
    "temperature": 1.2,
    "vibration": 1.25,
    "pressure": 1.15,
    "current": 1.1,
    "rpm": 1.0
}

def calculate_severity_and_confidence(
    anomaly_type: str,
    features: Dict[str, Any],
    ml_anomaly_score: float,
    machine_criticality: str,
    sensor_type: str,
    std_baseline: float,
    duration_steps: int = 1
) -> Tuple[float, str, float]:
    """
    Calculate severity score (0-100), severity level (IGNORE/MONITOR/URGENT),
    and confidence score (0-100).
    """
    if anomaly_type == "NONE":
        return 0.0, "IGNORE", 95.0

    deviation = features.get("baseline_deviation", 0.0)
    rate_of_change = abs(features.get("rate_of_change", 0.0))
    
    # 1. Base magnitude score (0 - 50)
    mag_ratio = deviation / max(std_baseline, 1e-4)
    if anomaly_type == "DROPOUT":
        base_mag = 45.0
    elif anomaly_type == "STUCK_SENSOR":
        base_mag = 35.0
    else:
        base_mag = min(50.0, mag_ratio * 8.0)

    # 2. Duration / persistence factor (0 - 20)
    dur_factor = min(20.0, (duration_steps - 1) * 2.5)

    # 3. ML Anomaly Score factor (0 - 20)
    ml_factor = ml_anomaly_score * 20.0

    # Raw score prior to weighting
    raw_score = base_mag + dur_factor + ml_factor

    # Apply Machine & Sensor Criticality Multipliers
    mach_mult = CRITICALITY_WEIGHTS.get(machine_criticality.upper(), 1.0)
    sens_mult = SENSOR_WEIGHTS.get(sensor_type.lower(), 1.0)

    total_severity = raw_score * mach_mult * sens_mult
    final_severity_score = round(min(100.0, max(0.0, total_severity)), 2)

    # Severity level mapping:
    # 0–30: IGNORE
    # 31–70: MONITOR
    # 71–100: URGENT
    if final_severity_score <= 30.0:
        severity_level = "IGNORE"
    elif final_severity_score <= 70.0:
        severity_level = "MONITOR"
    else:
        severity_level = "URGENT"

    # Derive Confidence Score (0 - 100) based on clear signatures
    if anomaly_type == "DROPOUT":
        confidence = 98.0
    elif anomaly_type == "STUCK_SENSOR":
        consec = features.get("consecutive_stuck_count", 0)
        confidence = min(99.0, 75.0 + consec * 5.0)
    elif anomaly_type == "SPIKE":
        confidence = min(96.0, 70.0 + (rate_of_change / max(std_baseline, 1e-4)) * 5.0 + ml_anomaly_score * 15.0)
    elif anomaly_type == "DRIFT":
        confidence = min(94.0, 65.0 + (deviation / max(std_baseline, 1e-4)) * 4.0 + ml_anomaly_score * 15.0)
    else:
        confidence = 70.0

    return final_severity_score, severity_level, round(confidence, 2)
