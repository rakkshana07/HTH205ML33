import React from 'react';
import type { Anomaly } from '../types/industrial';
import { Radio, AlertTriangle, ArrowUpRight, TrendingUp, ZapOff, Lock } from 'lucide-react';

interface AnomalyFeedProps {
  anomalies: Anomaly[];
}

export const AnomalyFeed: React.FC<AnomalyFeedProps> = ({ anomalies }) => {
  const getAnomalyIcon = (type: string) => {
    switch (type) {
      case 'SPIKE':
        return <ArrowUpRight size={14} className="text-rose-400" />;
      case 'DRIFT':
        return <TrendingUp size={14} className="text-amber-400" />;
      case 'DROPOUT':
        return <ZapOff size={14} className="text-purple-400" />;
      case 'STUCK_SENSOR':
        return <Lock size={14} className="text-cyan-400" />;
      default:
        return <AlertTriangle size={14} />;
    }
  };

  const getSeverityBadgeClass = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'URGENT':
        return 'severity-badge-urgent';
      case 'MONITOR':
        return 'severity-badge-monitor';
      case 'IGNORE':
        return 'severity-badge-ignore';
      default:
        return 'severity-badge-ignore';
    }
  };

  return (
    <div className="section-container">
      <div className="section-header">
        <h2 className="section-title">
          <Radio size={20} className="text-rose-400 animate-pulse" />
          REAL-TIME ANOMALY DETECTION FEED
        </h2>
        <span className="text-xs text-slate-400 font-mono">
          TOTAL DETECTED: {anomalies.length}
        </span>
      </div>

      {anomalies.length === 0 ? (
        <div className="empty-state-card">
          <p className="text-emerald-400 font-semibold mb-1">SYSTEM NOMINAL</p>
          <p className="text-slate-400 text-sm">No active anomalies detected across machines.</p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>TIMESTAMP</th>
                <th>MACHINE</th>
                <th>SENSOR</th>
                <th>ANOMALY TYPE</th>
                <th>SEVERITY</th>
                <th>SCORE</th>
                <th>CONFIDENCE</th>
                <th>DEVIATION</th>
                <th>POSSIBLE CAUSE</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.map((anom) => (
                <tr key={anom.anomaly_id} className="table-row-hover">
                  <td className="font-mono text-xs text-slate-400">
                    {new Date(anom.timestamp).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit',
                    })}
                  </td>
                  <td className="font-semibold text-cyan-400">{anom.machine_id}</td>
                  <td className="uppercase text-xs font-mono">{anom.sensor_type}</td>
                  <td>
                    <span className={`type-badge type-${anom.anomaly_type.toLowerCase()}`}>
                      {getAnomalyIcon(anom.anomaly_type)}
                      <span>{anom.anomaly_type}</span>
                    </span>
                  </td>
                  <td>
                    <span className={`severity-badge ${getSeverityBadgeClass(anom.severity)}`}>
                      {anom.severity}
                    </span>
                  </td>
                  <td className="font-mono font-bold">{anom.severity_score}</td>
                  <td className="font-mono text-cyan-400">{anom.confidence}%</td>
                  <td className="font-mono">{anom.deviation}</td>
                  <td className="text-xs text-slate-300 max-w-xs truncate" title={anom.possible_cause}>
                    {anom.possible_cause}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
