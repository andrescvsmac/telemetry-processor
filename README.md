# Telemetry Processing Module

Your team ingests temperature + humidity telemetry from HVAC sensors. Sensors push data to your ingestion service every ~5 seconds.
A downstream alerting system needs a simplified “health snapshot” for each device.

You need to implement a small ingestion + summarization module, plus a simple API to retrieve the summary.

## Structure

```sh
.
├── api.py
├── demo.py
├── README.md
├── telemetry_processor.py
└── test_telemetry_processor.py
```

- `telemetry_processor.py` - Core telemetry processing module.
- `api.py` - FastAPI microservice exposing the required endpoints.
- `test_telemetry_processor.py` - Unit tests for the telemetry processing module.
- `demo.py` - Simple demo script to showcase functionality.

## Part 1: Telemetry Processing Module

Inside `telemetry_processor.py`, implement the telemetry processing logic.

### Input format

Telemetry events arrive as Python dicts, example:

```python
{
    "device_id": "AC-445",
    "timestamp": 1732137200,  # unix ts
    "temperature_f": 78.2,
    "humidity": 46.1
}
```

### Task

Build a class TelemetryProcessor with:

- `ingest(event: dict)`: Stores the latest N events per device in memory (N=20).

- `get_summary(device_id: str) → dict`: Return a summary with:

```python
{
    "device_id": "...",
    "recent_avg_temperature_f": float,
    "recent_avg_humidity": float,
    "last_event_ts": int,
    "status": "ok" | "warning" | "critical"
}
```

- `get_all_device_ids(self) -> list`: Returns a list of all device IDs that have ingested events.

### Status rules

- temperature_f > `90` → `"critical"`
- temperature_f > `80` → `"warning"`
- otherwise → `"ok"`

> Important: Use the most recent event for status.

### Requirements

- Must handle unknown device IDs gracefully.
- Should be easy to extend (e.g., additional rules later).
- No DB needed — in-memory is fine.
- Clean, maintainable code is more important than performance.

## Part 2: Micro API Layer

Inside `api.py`, implement a minimal FastAPI service exposing:

### GET `/devices/{device_id}/summary`

Returns output from `get_summary`.

### POST `/ingest`

Accepts a telemetry event JSON body and calls `ingest`.

> No authentication needed. Keep this tiny.

## Testing

To check functionality of the processor, run the unit tests provided in `test_telemetry_processor.py` using the following command:

```sh
python test_telemetry_processor.py
```
