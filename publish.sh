#!/usr/bin/env bash
# First push of this folder to an empty GitHub repo you've already created.
#   ./publish.sh git@github.com:bppRomperRoom/coder-booth-kit.git
# Later changes: plain git add/commit/push.
set -euo pipefail
cd "$(dirname "$0")"
REMOTE="${1:-}"; [[ -z "$REMOTE" ]] && { echo "usage: $0 <git remote url>"; exit 1; }
[[ -d .git ]] || git init -q -b main
rm -rf fleet-ops/.git   # the seed script re-inits this on every run; it must not be a nested repo
git add -A
git -c user.name="${GIT_AUTHOR_NAME:-Ross Weatherford}" -c user.email="${GIT_AUTHOR_EMAIL:-ross@coder.com}" \
  commit -q -m "Coder booth kit: UAV sim + MCP on a Mac, demobuilder seed, EAIS Charlotte playbook" || true
git remote get-url origin >/dev/null 2>&1 || git remote add origin "$REMOTE"
git push -u origin main
echo "pushed to $REMOTE"
