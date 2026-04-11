# Sixth Borough — Architecture

## System diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │       ACER VERITON GN100 (NVIDIA DGX SPARK)         │
                    │       GB10 Grace Blackwell Superchip                │
                    │       128 GB unified memory · sm_121 CUDA arch      │
                    │       Runs entirely offline at runtime              │
                    └─────────────────────────────────────────────────────┘
                                          │
                ┌─────────────────────────┴─────────────────────────┐
                │                                                   │
                ▼                                                   ▼
┌────────────────────────────┐                      ┌────────────────────────────┐
│  BEVY 0.18.1               │                      │  llama.cpp                 │
│  ENCOUNTER RENDERER        │                      │  NARRATION SERVER          │
│  (Rust + wgpu, native)     │                      │                            │
│                            │                      │  NVIDIA Nemotron-3 Nano    │
│  PS2 post-process          │   POST /narrate      │  30B-A3B (Q8_K_XL GGUF)    │
│  Low-poly Blender ghosts   │ ───────────────────► │  from the NVIDIA Nemotron  │
│  Migration cone primitives │                      │  model family              │
│  (sibling manifest pattern)│                      │                            │
│                            │                      │  Port :8090                │
│  Bevy → WASM target via    │                      │  OpenAI-compatible API     │
│  Trunk + Cloudflare Pages  │                      │  --jinja --ngl 99          │
└────────────────────────────┘                      └────────────────────────────┘
                ▲                                                   ▲
                │                                                   │
                └────────────────────┬──────────────────────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │  FastAPI ORCHESTRATOR    │
                       │  src/orchestrator/main.py│
                       │                          │
                       │  - Loads events-seed.json│
                       │  - Builds Nemotron prompt│
                       │  - Routes to backend     │
                       │    (real / stub / cache) │
                       │  - Pre-baked cache as    │
                       │    venue WiFi insurance  │
                       │                          │
                       │  Port :30001 (real)      │
                       │  Port :30000 (stub)      │
                       └──────────────────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │   LOBBY RENDERER         │
                       │   deck.gl + maplibre     │
                       │   (browser, James)       │
                       │                          │
                       │   Year slider 1700-2026  │
                       │   8 architectural eras   │
                       │   750 NYPL Milstein      │
                       │     photos × 5 boroughs  │
                       │   manhattan_compact.json │
                       └──────────────────────────┘
```

## Data sources (all cached locally before code freeze)

- **NYC Open Data** — historical landmark records, zoning history, neighborhood boundaries
  - Cached at `assets/nyc-data/` (gitignored, downloaded once)
- **Wikimedia Commons** — historical photos of NYC neighborhoods by era
  - 24 photos already in James's `feature/sketch-overlay` branch
  - Cached at `assets/photos/` (gitignored)
- **Era metadata** — hand-curated by team, lives in `src/data/eras.json`

## Network topology

**At runtime: NONE.** The system is designed to run with the ethernet cable unplugged. The unplug-cable demo is the entire pitch — if anything in the system requires network at runtime, it goes in the trash.

**During build:** model weights and dataset assets are downloaded once, then cached. Once the box is set up, the cable comes out.

## Memory budget on the GN100 (128 GB unified)

| Component | Approximate footprint |
|---|---|
| NVIDIA Nemotron-3 Nano 30B (A3B variant, Q8_K_XL GGUF) | ~38 GB |
| Renderer scene + framebuffer | ~2 GB |
| Orchestrator + Python runtime | ~1 GB |
| Open data corpus + events seed + narration cache | <1 GB |
| OS + buffer cache | ~10 GB |
| **Total estimated** | **~52 GB** |
| **Headroom** | **~76 GB** |

**Verified Apr 11 ~14:50 ET** via `ssh gn100`: GB10 at 50°C, 17W power draw, 20% util while serving narrations. RAM 47 GB used, 72 GB available, swap 1.4 MiB. 5× headroom for additional concurrent models if needed. Full snapshot at `docs/GN100_HEALTH_APR11.md`.

**The Spark Story**: the unified memory architecture is what makes this whole thing fit on one box. Holding the 30B model + orchestrator + open data corpus + renderer state simultaneously would require copying tensors across PCIe on a non-unified architecture. On GB10 it's all the same address space — that's the rubric answer to "why does this run better on a DGX Spark."

If we hit OOM despite the headroom, the DGX Spark UMA caveat applies — flush the buffer cache:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

## Failure modes & fallbacks

| Failure | Detection | Fallback |
|---|---|---|
| Bevy native renderer crashes | Sat afternoon rehearsal | Pivot to James's deck.gl + maplibre browser path as primary visual (it's already the lobby surface and is independently functional) |
| `:8090` llama-server crashes | Tail tmux `llama` pane / `curl :30001/health` | Restart with `./scripts/start-llama-nano.sh`. Cost: ~30s + cache rebuild. **As of Apr 11 14:50 ET, llama-server has 6h 38m uptime — do not restart unless it actually breaks.** |
| `:30001` real orchestrator crashes | `curl :30001/health` returns non-200 | Stub orchestrator on `:30000` is the safety net (still alive). Renderer can switch endpoints. |
| Both backends down + venue WiFi flakes | Smoke test | **Pre-baked narration cache at `data/narration_cache.json`** has all 19 events served with `backend:"real"` from a Apr 11 14:53 ET batch. Renderer can serve from disk without any backend running. |
| Demo crashes on stage | Rehearsal | Pre-recorded 30-second OBS clip of the working loop as backup |
| Tailscale flakes at venue | Pre-demo check | Demo runs on the GN100's local screen via HDMI as the primary path, Tailscale is the secondary remote-debug path |

## Renderer asset pipeline (glb-only, sibling manifest pattern)

The native renderer is **Bevy 0.18.1** (Rust, built on wgpu). The Blender → Bevy contract is **glb-only** as of Apr 11 ~10:00 ET (`d6470aa`). The Blender → Bevy contract:

```
MARVENS (Blender)                                CARSON (Bevy 0.18.1)
─────────────────                                ────────────────────

