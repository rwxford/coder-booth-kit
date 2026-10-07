"""HTTP API. Run with: uvicorn fleet_ops.api:app --port 8090

Reads frames from the simulator at UAV_BACKEND_URL when set, otherwise from
data/sample_telemetry.json so the service works with the cable cut.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI

from . import __version__
from .alerts import evaluate
from .battery import fleet_burndown
from .telemetry import parse_frames

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_telemetry.json"
BACKEND = os.environ.get("UAV_BACKEND_URL")

app = FastAPI(title="fleet-ops", version=__version__)


def _load_frames():
    if BACKEND:
        import httpx
        r = httpx.get(f"{BACKEND}/api/telemetry/recent", timeout=5)
        r.raise_for_status()
        return parse_frames(r.json())
    return parse_frames(json.loads(SAMPLE.read_text()))


@app.get("/fleet")
def fleet():
    frames = _load_frames()
    latest = frames[-1]
    return {"timestamp_ms": latest.timestamp_ms, "running": latest.running,
            "vehicles": [v.__dict__ for v in latest.vehicles]}


@app.get("/burndown")
def burndown():
    frames = _load_frames()
    return fleet_burndown(frames[-2], frames[-1])


@app.get("/alerts")
def alerts():
    frames = _load_frames()
    table = fleet_burndown(frames[-2], frames[-1])
    return [a.__dict__ for a in evaluate(frames[-1], table)]
