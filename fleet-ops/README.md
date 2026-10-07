# fleet-ops

A small operations service that sits on top of the **UAV Defense Simulator**.
It reads the simulator's telemetry frames, estimates battery time remaining
for every aircraft, and raises alerts for anything flagged as a threat or
running short on battery.

It runs in two modes:

- **Connected:** set `UAV_BACKEND_URL` (for example `http://uav-backend:8080`)
  and it reads live frames from the simulator.
- **Disconnected (DDIL):** no env var, and it reads `data/sample_telemetry.json`.
  This is the default so the service works with the cable cut.

## Layout

| Path | What |
|---|---|
| `fleet_ops/telemetry.py` | Parse telemetry frames into `Frame` / `Vehicle` |
| `fleet_ops/battery.py` | Drain rate and minutes-to-reserve estimates |
| `fleet_ops/alerts.py` | Alert rules (threat, low battery) |
| `fleet_ops/api.py` | FastAPI app: `/fleet`, `/burndown`, `/alerts` |
| `data/sample_telemetry.json` | Two frames, 60 s apart, three aircraft |
| `tests/` | pytest suite |

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate   # Ubuntu blocks system-wide pip (PEP 668)
pip install -r requirements.txt
pytest -q
uvicorn fleet_ops.api:app --port 8090
curl localhost:8090/alerts
```

## Open issues

Tracked on GitHub (see the Issues tab). A mirror lives in
[`docs/ISSUES.md`](docs/ISSUES.md) for disconnected workspaces. Issue #3 is
the one currently breaking the test suite.

## Conventions

- Telemetry timestamps are **milliseconds** since epoch.
- Battery reserve floor is 20 %; estimates count minutes to that floor, not to 0 %.
- Keep `fleet_ops` dependency-light; `httpx` is only imported in connected mode.
