# Issue mirror

Snapshot of the GitHub issues for workspaces without GitHub access.

## #1 Add CSV export for alert history (enhancement)
Operators want to pull the alert log into a spreadsheet after a sortie.
Add `GET /alerts.csv` returning `callsign,level,message` with a header row.

## #2 Telemetry parser crashes on frames with a missing `batteryPercent` (bug)
When a vehicle is relaying but its battery sensor hasn't reported yet, the
frame has no `batteryPercent` key. `parse_vehicle` raises `KeyError` and the
whole frame is dropped. It should default to `None` (or `NaN`) and the battery
code should skip those vehicles instead of crashing.

## #3 Battery time-remaining estimate is off by 60x (bug, tests failing)
`drain_rate_pct_per_min` returns a per-second rate, not per-minute. With the
sample data VG22 shows ~270 minutes remaining when it has about 4.5.
`tests/test_battery.py::test_drain_rate_is_per_minute` fails on main.
Fix the unit conversion in `fleet_ops/battery.py` and make the suite green.

## #4 Add a `/health` endpoint that reports backend reachability (enhancement)
Return `{"status": "ok", "mode": "connected"|"disconnected", "backend": url-or-null}`.
In connected mode, try the backend's `/api/health` with a 2 s timeout and
report `degraded` if it fails, without raising.

## #5 Document DDIL (disconnected) operation (docs)
Write `docs/DDIL.md` explaining how the service behaves with no backend, how
to refresh `data/sample_telemetry.json` from a live capture, and what the
operator should expect on the alerts page while disconnected.
