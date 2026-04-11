# Sixth Borough

A time machine for niche subcultures across all five boroughs of New York City. Built for Spark Hack Series NYC, Apr 10–12 2026.

Drop into any neighborhood, scrub a year slider through decades of history, toggle a niche filter (hip-hop heads, queer history, demolished theaters, jazz, salsa, immigration flow), and watch the place re-render in the visual language of its era while a local language model narrates what mattered there. Everything runs on one box with the ethernet cable on the floor.

**Track:** Cultural Impact
**Hardware:** Acer Veriton GN100 (DGX Spark / GB10 Grace Blackwell, 128 GB unified memory, runs entirely offline)
**Renderer:** Bevy 0.16 (Rust + wgpu) with PS2-style post-process and `bevy_pointcloud` for the demolished-building ghost layer
**Narration:** Nemotron-3-Nano-30B-A3B (Q8 GGUF) via llama.cpp on the GB10
**Asset authoring:** Blender + OpenVAT for animated vertex-level point cloud animation

---

## Quick start (any laptop, no GPU required)

The orchestrator has two modes. **Stub mode** runs templated narration on any laptop with no GPU and no model download — this is how teammates develop their slice without depending on the GN100. **Real mode** swaps in the actual Nemotron-3-Nano via llama.cpp on the GN100 box at the venue. Both modes serve the same `/narrate` HTTP contract, so the renderer code never has to know which is wired.

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
./scripts/setup-gn100.sh    # builds llama.cpp, downloads Nemotron (~38 GB)
./scripts/start-gn100.sh    # starts the llama.cpp server on :30000
NARRATION_MODE=real ./scripts/dev-stub.sh   # starts the orchestrator pointed at the real backend
```

`scripts/test-narration.sh` smoke-tests the raw llama.cpp endpoint directly.

---

## Repository layout

```
sixth-borough/
├── README.md                    this file
├── ARCHITECTURE.md              system diagram + asset pipeline
├── CONTRIBUTING.md              branch playbook + collaboration model
├── requirements.txt             Python dependencies
├── pyproject.toml               Python project metadata
├── docs/
│   ├── STACK.md                 pinned tech stack with verbatim setup
│   ├── DECISIONS.md             append-only decision log
│   ├── DATA_SOURCES.md          NYC Open Data references
│   └── EVENT_RULES.md           Spark Hack rules + judging criteria
├── data/
│   └── events-seed.json         hand-curated cultural events
├── src/
│   ├── data/
│   │   ├── schema.py            CulturalEvent + NarrationRequest/Response Pydantic models
│   │   ├── niches.py            niche taxonomy + display metadata
│   │   ├── narration_prompts.py niche-conditioned prompt template
│   │   └── loader.py            seed JSON loader + query helpers
│   ├── orchestrator/
│   │   ├── main.py              FastAPI app
│   │   ├── narration_stub.py    templated narration (anyone, any laptop)
│   │   └── narration_real.py    real Nemotron via llama.cpp (GN100 only)
│   └── renderer/                Carson's Bevy + WGSL renderer
├── pointcloud-pipeline/
│   └── README.md                Blender → Bevy file format contract (PLY + OpenVAT)
├── assets/
│   └── pointclouds/
│       └── MANIFEST.json        list of available ghost assets
├── scripts/
│   ├── dev-stub.sh              start orchestrator in stub mode (anyone)
│   ├── dev-test.sh              run pytest suite
│   ├── setup-gn100.sh           build llama.cpp + download Nemotron (GN100 only)
│   ├── start-gn100.sh           start llama.cpp narration server (GN100 only)
│   └── test-narration.sh        smoke-test raw llama.cpp (GN100 only)
└── tests/                       pytest suite
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
