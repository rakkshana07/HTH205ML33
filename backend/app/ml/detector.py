import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, Tuple

class AnomalyDetector:
    """
    Isolation Forest Anomaly Detector trained on normal baseline operational data.
    Maintains clean pre-trained models per sensor type to avoid corruption by injected anomalies.
    """

    def __init__(self, contamination: float = 0.01):
        self.contamination = contamination
        self.models: Dict[str, IsolationForest] = {}
        self._initialize_baseline_models()

    def _initialize_baseline_models(self):
        """
        Train baseline IsolationForest models for standard sensor profiles
        using synthetic normal operating data with standard industrial noise.
        """
        np.random.seed(42)
        sensor_baselines = {
            "temperature": (65.0, 1.5),
            "vibration": (2.5, 0.2),
            "pressure": (6.0, 0.3),
            "rpm": (1750.0, 15.0),
            "current": (24.0, 0.8)
        }

        for sensor_type, (mean_val, std_val) in sensor_baselines.items():
            # Generate 500 normal samples of feature vectors:
            # [current_val, baseline_dev, rolling_std, rate_of_change, slope]
            normal_vals = np.random.normal(mean_val, std_val * 0.4, 500)
            baseline_devs = np.abs(normal_vals - mean_val)
            rolling_stds = np.full(500, std_val) + np.random.normal(0, std_val * 0.05, 500)
            rates_of_change = np.random.normal(0, std_val * 0.2, 500)
            slopes = np.random.normal(0, std_val * 0.05, 500)

            X_train = np.column_stack([normal_vals, baseline_devs, rolling_stds, rates_of_change, slopes])
            
            clf = IsolationForest(
                n_estimators=100,
                contamination=self.contamination,
                random_state=42
            )
            clf.fit(X_train)
            self.models[sensor_type] = clf

    def predict(self, sensor_type: str, features: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Predict whether current reading/features represent an anomaly.
        Returns:
            is_anomaly (bool)
            anomaly_score (float 0.0 to 1.0, higher = more anomalous)
        """
        if features.get("missing_data_indicator", 0) == 1:
            return True, 0.95

        curr_val = features["current_value"]
        if curr_val is None:
            return True, 0.95

        dev = features["baseline_deviation"]
        r_std = features["rolling_std"]
        roc = features["rate_of_change"]
        slope = features["trend_slope"]

        model = self.models.get(sensor_type)
        if model is None:
            is_anom = dev > 3.0 * max(r_std, 1.0)
            score = min(1.0, dev / (5.0 * max(r_std, 1.0)))
            return is_anom, score

        X_test = np.array([[curr_val, dev, r_std, roc, slope]])
        
        # decision_function gives negative values for anomalies, positive for normal
        decision_score = model.decision_function(X_test)[0]
        
        # Convert decision function to 0.0-1.0 anomaly score
        normalized_anomaly_score = float(np.clip((0.15 - decision_score) / 0.35, 0.0, 1.0))
        
        # Isolation forest flags true anomaly if decision_score is clearly negative (< -0.05)
        is_anomaly = (decision_score < -0.05) or (normalized_anomaly_score >= 0.70)
        return is_anomaly, round(normalized_anomaly_score, 4)

detector = AnomalyDetector()
