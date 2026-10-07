#!/usr/bin/env bash
# Bring the UAV Defense Simulator up on this Mac and expose its MCP server to Coder.
#
#   ./10-uav-up.sh            # full: fetch images, start stack, arm demo, open tunnel
#   ./10-uav-up.sh --no-tunnel
#
# Idempotent: re-run any time. Prints the URLs you need at the end and writes them to urls.txt.
set -euo pipefail
cd "$(dirname "$0")"

KIT_REPO="git@github.com:bppRomperRoom/coder-edge-kit.git"
KIT_HTTPS="https://github.com/bppRomperRoom/coder-edge-kit.git"
TAG="d20d480"
TUNNEL=1; [[ "${1:-}" == "--no-tunnel" ]] && TUNNEL=0

say(){ printf '\n\033[1;35m== %s\033[0m\n' "$*"; }
need(){ command -v "$1" >/dev/null 2>&1 || { echo "missing: $1 (run ./00-prereqs.sh)"; exit 1; }; }
need docker; need git; need curl
docker info >/dev/null 2>&1 || { echo "Docker Desktop is not running. Start it and re-run."; exit 1; }

# 1. Images -----------------------------------------------------------------
if ! docker image inspect uav/backend:$TAG >/dev/null 2>&1; then
  # Tarballs downloaded by hand (browser) are picked up from ./images or ~/Downloads, no git needed.
  mkdir -p coder-edge-kit/images/uav
  for f in uav-backend uav-frontend uav-mcp; do
    for src in "images/$f-$TAG.tar" "$HOME/Downloads/$f-$TAG.tar"; do
      [[ -s "$src" && ! -s "coder-edge-kit/images/uav/$f-$TAG.tar" ]] && mv "$src" coder-edge-kit/images/uav/
    done
  done
  if ls coder-edge-kit/images/uav/uav-{backend,frontend,mcp}-$TAG.tar >/dev/null 2>&1; then
    say "Using pre-downloaded tarballs in coder-edge-kit/images/uav"
  else
  say "Fetching UAV image tarballs from coder-edge-kit (sparse checkout, images/uav only)"
  if [[ ! -d coder-edge-kit/.git ]]; then
    rmdir coder-edge-kit/images/uav coder-edge-kit/images coder-edge-kit 2>/dev/null || true
    git clone --filter=blob:none --no-checkout --depth 1 "$KIT_REPO" coder-edge-kit 2>/dev/null \
      || git clone --filter=blob:none --no-checkout --depth 1 "$KIT_HTTPS" coder-edge-kit
  fi
  ( cd coder-edge-kit
    git sparse-checkout set images/uav
    git checkout main
    command -v git-lfs >/dev/null 2>&1 && git lfs pull --include "images/uav/*" || true
    cd images/uav
    for f in uav-backend uav-frontend uav-mcp; do
      [[ -s $f-$TAG.tar ]] || { echo "missing or empty $f-$TAG.tar (git-lfs? run: brew install git-lfs && git lfs install)"; exit 1; }
    done
    shasum -a 256 -c SHA256SUMS
  )
  fi
  say "docker load"
  for f in uav-backend uav-frontend uav-mcp; do docker load -i coder-edge-kit/images/uav/$f-$TAG.tar; done
  # Tarballs may carry the registry-prefixed name; normalise to uav/<name>:TAG
  for c in backend frontend mcp-server; do
    src=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep -E "(^|/)uav/$c:$TAG$" | head -1)
    [[ -n "$src" ]] && docker tag "$src" uav/$c:$TAG
  done
fi
docker image inspect uav/backend:$TAG uav/frontend:$TAG uav/mcp-server:$TAG >/dev/null

# 2. Stack ------------------------------------------------------------------
say "docker compose up"
docker compose up -d
printf 'waiting for backend'
for i in $(seq 1 60); do
  if curl -fsS http://localhost:8081/api/health >/dev/null 2>&1; then echo " ok"; break; fi
  printf '.'; sleep 2
  [[ $i == 60 ]] && { echo; echo "backend never became healthy: docker compose logs uav-backend"; exit 1; }
