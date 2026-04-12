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
│  deck.gl + maplibre        │                      │  llama.cpp                 │
│  LOBBY RENDERER (PRIMARY)  │                      │  NARRATION SERVER          │
│  (browser, James)          │                      │                            │
│                            │                      │  NVIDIA Nemotron-3 Nano    │
│  Year slider 1700-2026     │   POST /narrate      │  30B-A3B (Q8_K_XL GGUF)    │
│  8 architectural eras      │   POST /biography    │  from the NVIDIA Nemotron  │
│  750 NYPL Milstein photos  │ ───────────────────► │  model family              │
│  All 5 boroughs compacted  │                      │                            │
│  Click → biography RAG     │                      │  Port :8090                │
│                            │                      │  OpenAI-compatible API     │
│  (Bevy native v2 deferred) │                      │  --jinja --ngl 99          │
└────────────────────────────┘                      └────────────────────────────┘
                ▲                                                   ▲
                │                                                   │
                └────────────────────┬──────────────────────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────────┐
                       │  FastAPI ORCHESTRATOR        │
                       │  src/orchestrator/main.py    │
                       │                              │
                       │  POST /narrate               │
                       │    forensic narration of one │
                       │    cultural event, grounded  │
                       │    in events-seed.json       │
                       │                              │
                       │  POST /biography             │
                       │    src/biography/ structured │
                       │    retrieval over Building   │
                       │    Footprints + NYPL photos  │
                       │    + demolished landmarks +  │
                       │    events-seed by BIN/lat-lon│
                       │    proximity → Nemotron 4-   │
                       │    section forensic biography│
                       │                              │
                       │  GET /events  GET /niches    │
                       │  GET /health                 │
                       │                              │
                       │  Pre-baked cache at          │
                       │  data/narration_cache.json   │
                       │  as venue WiFi insurance     │
                       │                              │
                       │  Port :30001 (real)          │
                       │  Port :30000 (stub)          │
                       └──────────────────────────────┘
