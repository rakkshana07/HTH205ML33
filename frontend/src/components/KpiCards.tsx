import React from 'react';
import { Cpu, AlertTriangle, Bell, Zap } from 'lucide-react';
import type { Machine, Anomaly, Alert } from '../types/industrial';

interface KpiCardsProps {
  machines: Machine[];
  activeAnomalies: Anomaly[];
  alerts: Alert[];
}

export const KpiCards: React.FC<KpiCardsProps> = ({ machines, activeAnomalies, alerts }) => {
  const totalMachines = machines.length;
  const activeAnomalyCount = activeAnomalies.length;

  const activeAlerts = alerts.filter((a) => a.status === 'ACTIVE');
  const activeAlertCount = activeAlerts.length;

  const urgentAlerts = alerts.filter((a) => (a.severity === 'URGENT' || (a as any).alert_level === 'URGENT') && a.status === 'ACTIVE');
  const urgentAlertCount = urgentAlerts.length;

  return (
    <div className="kpi-grid">
      {/* 1. Total Machines */}
      <div className="kpi-card border-cyan-500/30">
        <div className="kpi-icon-wrapper bg-cyan-500/10 text-cyan-400">
          <Cpu size={24} />
        </div>
        <div>
          <div className="kpi-label">TOTAL MACHINES</div>
          <div className="kpi-value text-cyan-400">{totalMachines}</div>
          <div className="kpi-subtext">100% Telemetry Active</div>
        </div>
      </div>

      {/* 2. Active Anomalies */}
      <div className={`kpi-card ${activeAnomalyCount > 0 ? 'border-amber-500/50 bg-amber-500/5' : 'border-slate-700'}`}>
        <div className={`kpi-icon-wrapper ${activeAnomalyCount > 0 ? 'bg-amber-500/20 text-amber-400 animate-pulse' : 'bg-slate-800 text-slate-400'}`}>
          <AlertTriangle size={24} />
        </div>
        <div>
          <div className="kpi-label">ACTIVE ANOMALIES</div>
          <div className={`kpi-value ${activeAnomalyCount > 0 ? 'text-amber-400' : 'text-slate-300'}`}>
            {activeAnomalyCount}
          </div>
          <div className="kpi-subtext">
            {activeAnomalyCount === 0 ? 'Nominal Baseline' : `${activeAnomalyCount} Machine(s) Affected`}
          </div>
        </div>
      </div>

      {/* 3. Active Alerts */}
      <div className="kpi-card border-purple-500/30">
        <div className="kpi-icon-wrapper bg-purple-500/10 text-purple-400">
          <Bell size={24} />
        </div>
        <div>
          <div className="kpi-label">ACTIVE ALERTS</div>
          <div className="kpi-value text-purple-400">{activeAlertCount}</div>
          <div className="kpi-subtext">Routed & Deduplicated</div>
        </div>
      </div>

      {/* 4. Urgent Alerts */}
      <div className={`kpi-card ${urgentAlertCount > 0 ? 'border-rose-500/60 bg-rose-500/10' : 'border-slate-700'}`}>
        <div className={`kpi-icon-wrapper ${urgentAlertCount > 0 ? 'bg-rose-500/20 text-rose-400 animate-bounce' : 'bg-slate-800 text-slate-400'}`}>
          <Zap size={24} />
        </div>
        <div>
          <div className="kpi-label">URGENT ALERTS</div>
          <div className={`kpi-value ${urgentAlertCount > 0 ? 'text-rose-500' : 'text-slate-300'}`}>
            {urgentAlertCount}
          </div>
          <div className="kpi-subtext">
            {urgentAlertCount > 0 ? 'Immediate Action Required' : 'Zero High Priority Alerts'}
          </div>
        </div>
      </div>
    </div>
  );
};
