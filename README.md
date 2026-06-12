# Spacecraft Telemetry Pipeline

A full-stack telemetry pipeline that ingests sensor data from a simulated spacecraft, stores it in a database, detects real-time anomalies, and visualizes it on a live dashboard.

---

## Architecture

```
[Spacecraft Simulator] --POST /telemetry--> [FastAPI Server] --> [SQLite Database]
                                                                        |
                                              [TypeScript Dashboard] <--GET /telemetry--
```

The simulator generates realistic sensor readings using a **random walk algorithm** and periodically injects out-of-bounds spikes to trigger anomaly detection. The server ingests each packet, validates it, flags anomalies at ingest time, and stores everything with a full audit trail. The frontend polls the API every 2 seconds and updates live charts.

---

## Features

- **Telemetry ingest** — POST endpoint validates and stores incoming packets using Pydantic type enforcement
- **Real-time anomaly detection** — each packet is evaluated against nominal bounds at ingest; anomaly flag stored with the record
- **Live dashboard** — TypeScript frontend with Chart.js visualizations, polls every 2 seconds, displays red alert banner on anomalous readings
- **Queryable history** — GET endpoint supports filtering by spacecraft ID, time range, sort order, and result limit
- **Realistic simulator** — random walk per sensor field with occasional out-of-bounds spike injection (3% rate)

---

## Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Backend    | Python, FastAPI, Pydantic |
| Database   | SQLite                  |
| Frontend   | TypeScript, Vite, Chart.js |
| Simulator  | Python, requests        |

---

## How to Run

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API server

```bash
uvicorn server:app --reload
```

Server runs at `http://localhost:8000`. The database is created automatically on first run.

### 3. Start the frontend dashboard

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs at `http://localhost:5173`.

### 4. Start the telemetry simulator

In a separate terminal:

```bash
python sc_simulator.py
```

The simulator sends one telemetry packet per second to the server. Watch the dashboard update live.

---

## Project Structure

```
Spacecraft_Telemetry_Pipeline/
├── server.py            # FastAPI server — ingest, storage, anomaly detection, query API
├── sc_simulator.py      # Telemetry simulator — random walk, spike injection
├── telemetry.db         # SQLite database (auto-created on first run)
├── requirements.txt     # Python dependencies
└── frontend/
    ├── index.html       # Dashboard layout — charts + anomaly alert banner
    └── src/
        ├── api.ts       # API client — fetch telemetry, TypeScript types
        ├── charts.ts    # Chart.js setup and update logic
        ├── main.ts      # Polling loop, anomaly banner control
        └── style.css    # Dashboard styling
```

---

## API Reference

### `POST /telemetry`

Ingest a telemetry packet. Returns `201` on success.

**Request body:**
```json
{
  "spacecraft_id": "SC-1",
  "timestamp": "2026-06-12T10:00:00",
  "temperature": 22.5,
  "battery_voltage": 25.1,
  "altitude": 408.3,
  "attitude": 12.4
}
```

### `GET /telemetry`

Retrieve stored telemetry with optional filters.

| Parameter      | Type   | Description                    |
|----------------|--------|--------------------------------|
| `spacecraft_id`| string | Filter by spacecraft ID        |
| `start`        | datetime | Filter by start timestamp    |
| `end`          | datetime | Filter by end timestamp      |
| `order`        | string | `ASC` or `DESC` (default DESC) |
| `limit`        | int    | Max records returned (default 15) |

---

## Nominal Sensor Bounds

| Sensor           | Min     | Max    |
|------------------|---------|--------|
| Temperature (°C) | -40.0   | 85.0   |
| Battery Voltage (V) | 22.0 | 29.5   |
| Altitude (km)    | 400.0   | 420.0  |
| Attitude (°)     | -180.0  | 180.0  |

Readings outside these bounds are flagged as anomalies in the database and trigger the dashboard alert.
