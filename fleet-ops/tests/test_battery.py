from fleet_ops.battery import drain_rate_pct_per_min, minutes_remaining
from fleet_ops.telemetry import Vehicle


def _v(pct: float) -> Vehicle:
    return Vehicle("VG22", "quad", 0, 0, 400, 22, pct, "on patrol")


def test_drain_rate_is_per_minute():
    # 2% consumed over exactly 60 seconds -> 2.0 %/min
    rate = drain_rate_pct_per_min(_v(31.0), _v(29.0), 0, 60_000)
    assert abs(rate - 2.0) < 1e-9


def test_minutes_remaining_to_reserve():
    # 29% left, 20% reserve, 2 %/min -> 4.5 minutes
    assert abs(minutes_remaining(29.0, 2.0) - 4.5) < 1e-9


def test_no_drain_means_infinite():
    assert minutes_remaining(50.0, 0.0) == float("inf")


def test_rejects_out_of_order_frames():
    import pytest
    with pytest.raises(ValueError):
        drain_rate_pct_per_min(_v(31.0), _v(29.0), 60_000, 0)
