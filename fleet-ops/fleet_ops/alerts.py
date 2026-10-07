"""Alert rules evaluated against a burndown table."""
from __future__ import annotations

from dataclasses import dataclass

from .telemetry import Frame

LOW_MINUTES = 15.0


@dataclass(frozen=True)
class Alert:
    callsign: str
    level: str   # "warn" | "critical"
    message: str


def evaluate(frame: Frame, burndown: dict[str, float]) -> list[Alert]:
    alerts: list[Alert] = []
    for v in frame.vehicles:
        if v.status == "threat":
            alerts.append(Alert(v.callsign, "critical", f"{v.callsign} flagged as threat"))
        mins = burndown.get(v.callsign)
        if mins is not None and mins < LOW_MINUTES:
            alerts.append(Alert(v.callsign, "warn",
                                f"{v.callsign} has {mins:.0f} min to reserve"))
    return alerts