```

## Data sources (everything is committed in the repo, no runtime fetches)

| Source | Where in repo | What it provides |
|---|---|---|
| NYC Building Footprints `5zhs-2jue` (NYC OTI) | `data/{manhattan,bronx,brooklyn,queens,staten}_compact.json` | LiDAR roof heights + construction year + BIN + polygon for every building in NYC. 5 boroughs compacted Apr 11 21:43 ET, 262 MB total. Schema `{p, h, y, b}` byte-compatible with James's original Manhattan compactor. |
| NYPL Milstein Picture Collection | `cultural-content/oldnyc/index.json` (James's `bde0148`) | 750 georeferenced archival photos × 5 boroughs, 1900-1956. Schema `{id, boro, lat, lon, year, title, thumb, nypl_url}`. |
| Wikidata demolished NYC landmarks | `data/demolished-landmarks.json` | 295 demolished landmarks with name, built/demolished years, lat/lon. Sourced via SPARQL on `feature/sketch-overlay@277e8d9`. |
| Hand-curated cultural events | `data/events-seed.json` | 19 events anchored on the Bronx hip-hop birth chain — Cross-Bronx displacement 1959 → Puerto Rican migration → Loew's Paradise → Kool Herc 1973 → Wild Style → Beat Street. Each event carries `{id, coordinate, start_year, end_year, niche_tags, title, narration_seed, era_visual_mode, source_url, importance_score}`. Pre-baked narrations at `data/narration_cache.json` as venue WiFi insurance. |

**No external network fetches at runtime.** Everything in the table above is committed at code freeze and read from disk by the `src/biography/lookup.py` retrieval layer. The `lookup.py` `assemble_record()` entry point joins these sources by BIN and haversine lat/lon proximity into a single flat record passed to Nemotron via `src/biography/synthesize.py`.

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

## The Sun demo path (one renderer + one engine + one causal arc)

The locked thesis (`docs/DEMO_VIDEO_SCRIPT.CROSS_BRONX.md`) is **cultural memory infrastructure on local hardware** anchored on a single causal arc: Cross-Bronx Expressway 1948-1972 → 60K displaced → Sedgwick Avenue → Kool Herc Aug 11 1973 → hip-hop birth. The Sun demo runs on one renderer and one engine:

| Layer | Choice | Owner | What it does |
|---|---|---|---|
| **Renderer (PRIMARY)** | deck.gl + maplibre browser on the GN100 | James | Year slider scrubbing 1700-2026 across all 5 boroughs, 8 architectural eras color-coded by construction year, 750 NYPL Milstein photos georeferenced, click-any-building → biography panel. The Sun demo verb. |
| **Migration cone** | static glb + click panel | Marvens | Cross-Bronx displacement primitive at the corridor centroid, magnitude/spread/tilt encoded per `docs/MIGRATION_FLOW_PROTOTYPE.html`. Sibling manifest at `assets/migration-flows/MANIFEST.json`. Beat 3 of the demo (was Beat 5 pre-pivot). |
| **Biography RAG** | `src/biography/` zero-dependency stdlib + httpx | Alex | Click any building polygon → structured retrieval over 4 local data sources → forensic 4-section biography from Nemotron in 5-30 sec. The payoff click. |
| **Narration LLM** | NVIDIA Nemotron-3 Nano 30B (A3B) via llama.cpp on `:8090` | Alex | 30B reasoning model warm-loaded in 128 GB unified memory, ethernet unplugged at demo time. |

Bevy 0.18.1 (Rust + wgpu) lives on `renderer-rust`, frozen at `b394623`, **deferred to post-hack v2.** Carson left the team Apr 11 ~21:30 ET; the Bevy native renderer is shipped as documented but not part of the Sun demo path. The deck.gl browser is the primary surface and the only surface judges will see Sunday afternoon.

The product wedge story (tenant lawyer compliance lock + museum reanimation + 18-month roadmap) lives in `docs/PRODUCT_WEDGES.md` and is the post-demo Q&A pitch, not the 90-second video. Alex's Antler unicorn-bounty pitch is in `docs/DEMO_VIDEO_SCRIPT.CROSS_BRONX.md` (2-min Antler 1:1 version).

---

## Cultural events table (the data layer)

Events are stored as a JSON array in `data/events-seed.json` (19 events as of Apr 11). Pre-baked narrations from the real backend live at `data/narration_cache.json`. See `docs/STACK.md` for the field-level schema. The orchestrator loads the file at startup, indexes events by year and by niche tag, and serves queries:

- **Time slider drag → era events:** "give me all events where `start_year ≤ current_year ≤ (end_year ?? infinity)` AND `current_niche` is in `niche_tags`"
- **Pin click → narration:** "give me the narration_seed for event X, build a Nemotron prompt with the niche + era + nearby events context, return the generated text"

For the demo, ~30 hand-curated events. For the universal architecture pitch, "the data layer scales next via Cartewei or live NYC Open Data ingestion" (deferred work).

---

## The Sun demo verb (Cross-Bronx walkthrough)

```
USER lands on the deck.gl + maplibre browser at the venue
       │
       ▼
Default state: year slider at 2026, all 5 boroughs of building polygons
extruded by LiDAR roof height, 750 NYPL Milstein photo pins, modern view
       │
       │ Alex grabs the year slider and scrubs 2026 → 1948
       ▼
Building polygons morph era by era as construction_year filters apply.
Postwar Bronx fills back in.
       │
       │ Alex scrubs 1948 → 1972 (the Cross-Bronx Expressway era)
       ▼
The 7-mile Cross-Bronx corridor visibly empties as buildings whose
construction_year predates 1972 disappear from the displaced footprint.
Marvens's migration cone fires upward at the corridor centroid with
the documented displacement count (60,000 per Caro) on the click panel.
       │
       │ Alex clicks the 1520 Sedgwick Avenue building polygon
       ▼
Browser POST :30001/biography {"bin": "2008888"}  (or lat/lon)
       │
       ▼
src/biography/lookup.py · assemble_record():
  - resolves BIN against bronx_compact.json (height_m, year_built, polygon)
  - haversine within 200m → 8 nearest NYPL Milstein photos
  - haversine within 500m → nearby cultural events from events-seed.json
  - haversine within 1km → demolished landmarks from Wikidata
  - returns flat structured dict + dataset citations
       │
       ▼
src/biography/synthesize.py · synthesize():
  POST :8090/v1/chat/completions to local llama-server with:
  - SYSTEM: forensic building historian, no speculation, no invented owners
  - USER: structured record verbatim with field names preserved
       │
       ▼
NVIDIA Nemotron-3 Nano 30B returns the 4-section markdown biography
(Identification / Physical history / Cultural significance / What the
receipts prove) in 5-30 sec on the warm-loaded model
       │
       ▼
