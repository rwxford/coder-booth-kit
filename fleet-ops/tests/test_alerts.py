from fleet_ops.alerts import evaluate
from fleet_ops.telemetry import Frame, Vehicle


def test_threat_and_low_battery_alerts():
    f = Frame(0, True, (
        Vehicle("FL11", "isr", 0, 0, 18000, 118, 71.5, "threat"),
        Vehicle("VG22", "quad", 0, 0, 400, 22, 29.0, "on patrol"),
    ))
    alerts = evaluate(f, {"FL11": 90.0, "VG22": 4.5})
    kinds = {(a.callsign, a.level) for a in alerts}
    assert ("FL11", "critical") in kinds
    assert ("VG22", "warn") in kinds
    assert len(alerts) == 2
