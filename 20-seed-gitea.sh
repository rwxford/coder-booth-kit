#!/usr/bin/env bash
# Seed the demo repo (fleet-ops) + 5 issues into the demobuilder Gitea.
#
#   ./20-seed-gitea.sh https://gitea--XXXX.demos.cdrsandboxes.com
#
# Prompts for the Gitea admin password (from DemoBuilder > Personas > Admin > Reveal).
# Re-runnable: if the repo exists it force-pushes main and only creates issues that
# are missing (matched by title).
set -euo pipefail
cd "$(dirname "$0")"
GITEA_URL="${1:-${GITEA_URL:-}}"; [[ -z "$GITEA_URL" ]] && { echo "usage: $0 https://gitea--XXXX.demos.cdrsandboxes.com"; exit 1; }
GITEA_URL="${GITEA_URL%/}"
USER_="${GITEA_USER:-admin}"
REPO="fleet-ops"
command -v jq >/dev/null || { echo "need jq (./00-prereqs.sh)"; exit 1; }
read -r -s -p "Gitea password for $USER_: " PASS; echo

api(){ curl -fsS -u "$USER_:$PASS" -H 'Content-Type: application/json' "$GITEA_URL/api/v1$1" "${@:2}"; }

# 1. Repo
if ! api "/repos/$USER_/$REPO" >/dev/null 2>&1; then
  echo "creating $USER_/$REPO"
  api /user/repos -X POST -d "{\"name\":\"$REPO\",\"description\":\"Fleet operations service for the UAV Defense Simulator\",\"private\":false,\"default_branch\":\"main\",\"auto_init\":false}" >/dev/null
else
  echo "$USER_/$REPO exists; will force-push main"
fi

# 2. Short-lived token for git push (avoids putting the password in a URL)
TOKEN=$(api "/users/$USER_/tokens" -X POST -d "{\"name\":\"seed-$(date +%s)\",\"scopes\":[\"write:repository\"]}" | jq -r .sha1)

# 3. Push
( cd fleet-ops
  rm -rf .git; git init -q -b main
  git -c user.name='Ross Weatherford' -c user.email='ross@coder.com' add -A
  git -c user.name='Ross Weatherford' -c user.email='ross@coder.com' commit -q -m "fleet-ops 0.3.1: telemetry parsing, battery burndown, alerts API"
  git push -q --force "https://$USER_:$TOKEN@${GITEA_URL#https://}/$USER_/$REPO.git" main
  rm -rf .git )
echo "pushed main"

# 4. Issues (idempotent by title)
existing=$(api "/repos/$USER_/$REPO/issues?state=all&limit=50" | jq -r '.[].title')
mk(){ local title="$1" body="$2"
  if grep -Fxq "$title" <<<"$existing"; then echo "  exists: $title"; return; fi
  api "/repos/$USER_/$REPO/issues" -X POST -d "$(jq -n --arg t "$title" --arg b "$body" '{title:$t, body:$b}')" >/dev/null
  echo "  created: $title"; }
echo "issues:"
mk "Add CSV export for alert history" \
"Operators want to pull the alert log into a spreadsheet after a sortie.

Add \`GET /alerts.csv\` returning \`callsign,level,message\` with a header row."
mk "Telemetry parser crashes on frames with a missing batteryPercent" \
"When a vehicle is relaying but its battery sensor hasn't reported yet, the frame has no \`batteryPercent\` key. \`parse_vehicle\` raises \`KeyError\` and the whole frame is dropped.

It should default to \`None\` (or NaN) and the battery code should skip those vehicles instead of crashing."
mk "Battery time-remaining estimate is off by 60x" \
"\`drain_rate_pct_per_min\` in \`fleet_ops/battery.py\` returns a per-**second** rate, not per-minute. With the sample data VG22 shows ~270 minutes remaining when it has about 4.5.

\`tests/test_battery.py::test_drain_rate_is_per_minute\` fails on main.

Fix the unit conversion and make the suite green (\`pytest -q\`)."
mk "Add a /health endpoint that reports backend reachability" \
"Return \`{\"status\": \"ok\", \"mode\": \"connected\"|\"disconnected\", \"backend\": url-or-null}\`.

In connected mode, try the backend's \`/api/health\` with a 2 s timeout and report \`degraded\` if it fails, without raising."
mk "Document DDIL (disconnected) operation" \
"Write \`docs/DDIL.md\` explaining how the service behaves with no backend, how to refresh \`data/sample_telemetry.json\` from a live capture, and what the operator should expect on the alerts page while disconnected."

# 5. Clean up the token
TID=$(api "/users/$USER_/tokens" | jq -r '.[] | select(.name|startswith("seed-")) | .id' | tail -1)
[[ -n "$TID" ]] && api "/users/$USER_/tokens/$TID" -X DELETE >/dev/null || true

echo
echo "Repo:   $GITEA_URL/$USER_/$REPO"
echo "Clone:  git clone $GITEA_URL/$USER_/$REPO.git"
echo "Issues: $GITEA_URL/$USER_/$REPO/issues"
echo "$GITEA_URL/$USER_/$REPO.git" > repo-url.txt
