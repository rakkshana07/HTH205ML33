import { useState, useEffect, useRef, useCallback } from 'react';
import type { Machine, Anomaly, Alert, AnalyticsData, SensorReading } from '../types/industrial';
import { api } from '../services/api';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const WS_URL = API_BASE.replace(/^http/, 'ws') + '/ws/live';

export interface RollingHistoryPoint {
  time: string;
  temperature?: number | null;
  vibration?: number | null;
  pressure?: number | null;
  rpm?: number | null;
  current?: number | null;
}

export function useLiveStream() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [activeAnomalies, setActiveAnomalies] = useState<Anomaly[]>([]);
  const [allAnomalies, setAllAnomalies] = useState<Anomaly[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isWebSocket, setIsWebSocket] = useState<boolean>(false);
  const [selectedMachineId, setSelectedMachineId] = useState<string>('MACHINE-01');

  // Rolling history for chart visualizations: machineId -> SensorHistoryPoint[]
  const [sensorHistory, setSensorHistory] = useState<Record<string, RollingHistoryPoint[]>>({});

  const wsRef = useRef<WebSocket | null>(null);
  const pollTimerRef = useRef<number | null>(null);

  const fetchInitialData = useCallback(async () => {
    try {
      const [mList, anomList, altList, stats] = await Promise.all([
        api.getMachines(),
        api.getAnomalies(),
        api.getAlerts(),
        api.getAnalytics(),
      ]);
      setMachines(mList);
      setAllAnomalies(anomList);
      setActiveAnomalies(anomList.filter((a) => a.status === 'ACTIVE'));
      setAlerts(altList);
      setAnalytics(stats);
      setIsConnected(true);
    } catch (err) {
      console.warn('Initial backend fetch failed:', err);
      setIsConnected(false);
    }
  }, []);

  const updateSensorHistory = useCallback((readings: SensorReading[]) => {
    if (!readings || readings.length === 0) return;

    setSensorHistory((prevHistory) => {
      const updated = { ...prevHistory };

      // Group readings by machine_id
      const byMachine: Record<string, Record<string, number | null>> = {};
      let timeStr = new Date().toLocaleTimeString();

      readings.forEach((r) => {
        if (r.timestamp) {
          timeStr = new Date(r.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          });
        }
        if (!byMachine[r.machine_id]) {
          byMachine[r.machine_id] = {};
        }
        byMachine[r.machine_id][r.sensor_type] = r.value;
      });

      Object.entries(byMachine).forEach(([mId, sensorVals]) => {
        const existing = updated[mId] || [];
        const point: RollingHistoryPoint = {
          time: timeStr,
          temperature: sensorVals['temperature'],
          vibration: sensorVals['vibration'],
          pressure: sensorVals['pressure'],
          rpm: sensorVals['rpm'],
          current: sensorVals['current'],
        };
        // Keep last 30 readings
        const newHistory = [...existing, point].slice(-30);
        updated[mId] = newHistory;
      });

      return updated;
    });
  }, []);

  // Refresh anomalies, alerts & analytics
  const refreshAuxiliaryData = useCallback(async () => {
    try {
      const [anomList, altList, stats, mList] = await Promise.all([
        api.getAnomalies(),
        api.getAlerts(),
        api.getAnalytics(),
        api.getMachines(),
      ]);
      setAllAnomalies(anomList);
      setActiveAnomalies(anomList.filter((a) => a.status === 'ACTIVE'));
      setAlerts(altList);
      setAnalytics(stats);
      setMachines(mList);
    } catch (e) {
      console.warn('Auxiliary refresh error:', e);
    }
  }, []);

  // WebSocket lifecycle
  useEffect(() => {
    let isMounted = true;

    fetchInitialData();

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!isMounted) return;
          console.log('[WS] Connected to live backend stream');
          setIsConnected(true);
          setIsWebSocket(true);
          // Stop polling if polling was active
          if (pollTimerRef.current) {
            window.clearInterval(pollTimerRef.current);
            pollTimerRef.current = null;
          }
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data = JSON.parse(event.data);
            if (data.event === 'live_update' || data.readings) {
              if (data.readings) {
                updateSensorHistory(data.readings);
              }
              refreshAuxiliaryData();
            }
          } catch (e) {
            console.error('[WS] Message parse error:', e);
          }
        };

        ws.onerror = (err) => {
          console.warn('[WS] Connection error:', err);
          setIsWebSocket(false);
        };

        ws.onclose = () => {
          if (!isMounted) return;
          console.warn('[WS] Closed. Falling back to HTTP polling.');
          setIsWebSocket(false);
          startPolling();
        };
      } catch (err) {
        console.warn('[WS] Instantiation failed:', err);
        setIsWebSocket(false);
        startPolling();
      }
    };

    const startPolling = () => {
      if (pollTimerRef.current) return;
      console.log('[HTTP] Starting HTTP polling fallback...');
      pollTimerRef.current = window.setInterval(async () => {
        try {
          const live = await api.getLiveData();
          setIsConnected(true);
          if (live.readings) {
            updateSensorHistory(live.readings);
          }
          if (live.machines) {
            setMachines(live.machines);
          }
          refreshAuxiliaryData();
        } catch (e) {
          console.warn('[HTTP] Polling tick error:', e);
          setIsConnected(false);
        }
      }, 1500);
    };

    // Try WebSocket first
    connectWebSocket();

    return () => {
      isMounted = false;
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (pollTimerRef.current) {
        window.clearInterval(pollTimerRef.current);
      }
    };
  }, [fetchInitialData, updateSensorHistory, refreshAuxiliaryData]);

  return {
    machines,
    activeAnomalies,
    allAnomalies,
    alerts,
    analytics,
    isConnected,
    isWebSocket,
    selectedMachineId,
    setSelectedMachineId,
    sensorHistory: sensorHistory[selectedMachineId] || [],
    refreshAuxiliaryData,
  };
}
