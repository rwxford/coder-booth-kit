#!/usr/bin/env bash
# Booth health check. Run before the doors open and whenever something looks off.
cd "$(dirname "$0")"
ok(){ printf '  \033[32m✓\033[0m %s\n' "$*"; }; bad(){ printf '  \033[31m✗\033[0m %s\n' "$*"; }
echo "== containers"; docker compose ps --format '  {{.Name}}  {{.Status}}' 2>/dev/null || bad "docker compose not running"
echo "== backend";  curl -fsS --max-time 5 http://localhost:8081/api/health >/dev/null && ok "api/health" || bad "api/health"
echo "== frontend"; curl -fsS --max-time 5 -o /dev/null http://localhost:8081/ && ok "map UI" || bad "map UI"
curl -fsS --max-time 5 -o /dev/null http://localhost:8081/arm.html && ok "arm page" || bad "arm page"
echo "== mcp (local)"
N=$(curl -s --max-time 10 -X POST http://localhost:3030/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
   -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | grep -o '"name"' | wc -l | tr -d ' ')
[[ "$N" -gt 0 ]] && ok "$N tools" || bad "tools/list returned nothing"
RUN=$(curl -s --max-time 15 -X POST http://localhost:3030/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
   -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_fleet_status","arguments":{}}}' | grep -o '\\"running\\": *[a-z]*' | head -1 | grep -o '[a-z]*$')
[[ "$RUN" == "true" ]] && ok "simulation running" || bad "simulation not running (open http://localhost:8081/arm.html and press ARM)"
echo "== mcp (public, what Coder sees)"
PUB=$(grep -a -o 'https://[a-z0-9-]*\.trycloudflare\.com' tunnel.log 2>/dev/null | head -1)
if [[ -n "$PUB" ]]; then
  M=$(curl -s --max-time 15 -X POST "$PUB/mcp" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | grep -o '"name"' | wc -l | tr -d ' ')
  [[ "$M" -gt 0 ]] && ok "$PUB/mcp ($M tools)" || bad "$PUB/mcp not answering; restart with ./10-uav-up.sh"
else bad "no tunnel URL in tunnel.log"; fi
echo "== map (public, for the iPad)"
MAP=$(grep -a -o 'https://[a-z0-9-]*\.trycloudflare\.com' map-tunnel.log 2>/dev/null | head -1)
if [[ -n "$MAP" ]]; then
  curl -fsS --max-time 15 -o /dev/null "$MAP/api/health" && ok "$MAP  (arm: $MAP/arm.html)" || bad "$MAP not answering"
else echo "  (no map tunnel; iPad must reach the Mac directly)"; fi
echo "== coder"
CODER=$(cat coder-url.txt 2>/dev/null)
[[ -n "$CODER" ]] && { curl -fsS --max-time 8 "$CODER/healthz" >/dev/null && ok "$CODER" || bad "$CODER unreachable"; } || echo "  (put the demobuilder Coder URL in coder-url.txt)"
echo "== urls"; cat urls.txt 2>/dev/null
