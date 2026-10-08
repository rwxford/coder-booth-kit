# EAIS booth demo kit (Mac + iPad edition)

Everything to run the "Coder anywhere" demo without the flyaway case:
the UAV Defense Simulator runs on this Mac in Docker, its MCP server is
exposed to the demobuilder Coder through a tunnel, and a seeded repo
(`fleet-ops`) with five issues lives in the demobuilder Gitea for the
Coder Agents walkthrough.

## Wednesday morning: click and go (about 10 minutes)

Already done tonight: the `eais` demobuilder env was extended to its 24h cap
(deadline **Wed Oct 7, 8:44 PM EDT**; it would have died at 8:44 AM).

1. Open Docker Desktop. Make sure Tailscale is connected.
2. In Terminal:
   ```bash
   cd ~/Downloads/eais-demo
   ./00-prereqs.sh          # first time only: git-lfs, cloudflared, jq
   ./10-uav-up.sh           # clones the image tarballs from coder-edge-kit, loads, starts, arms, tunnels
   ```
   It ends by printing `urls.txt`. First run downloads ~1–2 GB of image tarballs; after that it's seconds.
3. Seed the repo into Gitea (needs the admin password from DemoBuilder › Personas › Admin › Reveal):
   ```bash
   ./20-seed-gitea.sh https://gitea--quz9.demos.cdrsandboxes.com
   ```
4. Register the MCP server in Coder (manual, 1 minute). See `30-register-mcp.md`.
   Then build the two workspaces from **Coder Agents Generic** (`fleet-ops-1`, `fleet-ops-2`). The template asks
   for **Login with Gitea** once (OAuth consent as the admin persona); after that, in each workspace terminal:
   `git clone https://gitea--quz9.demos.cdrsandboxes.com/admin/fleet-ops.git && cd fleet-ops && python3 -m venv .venv && source .venv/bin/activate && pip install -q -r requirements.txt && pytest -q`
   → `1 failed, 4 passed`. That failure is issue #3.
5. `./check.sh` — everything green. Put the Coder URL in `coder-url.txt` so check.sh tests it too:
   ```bash
   echo https://coder--quz9.demos.cdrsandboxes.com > coder-url.txt
   ```
6. iPad: open the Tailscale URL from `urls.txt` (`http://<mac-tailscale-ip>:8081`). Add to Home Screen.
   `/arm.html` on the iPad re-arms the sim between visitors (every ~20 min).

## Files

| File | Purpose |
|---|---|
| `10-uav-up.sh` | Fetch images, start stack, arm sim, open cloudflared tunnel, print URLs |
| `check.sh` | Health check: containers, backend, MCP local + public, Coder reachability |
| `90-uav-down.sh` | Stop everything (images stay cached) |
| `20-seed-gitea.sh` | Create `fleet-ops` repo + 5 issues in the demobuilder Gitea |
| `30-register-mcp.md` | Coder UI steps to add the UAV MCP server and test it |
| `DEMO-SCRIPT.md` | The talk track and the exact agent prompts |
| `PLAYBOOK.md` | Wednesday-night rebuild, step by step, with a checklist |
| `docker-compose.yml`, `arm.html`, `brand/` | The UAV stack |
| `fleet-ops/` | The seeded demo repo (pushed to Gitea by the seed script) |

## Where things came from

- UAV images: `bppRomperRoom/coder-edge-kit/images/uav` (docker-save tarballs, tag d20d480, amd64).
- Compose + arm page: `coder/usg-edge/stacks/uav` (Austen's island kit).
- MCP tool names (e.g. `get_fleet_status`): `coder-edge-kit/scripts/lab-check.sh`.
