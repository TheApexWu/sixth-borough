# Sixth Borough

**Cultural memory infrastructure that runs on the community's own hardware instead of someone else's cloud.** Built for Spark Hack Series NYC, Apr 10–12 2026.

Every building in New York City has a birthday, a biography, and (sometimes) a death record — all of it in open data. Sixth Borough renders the city as it was, layer by layer, year by year, on local hardware. Click any building to see when it went up, what stood there before, who was displaced, what the photo from 1925 looked like. A 30-billion-parameter NVIDIA Nemotron model narrates the moment, live, from a box ten feet from the user with the ethernet cable on the floor.

**We don't predict gentrification. We trace it from the receipts.** Every particle on screen is a person who moved, on the record, in NYC Open Data. See `docs/PRODUCT_WEDGES.md` for the five buyer segments and the non-ML data thesis.

**Track:** Cultural Impact
**Hardware:** Acer Veriton GN100 (NVIDIA DGX Spark / GB10 Grace Blackwell Superchip, 128 GB unified memory, runs entirely offline)
**Narration:** **NVIDIA Nemotron-3 Nano 30B (A3B variant)** from the NVIDIA Nemotron model family, served via llama.cpp on the GB10. 29 tokens/sec sustained.
**Renderer (primary):** deck.gl + maplibre browser surface (James, `feature/sketch-overlay`) — year slider 1700-2026, 8 architectural eras, 750 georeferenced NYPL Milstein photos across all 5 boroughs, click-to-biography on every building polygon.
**Renderer (post-hack v2):** Bevy 0.18.1 (Rust + wgpu) with PS2-era post-process — `renderer-rust` branch, frozen for the Sun demo.
**Asset authoring:** Blender → glb (low-poly ghost meshes for demolished buildings).
**Structured retrieval:** zero-dependency RAG over local files (`src/biography/`) — joins all 5 borough Building Footprints compactions, NYPL Milstein photo index, hand-curated cultural events, and Wikidata demolished landmarks by BIN and lat/lon proximity. No embeddings, no vector DB, no LangChain, no cloud calls.
**Data spine:** NYC Open Data Building Footprints `5zhs-2jue` (LiDAR roof heights + construction years, all 5 boroughs compacted to 262 MB total), NYPL Milstein photo index (750 photos × 5 boroughs), Wikidata demolished landmarks (295 records), hand-curated cultural events (`data/events-seed.json`).

---

## Quick start (any laptop, no GPU required)

The orchestrator has two modes. **Stub mode** runs templated narration on any laptop with no GPU and no model download — this is how teammates develop their slice without depending on the GN100. **Real mode** swaps in the actual NVIDIA Nemotron-3 Nano 30B (A3B variant, Q8 GGUF) via llama.cpp on the GN100 box at the venue. Both modes serve the same `/narrate` HTTP contract, so the renderer code never has to know which is wired.

```bash
git clone https://github.com/TheApexWu/sixth-borough.git
cd sixth-borough
pip install -r requirements.txt
./scripts/dev-stub.sh
```

The orchestrator is now live on `http://localhost:30000`. Endpoints:

```
GET  /health      sanity check + which backend is wired
GET  /events      filtered list of cultural events (year, niche)
GET  /niches      niche taxonomy with display metadata
POST /narrate     generate a 2-3 sentence narration for one event
```

Run the test suite with `./scripts/dev-test.sh` (15 tests cover the schema, the loader, and the stub backend).

---

## On the GN100 (real mode)

Only one machine in the world runs Sixth Borough at full fidelity: the Acer Veriton GN100 box at the venue. After checking out the box:

```bash
./scripts/start-llama-nano.sh                # idempotent llama-server launcher (Nemotron 30B Q8 on :8090)
NARRATION_MODE=real LLAMA_SERVER_URL=http://127.0.0.1:8090 \
  python -m uvicorn src.orchestrator.main:app --host 0.0.0.0 --port 30001
```

The real backend runs the model on `:8090` and the orchestrator on `:30001`. The stub orchestrator on `:30000` stays alive as fallback. Verified live Apr 11 ~14:45 ET via `ssh gn100 curl :30001/narrate` — returns `backend:"real"` in ~23 seconds for the canonical Sedgwick event.

