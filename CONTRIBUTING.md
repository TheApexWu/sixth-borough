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
| `real` | NVIDIA Nemotron-3 Nano 30B via llama.cpp on the GB10. GN100 only. | Alex (at the venue) + Sat night integration |

Switch with `NARRATION_MODE=stub` or `NARRATION_MODE=real`. Same Pydantic models, same HTTP contract.

**Live as of Apr 11 ~14:45 ET**: real backend on `:30001` returning `backend:"real"` for the canonical Sedgwick event in ~23s. Pre-baked cache at `data/narration_cache.json` (all 19 events) is venue-WiFi insurance.

---

## Branch assignments

### `renderer-rust` — Carson

**Goal:** Bevy 0.18.1 renderer (Rust + wgpu, native + WASM target). Loads the seed JSON. Renders a scene with PS2 post-process. Calls `/narrate` on pin click. Ingests Marvens's low-poly Blender ghost meshes (`assets/ghosts/MANIFEST.json`) and migration cone primitives (`assets/migration-flows/MANIFEST.json`) via Bevy's stock `SceneRoot(asset_server.load(GltfAssetLabel::Scene(0).from_asset(...)))`.

**Engine pin:** Bevy 0.18.1. The earlier 0.16 pin was driven by `bevy_pointcloud` plugin compat — once the team moved to glb-only single-format ghosts (Apr 11 ~10:00 ET, `d6470aa`), the plugin was dropped and the version constraint was lifted. Carson shipped `819a7f3 wasm` + `54a431f cicd` Apr 11 11:59 ET on `renderer-rust`.

**Owns:** `src/renderer/` only. Don't touch `src/orchestrator/` or `src/data/`.

**Status as of Apr 12 ~21:30 ET (Session 45)**: Carson is OUT of the team, "out of commission." The Bevy native renderer is FROZEN at `b394623`. The branch is shipped as-is and is now post-hack v2 territory, NOT the Sun demo path. Don't try to revive it; the deck.gl + maplibre browser is the live demo. Schema verification of the Bevy click handler ({event_id, year, niche, style}) is inherited by Alex.

**First PR done when:** window opens, loads seed JSON, time slider scrubs, one niche filter button works, one narration call returns text from stub, one PS2 shader stage running, one ghost mesh loaded from `assets/ghosts/MANIFEST.json`.

**Doesn't need:** GN100, Nemotron, llama.cpp.

---

### `feature/sketch-overlay` — James (PRIMARY for Sun demo)

**Goal:** deck.gl + maplibre browser renderer. Year slider 1700-2026, 8 architectural eras color-coded by construction year, guided 8-era tour with cutscenes, GSAP motion engine, dev panel with feature flags. Same `/narrate` endpoint as the rest of the team. Now also wired into `POST /biography` for the click payoff.

**Status as of Session 45**: PRIMARY demo path (Carson out, Bevy frozen). All 5 boroughs of building polygons now load (manhattan + bronx wired in `e0b2428`, the other 3 are session-44/borough-expansion-bronx files James can pull). 750 NYPL Milstein photos georeferenced across all 5 boroughs in `bde0148`.

**Owns:** `index.html`, all `data/*_compact.json` files, `cultural-content/oldnyc/`, `scripts/export_buildings*.py`, `scripts/build_oldnyc_index.py`. Don't touch `src/`.

**Open work for Sun demo**: see `docs/UX_AUDIT_SESSION_45.md` for the 3 click-handler bugs (building name stub, photo fallback too generous, dev placeholder body text) and the biography RAG wire-up that replaces them. See `docs/MARVENS_PREP.md` for the right-side widget keep/hide/scrap audit and the immigration-origins-panel rebind plan.

---

### `pointcloud-pipeline` — Marvens

**Goal:** Blender → glb export pipelines for **(1)** low-poly ghost meshes for demolished buildings, and **(2)** migration cone primitives per `docs/MIGRATION_FLOW_PROTOTYPE.html` design grammar (Cross-Bronx Expressway 1948-1972 as canonical anchor).

