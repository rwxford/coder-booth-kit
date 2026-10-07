#!/usr/bin/env bash
# Stop the UAV stack and the tunnel. Images stay loaded, so the next up is fast.
cd "$(dirname "$0")"
pkill -f 'cloudflared tunnel --url http://localhost' 2>/dev/null || true
docker compose down
rm -f urls.txt tunnel.log map-tunnel.log
echo "stopped"
