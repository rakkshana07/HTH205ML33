import React from 'react';
import type { AnalyticsData } from '../types/industrial';
import { PieChart, Cpu, ShieldCheck, AlertCircle, AlertOctagon, BarChart2 } from 'lucide-react';

interface AnalyticsPanelProps {
  analytics: AnalyticsData | null;
}

export const AnalyticsPanel: React.FC<AnalyticsPanelProps> = ({ analytics }) => {
  if (!analytics) {
    return (
      <div className="section-container p-6 text-center text-slate-400">
        Loading analytics dataset...
      </div>
    );
  }

  const byType = analytics.anomaly_counts_by_type || {};
  const bySev = analytics.anomaly_counts_by_severity || {};
  const bySensor = analytics.sensor_anomaly_counts || {};

  return (
    <div className="section-container">
      <div className="section-header">
        <h2 className="section-title">
          <PieChart size={20} className="text-purple-400" />
          SYSTEM-WIDE ANOMALY & HEALTH ANALYTICS
        </h2>
        <span className="text-xs text-slate-400 font-mono">Aggregated from /api/analytics</span>
      </div>

      <div className="analytics-grid">
        {/* Machine Health Status Distribution */}
        <div className="analytics-card">
          <h3 className="analytics-card-title flex items-center gap-2">
            <Cpu size={16} className="text-cyan-400" /> Machine Status Overview
          </h3>
          <div className="space-y-3 mt-3">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 text-emerald-400">
                <ShieldCheck size={14} /> Healthy Machines
              </span>
              <span className="font-mono font-bold">{analytics.healthy_machines} / {analytics.total_machines}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 text-amber-400">
                <AlertCircle size={14} /> Requiring Monitoring
              </span>
              <span className="font-mono font-bold">{analytics.machines_requiring_monitoring}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 text-rose-500">
                <AlertOctagon size={14} /> Urgent Attention
              </span>
              <span className="font-mono font-bold text-rose-500">{analytics.urgent_machines}</span>
            </div>
          </div>
        </div>

        {/* Anomaly Distribution by Type */}
        <div className="analytics-card">
          <h3 className="analytics-card-title flex items-center gap-2">
            <BarChart2 size={16} className="text-amber-400" /> Anomalies by Classification
          </h3>
          <div className="space-y-2.5 mt-3">
            {['SPIKE', 'DRIFT', 'DROPOUT', 'STUCK_SENSOR'].map((type) => (
              <div key={type} className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold">{type}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-400 rounded-full"
                      style={{
                        width: `${Math.min(100, (byType[type] || 0) * 25)}%`,
                      }}
                    />
                  </div>
                  <span className="font-mono text-slate-300 font-bold w-4 text-right">
                    {byType[type] || 0}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="analytics-card">
          <h3 className="analytics-card-title flex items-center gap-2">
            <BarChart2 size={16} className="text-rose-400" /> Severity Routing Breakdown
          </h3>
          <div className="space-y-3 mt-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">IGNORE (0-30)</span>
              <span className="font-mono text-slate-400 font-bold">{bySev['IGNORE'] || 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-amber-400">MONITOR (31-70)</span>
              <span className="font-mono text-amber-400 font-bold">{bySev['MONITOR'] || 0}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-rose-500 font-bold">URGENT (71-100)</span>
              <span className="font-mono text-rose-500 font-bold">{bySev['URGENT'] || 0}</span>
            </div>
          </div>
        </div>

        {/* Sensor Failure Frequency */}
        <div className="analytics-card">
          <h3 className="analytics-card-title flex items-center gap-2">
            <BarChart2 size={16} className="text-cyan-400" /> Sensor Anomaly Frequency
          </h3>
          <div className="space-y-2 mt-3 text-xs">
            {['temperature', 'vibration', 'pressure', 'rpm', 'current'].map((s) => (
              <div key={s} className="flex items-center justify-between">
                <span className="uppercase font-mono text-slate-300">{s}</span>
                <span className="font-mono font-bold text-cyan-400">{bySensor[s] || 0}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
