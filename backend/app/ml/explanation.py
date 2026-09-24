from typing import Tuple

EXPLANATION_MAP = {
    ("temperature", "SPIKE"): (
        "Possible overheating, cooling-system failure, or sudden thermal surge.",
        "Inspect cooling system fan, verify coolant fluid levels, and check heat exchanger immediately."
    ),
    ("temperature", "DRIFT"): (
        "Possible gradual thermal buildup, coolant restriction, or radiator degradation.",
        "Check coolant flow regulation, clean heat exchanger fins, and monitor temperature trend."
    ),
    ("vibration", "SPIKE"): (
        "Possible mechanical imbalance, bearing impact, rotor defect, or loose structural mounting.",
        "Inspect bearing housing, check rotor balance, and tighten mechanical foundation bolts."
    ),
    ("vibration", "DRIFT"): (
        "Possible progressive bearing wear, shaft misalignment, or mechanical degradation.",
        "Schedule predictive maintenance for bearing replacement and verify laser alignment."
    ),
    ("pressure", "SPIKE"): (
        "Possible hydraulic surge, sudden valve closure, or pressure shock wave.",
        "Inspect pressure relief valve, verify surge suppressor condition, and re-check valve timing."
    ),
    ("pressure", "DRIFT"): (
        "Possible pressure regulation valve leakage, seal wear, or line constriction.",
        "Check pressure control valve calibration, inspect line seals, and test regulator diaphragm."
    ),
    ("rpm", "SPIKE"): (
        "Possible motor speed governor glitch, load shed, or drive inverter anomaly.",
        "Inspect motor drive controller parameters and check VFD tachometer feedback."
    ),
    ("rpm", "DRIFT"): (
        "Possible belt slippage, motor winding degradation, or mechanical friction drag.",
        "Check drive belt tension, inspect motor bearings, and test stator resistance."
    ),
    ("current", "SPIKE"): (
        "Possible electrical short circuit, transient voltage spike, or motor rotor lock.",
        "Inspect electrical circuit breaker, check motor winding insulation, and verify overload relay."
    ),
    ("current", "DRIFT"): (
        "Possible motor overload, increased mechanical friction, or phase imbalance.",
        "Verify motor load demands, check 3-phase balance, and inspect mechanical drive line."
    ),
}

GENERIC_TYPE_MAP = {
    "DROPOUT": (
        "Possible sensor connectivity or communication interruption.",
        "Verify physical sensor wiring, check fieldbus connectors, and test gateway interface."
    ),
    "STUCK_SENSOR": (
        "Possible sensor transducer malfunction, frozen output, or communication freeze.",
        "Inspect sensor unit, power-cycle field transmitter, and re-calibrate sensor module."
    )
}

def generate_explanation_and_action(
    sensor_type: str,
    anomaly_type: str,
    severity: str
) -> Tuple[str, str]:
    """
    Generate explainable 'Possible Cause' hint and practical recommended action.
    """
    if anomaly_type == "NONE":
        return "Normal operating conditions.", "Continue standard monitoring."

    sensor_lower = sensor_type.lower()
    
    if anomaly_type in GENERIC_TYPE_MAP:
        cause, action = GENERIC_TYPE_MAP[anomaly_type]
    elif (sensor_lower, anomaly_type) in EXPLANATION_MAP:
        cause, action = EXPLANATION_MAP[(sensor_lower, anomaly_type)]
    else:
        cause = f"Possible anomalous condition detected in {sensor_type} signal."
        action = f"Inspect {sensor_type} sensor and associated mechanical/electrical subsystems."

    if severity == "URGENT":
        action += " (Immediate inspection required)."

    return cause, action
