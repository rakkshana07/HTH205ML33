export type CriticalityLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type MachineStatusType = 'HEALTHY' | 'MONITORING' | 'URGENT';

export interface SensorState {
  sensor_type: string;
  unit: string;
  baseline_value: number;
  current_value: number | null;
  min_value: number;
  max_value: number;
  last_update: string;
  status: 'NORMAL' | 'ANOMALOUS';
}

export interface Machine {
  machine_id: string;
  machine_name: string;
  machine_type: string;
  location: string;
  criticality: CriticalityLevel;
  health_score: number;
  status: MachineStatusType;
  last_update: string;
  sensors: Record<string, SensorState>;
}

export interface SensorReading {
  timestamp: string;
  machine_id: string;
  sensor_type: string;
  value: number | null;
  unit: string;
  is_missing: boolean;
}

export type AnomalyType = 'SPIKE' | 'DRIFT' | 'DROPOUT' | 'STUCK_SENSOR' | 'NONE';
export type SeverityLevel = 'IGNORE' | 'MONITOR' | 'URGENT';
export type AnomalyStatus = 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';

export interface Anomaly {
  anomaly_id: string;
  machine_id: string;
  sensor_type: string;
  anomaly_type: AnomalyType;
  severity: SeverityLevel;
  severity_score: number;
  confidence: number;
  current_value: number | null;
  baseline_value: number;
  deviation: number;
  timestamp: string;
  duration: number;
  possible_cause: string;
  recommended_action: string;
  status: AnomalyStatus;
}

export interface Alert {
  alert_id: string;
  anomaly_id: string;
  machine_id: string;
  sensor_type: string;
  severity: SeverityLevel;
  severity_score: number;
  timestamp: string;
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
  message: string;
}

export interface AnalyticsData {
  total_machines: number;
  healthy_machines: number;
  machines_requiring_monitoring: number;
  urgent_machines: number;
  active_anomalies: number;
  anomaly_counts_by_type: Record<AnomalyType | string, number>;
  anomaly_counts_by_severity: Record<SeverityLevel | string, number>;
  sensor_anomaly_counts: Record<string, number>;
}