done

# 3. Arm the demo (same calls as /arm.html) ---------------------------------
say "Arming demo (defense_training, 20x warm-up for 15s, then 2x)"
post(){ curl -fsS -X POST "http://localhost:8081/api/$1" -H 'Content-Type: application/json' -d "$2" >/dev/null; }
post scenarios/switch '{"scenarioId":"defense_training"}'
post simulation/control '{"command":"reset"}'
post simulation/control '{"command":"resume"}'
post simulation/timescale '{"multiplier":20}'; sleep 15
post simulation/timescale '{"multiplier":2}'

# 4. MCP sanity ---------------------------------------------------------------
say "MCP tools/list"
TOOLS=$(curl -s --max-time 10 -X POST http://localhost:3030/mcp -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | grep -o '"name"' | wc -l | tr -d ' ')
echo "MCP server exposes $TOOLS tools"

# 5. Tunnel ---------------------------------------------------------------------
MCP_PUBLIC=""; MAP_PUBLIC=""
if [[ $TUNNEL == 1 ]]; then
  need cloudflared
  say "Opening cloudflared quick tunnel to the MCP server"
  pkill -f 'cloudflared tunnel --url http://localhost:3030' 2>/dev/null || true
  sleep 1
  # --protocol http2: hotspots and venue Wi-Fi often block QUIC (UDP 7844); HTTP/2 over TCP 443 always gets through.
  nohup cloudflared tunnel --url http://localhost:3030 --protocol http2 --no-autoupdate > tunnel.log 2>&1 &
  for i in $(seq 1 30); do
    MCP_PUBLIC=$(grep -a -o 'https://[a-z0-9-]*\.trycloudflare\.com' tunnel.log | head -1 || true)
    [[ -n "$MCP_PUBLIC" ]] && break; sleep 1
  done
  [[ -z "$MCP_PUBLIC" ]] && echo "tunnel URL not found yet; check tunnel.log"
  # Second tunnel for the map UI, so the iPad works from any network (tailnet ACLs blocked direct access).
  pkill -f 'cloudflared tunnel --url http://localhost:8081' 2>/dev/null || true; sleep 1
  nohup cloudflared tunnel --url http://localhost:8081 --protocol http2 --no-autoupdate > map-tunnel.log 2>&1 &
  MAP_PUBLIC=""
  for i in $(seq 1 30); do
    MAP_PUBLIC=$(grep -a -o 'https://[a-z0-9-]*\.trycloudflare\.com' map-tunnel.log | head -1 || true)
    [[ -n "$MAP_PUBLIC" ]] && break; sleep 1
  done
fi

# 6. Summary ------------------------------------------------------------------
TS_IP=$(command -v tailscale >/dev/null 2>&1 && tailscale ip -4 2>/dev/null | head -1 || /Applications/Tailscale.app/Contents/MacOS/Tailscale ip -4 2>/dev/null | head -1 || true)
LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || true)
{
  echo "UAV map (Mac):        http://localhost:8081"
  echo "Arm page (Mac):       http://localhost:8081/arm.html"
  [[ -n "$TS_IP" ]]  && echo "UAV map (iPad, Tailscale): http://$TS_IP:8081"
  [[ -n "$LAN_IP" ]] && echo "UAV map (iPad, same Wi-Fi): http://$LAN_IP:8081"
  [[ -n "${MAP_PUBLIC:-}" ]] && echo "UAV map (iPad, any network): $MAP_PUBLIC   arm: $MAP_PUBLIC/arm.html"
  echo "MCP local:            http://localhost:3030/mcp"
  [[ -n "$MCP_PUBLIC" ]] && echo "MCP for Coder:        $MCP_PUBLIC/mcp   <- paste into Coder: Admin > AI > MCP servers (slug uav-sim)"
} | tee urls.txt
say "Done. Run ./check.sh any time; ./90-uav-down.sh to stop."