Browser overlays the biography panel + photo strip + dataset citation row.
Alex pulls the ethernet cable. The next visitor clicks a building anywhere
in NYC and the same flow runs with the cable on the floor.
```

**The verb is the year slider, the wow beat is the Cross-Bronx scrub, the payoff is the 1520 Sedgwick biography click.** The niche filter is a Q&A "what else can it do" answer, not the cinematic. The biography RAG is what makes the product more than a visualization — every click returns a footnoted historical document, not a vibe poem.

---

## Why this architecture wins points (mapped to the Spark Hack rubric)

The full rubric is in `docs/EVENT_RULES.md`. Total: 100 pts.

### 1. Technical Execution & Completeness (30 pts)
- **Completeness (15 pts)**: full data workflow runs end-to-end. NYC Building Footprints citywide GeoJSON → `scripts/export_buildings_all_boroughs.py` → 5 borough compact JSONs → deck.gl + maplibre browser → click building → `POST /biography` → `src/biography/lookup.py` structured retrieval → `src/biography/synthesize.py` Nemotron prompt → llama.cpp on `:8090` → 4-section forensic biography → browser overlay. Verified Apr 12 ~01:06 UTC via smoke test returning `backend:"real"` Sedgwick narration in 5 sec on warm-loaded model.
- **Technical Depth (15 pts)**: not a static dashboard, not an API wrapper. Zero-dependency RAG (`src/biography/`) over 4 local data sources joined by BIN and haversine lat/lon proximity, no embeddings, no vector DB, no LangChain, no cloud calls. Custom multi-stage pipeline grounding the LLM in 4 fused datasets: NYC Building Footprints (citywide LiDAR), NYPL Milstein photo index (750 georeferenced archival photos), Wikidata demolished landmarks (295 records), hand-curated cultural events (19 anchored on the Bronx hip-hop birth chain). Pre-baked narration cache as venue WiFi insurance. FastAPI orchestrator with two endpoints (`/narrate`, `/biography`) sharing a common forensic posture.

### 2. NVIDIA Ecosystem & Spark Utility (30 pts)
- **The Stack (15 pts)**: **NVIDIA Nemotron-3 Nano 30B (A3B variant) from the NVIDIA Nemotron model family**, served via llama.cpp on the GB10. Nemotron is in the NeMo Models category explicitly listed by the rubric. **The model attribution must be named in the demo for the rubric to score it as a NeMo Model use** (see `docs/STACK.md` "verbatim words to lock").
- **The Spark Story (15 pts)**: 128 GB unified memory holds the 30B model + open data corpus + renderer state simultaneously, no PCIe round trips. Local-only inference for sovereignty/privacy. The unplug-cable demo is the punchline. We use the unified memory the way it was designed to be used.

### 3. Value & Impact (20 pts)
- **Insight Quality (10 pts)**: Cross-Bronx Expressway 1948-1972 displaced ~60,000 people (Caro). Receipts traceable to NYC Building Footprints construction_year + Wikidata demolished landmarks + NYPL Milstein photo provenance + hand-curated events-seed cultural events. Specific, sourced, non-obvious. "We don't predict gentrification, we trace it from the receipts."
- **Usability (10 pts)**: a tenant lawyer in the South Bronx could pull a 4-section footnoted building biography in 30 sec for any NYC address — vs ~6 paralegal hours of records work today. The NY right-to-counsel expansion of 2022 generates ~20K new tenant cases/yr that legally cannot be uploaded to a cloud LLM (Rule 1.6 of the NY Rules of Professional Conduct, client confidentiality), so the local-inference architecture is a compliance lock, not a flex. A preservation researcher could surface every demolished landmark within a radius of any address with one query. The same engine serves the museum/curator reanimation use case post-hack.

### 4. The "Frontier" Factor (20 pts)
- **Creativity (10 pts)**: novel combination of 4 fused datasets (NYC Building Footprints citywide LiDAR + NYPL Milstein photo index + Wikidata demolished landmarks + hand-curated cultural events) joined zero-dependency by BIN and lat/lon proximity, then grounded into a 30B local reasoning model that returns a 4-section forensic biography. PS2 constraint language for the renderer post-process. Cross-Bronx → Kool Herc causal arc as the cinematic anchor — the demo doesn't just visualize NYC, it traces a single 25-year story from urban renewal trauma to the birth of hip-hop, all from public records on local hardware.
- **Performance (10 pts)**: **29 tokens per second** sustained generation on a 30B Q8 reasoning model. **262 megabytes** total for all 5 boroughs of NYC building polygons + LiDAR roof heights + construction years (~1.05 million buildings). **Zero** network round trips at runtime — the ethernet cable comes out before the demo starts.