Low-poly ghost meshes ─────────► .glb ─────────► SceneRoot via bevy_gltf
(demolished buildings,            (~2K verts,       (built-in loader)
~2K verts, vertex normals)        vertex normals,
                                  vertex colors
                                  for era band)

Migration cone primitives ─────► .glb ─────────► SceneRoot via bevy_gltf
(per docs/MIGRATION_FLOW_         (parameter-      (independent loader)
PROTOTYPE.html design grammar)    encoded geometry)

                                 ┌──────────────────────────────┐
                                 │  assets/ghosts/              │
                                 │    MANIFEST.json (committed) │
                                 │    *.preview.png (committed) │
                                 │    *.glb (gitignored, sync   │
                                 │      via shared storage)     │
                                 │                              │
                                 │  assets/migration-flows/     │
                                 │    MANIFEST.json (committed) │
                                 │    *.glb (gitignored)        │
                                 └──────────────────────────────┘
```

**Sibling manifest pattern**: each asset family gets its own MANIFEST.json. The two loaders are independent in the Bevy ECS startup phase. New asset families add new sibling manifests, not nested keys. This keeps Marvens's two deliverables (ghost meshes and migration cones) from blocking each other.

Marvens never touches Rust. Carson never touches Blender. The contract between them is `pointcloud-pipeline/README.md` (legacy directory name retained; the format is glb-only now).

---

## The two-mode product map

The locked thesis (`docs/DEMO_VIDEO_SCRIPT.md`) is **cultural memory infrastructure on local hardware**. The architecture splits into two surfaces that share a data spine:

| Mode | Surface | Owner | What it does |
|---|---|---|---|
| **Mode A — Lobby (breadth)** | deck.gl + maplibre browser | James | Year slider scrubbing 1700-2026 across all 5 boroughs, 8 architectural eras color-coded by construction year, 750 NYPL Milstein photos georeferenced, click-any-building biography panel. The "every building has a birthday" pitch surface. |
| **Mode B — Encounter (depth)** | Bevy 0.18.1 native on GB10 | Carson + Marvens | Drop into one specific event (Cross-Bronx canonical). Low-poly ghost meshes for demolished buildings. Migration cone primitives for displaced communities (sibling manifest at `assets/migration-flows/MANIFEST.json`). NVIDIA Nemotron-3 Nano 30B narration generated live on the GB10. PS2 post-process. The "computational ghosts need local hardware" pitch surface. |

Both modes consume the same `{p, h, y, b}` building polygon JSONs, the same `events-seed.json`, the same NYPL OldNYC index, and the same `/narrate` orchestrator contract. **The merge of James + Carson + Marvens is the demo** — corrected from an earlier "park renderer-rust" mistake at Apr 11 morning.

The product wedge story (5 buyer segments, non-ML data layers) lives in `docs/PRODUCT_WEDGES.md` and is the post-demo Q&A pitch, not the 90-second video.

---

## Cultural events table (the data layer)

Events are stored as a JSON array in `data/events-seed.json` (19 events as of Apr 11). Pre-baked narrations from the real backend live at `data/narration_cache.json`. See `docs/STACK.md` for the field-level schema. The orchestrator loads the file at startup, indexes events by year and by niche tag, and serves queries:

- **Time slider drag → era events:** "give me all events where `start_year ≤ current_year ≤ (end_year ?? infinity)` AND `current_niche` is in `niche_tags`"
- **Pin click → narration:** "give me the narration_seed for event X, build a Nemotron prompt with the niche + era + nearby events context, return the generated text"

For the demo, ~30 hand-curated events. For the universal architecture pitch, "the data layer scales next via Cartewei or live NYC Open Data ingestion" (deferred work).

---

## Niche filter UI flow

```
USER opens Sixth Borough
       │
       ▼