**glb-only single-format contract** (Apr 11 ~10:00 ET, `d6470aa`):
- ~2K verts per mesh
- Vertex normals only (no PBR)
- Vertex colors for era band encoding
- Cool PS2 palette per `docs/VISUAL_DIRECTION.md` (deep navy → washed periwinkle → memory blue + dusty gold accent for origin click-target)
- **Anti-patterns**: no red/orange/yellow, no fast turbulent motion, no plume shape, no PBR/photoreal

**Sibling manifest pattern**: each asset family gets its own MANIFEST.json. Drop ghosts into `assets/ghosts/` + bump `assets/ghosts/MANIFEST.json`. Drop migration cones into `assets/migration-flows/` + bump `assets/migration-flows/MANIFEST.json`. The two loaders are independent.

**Owns:** `pointcloud-pipeline/` (legacy directory name, format is glb-only now), `assets/ghosts/`, `assets/migration-flows/`.

**Sun deliverable (locked target):**
- 1-2 ghost meshes per the visual direction contract
- 1 migration cone prototype anchored to Cross-Bronx (most cinematic, best-documented, ~60K Caro number)

One canonical example sells the framework. Other events stay as v2 catalog post-hack.

**Authoring stack:** Blender + vanilla glTF export.

**Doesn't need:** code skills, GN100, the narration loop, the renderer to be done.

**Asset rule:** large `.glb` files are gitignored. Manifest JSON + preview PNGs committed. Files sync via shared storage.

---

### `orchestrator-narration` — Alex

**Goal:** Real path that swaps in **NVIDIA Nemotron-3 Nano 30B (A3B variant, Q8_K_XL GGUF)** from the NVIDIA Nemotron model family when `NARRATION_MODE=real`. llama.cpp's OpenAI-compatible API on `:8090`, FastAPI orchestrator wrapping it on `:30001`.

**Owns:** `src/orchestrator/main.py`, `narration_real.py`, GN100 runbook. Don't touch `narration_stub.py`.

**First PR done when:** `narration_real.py` parses the same Pydantic models the stub uses, returns the same response shape, mode-switch test passes both paths. **Done as of Apr 11 morning** (`4ce1930` — reasoning_content fallback + LLAMA_MAX_TOKENS bump).

**Test:** stub locally on MacBook, real on the GN100 at the venue. Verified live Apr 11 14:45 ET.

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
| `renderer-rust/` | Carson (frozen at `b394623`, post-hack v2) |
| `index.html`, `data/*_compact.json` (all 5 boroughs), `data/borough_boundaries.geojson`, `cultural-content/oldnyc/`, `scripts/export_buildings*.py`, `scripts/build_oldnyc_index.py` | James (also `feature/sketch-overlay` branch) |
| `pointcloud-pipeline/` + `assets/ghosts/` + `assets/migration-flows/` | Marvens |
| `src/orchestrator/main.py` + `narration_real.py` + `narration_stub.py` | Alex |
| `src/biography/{__init__,lookup,synthesize,router}.py` | Alex (zero-dependency RAG endpoint, Session 45) |
| `src/data/schema.py` + `loader.py` + `niches.py` | Alex (ping before changing) |
| `data/events-seed.json` + `data/narration_cache.json` + `data/biography_cache.json` | Alex / James (rolling, small PRs) |
| `data/demolished-landmarks.json` | James (Wikidata SPARQL output, `277e8d9` on sketch-overlay) |
| `scripts/dev-stub.sh` + `scripts/start-llama-nano.sh` + `scripts/prebake_*.py` | Alex (stable) |
| `tests/` | area owner adds tests for their area |
| `docs/DECISIONS.md` | anyone (append-only) |
| `docs/PRODUCT_WEDGES.md` + `docs/DEMO_VIDEO_SCRIPT*.md` + `docs/VISUAL_DIRECTION.md` + `docs/MARVENS_PREP.md` + `docs/UX_AUDIT_*.md` | Alex (pitch + handoff surface) |

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

*Last updated: Apr 12 2026 ~03:30 ET, Session 45. Carson out, Cross-Bronx pivot locked, biography RAG live, all 5 boroughs compacted. This doc is the source of truth for the workflow. If something changes, update it and post in chat.*
