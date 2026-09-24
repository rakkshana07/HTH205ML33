import React, { useState } from 'react';
import type { Machine } from '../types/industrial';
import { Syringe, Flame, Waves, Gauge, RotateCw, Zap, ArrowUpRight, TrendingUp, ZapOff, Lock, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

interface InjectionControlPanelProps {
  machines: Machine[];
  onInjectionSuccess: () => void;
}

export const InjectionControlPanel: React.FC<InjectionControlPanelProps> = ({
  machines,
  onInjectionSuccess,
}) => {
  const [targetMachine, setTargetMachine] = useState<string>('MACHINE-01');
  const [targetSensor, setTargetSensor] = useState<string>('temperature');
  const [anomalyType, setAnomalyType] = useState<'SPIKE' | 'DRIFT' | 'DROPOUT' | 'STUCK_SENSOR'>('SPIKE');
  const [magnitude, setMagnitude] = useState<number>(45.0);
  
  const [loading, setLoading] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const handleInject = async () => {
    try {
      setLoading(true);
      if (anomalyType === 'SPIKE') {
        await api.injectSpike(targetMachine, targetSensor, magnitude);
      } else if (anomalyType === 'DRIFT') {
        await api.injectDrift(targetMachine, targetSensor, magnitude / 10.0);
      } else if (anomalyType === 'DROPOUT') {
        await api.injectDropout(targetMachine, targetSensor);
      } else if (anomalyType === 'STUCK_SENSOR') {
        await api.injectStuck(targetMachine, targetSensor);
      }

      setToastMessage(`SUCCESS: Injected ${anomalyType} on ${targetMachine} [${targetSensor.toUpperCase()}]`);
      setTimeout(() => setToastMessage(null), 4000);
      onInjectionSuccess();
    } catch (e) {
      console.error('Injection failed:', e);
      setToastMessage(`ERROR: Injection failed`);
      setTimeout(() => setToastMessage(null), 4000);
    } finally {
      setLoading(false);
    }
  };

  const sensorsList = [
    { id: 'temperature', name: 'Temperature', icon: Flame },
    { id: 'vibration', name: 'Vibration', icon: Waves },
    { id: 'pressure', name: 'Pressure', icon: Gauge },
    { id: 'rpm', name: 'RPM', icon: RotateCw },
    { id: 'current', name: 'Current', icon: Zap },
  ];

  const typesList = [
    { id: 'SPIKE', name: 'SPIKE (Sudden Jump)', icon: ArrowUpRight, desc: 'Large instant step offset' },
    { id: 'DRIFT', name: 'DRIFT (Gradual Shift)', icon: TrendingUp, desc: 'Steady movement away from baseline' },
    { id: 'DROPOUT', name: 'DROPOUT (Comms Fault)', icon: ZapOff, desc: 'Missing / Null sensor readings' },
    { id: 'STUCK_SENSOR', name: 'STUCK SENSOR (Frozen Output)', icon: Lock, desc: 'Identical static output with zero variance' },
  ];

  return (
    <div className="section-container">
      <div className="section-header">
        <h2 className="section-title">
          <Syringe size={20} className="text-amber-400" />
          REAL ANOMALY INJECTION CONTROLS
        </h2>
        <span className="text-xs text-slate-400">Modifies simulator state for future sensor streams</span>
      </div>

      {toastMessage && (
        <div className="injection-toast">
          <CheckCircle2 size={16} className="text-emerald-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      <div className="injection-grid">
        {/* Step 1: Select Target Machine */}
        <div className="injection-card">
          <label className="injection-label">1. SELECT TARGET MACHINE</label>
          <select
            value={targetMachine}
            onChange={(e) => setTargetMachine(e.target.value)}
            className="injection-select"
          >
            {machines.map((m) => (
              <option key={m.machine_id} value={m.machine_id}>
                {m.machine_id} — {m.machine_name} ({m.criticality})
              </option>
            ))}
          </select>
        </div>

        {/* Step 2: Select Sensor */}
        <div className="injection-card">
          <label className="injection-label">2. SELECT TARGET SENSOR</label>
          <div className="sensor-chip-grid">
            {sensorsList.map((s) => {
              const IconComp = s.icon;
              const isSelected = targetSensor === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => setTargetSensor(s.id)}
                  className={`chip-btn ${isSelected ? 'chip-btn-active' : ''}`}
                >
                  <IconComp size={14} />
                  <span>{s.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 3: Select Anomaly Type */}
        <div className="injection-card col-span-2">
          <label className="injection-label">3. SELECT ANOMALY TYPE</label>
          <div className="type-chip-grid">
            {typesList.map((t) => {
              const IconComp = t.icon;
              const isSelected = anomalyType === t.id;
              return (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setAnomalyType(t.id as any)}
                  className={`type-card-btn ${isSelected ? 'type-card-active' : ''}`}
                >
                  <div className="flex items-center gap-2 font-bold text-sm">
                    <IconComp size={16} />
                    <span>{t.id}</span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1">{t.desc}</div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Magnitude Slider (for SPIKE / DRIFT) */}
      {(anomalyType === 'SPIKE' || anomalyType === 'DRIFT') && (
        <div className="mt-4 p-4 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center gap-4">
          <label className="text-xs font-bold text-slate-300 uppercase">
            Magnitude Offset: <span className="text-cyan-400 font-mono">{magnitude}</span>
          </label>
          <input
            type="range"
            min="10"
            max="100"
            step="5"
            value={magnitude}
            onChange={(e) => setMagnitude(Number(e.target.value))}
            className="flex-1 accent-cyan-400 cursor-pointer"
          />
        </div>
      )}

      {/* Submit Trigger Button */}
      <div className="mt-6 flex justify-end">
        <button
          onClick={handleInject}
          disabled={loading}
          className="btn-inject-trigger"
        >
          <Syringe size={18} />
          <span>{loading ? 'INJECTING...' : 'INJECT ANOMALY INTO SIMULATOR'}</span>
        </button>
      </div>
    </div>
  );
};
