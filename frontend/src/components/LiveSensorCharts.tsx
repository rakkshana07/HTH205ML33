import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import type { Machine, Anomaly } from '../types/industrial';
import type { RollingHistoryPoint } from '../hooks/useLiveStream';
import { LineChart as ChartIcon, Flame, Waves, Gauge, RotateCw, Zap } from 'lucide-react';

interface LiveSensorChartsProps {
  machine: Machine | undefined;
  history: RollingHistoryPoint[];
  activeAnomalies: Anomaly[];
}

export const LiveSensorCharts: React.FC<LiveSensorChartsProps> = ({
  machine,
  history,
  activeAnomalies,
}) => {
  const [activeSensorTab, setActiveSensorTab] = useState<
    'temperature' | 'vibration' | 'pressure' | 'rpm' | 'current'
  >('temperature');

  if (!machine) {
    return (
      <div className="section-container p-6 text-center text-slate-400">
        Select a machine from the matrix to inspect live telemetry charts.
      </div>
    );
  }

  const sensorConfigs = {
    temperature: { name: 'Temperature', unit: '°C', color: '#FF7700', baseline: 65.0, icon: Flame },
    vibration: { name: 'Vibration', unit: 'mm/s', color: '#00F0FF', baseline: 2.5, icon: Waves },
    pressure: { name: 'Pressure', unit: 'bar', color: '#0088FF', baseline: 6.0, icon: Gauge },
    rpm: { name: 'RPM', unit: 'RPM', color: '#A020F0', baseline: 1750.0, icon: RotateCw },
    current: { name: 'Current', unit: 'A', color: '#FFD700', baseline: 24.0, icon: Zap },
  };

  const currConfig = sensorConfigs[activeSensorTab];

  const machineAnomalies = activeAnomalies.filter(
    (a) => a.machine_id === machine.machine_id && a.sensor_type === activeSensorTab
  );
  const activeAnom = machineAnomalies.length > 0 ? machineAnomalies[0] : null;

  return (
    <div className="section-container">
      <div className="section-header">
        <h2 className="section-title">
          <ChartIcon size={20} className="text-cyan-400" />
          LIVE STREAMING TELEMETRY — <span className="text-cyan-400">{machine.machine_id}</span> ({machine.machine_name})
        </h2>
        <span className="text-xs text-slate-400 font-mono">
          STATUS: <span className="text-emerald-400">{machine.status}</span> | HEALTH: {machine.health_score}%
        </span>
      </div>

      {/* Sensor Stream Tabs */}
      <div className="sensor-tabs font-sans">
        {(Object.keys(sensorConfigs) as Array<keyof typeof sensorConfigs>).map((sType) => {
          const cfg = sensorConfigs[sType];
          const TabIcon = cfg.icon;
          const isAnom = activeAnomalies.some(
            (a) => a.machine_id === machine.machine_id && a.sensor_type === sType
          );

          return (
            <button
              key={sType}
              onClick={() => setActiveSensorTab(sType)}
              className={`sensor-tab-btn ${
                activeSensorTab === sType ? 'sensor-tab-active' : ''
              } ${isAnom ? 'border-amber-500/70 bg-amber-500/10' : ''}`}
            >
              <TabIcon size={14} style={{ color: cfg.color }} />
              <span>{cfg.name}</span>
              {isAnom && <span className="badge-dot-amber" />}
            </button>
          );
        })}
      </div>

      {/* Active Anomaly Banner for Chart */}
      {activeAnom && (
        <div className="chart-anomaly-callout">
          <span className="font-bold text-rose-400">ANOMALY DETECTED:</span> {activeAnom.anomaly_type} (
          Severity: <span className="font-semibold">{activeAnom.severity}</span>, Score: {activeAnom.severity_score})
          <span className="ml-auto text-xs text-slate-300">Cause: {activeAnom.possible_cause}</span>
        </div>
      )}

      {/* Recharts Live Stream Chart */}
      <div className="chart-wrapper">
        <div className="chart-legend">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 rounded" style={{ backgroundColor: currConfig.color }} />
            Streaming {currConfig.name} ({currConfig.unit})
          </span>
          <span className="flex items-center gap-1.5 opacity-75">
            <span className="w-3 h-0.5 border-t border-dashed border-cyan-300" />
            Operational Baseline ({currConfig.baseline} {currConfig.unit})
          </span>
        </div>

        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={history} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
            <XAxis dataKey="time" stroke="#64748B" fontSize={11} />
            <YAxis stroke="#64748B" fontSize={11} domain={['auto', 'auto']} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1E293B',
                borderColor: '#334155',
                borderRadius: '8px',
                color: '#F8FAFC',
              }}
            />
            <ReferenceLine
              y={currConfig.baseline}
              stroke="#00F0FF"
              strokeDasharray="4 4"
              label={{
                value: `Baseline: ${currConfig.baseline}`,
                fill: '#00F0FF',
                fontSize: 10,
                position: 'insideTopRight',
              }}
            />
            <Line
              type="monotone"
              dataKey={activeSensorTab}
              stroke={currConfig.color}
              strokeWidth={2.5}
              dot={{ r: 3, fill: currConfig.color }}
              activeDot={{ r: 6 }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
