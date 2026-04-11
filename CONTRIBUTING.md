# Contributing — Sixth Borough Branch Playbook

Read this once. Five minutes to onboard. Spark Hack Series NYC, Apr 10–12 2026.

The point: every teammate writes code on their own branch within 60 seconds of cloning, with zero dependency on the GN100 or the 38 GB Nemotron model. We use a stub narration server that runs on any laptop.

---

## Universal first 5 commands

```bash
git clone https://github.com/TheApexWu/sixth-borough.git
cd sixth-borough
git checkout YOUR_BRANCH        # see assignments below
git merge main                   # pick up the foundation
pip install -r requirements.txt  # ~5 deps, ~30 sec
./scripts/dev-stub.sh            # narration server live on localhost:30000
```

The stub server runs the same `POST /narrate` contract as the real Nemotron. Your code never has to know the difference.

---

## Two-mode design

| Mode | What it is | Who uses it |
|---|---|---|
| `stub` | Templated narration. No model. Any laptop. | Carson, James, Marvens, Alex (off-box) |
| `real` | Nemotron-3-Nano via llama.cpp. GN100 only. | Alex (at the venue) + Sat night integration |

Switch with `NARRATION_MODE=stub` or `NARRATION_MODE=real`. Same Pydantic models, same HTTP contract.

---

## Branch assignments

### `renderer-rust` — Carson

**Goal:** Bevy 0.16 renderer (Rust + wgpu). Loads the seed JSON. Renders a scene with PS2 post-process. Calls `/narrate` on pin click. Ingests Marvens's static point clouds via `bevy_pointcloud` and animated point clouds via custom WGSL shader sampling OpenVAT textures.

**Engine pin:** Bevy 0.16 (mid-2025), NOT 0.18. Plugin compat reasons. Bumping to 0.17 OK if `bevy_pointcloud` works on it.

**Owns:** `src/renderer/` only. Don't touch `src/orchestrator/` or `src/data/`.

**Pair with Marvens Friday night** to lock the file format contract in `pointcloud-pipeline/README.md` BEFORE writing ingest code.

**First PR done when:** window opens, loads seed JSON, time slider scrubs, one niche filter button works, one narration call returns text from stub, one PS2 shader stage running, one static point cloud loaded via `bevy_pointcloud`.

**Doesn't need:** GN100, Nemotron, llama.cpp.

---

### `webgl-fallback` — James

**Goal:** WebGL + Three.js renderer (likely a port of `feature/sketch-overlay`). Same `/narrate` endpoint as Carson. Era-conditioned cutscenes.

**Owns:** `web/` only. Don't touch `src/`.

**First PR done when:** browser-renderable demo with year slider, Sobel pass, niche filter, narration call working. At least one of the 8 cutscenes ported.

**Test against the stub:** `python -m http.server 8080` in `web/`, open in browser, scrub year, click pin, see narration overlay.

**Bonus:** safety net — if the Bevy renderer doesn't stabilize on the GN100 by Sat 4 PM, the demo runs from this browser path.

---

### `pointcloud-pipeline` — Marvens

**Goal:** Blender → PLY (static) and Blender → glb-with-OpenVAT (animated) export pipelines + first sample point cloud asset (1520 Sedgwick rec room interior, 1973). **Pair with Carson Friday night** to lock the file format contract.

**Two formats from day one:**
- **Static ghosts**: PLY (binary, little-endian). Loaded by `bevy_pointcloud`. Use for architectural exteriors and frozen interiors.
- **Animated ghosts (the ODESZA technique)**: glb with embedded base mesh + OpenVAT vertex animation texture. Loaded by Carson's custom WGSL shader. Use for the killer demo moments.

**Owns:** `pointcloud-pipeline/` and `assets/pointclouds/` only.

**First PR done when:** README documents both file formats (already in place), one preview PNG committed, one MANIFEST.json entry committed, actual asset synced to shared storage.

**Authoring stack:** Blender + OpenVAT addon (sharpen3d/openvat) + Meshroom or COLMAP for photogrammetry from Joe Conzo Jr.'s Cornell archive (6,000+ free, geocoded negatives at digital.library.cornell.edu/collections/conzo).

**Doesn't need:** code skills, GN100, the narration loop, the renderer to be done.

**Asset rule:** large `.ply` / `.glb` files are gitignored. Manifest JSON + preview PNGs committed. Files sync via shared storage.

---

### `orchestrator-narration` — Alex

**Goal:** Real Nemotron-3-Nano path that swaps in for the stub when `NARRATION_MODE=real`. llama.cpp's OpenAI-compatible API.

**Owns:** `src/orchestrator/main.py`, `narration_real.py`, GN100 runbook. Don't touch `narration_stub.py`.

**First PR done when:** `narration_real.py` parses the same Pydantic models the stub uses, returns the same response shape, mode-switch test passes both paths.

**Test:** stub locally on MacBook, real on the GN100 at the venue.

---

### `data-curation` — Alex / James (rolling)

**Goal:** Expand `data/events-seed.json` from 19 → ~35-40 events with narration seeds, validate against schema.

