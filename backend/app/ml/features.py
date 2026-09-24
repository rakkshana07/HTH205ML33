import numpy as np
from typing import List, Optional, Dict, Any

def extract_features(
    history: List[Optional[float]],
    baseline_value: float,
    current_value: Optional[float]
) -> Dict[str, Any]:
    """
    Extract rolling behavioral features from sensor history.
    History is an ordered list of recent values [oldest ... newest].
    Handles missing data (None) and short history safely.
    """
    # Missing data indicator
    is_missing = (current_value is None)
    missing_indicator = 1 if is_missing else 0

    # Filter non-None valid values from history
    valid_history = [v for v in history if v is not None]
    
    if not valid_history:
        # Fallback if no valid history exists
        return {
            "current_value": current_value,
            "rolling_mean": baseline_value,
            "rolling_std": 0.0,
            "baseline_value": baseline_value,
            "baseline_deviation": 0.0,
            "rate_of_change": 0.0,
            "rolling_min": baseline_value,
            "rolling_max": baseline_value,
            "rolling_variance": 0.0,
            "trend_slope": 0.0,
            "missing_data_indicator": missing_indicator,
            "consecutive_stuck_count": 0,
            "sample_count": 0
        }

    valid_arr = np.array(valid_history, dtype=float)
    sample_count = len(valid_arr)
    
    rolling_mean = float(np.mean(valid_arr))
    rolling_std = float(np.std(valid_arr)) if sample_count > 1 else 0.0
    rolling_min = float(np.min(valid_arr))
    rolling_max = float(np.max(valid_arr))
    rolling_variance = float(np.var(valid_arr)) if sample_count > 1 else 0.0

    # Baseline deviation
    if current_value is not None:
        baseline_deviation = abs(current_value - baseline_value)
    else:
        baseline_deviation = 0.0

    # Rate of change: difference between current reading and previous valid reading
    rate_of_change = 0.0
    if current_value is not None and len(valid_arr) >= 2:
        # If current_value is the latest element in valid_arr, compare with second latest
        prev_val = valid_arr[-2] if valid_arr[-1] == current_value else valid_arr[-1]
        rate_of_change = float(current_value - prev_val)

    # Trend / Slope via linear regression on valid values
    trend_slope = 0.0
    if sample_count >= 3:
        x = np.arange(sample_count)
        # polyfit degree 1 gives slope
        slope, _ = np.polyfit(x, valid_arr, 1)
        trend_slope = float(slope)

    # Consecutive stuck count (number of identical/near-identical readings at the end)
    consecutive_stuck_count = 0
    if len(valid_arr) >= 2:
        last_val = valid_arr[-1]
        for val in reversed(valid_arr):
            if abs(val - last_val) < 1e-4:
                consecutive_stuck_count += 1
            else:
                break

    return {
        "current_value": current_value,
        "rolling_mean": rolling_mean,
        "rolling_std": rolling_std,
        "baseline_value": baseline_value,
        "baseline_deviation": baseline_deviation,
        "rate_of_change": rate_of_change,
        "rolling_min": rolling_min,
        "rolling_max": rolling_max,
        "rolling_variance": rolling_variance,
        "trend_slope": trend_slope,
        "missing_data_indicator": missing_indicator,
        "consecutive_stuck_count": consecutive_stuck_count,
        "sample_count": sample_count
    }
