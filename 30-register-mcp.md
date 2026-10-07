# Register the UAV MCP server in Coder

MCP = Model Context Protocol, the tool interface Coder Agents use to call external systems.
The UAV simulator ships an MCP server (streamable HTTP, `POST /mcp`). `10-uav-up.sh` exposes it
through a cloudflared quick tunnel and prints the public URL in `urls.txt`
(looks like `https://<random-words>.trycloudflare.com/mcp`).

## Steps (Coder admin, about 1 minute)

1. Go straight to the form (admin persona): `https://coder--pk36.demos.cdrsandboxes.com/ai/settings/mcp-servers/add?org=coder`
   (nav path: Admin settings › AI › **MCP servers** › **Add server**).
2. Fill in:
   - Slug: `uav-sim`  ·  Display name: `UAV Defense Simulator`  ·  Organization: Coder
   - Server URL: the `MCP for Coder:` line from `urls.txt` (ends in `/mcp`)
   - Transport: **Streamable HTTP** (the default)
   - Details (optional): "Fleet status, threats, pause/resume for the booth UAV sim"
   - Authentication: none
   - Behavior › Availability: **default on** (so every agent chat gets it without per-user setup)
3. **Add server**. Open it and confirm Coder lists the tools (expect ~10, including `get_fleet_status`).
5. Test: open **Agents**, start a chat with the default model, ask
   *"Use the uav-sim tool to list the fleet and tell me which aircraft is a threat."*
   Expect per-aircraft status with FL11 flagged.

## If the tools list is empty

- `./check.sh` → is the public MCP answering? If not, `./10-uav-up.sh` again (tunnel restarts; URL changes, re-paste it).
- The tunnel URL changes every time cloudflared restarts. Update the MCP server URL in Coder when it does.
- The backend must be running (arm page shows **running**). If paused, press **Resume** on `/arm.html`.

## Security note

The quick tunnel is a random public URL with no auth, and the MCP server can control the sim
(pause, reset, scenario switch). Fine for a two-day booth; run `./90-uav-down.sh` at teardown.