Default state: time slider at 2026, no niche filter, modern view
       │
       │ user drags slider 2026 → 1973
       ▼
Renderer morphs through era_visual_modes (PS2 palette/post-process changes)
       │
       │ user clicks "Hip-hop heads" toggle in niche filter list
       ▼
Orchestrator queries events: hip-hop tag, year window 1965-1985
       │
       ▼
Pins appear/disappear on map as slider passes their start_years
       │
       │ user drags slider forward to 1973
       ▼
1520 Sedgwick pin lights up
       │
       │ user clicks the pin
       ▼
Orchestrator builds prompt:
  niche=hip-hop, year=1973, place=Bronx, event=Kool Herc breakbeat,
  narration_seed=..., recent_nearby=[...]
       │
       ▼
POST :30000/v1/chat/completions
       │
       ▼
Nemotron-3-Nano returns 2-3 sentence narration
       │
       ▼
Orchestrator overlays narration text on the renderer scene
       │
       │ user toggles "Hip-hop" off, "Immigration flow" on
       ▼
Same map, same year, totally different pin set (immigration events)
```

The toggle is the critical UX element. **Niche switching is what proves the architecture works on multiple lenses.** Even if only one niche is fully populated, the toggle has to feel real.

---

## Why this architecture wins points (mapped to the Spark Hack rubric)

The full rubric is in `docs/EVENT_RULES.md`. Total: 100 pts.

### 1. Technical Execution & Completeness (30 pts)
- **Completeness (15 pts)**: full data workflow runs end-to-end. NYC Open Data → compactor → JSON → renderer → orchestrator → llama.cpp → NVIDIA Nemotron → narration → screen. Verified Apr 11 14:45 ET via `ssh gn100 curl :30001/narrate` returning `backend:"real"` Sedgwick narration in 23.4s.
- **Technical Depth (15 pts)**: not a static dashboard. Custom multi-stage pipeline with structured retrieval grounding the LLM in historical records (events-seed + open data layers + NYPL Milstein index). Bevy native renderer + WASM target + deck.gl breadth surface + FastAPI orchestrator + llama.cpp inference + Blender authoring → glb sibling manifests. Six datasets fused.

### 2. NVIDIA Ecosystem & Spark Utility (30 pts)
- **The Stack (15 pts)**: **NVIDIA Nemotron-3 Nano 30B (A3B variant) from the NVIDIA Nemotron model family**, served via llama.cpp on the GB10. Nemotron is in the NeMo Models category explicitly listed by the rubric. **The model attribution must be named in the demo for the rubric to score it as a NeMo Model use** (see `docs/STACK.md` "verbatim words to lock").
- **The Spark Story (15 pts)**: 128 GB unified memory holds the 30B model + open data corpus + renderer state simultaneously, no PCIe round trips. Local-only inference for sovereignty/privacy. The unplug-cable demo is the punchline. We use the unified memory the way it was designed to be used.

### 3. Value & Impact (20 pts)
- **Insight Quality (10 pts)**: Cross-Bronx Expressway 1948-1972 displaced ~60,000 people (Caro). Receipts traceable to BUILDING_HISTORIC + DOB demolition records + ACS tract delta. Specific, sourced, non-obvious. "We don't predict gentrification, we trace it from the receipts."
- **Usability (10 pts)**: a tenant lawyer in the South Bronx could use this to build a displacement case tomorrow. A preservation researcher at LPC could pull every demolished building in a historic district with one query. A ProPublica reporter could trace the receipts of any gentrification claim. Five named buyer segments in `docs/PRODUCT_WEDGES.md`.

### 4. The "Frontier" Factor (20 pts)
- **Creativity (10 pts)**: novel combination of six datasets (DOB filings + Building Footprints Historical + ACS census + NYPL archives + LiDAR roof heights + 30B local LLM) with PS2 constraint language for memory rendering on Blackwell silicon.
- **Performance (10 pts)**: **29 tokens per second** sustained generation on a 30B Q8 reasoning model. **60 megabytes** browser-deliverable carrying 175 years of NYC building biography across 5 boroughs. **Zero** network round trips at runtime.

