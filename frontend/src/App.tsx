import { useLiveStream } from './hooks/useLiveStream';
import { Header } from './components/Header';
import { KpiCards } from './components/KpiCards';
import { MachineGrid } from './components/MachineGrid';
import { LiveSensorCharts } from './components/LiveSensorCharts';
import { AnomalyFeed } from './components/AnomalyFeed';
import { AlertPanel } from './components/AlertPanel';
import { InjectionControlPanel } from './components/InjectionControlPanel';
import { AnalyticsPanel } from './components/AnalyticsPanel';
import { AlertOctagon, RefreshCw } from 'lucide-react';

export function App() {
  const {
    machines,
    activeAnomalies,
    allAnomalies,
    alerts,
    analytics,
    isConnected,
    isWebSocket,
    selectedMachineId,
    setSelectedMachineId,
    sensorHistory,
    refreshAuxiliaryData,
  } = useLiveStream();

  const selectedMachine = machines.find((m) => m.machine_id === selectedMachineId);

  return (
    <div className="app-container">
      {/* Top Navigation & Controls */}
      <Header
        isConnected={isConnected}
        isWebSocket={isWebSocket}
        onRefresh={refreshAuxiliaryData}
      />

      {/* Backend Offline Warning Banner */}
      {!isConnected && (
        <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/40 text-rose-300 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertOctagon size={24} className="text-rose-400 animate-pulse" />
            <div>
              <div className="font-bold text-sm">BACKEND DISCONNECTED</div>
              <div className="text-xs text-rose-300/80">
                Cannot reach FastAPI server at {import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}. Make sure the backend is running.
              </div>
            </div>
          </div>
          <button
            onClick={refreshAuxiliaryData}
            className="px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 text-xs font-bold flex items-center gap-1.5 border border-rose-500/40 cursor-pointer"
          >
            <RefreshCw size={14} /> Retry Connection
          </button>
        </div>
      )}

      {/* KPI Cards Header */}
      <KpiCards
        machines={machines}
        activeAnomalies={activeAnomalies}
        alerts={alerts}
      />

      {/* Machine Telemetry Matrix (10 Machines) */}
      <MachineGrid
        machines={machines}
        activeAnomalies={activeAnomalies}
        selectedMachineId={selectedMachineId}
        onSelectMachine={setSelectedMachineId}
      />

      {/* Live Streaming Charts for Selected Machine */}
      <LiveSensorCharts
        machine={selectedMachine}
        history={sensorHistory}
        activeAnomalies={activeAnomalies}
      />

      {/* Anomaly Injection Controls */}
      <InjectionControlPanel
        machines={machines}
        onInjectionSuccess={refreshAuxiliaryData}
      />

      {/* Real-time Anomaly Stream Table */}
      <AnomalyFeed anomalies={allAnomalies} />

      {/* Alerts & Interactive Resolution */}
      <AlertPanel alerts={alerts} onAlertUpdated={refreshAuxiliaryData} />

      {/* Analytics Summary */}
      <AnalyticsPanel analytics={analytics} />

      {/* Footer */}
      <footer className="mt-8 pt-4 border-t border-slate-800 text-center text-xs text-slate-500 flex justify-between">
        <span>INDUSTRIALGUARD AI — Severity-Aware Streaming Anomaly Detector</span>
        <span>HTH-ML-10 Hackathon Solution</span>
      </footer>
    </div>
  );
}

export default App;
