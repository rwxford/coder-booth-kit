"""Telemetry frame parsing.

A frame is the JSON the simulator publishes at 4 Hz on
``/api/simulation/telemetry``::

    {"timestamp_ms": 1759790000000, "running": true,
     "vehicles": [{"callsign": "FL11", "type": "MALE ISR", "lat": 37.2, "lon": -116.9,
                   "altitudeFt": 18000, "speedKts": 120, "batteryPercent": 71.5,
                   "status": "threat"}]}
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class Vehicle:
    callsign: str
    type: str
    lat: float
    lon: float
    altitude_ft: float
    speed_kts: float
    battery_pct: float
    status: str


@dataclass(frozen=True)
class Frame:
    timestamp_ms: int
    running: bool
    vehicles: tuple[Vehicle, ...]


def parse_vehicle(raw: dict[str, Any]) -> Vehicle:
    return Vehicle(
        callsign=raw["callsign"],
        type=raw.get("type", "unknown"),
        lat=float(raw.get("lat", 0.0)),
        lon=float(raw.get("lon", 0.0)),
        altitude_ft=float(raw.get("altitudeFt", 0.0)),
        speed_kts=float(raw.get("speedKts", 0.0)),
        battery_pct=float(raw["batteryPercent"]),
        status=str(raw.get("status", "unknown")).lower(),
    )


def parse_frame(raw: dict[str, Any]) -> Frame:
    return Frame(
        timestamp_ms=int(raw["timestamp_ms"]),
        running=bool(raw.get("running", False)),
        vehicles=tuple(parse_vehicle(v) for v in raw.get("vehicles", [])),
    )


def parse_frames(raws: Iterable[dict[str, Any]]) -> list[Frame]:
    return [parse_frame(r) for r in raws]
