import React, { useState } from 'react';
import { ShieldAlert, Play, Pause, Square, RotateCcw, Activity, Wifi, WifiOff } from 'lucide-react';
import { api } from '../services/api';

interface HeaderProps {
  isConnected: boolean;
  isWebSocket: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ isConnected, isWebSocket, onRefresh }) => {
  const [actionStatus, setActionStatus] = useState<string | null>(null);

  const handleControl = async (action: 'start' | 'pause' | 'stop' | 'reset') => {
    try {
      if (action === 'start') await api.startSimulation();
      if (action === 'pause') await api.pauseSimulation();
      if (action === 'stop') await api.stopSimulation();
      if (action === 'reset') await api.resetSimulation();
      
      setActionStatus(`Simulation ${action.toUpperCase()} requested`);
      setTimeout(() => setActionStatus(null), 2500);
      onRefresh();
    } catch (e) {
      console.error(`Failed to execute simulation ${action}:`, e);
      setActionStatus(`Error executing ${action}`);
      setTimeout(() => setActionStatus(null), 3000);
    }
  };

  return (
    <header className="header-container">
      <div className="header-left">
        <div className="logo-badge">
          <ShieldAlert className="logo-icon text-cyan-400" size={32} />
        </div>
        <div>
          <h1 className="header-title">
            INDUSTRIAL<span className="text-cyan-400">GUARD</span> AI
          </h1>
          <p className="header-tagline">"Detect. Understand. Prioritize. Act."</p>
        </div>
      </div>

      <div className="header-right">
        {/* Status indicator */}
        <div className={`status-pill ${isConnected ? 'status-connected' : 'status-disconnected'}`}>
          {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
          <span>{isConnected ? 'CONNECTED' : 'DISCONNECTED'}</span>
          <span className="text-xs opacity-75">({isWebSocket ? 'WS STREAM' : 'HTTP POLL'})</span>
        </div>

        {/* Simulation Controls */}
        <div className="sim-controls">
          <button onClick={() => handleControl('start')} title="Start Simulation Stream" className="sim-btn sim-start">
            <Play size={16} /> Start
          </button>
          <button onClick={() => handleControl('pause')} title="Pause Simulation" className="sim-btn sim-pause">
            <Pause size={16} /> Pause
          </button>
          <button onClick={() => handleControl('stop')} title="Stop Simulation" className="sim-btn sim-stop">
            <Square size={16} /> Stop
          </button>
          <button onClick={() => handleControl('reset')} title="Reset Simulation & Clear Anomalies" className="sim-btn sim-reset">
            <RotateCcw size={16} /> Reset
          </button>
        </div>
      </div>

      {actionStatus && (
        <div className="toast-notification">
          <Activity size={14} className="animate-spin" /> {actionStatus}
        </div>
      )}
    </header>
  );
};
