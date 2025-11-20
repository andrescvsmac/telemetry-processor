from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import the processor from Part 1
from telemetry_processor import TelemetryProcessor


app = FastAPI(title="Telemetry Ingestion API")
processor = TelemetryProcessor()


# TODO: Implement API to ingest telemetry events and retrieve summaries