**Owns:** the seed JSON, `data/niche-coverage.md`, the loader test only.

**Special:** rolling branch — small PRs, fast merges. Don't accumulate hours of work and merge a giant blob.

**Test:** `pytest tests/test_loader.py` after each addition.

---

## File ownership map

| Path | Owner |
|---|---|
| `src/renderer/` | Carson |
| `web/` | James |
| `pointcloud-pipeline/` + `assets/pointclouds/` | Marvens |
| `src/orchestrator/main.py` + `narration_real.py` | Alex |
| `src/data/schema.py` | Alex (ping before changing) |
| `data/events-seed.json` | Alex / James (rolling, small PRs) |
| `scripts/dev-stub.sh` + `setup-gn100.sh` | Alex (stable) |
| `tests/` | area owner adds tests for their area |
| `docs/DECISIONS.md` | anyone (append-only) |

---

## Merge order

1. `orchestrator-narration` first (Alex's real path — low conflict risk)
2. Parallel: `renderer-rust` + `webgl-fallback` + `pointcloud-pipeline` (zero overlap by design)
3. Rolling anytime: `data-curation` (small PRs)

The file ownership boundaries are designed so only `data-curation` has merge-conflict risk. That's why it's rolling with small PRs.

---

## Don't do

- **No cloud LLM calls anywhere, ever.** Zeros our NVIDIA Stack judging score (15 of 30 points).
- **No new dependencies less than 2 weeks old as of Apr 10.** Cutoff: Mar 27 2026. NVIDIA stack is exempt; everything else isn't.
- **Don't touch a directory you don't own** without pinging the owner in chat first.
- **Don't break stub mode.** Every PR into main has to leave main running in stub mode. If your PR breaks the stub server, the PR is wrong.
- **Don't judge narration quality against the stub.** Stub returns templated text. Quality testing is Sat night with the real Nemotron on the GN100.
- **Don't skip sleep windows.** Sat 2-8 AM and Sun 2-8 AM are non-negotiable.

---

## Key dates

| When | What |
|---|---|
| Friday night | Foundation push lands. Pull main, branch, start. |
| Sat 4:30 PM | Mandatory team checkin. Bring whatever's working. Integration window. |
| Sat 8 PM | Polish what works, drop what doesn't. |
| Sun 9 AM | Start the YouTube upload. NOT 10:55 — bad wifi makes the upload risky. |
| Sun 11 AM | **HARD freeze.** Airtable submission. Repo public. Done. |

---

## GN100 access (Alex's box at the venue)

The Acer Veriton GN100 is the only machine running `NARRATION_MODE=real`. Everyone else codes against the stub. If you need to debug the real backend or watch it run during integration, here's the path in.

**Network:** Tailscale only. The venue wifi has AP isolation, so the box is unreachable by IP. Tailscale node name: `gn100-3857`.

**Get on the tailnet:**
1. Install Tailscale on your laptop (`brew install --cask tailscale` or download from tailscale.com).
2. Ping Alex in chat with your Tailscale email — he'll share the node from the admin panel.
3. Drop your SSH public key (`cat ~/.ssh/id_ed25519.pub`) in chat. Alex appends it to `authorized_keys` on the box.

**SSH config (recommended):** add to `~/.ssh/config` on your laptop:

```
Host gn100
  HostName gn100-3857
  User acergn100_7
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 4
```

Then `ssh gn100` works from anywhere on the tailnet. The `ServerAlive` flags keep the connection from timing out on flaky venue wifi.

**tmux session naming convention on the box:**

| Session | Purpose | Owner | Touch? |
|---|---|---|---|
| `stub` | Orchestrator stub server on :30000 | Alex | **NEVER** — this is the safety net |
| `llama` | llama.cpp server hosting Nemotron-3-Nano on :8090 | Alex | Read-only attaches only |
| `nano-dl` | (transient) GGUF download | Alex | Don't touch — auto-cleans when done |
| `your-name-foo` | Anything you spin up | You | Yours, prefix with your name |

**Rules:**
- Always launch long-running processes inside tmux. SSH dies, tmux survives.
- Never `tmux kill-session` on a session you didn't start.
- Read-only is fine: `tmux attach -r -t llama`. Non-readonly attaches steal control.
- Stub on :30000 is sacred. If you suspect it's dead, ping Alex before doing anything.

**What you can / can't touch:**
- ✅ Your own tmux sessions, your own files under `~/your-name/`, the public repo.
- ❌ sshd config, tailscale, networking, firewall, the `stub` tmux session, anything in `/etc`, `sudo` of anything that isn't a documented apt package.

---

## If you're stuck

1. Re-read this doc.
2. Check the README in your branch's directory.
3. Ping the team in chat — don't burn 30+ minutes alone.
4. Stub-vs-real questions → Alex
5. Renderer / shader questions → Carson
6. Three.js / WebGL questions → James
7. Blender / point cloud questions → Marvens

---

*Last updated: Apr 10 2026 evening, kickoff. This doc is the source of truth for the workflow. If something changes, update it and post in chat.*
