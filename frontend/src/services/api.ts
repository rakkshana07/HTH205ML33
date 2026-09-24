import axios from 'axios';
import type { Machine, Anomaly, Alert, AnalyticsData, SensorReading } from '../types/industrial';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const client = axios.create({
  baseURL: `${API_BASE}/api`,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  async getHealth() {
    const res = await client.get('/health');
    return res.data;
  },

  // Machines
  async getMachines(): Promise<Machine[]> {
    const res = await client.get('/machines');
    return res.data;
  },

  async getMachine(machineId: string): Promise<Machine> {
    const res = await client.get(`/machines/${machineId}`);
    return res.data;
  },

  // Live Data (Fallback Polling)
  async getLiveData(): Promise<{
    timestamp: string | null;
    machines: Machine[];
    active_anomalies: Anomaly[];
    readings: SensorReading[];
  }> {
    const res = await client.get('/live-data');
    return res.data;
  },

  // Anomalies & Alerts
  async getAnomalies(): Promise<Anomaly[]> {
    const res = await client.get('/anomalies');
    return res.data;
  },

  async getAlerts(): Promise<Alert[]> {
    const res = await client.get('/alerts');
    return res.data;
  },

  async acknowledgeAlert(alertId: string): Promise<Alert> {
    const res = await client.post(`/alerts/${alertId}/acknowledge`);
    return res.data;
  },

  async resolveAlert(alertId: string): Promise<Alert> {
    const res = await client.post(`/alerts/${alertId}/resolve`);
    return res.data;
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsData> {
    const res = await client.get('/analytics');
    return res.data;
  },

  // Simulation Controls
  async startSimulation() {
    const res = await client.post('/simulation/start');
    return res.data;
  },

  async pauseSimulation() {
    const res = await client.post('/simulation/pause');
    return res.data;
  },

  async stopSimulation() {
    const res = await client.post('/simulation/stop');
    return res.data;
  },

  async resetSimulation() {
    const res = await client.post('/simulation/reset');
    return res.data;
  },

  // Anomaly Injection
  async injectSpike(machineId: string, sensorType: string, magnitude?: number) {
    const res = await client.post('/simulation/inject/spike', {
      machine_id: machineId,
      sensor_type: sensorType,
      magnitude: magnitude || 45.0,
    });
    return res.data;
  },

  async injectDrift(machineId: string, sensorType: string, rate?: number) {
    const res = await client.post('/simulation/inject/drift', {
      machine_id: machineId,
      sensor_type: sensorType,
      rate: rate || 3.0,
    });
    return res.data;
  },

  async injectDropout(machineId: string, sensorType: string) {
    const res = await client.post('/simulation/inject/dropout', {
      machine_id: machineId,
      sensor_type: sensorType,
    });
    return res.data;
  },

  async injectStuck(machineId: string, sensorType: string) {
    const res = await client.post('/simulation/inject/stuck', {
      machine_id: machineId,
      sensor_type: sensorType,
    });
    return res.data;
  },
};
