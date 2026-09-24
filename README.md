# INDUSTRIALGUARD AI

> **"Detect. Understand. Prioritize. Act."**

[![Hackathon Problem](https://img.shields.io/badge/Hackathon--Problem-HTH--ML--10-blue.svg)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0-61dafb.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646cff.svg)](https://vitejs.dev/)
[![ML](https://img.shields.io/badge/scikit--learn-Isolation%20Forest-orange.svg)](https://scikit-learn.org/)

A real-time, severity-aware streaming anomaly detection and industrial telemetry dashboard for Internet of Things (IIoT) sensors.

---

## Table of Contents
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Machine Learning & Anomaly Engine](#machine-learning--anomaly-engine)
  - [Feature Engineering](#feature-engineering)
  - [Isolation Forest Detector](#isolation-forest-detector)
  - [Anomaly Classifications](#anomaly-classifications)
  - [Severity & Confidence Scoring](#severity--confidence-scoring)
  - [Explainable Root-Cause Hints](#explainable-root-cause-hints)
- [REST API Reference](#rest-api-reference)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Demonstration & Testing](#demonstration--testing)

---

## Problem Statement

**HTH-ML-10 — Severity-Aware Streaming Anomaly Detector for Industrial Sensors**

In high-stakes industrial environments (power plants, chemical processing, heavy manufacturing), sensor streams generate massive volumes of continuous telemetry data. Traditional threshold monitoring produces either excessive false alarms or fails to detect insidious failure patterns (such as subtle sensor drift or frozen transducer lockups).

**IndustrialGuard AI** addresses this challenge by providing an intelligent, streaming anomaly detector that flags anomalies using machine learning, classifies the failure mode, calculates context-aware severity (0–100), provides human-explainable *"Possible Cause"* hints, and routes prioritized alerts to field engineers.

---

## Solution Overview

IndustrialGuard AI features a decoupled high-performance architecture:

1. **Python 3.11 + FastAPI ML Backend**: A streaming simulator generating realistic multi-sensor telemetry for 10 industrial machines across 5 sensor channels (`temperature`, `vibration`, `pressure`, `rpm`, `current`).
2. **Hybrid Anomaly Engine**: Integrates `scikit-learn` Isolation Forest unsupervised learning with deterministic rolling feature metrics (`rolling_mean`, `rolling_std`, `rate_of_change`, `trend_slope`, `missing_data_indicator`) to eliminate false positives on baseline normal operations.
3. **Stateful Anomaly Injection Engine**: REST API endpoints allowing live injection of `SPIKE`, `DRIFT`, `DROPOUT`, and `STUCK_SENSOR` behaviors to simulate real-world equipment failures.
4. **React + TypeScript + Vite Dashboard**: An industrial telemetry monitoring dashboard with real-time WebSocket streaming (`/ws/live`), HTTP polling fallback, dynamic sensor charts (Recharts), incident alert lifecycles, and aggregated analytics.

---

## Key Features

- **10 Industrial Machines Monitored**: Pre-configured telemetry for critical assets (`MACHINE-01` to `MACHINE-10`) such as Steam Turbines, Boiler Feedwater Pumps, Hydraulic Presses, and Power Transformers.
- **5 Sensor Channels per Asset**: Live monitoring of Temperature (°C), Vibration (mm/s), Pressure (bar), Speed (RPM), and Current (A).
- **Zero False-Positive Startup**: Pre-seeded warm-up history guarantees nominal baseline operation with **0 active anomalies** upon normal startup.
- **4 Real Anomaly Injections**:
  - `SPIKE`: Sudden large step changes (e.g., thermal surge, electrical shock).
  - `DRIFT`: Gradual sustained deviation (e.g., valve leakage, bearing degradation).
  - `DROPOUT`: Communication loss or fieldbus disconnect (`Null` / missing readings).
  - `STUCK_SENSOR`: Transducer lockup with zero signal variance.
- **Contextual Severity Scoring (0–100)**: Considers anomaly magnitude, duration, machine criticality (`HIGH`, `MEDIUM`, `LOW`), and sensor sensitivity.
- **Tri-Level Alert Routing**:
  - `IGNORE` (0–30): Filtered or logged for baseline tracking.
  - `MONITOR` (31–70): Flagged for predictive maintenance review.
  - `URGENT` (71–100): Triggers high-priority alerts for immediate inspection.
- **Deduplicated Alert Lifecycle**: Grouping and cooldown mechanisms prevent alert flooding by maintaining active state transitions (`ACTIVE` → `ACKNOWLEDGED` → `RESOLVED`).
- **Resilient Telemetry Pipeline**: Dual-mode streaming supporting WebSockets (`/ws/live`) with automatic fallback to HTTP polling (`/api/live-data`).

---

## System Architecture

```
                       +-----------------------------------+
                       |    INDUSTRIAL SENSOR STREAMING    |
                       |       SIMULATOR (10 Assets)       |
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------+-----------------+
                       |       FEATURE ENGINEERING         |
                       | (Mean, Std, Rate-of-Change, Slope)|
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------+-----------------+
                       |    HYBRID ANOMALY DETECTOR        |
                       |   - scikit-learn IsolationForest  |
                       |   - Behavioral Rule Classifier    |
                       +-----------------+-----------------+
                                         |
                                         v
                       +-----------------+-----------------+
                       |   SEVERITY & EXPLANATION ENGINE   |
                       |  - Severity Score (0-100)         |
                       |  - Possible Cause & Rec Action    |
                       +-----------------+-----------------+
                                         |
                                         v
             +---------------------------+---------------------------+
             |                                                       |
             v                                                       v
+------------------------+                              +------------------------+
|  REST & WEBSOCKET API  |                              |    ALERT SERVICE       |
|    (FastAPI / Uvicorn) |                              |  (Grouping / Cooldown) |
+------------+-----------+                              +------------+-----------+
             |                                                       |
             +---------------------------+---------------------------+
                                         |
                                         v
                       +-----------------+-----------------+
                       |    REACT + TS VITE DASHBOARD      |
                       | (Recharts, Telemetry, Controls)   |
                       +-----------------------------------+
```

---

## Machine Learning & Anomaly Engine

### Feature Engineering (`app/ml/features.py`)
Features extracted across rolling historical windows:
- `current_value`: Latest reading from sensor stream.
- `rolling_mean`: Moving average of valid readings.
- `rolling_std`: Standard deviation across recent window.
- `baseline_value`: Target baseline constant per sensor profile.
- `baseline_deviation`: `abs(current_value - baseline_value)`.
- `rate_of_change`: Instantaneous delta between consecutive valid readings.
- `trend_slope`: Linear regression slope across window.
- `missing_data_indicator`: Binary flag (1 if value is `None`/`NaN`).
- `consecutive_stuck_count`: Count of consecutive identical float values.

### Isolation Forest Detector (`app/ml/detector.py`)
- Baseline models (`sklearn.ensemble.IsolationForest`) are initialized per sensor type on synthetic normal operational baseline data during service startup.
- **Model Integrity**: Baseline models remain focused on clean normal distributions and are not retrained on injected anomalies to prevent baseline drift corruption.

### Anomaly Classifications (`app/ml/classification.py`)
- **`SPIKE`**: Triggered by high rate of change combined with significant baseline deviation.
- **`DRIFT`**: Triggered by sustained linear slope and progressive deviation.
- **`DROPOUT`**: Triggered by missing data indicators or `None` values.
- **`STUCK_SENSOR`**: Triggered when window variance drops below threshold or consecutive identical count >= 4.
- **`NONE`**: Returned for standard stochastic operational noise.

### Severity & Confidence Scoring (`app/ml/severity.py`)
- Severity is calculated on a 0–100 scale using detected anomaly characteristics, duration, machine criticality, and sensor weights implemented by the severity engine.
- **Routing Rules**:
  - `0 – 30`: `IGNORE`
  - `31 – 70`: `MONITOR`
  - `71 – 100`: `URGENT`

### Explainable Root-Cause Hints (`app/ml/explanation.py`)
Generates actionable, non-presumptuous *"Possible Cause"* hints and practical recommended actions.
*Example*:
> **Anomaly**: Temperature Spike on `MACHINE-01`
> **Possible Cause**: *"Possible overheating, cooling-system failure, or sudden thermal surge."*
> **Recommended Action**: *"Inspect cooling system fan, verify coolant fluid levels, and check heat exchanger immediately. (Immediate inspection required)."*

---

## REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status and version metadata |
| `GET` | `/api/machines` | List all 10 industrial machines and current statuses |
| `GET` | `/api/machines/{machine_id}` | Detailed telemetry and sensor states for a machine |
| `GET` | `/api/sensors` | List current readings across all sensor channels |
| `GET` | `/api/live-data` | Polling fallback endpoint returning full live snapshot |
| `GET` | `/api/anomalies` | Query detected anomaly records (filter by status, severity) |
| `GET` | `/api/alerts` | Query active and historical incident alerts |
| `GET` | `/api/analytics` | Aggregated metrics (health counts, anomaly types) |
| `POST` | `/api/simulation/start` | Start live simulator stream |
| `POST` | `/api/simulation/pause` | Pause live simulator stream |
| `POST` | `/api/simulation/stop` | Stop live simulator stream |
| `POST` | `/api/simulation/reset` | Reset simulation to clean operational baseline |
| `POST` | `/api/simulation/inject/spike` | Inject instant SPIKE anomaly into machine sensor |
| `POST` | `/api/simulation/inject/drift` | Inject progressive DRIFT anomaly into machine sensor |
| `POST` | `/api/simulation/inject/dropout` | Inject communication DROPOUT into machine sensor |
| `POST` | `/api/simulation/inject/stuck` | Inject STUCK_SENSOR freeze into machine sensor |
| `POST` | `/api/alerts/{alert_id}/acknowledge` | Acknowledge active incident alert |
| `POST` | `/api/alerts/{alert_id}/resolve` | Resolve active incident alert |
| `WS` | `/ws/live` | Real-time WebSocket connection for live telemetry & anomalies |

---

## Project Structure

```text
industrialguard-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── schemas/
│   │   │   ├── machine.py
│   │   │   ├── sensor.py
│   │   │   └── anomaly.py
│   │   ├── services/
│   │   │   ├── simulation_service.py
│   │   │   ├── anomaly_service.py
│   │   │   └── alert_service.py
│   │   ├── ml/
│   │   │   ├── features.py
│   │   │   ├── detector.py
│   │   │   ├── classification.py
│   │   │   ├── severity.py
│   │   │   └── explanation.py
│   │   └── simulation/
│   │       ├── simulator.py
│   │       └── injection.py
│   ├── requirements.txt
│   ├── .env.example
│   └── test_backend.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── main.tsx
        ├── index.css
        ├── types/industrial.ts
        ├── services/api.ts
        ├── hooks/useLiveStream.ts
        └── components/
            ├── Header.tsx
            ├── KpiCards.tsx
            ├── MachineGrid.tsx
            ├── LiveSensorCharts.tsx
            ├── AnomalyFeed.tsx
            ├── AlertPanel.tsx
            ├── InjectionControlPanel.tsx
            └── AnalyticsPanel.tsx
```

---

## Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and `npm`

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   *The backend will start at `http://127.0.0.1:8000` with interactive API docs at `http://127.0.0.1:8000/docs`.*

### Frontend Setup

1. Open a new terminal and navigate to `frontend`:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npx vite --host 0.0.0.0 --port 5173
   ```
   *The dashboard will be available at `http://localhost:5173`.*

---

## Demonstration & Testing

### Running Automated Test Suite
Run the backend test suite to verify health endpoints, machine counts, sensor profiles, normal startup baseline, anomaly injection detection, severity mapping, alert lifecycles, and analytics:

```bash
cd backend
.\venv\Scripts\python test_backend.py
```

### Live Hackathon Demo Workflow

1. Open `http://localhost:5173` in your browser.
2. Confirm the **CONNECTED** status badge in the top-right corner.
3. Observe the **10 Machine Cards** with live sensor streams (`temperature`, `vibration`, `pressure`, `rpm`, `current`).
4. Observe the **Live Streaming Telemetry Charts** in the dashboard and monitor the selected sensor streams.
5. Scroll to the **Anomaly Injection Controls**:
   - Select `MACHINE-01`
   - Select `temperature`
   - Select `SPIKE`
   - Click **INJECT ANOMALY INTO SIMULATOR**.
6. Observe the immediate updates:
   - **Machine Matrix**: `MACHINE-01` status and severity indicators update according to the calculated severity.
   - **Telemetry Chart**: Spike jump rendered on the live graph.
   - **Anomaly Feed**: Injected anomaly appears with score, confidence %, and *"Possible Cause"*.
   - **Incident Alerts**: New alert generated in queue.
7. Click **Acknowledge** and **Mark Resolved** on the alert to demonstrate the full alert lifecycle (`ACTIVE` → `ACKNOWLEDGED` → `RESOLVED`).
8. Click **Reset** in the top header controls to return all 10 machines to clean operational baseline.

---

*IndustrialGuard AI — HTH-ML-10 Hackathon Solution*
