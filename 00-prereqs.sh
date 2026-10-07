#!/usr/bin/env bash
# One-time prerequisites for the booth Mac. Safe to re-run.
set -euo pipefail
command -v brew >/dev/null || { echo "Homebrew missing: https://brew.sh"; exit 1; }
brew list --formula git-lfs >/dev/null 2>&1 || brew install git-lfs
brew list --formula cloudflared >/dev/null 2>&1 || brew install cloudflared
brew list --formula jq >/dev/null 2>&1 || brew install jq
git lfs install >/dev/null
if ! command -v docker >/dev/null; then
  echo "Docker Desktop is not installed: brew install --cask docker   (then open it once)"; exit 1
fi
docker info >/dev/null 2>&1 || echo "Docker Desktop is installed but not running. Open it before 10-uav-up.sh."
# Apple Silicon: the UAV images are amd64. Turn on Rosetta in Docker Desktop
# (Settings > General > "Use Rosetta for x86_64/amd64 emulation") for a big speed-up.
chmod +x ./*.sh
echo "prereqs ok"
