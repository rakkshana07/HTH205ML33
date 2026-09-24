import React, { useState } from 'react';
import type { Alert } from '../types/industrial';
import { Bell, CheckCircle2, ShieldAlert, Check } from 'lucide-react';
import { api } from '../services/api';

interface AlertPanelProps {
  alerts: Alert[];
  onAlertUpdated: () => void;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({ alerts, onAlertUpdated }) => {
  const [loadingAlertId, setLoadingAlertId] = useState<string | null>(null);

  const handleAcknowledge = async (alertId: string) => {
    try {
      setLoadingAlertId(alertId);
      await api.acknowledgeAlert(alertId);
      onAlertUpdated();
    } catch (e) {
      console.error('Failed to acknowledge alert:', e);
    } finally {
      setLoadingAlertId(null);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      setLoadingAlertId(alertId);
      await api.resolveAlert(alertId);
      onAlertUpdated();
    } catch (e) {
      console.error('Failed to resolve alert:', e);
    } finally {
      setLoadingAlertId(null);
    }
  };

  return (
    <div className="section-container">
      <div className="section-header">
        <h2 className="section-title">
          <Bell size={20} className="text-purple-400" />
          INCIDENT ALERTS & RECOMMENDED ACTIONS
        </h2>
        <span className="text-xs text-slate-400 font-mono">
          ACTIVE ALERTS: {alerts.filter((a) => a.status === 'ACTIVE').length}
        </span>
      </div>

      {alerts.length === 0 ? (
        <div className="empty-state-card">
          <CheckCircle2 size={32} className="text-emerald-400 mb-2" />
          <p className="text-emerald-400 font-semibold mb-1">ALL ALERTS RESOLVED</p>
          <p className="text-slate-400 text-sm">No actionable alerts currently in queue.</p>
        </div>
      ) : (
        <div className="alert-cards-grid">
          {alerts.map((alert) => {
            const isResolved = alert.status === 'RESOLVED';
            const isAck = alert.status === 'ACKNOWLEDGED';
            const isLoading = loadingAlertId === alert.alert_id;

            const sevLevel = alert.severity || (alert as any).alert_level || 'MONITOR';
            const sevScore = alert.severity_score ?? (alert as any).occurrence_count ?? 50;

            let borderClass = 'border-purple-500/40 bg-purple-500/5';
            if (sevLevel === 'URGENT') {
              borderClass = 'border-rose-500/60 bg-rose-500/10';
            } else if (sevLevel === 'MONITOR') {
              borderClass = 'border-amber-500/50 bg-amber-500/5';
            }
            if (isResolved) {
              borderClass = 'border-slate-800 bg-slate-900/40 opacity-60';
            }

            return (
              <div key={alert.alert_id} className={`alert-card ${borderClass}`}>
                <div className="alert-card-header">
                  <div className="flex items-center gap-2">
                    <ShieldAlert
                      size={18}
                      className={
                        sevLevel === 'URGENT'
                          ? 'text-rose-400 animate-pulse'
                          : sevLevel === 'MONITOR'
                          ? 'text-amber-400'
                          : 'text-slate-400'
                      }
                    />
                    <span className="font-mono font-bold text-slate-200">{alert.alert_id}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`severity-badge severity-badge-${sevLevel.toLowerCase()}`}>
                      {sevLevel} ({sevScore})
                    </span>
                    <span className={`status-pill-sm status-${alert.status.toLowerCase()}`}>
                      {alert.status}
                    </span>
                  </div>
                </div>

                <div className="alert-card-body">
                  <div className="text-sm font-semibold text-cyan-300 mb-1">
                    {alert.machine_id} — [{alert.sensor_type.toUpperCase()}]
                  </div>
                  <p className="text-xs text-slate-300 mb-3">{alert.message}</p>

                  <div className="alert-meta-box">
                    <div className="text-xs">
                      <span className="font-semibold text-slate-400">Time:</span>{' '}
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                {!isResolved && (
                  <div className="alert-card-actions">
                    {!isAck && (
                      <button
                        onClick={() => handleAcknowledge(alert.alert_id)}
                        disabled={isLoading}
                        className="btn-ack"
                      >
                        <Check size={14} /> Acknowledge
                      </button>
                    )}
                    <button
                      onClick={() => handleResolve(alert.alert_id)}
                      disabled={isLoading}
                      className="btn-resolve"
                    >
                      <CheckCircle2 size={14} /> Mark Resolved
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
