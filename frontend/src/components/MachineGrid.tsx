import React from 'react';
import type { Machine, Anomaly } from '../types/industrial';
import { Activity, ShieldCheck, AlertCircle, AlertOctagon, Flame, Waves, Gauge, RotateCw, Zap } from 'lucide-react';

interface MachineGridProps {
  machines: Machine[];
  activeAnomalies: Anomaly[];
  selectedMachineId: string;
  onSelectMachine: (machineId: string) => void;
}

export const MachineGrid: React.FC<MachineGridProps> = ({
  machines,
  activeAnomalies,
  selectedMachineId,
  onSelectMachine,
}) => {
  const getActiveAnomalyForMachine = (machineId: string) => {
    return activeAnomalies.filter((a) => a.machine_id === machineId);
  };

  return (
    <div className="section-container">
      <div className="section-header">
        <h2 className="section-title">
          <Activity size={20} className="text-cyan-400" />
          MACHINE TELEMETRY MATRIX (10 MACHINES)
        </h2>
        <span className="text-xs text-slate-400">Select machine to view real-time sensor streams</span>
      </div>

      <div className="machine-grid">
        {machines.map((machine) => {
          const isSelected = machine.machine_id === selectedMachineId;
          const machineAnomalies = getActiveAnomalyForMachine(machine.machine_id);
          const hasAnomaly = machineAnomalies.length > 0;

          // Status Badge details
          let statusBadgeClass = 'badge-healthy';
          let StatusIcon = ShieldCheck;
          if (machine.status === 'MONITORING') {
            statusBadgeClass = 'badge-monitoring';
            StatusIcon = AlertCircle;
          } else if (machine.status === 'URGENT') {
            statusBadgeClass = 'badge-urgent';
            StatusIcon = AlertOctagon;
          }

          const sensors = machine.sensors || {};

          return (
            <div
              key={machine.machine_id}
              onClick={() => onSelectMachine(machine.machine_id)}
              className={`machine-card ${isSelected ? 'machine-card-selected' : ''} ${
                hasAnomaly ? 'machine-card-anomalous' : ''
              }`}
            >
              {/* Header */}
              <div className="machine-card-header">
                <div>
                  <div className="machine-id">{machine.machine_id}</div>
                  <div className="machine-name">{machine.machine_name}</div>
                </div>
                <div className={`status-badge ${statusBadgeClass}`}>
                  <StatusIcon size={12} />
                  <span>{machine.status}</span>
                </div>
              </div>

              {/* Location & Criticality */}
              <div className="machine-meta">
                <span>{machine.location}</span>
                <span className={`crit-badge crit-${machine.criticality.toLowerCase()}`}>
                  {machine.criticality} CRIT
                </span>
              </div>

              {/* Health Score Bar */}
              <div className="health-bar-wrapper">
                <div className="health-label">
                  <span>HEALTH INDEX</span>
                  <span className="font-mono">{machine.health_score}%</span>
                </div>
                <div className="health-track">
                  <div
                    className="health-fill"
                    style={{
                      width: `${machine.health_score}%`,
                      backgroundColor:
                        machine.health_score >= 80 ? '#00FF88' : machine.health_score >= 50 ? '#FFB800' : '#FF3366',
                    }}
                  />
                </div>
              </div>

              {/* 5 Sensors Grid */}
              <div className="sensors-readout-grid">
                <div className="sensor-readout-item">
                  <span className="sensor-readout-label"><Flame size={12} className="text-orange-400" /> TEMP</span>
                  <span className="sensor-readout-val">
                    {sensors['temperature']?.current_value !== null && sensors['temperature']?.current_value !== undefined
                      ? `${sensors['temperature'].current_value} °C`
                      : 'N/A'}
                  </span>
                </div>

                <div className="sensor-readout-item">
                  <span className="sensor-readout-label"><Waves size={12} className="text-cyan-400" /> VIB</span>
                  <span className="sensor-readout-val">
                    {sensors['vibration']?.current_value !== null && sensors['vibration']?.current_value !== undefined
                      ? `${sensors['vibration'].current_value} mm/s`
                      : 'N/A'}
                  </span>
                </div>

                <div className="sensor-readout-item">
                  <span className="sensor-readout-label"><Gauge size={12} className="text-blue-400" /> PRESS</span>
                  <span className="sensor-readout-val">
                    {sensors['pressure']?.current_value !== null && sensors['pressure']?.current_value !== undefined
                      ? `${sensors['pressure'].current_value} bar`
                      : 'N/A'}
                  </span>
                </div>

                <div className="sensor-readout-item">
                  <span className="sensor-readout-label"><RotateCw size={12} className="text-purple-400" /> RPM</span>
                  <span className="sensor-readout-val">
                    {sensors['rpm']?.current_value !== null && sensors['rpm']?.current_value !== undefined
                      ? `${sensors['rpm'].current_value} RPM`
                      : 'N/A'}
                  </span>
                </div>

                <div className="sensor-readout-item col-span-2">
                  <span className="sensor-readout-label"><Zap size={12} className="text-yellow-400" /> CURRENT</span>
                  <span className="sensor-readout-val">
                    {sensors['current']?.current_value !== null && sensors['current']?.current_value !== undefined
                      ? `${sensors['current'].current_value} A`
                      : 'N/A'}
                  </span>
                </div>
              </div>

              {/* Active Anomaly Indicator */}
              {hasAnomaly && (
                <div className="machine-anomaly-banner">
                  <AlertCircle size={14} className="animate-pulse text-amber-400" />
                  <span>
                    {machineAnomalies[0].anomaly_type} detected on [{machineAnomalies[0].sensor_type}]
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
