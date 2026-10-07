"""Battery burndown estimates.

Given two telemetry frames for the same aircraft, estimate how many minutes of
flight remain at the observed drain rate.
"""
from __future__ import annotations

from .telemetry import Frame, Vehicle

RESERVE_PCT = 20.0  # never plan below this


def drain_rate_pct_per_min(earlier: Vehicle, later: Vehicle,
                           earlier_ts_ms: int, later_ts_ms: int) -> float:
    """Percent of battery consumed per minute between two observations."""
    elapsed_ms = later_ts_ms - earlier_ts_ms
    if elapsed_ms <= 0:
        raise ValueError("later frame must be after earlier frame")
    elapsed_min = elapsed_ms / 1000.0  # ms -> minutes
    return (earlier.battery_pct - later.battery_pct) / elapsed_min


def minutes_remaining(current_pct: float, rate_pct_per_min: float,
                      reserve_pct: float = RESERVE_PCT) -> float:
    """Minutes until the battery hits the reserve floor at the given rate."""
    usable = max(current_pct - reserve_pct, 0.0)
    if rate_pct_per_min <= 0:
        return float("inf")
    return usable / rate_pct_per_min


def fleet_burndown(earlier: Frame, later: Frame) -> dict[str, float]:
    """Minutes remaining per callsign present in both frames."""
    by_callsign = {v.callsign: v for v in earlier.vehicles}
    out: dict[str, float] = {}
    for v in later.vehicles:
        prev = by_callsign.get(v.callsign)
        if prev is None:
            continue
        rate = drain_rate_pct_per_min(prev, v, earlier.timestamp_ms, later.timestamp_ms)
        out[v.callsign] = minutes_remaining(v.battery_pct, rate)
    return out