A pre-baked cache of all 19 events lives at `data/narration_cache.json` as venue-WiFi insurance: 19/19 events, ~15 sec average per generation, all `backend:"real"`. See `docs/GN100_HEALTH_APR11.md` for the standup-ready health snapshot.

---

## Repository layout

```
sixth-borough/
├── README.md                          this file
├── ARCHITECTURE.md                    system diagram + asset pipeline
├── CONTRIBUTING.md                    branch playbook + collaboration model
├── requirements.txt                   Python dependencies
├── pyproject.toml                     Python project metadata
├── docs/
│   ├── DEMO_VIDEO_SCRIPT.md           90s pitch script (locked)
│   ├── PRODUCT_WEDGES.md              receipts-not-predictions thesis + buyer segments
│   ├── VISUAL_DIRECTION.md            PS2 as constraint language for memory
│   ├── MIGRATION_FLOW_PROTOTYPE.html  Cross-Bronx canonical static cone sample
│   ├── PITCH_FRAMINGS.md              5 framings explored before lock
│   ├── GN100_HEALTH_APR11.md          standup-ready hardware snapshot
│   ├── STACK.md                       pinned tech stack
│   ├── DECISIONS.md                   append-only decision log
│   ├── DATA_SOURCES.md                NYC Open Data references
│   ├── EVENT_RULES.md                 Spark Hack rules + judging rubric
│   └── refs/visual/                   SMT3 reference images + NOTICE.md
├── cultural-content/
│   └── oldnyc/index.json              750 NYPL Milstein photos × 5 boroughs
├── data/
│   ├── events-seed.json               19 hand-curated cultural events
│   ├── narration_cache.json           pre-baked narrations (venue WiFi insurance)
│   ├── demolished-landmarks.json      Wikidata NYC demolished landmarks (295 records)
│   ├── manhattan_compact.json         Manhattan building polygons {p,h,y,b} schema
│   ├── bronx_compact.json             Bronx building polygons (104K buildings)
│   ├── brooklyn_compact.json          Brooklyn building polygons
│   ├── queens_compact.json            Queens building polygons
│   └── staten_compact.json            Staten Island building polygons
├── src/
│   ├── data/
│   │   ├── schema.py                  Pydantic models
│   │   ├── niches.py                  niche taxonomy
│   │   └── loader.py                  seed JSON loader
│   ├── orchestrator/
│   │   ├── main.py                    FastAPI app (POST /narrate, POST /biography)
│   │   ├── narration_stub.py          templated narration (forensic posture)
│   │   └── narration_real.py          NVIDIA Nemotron via llama.cpp (GN100 only)
│   └── biography/                     zero-dependency RAG endpoint
│       ├── lookup.py                  structured retrieval (BIN + haversine joins)
│       ├── synthesize.py              Nemotron prompt + llama-server client
│       └── router.py                  POST /biography FastAPI route
├── renderer-rust/                     Bevy 0.18.1 + wgpu (post-hack v2, frozen)
├── assets/
│   └── ghosts/
│       └── MANIFEST.json              low-poly Blender ghost mesh registry
├── scripts/
│   ├── dev-stub.sh                    start orchestrator in stub mode
│   ├── dev-test.sh                    run pytest suite
│   ├── start-llama-nano.sh            idempotent llama-server launcher (GN100 only)
│   ├── export_buildings.py            Building Footprints → compact JSON (legacy)
│   ├── export_buildings_all_boroughs.py  citywide compactor (5zhs-2jue, 5 boroughs)
│   └── build_oldnyc_index.py          NYPL Milstein → georeferenced index
└── tests/                             pytest suite
```

---

## For teammates

- **Branch playbook:** [`CONTRIBUTING.md`](CONTRIBUTING.md) — what each teammate works on, file ownership boundaries, the merge model
- **Tech stack:** [`docs/STACK.md`](docs/STACK.md) — pinned versions, setup commands, dependency-age audit
- **System architecture:** [`ARCHITECTURE.md`](ARCHITECTURE.md) — diagram, data flow, failure modes
- **NYC Open Data references:** [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — every dataset cited with field schemas and access notes
- **Build decisions:** [`docs/DECISIONS.md`](docs/DECISIONS.md) — append-only log

---

## License

TBD before submission. Default placeholder: All Rights Reserved during the hackathon weekend; will be updated to a permissive license (likely MIT or Apache 2.0) before public release.
