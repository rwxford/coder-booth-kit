# Rebuild playbook (Wednesday night, and any time the env dies)

The demobuilder env lives 24h max. The current one (`eais`, pk36) dies **Wed Oct 7, 8:44 PM EDT**.
Rebuild Wednesday evening so Thursday's env runs until ~Thursday night. Budget 25 minutes; most of it is waiting.

## A. New demobuilder env (10 min, mostly waiting)
1. https://cdrsandboxes.com/demos → **Create demo**. Name `eais2`, template `demo-host`.
2. While it provisions (Submitted → Build → Health → Bootstrap → Seed), note the new URLs on the demo page:
   `https://coder--XXXX.demos.cdrsandboxes.com` and `https://gitea--XXXX.demos.cdrsandboxes.com`.
3. **Extend to 24h immediately**: Retention › Add hours `12` › Extend. Confirm the deadline reads Thursday evening.
   (Default is 12h. Tonight's env would have expired as the booth opened.)
4. Personas › Admin › **Reveal** → sign in to Coder and Gitea in the **Booth** Chrome profile.
5. Save the URLs locally:
   ```bash
   cd ~/Downloads/eais-demo
   echo https://coder--XXXX.demos.cdrsandboxes.com > coder-url.txt
   ```

## B. UAV stack on the Mac (2 min)
```bash
./90-uav-down.sh      # clears alert history; images stay cached
./10-uav-up.sh        # starts, arms, new tunnel URL in urls.txt
```

## C. Seed the repo into the new Gitea (1 min)
```bash
./20-seed-gitea.sh https://gitea--XXXX.demos.cdrsandboxes.com
```
Verify `https://gitea--XXXX.demos.cdrsandboxes.com/admin/fleet-ops/issues` shows 5 issues and #3 is the battery bug.

## D. Coder configuration (5 min)
1. **MCP server**: Agents › MCP servers › Add `uav-sim`, URL = `MCP for Coder` line in `urls.txt`, default on. See `30-register-mcp.md`.
2. **AI Governance** (if not already seeded by demobuilder): confirm at least one model is enabled and a budget exists for the `dev` persona, so the governance screen has something to show.
3. **Workspaces**: Templates › Coder Agents Generic › Create `fleet-ops-1` and `fleet-ops-2`. In each terminal:
   ```bash
   git clone https://gitea--XXXX.demos.cdrsandboxes.com/admin/fleet-ops.git && cd fleet-ops && python3 -m venv .venv && source .venv/bin/activate && pip install -q -r requirements.txt && pytest -q
   ```
   Expect `1 failed, 4 passed`. That failure is issue #3.
4. **Warm-up**: run the issue #3 prompt from `DEMO-SCRIPT.md` once in `fleet-ops-2` so you know what the agent says. Leave `fleet-ops-1` untouched for the live run. (Re-clone `fleet-ops-2` after, or just use it as the "already fixed" example.)
5. **Warm-up MCP**: in Agents ask for the fleet status once; confirm it names FL11 as the threat.

## E. Browser (2 min)
Booth Chrome profile bookmarks, in order: Templates · Workspaces · fleet-ops-1 · Agents · Admin AI · Gitea issues · `http://localhost:8081/arm.html`.
Update them for the new hostname (find/replace `pk36` → new id).

## F. iPad (1 min)
Tailscale on. Open `http://<mac-tailscale-ip>:8081` from `urls.txt`. Add to Home Screen. Open `/arm.html` once, press **ARM**.

## G. Verify
```bash
./check.sh
```
All green, then `DEMO-SCRIPT.md` section 0.

## Checklist
- [ ] New env created and **extended to 24h**
- [ ] coder-url.txt updated
- [ ] UAV stack up, armed, tunnel URL in urls.txt
- [ ] fleet-ops seeded; 5 issues; #3 = battery bug
- [ ] MCP server `uav-sim` registered with the new tunnel URL; tools listed
- [ ] fleet-ops-1 and fleet-ops-2 built and running; tests show 1 failed / 4 passed
- [ ] Agent warm-ups done (issue #3 and fleet status)
- [ ] Bookmarks updated; iPad map open; arm page works
- [ ] check.sh green
- [ ] Screen recording fallback still valid (re-record if UI changed)

## Known traps
- Demobuilder default retention is 12h, not 24h. Extend every time.
- cloudflared must run with `--protocol http2` (the script does). Hotspots block QUIC; the symptom is `Failed to dial a quic connection` in tunnel.log and HTTP 530 from the public URL.
- cloudflared quick-tunnel URLs change on every restart. Any `10-uav-up.sh` run means re-pasting the MCP URL in Coder.
- Alert history in the UAV backend is append-only; only a stack restart clears it. Stale callsigns confuse the agent.
- The UAV images are amd64. If Docker Desktop lacks Rosetta emulation the backend is slow to become healthy; the script waits up to 2 minutes.
- Chrome profile hygiene: no Okta tooltip, no Salesforce/Clari/Gmail bookmarks on the booth monitor.
