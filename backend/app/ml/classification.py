from typing import Dict, Any

def classify_anomaly(
    features: Dict[str, Any],
    is_ml_anomaly: bool,
    anomaly_score: float,
    std_baseline: float
) -> str:
    """
    Classify anomaly into: SPIKE, DRIFT, DROPOUT, STUCK_SENSOR, or NONE.
    Deterministic, explainable classifier based on extracted features and ML evidence.
    Ensures normal stochastic noise does not trigger false anomalies.
    """
    # 1. DROPOUT Check
    if features.get("missing_data_indicator", 0) == 1 or features.get("current_value") is None:
        return "DROPOUT"

    sample_count = features.get("sample_count", 0)
    consecutive_stuck = features.get("consecutive_stuck_count", 0)
    rolling_var = features.get("rolling_variance", 1.0)
    rate_of_change = abs(features.get("rate_of_change", 0.0))
    trend_slope = abs(features.get("trend_slope", 0.0))
    deviation = features.get("baseline_deviation", 0.0)
    rolling_std = max(features.get("rolling_std", 1.0), std_baseline)

    # 2. STUCK_SENSOR Check
    # Needs at least 4 readings in window. If variance is near 0 or consecutive identical count >= 4
    if sample_count >= 4 and (consecutive_stuck >= 4 or rolling_var < 1e-4):
        return "STUCK_SENSOR"

    # 3. SPIKE Check
    # High instant rate of change (e.g. > 3 * std_baseline) or sudden sharp jump
    if rate_of_change >= 2.5 * std_baseline and deviation >= 2.5 * std_baseline:
        return "SPIKE"

    # 4. DRIFT Check
    # Sustained non-zero slope and significant deviation from baseline
    if trend_slope >= 0.03 * std_baseline and deviation >= 2.5 * std_baseline:
        return "DRIFT"

    # 5. General Significant Anomaly Check
    if (is_ml_anomaly or anomaly_score >= 0.70) and deviation >= 3.0 * std_baseline:
        if rate_of_change >= trend_slope * 2:
            return "SPIKE"
        else:
            return "DRIFT"

    # Default: Normal operation
    return "NONE"
