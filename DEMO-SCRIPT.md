# Demo script: "Coder anywhere" with agents in the loop

Three screens: booth monitor (Coder UI, mirrored from the Mac), MacBook (your cockpit), iPad (UAV map + arm page over Tailscale).

## 0. Before the first visitor
- `./check.sh` is green. Arm page shows **running**.
- Coder: two workspaces pre-built and running from **Coder Agents Generic** (name them `fleet-ops-1`, `fleet-ops-2`), each with `fleet-ops` cloned:
  `git clone https://gitea--quz9.demos.cdrsandboxes.com/admin/fleet-ops.git` (public, no token).
- Agents chat open in one tab. MCP server `uav-sim` registered and showing tools.
- Bookmarks bar: Templates · Workspaces · Agents · Admin AI (governance) · Gitea issues · arm page.

## 1. Hook (15 s)
"Every engineer and every AI agent at your org works inside a workspace you define, on infrastructure you own. Same platform in our cloud, your data center, or a box with the cable cut. Let me show you the agent half."

## 2. Workspace (20 s)
Templates → open `fleet-ops-1`. "Ubuntu, Node, Python, git, code-server. The repo's already here. Nothing on anyone's laptop."

## 3. Agent on the repo (45 s) — the seeded-repo moment
In Agents (or Claude Code inside the workspace), prompt:

> Clone https://gitea--quz9.demos.cdrsandboxes.com/admin/fleet-ops.git if it isn't here, read `docs/ISSUES.md`, summarize the open issues in one line each, then fix issue #3 and prove it with `pytest -q` (use a venv: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`; the system pip is locked).

What happens: it reads the five issues, finds the 60x unit bug in `fleet_ops/battery.py` (`/ 1000.0` should be `/ 60000.0`), patches it, tests go from 1 failed to 5 passed. Say: "That ran in a governed workspace: model allow-listed, spend budgeted, every tool call logged."

Shorter variant if time is tight: *"Read docs/ISSUES.md and fix #3; run the tests."*

## 4. Agent on the world (45 s) — the UAV/MCP moment
Point at the iPad map. Prompt in Agents:

> Use the uav-sim tools: get the fleet status, tell me which aircraft is flagged as a threat and which has the lowest battery, and pause the simulation.

The map on the iPad freezes when it pauses. Then: *"Resume the simulation."* It moves again.
"Same agent, same governance, now talking to an operational system through MCP. In the flyaway kit this ran with no internet at all — two GPU boxes serving a 235B model locally."

Re-arm between visitors from the iPad (`/arm.html`, press ARM). Roughly every 20 minutes.

## 5. Governance (20 s)
Admin › AI: model list, per-group budgets, the log of what the agent just did. "This is how you say yes to agents without saying yes to everything."

## 6. Closer by audience
- **Enterprise:** platform team owns templates/SSO/budgets; developers get a URL.
- **Defense (Northrop, NIWC, Sigma, Leidos):** the kit ran last week with the WAN cable unplugged: Coder + GitLab SSO + private registry + local models. DDIL (denied, disrupted, intermittent, limited) by design. Show the case photo.
- **Oversight (USPS OIG):** governed model access, data stays in boundary, every interaction auditable.

Then: "What are you doing for agents today?" and listen.

## Fallbacks
- Tunnel died → `./10-uav-up.sh`, re-paste the new URL into Coder's MCP server. 60 seconds.
- Venue Wi-Fi died → phone hotspot for the Mac; iPad still reaches the map over Tailscale or the hotspot.
- Coder env died → the screen recording (make one tonight: QuickTime, 90 s) plus the iPad map, which runs with no internet at all.
