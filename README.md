# Sixth Borough

NYC's cultural memory infrastructure, localized in one box.

## Why

Every city has a memory. Most of it lives in filing cabinets, microfiche, and the heads of old-timers who are dying. Digitization without intelligence is just storage. Sixth Borough makes cultural memory visible, queryable, and local.

NYC's right-to-counsel expansion guarantees legal representation for 20,000 new tenant cases per year. Every case needs a building history. A paralegal pulls from 8 databases for 6 hours. We do it in 30 seconds on a $3,000 box the firm owns outright. Rule 1.6 of the NY Rules of Professional Conduct requires client confidentiality -- tenant attorneys legally cannot upload case files to a cloud LLM. Local inference is the only compliant path.

## What It Does

3D map of 1,082,831 buildings across all five boroughs, extruded to real LiDAR roof heights, with an animated year scrubber from 1700 to 2026. Click any building and a 30-billion-parameter NVIDIA Nemotron model generates a forensic biography from four public NYC datasets. No cloud. No internet at runtime.

- **Ghost buildings**: Twin Towers rise in 1970 and vanish in 2001. Penn Station disappears in 1963. Singer Building gone by 1968. The machine remembers what the city demolished.
- **Cross-Bronx Expressway**: 117 green ghost tenements along the corridor vanish as you drag 1948 to 1972, replaced by the expressway road surface. 60,000 people displaced.
- **Infrastructure**: 8 major bridges and 8 stadiums (including 3 ghost: Polo Grounds, Ebbets Field, original Yankee Stadium) rendered from a shared data layer.
- **Demolished landmarks**: 295 Wikidata pins across the city. White while standing, amber after demolition.
- **Archival photos**: 750 NYPL Milstein Division photos georeferenced to buildings.
- **Immigration flow**: Toggle-able animation of historical migration patterns by origin country and decade.
- **Guided tour**: 9-station era walk from Colonial (1760) through Glass Tower (2020).

## Dual-Renderer Architecture

Two renderers, one data contract.

**deck.gl + MapLibre (browser demo)** -- `feature/sketch-overlay` branch. Single-file `index.html` running deck.gl 9.1.4 on MapLibre 3.6.2. Renders all 5 boroughs as extruded polygons on a flat map plane with time-gated construction/demolition, 8 era color bands, immigration particle simulation, NYPL photo pins, and a CPU Sobel sketch overlay. Runs on any laptop with a browser. This is the demo surface -- proof of concept, not the production target.

**Bevy 0.18.1 + wgpu (native)** -- `renderer-rust-v2` branch. Rust, GPU-native, built for the NVIDIA DGX Spark (GB10 Blackwell, 128 GB unified memory). Real 3D scene graph with camera, directional lighting, and shadows. Demolished buildings are artist-authored low-poly .glb meshes loaded via a manifest system (ECS entity per ghost with coordinate, era window, and niche tags as components). PS2-era post-process (Sobel, vignette, palette quantization) as GPU shaders. Compiles to WASM for web fallback. This is the production architecture -- incomplete on assets, but the renderer scaffolding, ECS data model, and asset pipeline are in place.

The browser version fakes depth with extruded polygons on z=0. The Rust version renders real 3D geometry with proper lighting. The engineering choice was not about performance alone -- demolished buildings need to be authored 3D objects in a proper scene, not procedural rectangles on a flat map.

## Key Numbers

| Metric | Value |
|--------|-------|
| Buildings rendered | 1,082,831 |
| Geometry data | 231 MB (recompacted) |
| Bridges | 8 |
| Stadiums | 8 (5 active + 3 ghost) |
| Archival photos (NYPL) | 750 |
| Demolished landmarks | 295 |
| Cross-Bronx ghost buildings | 117 |
| Model | Nemotron-3 Nano 30B (Q8_K_XL) |
| Inference speed | 29 tok/sec |
| Hardware cost | $3,000 |

## Stack

- **Browser renderer**: deck.gl 9.1.4 + MapLibre GL 3.6.2 + GSAP 3.12.5
- **Native renderer**: Bevy 0.18.1 + wgpu (Rust)
- **Inference**: NVIDIA Nemotron-3 Nano 30B (A3B) via llama.cpp (CUDA 12.8, cuBLAS, 99 layers on GPU)
- **Orchestrator**: FastAPI (biography RAG, caching, photo overlay)
- **Hardware**: Acer GN100 / NVIDIA DGX Spark / GB10 Grace Blackwell / 128 GB unified LPDDR5X

## Repo Structure

```
index.html                          -- deck.gl browser demo (all boroughs, ghost buildings, year scrubber)
data/                               -- compacted building geometry JSONs (5 boroughs)
data/landmarks-infrastructure.json  -- shared data: bridges, stadiums, ghost buildings
data/demolished-landmarks.json      -- 295 Wikidata demolished landmark pins
cultural-content/                   -- archival photos, MARQUEE content, Bronx hip-hop assets
cultural-content/oldnyc/            -- 750 NYPL Milstein photos + thumbnails
scripts/                            -- data pipelines, recompaction, export
src/                                -- FastAPI orchestrator, biography RAG, inference wiring
docs/                               -- hardware documentation
```

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable integration point |
| `feature/sketch-overlay` | Browser demo (deck.gl + MapLibre) |
| `renderer-rust-v2` | Native Bevy/wgpu renderer |
| `data-curation` | Building data pipelines |
| `orchestrator-narration` | Nemotron inference + orchestrator |
| `pointcloud-pipeline` | Point cloud processing |

## Quick Start

```bash
# Browser demo (any machine)
python3 -m http.server 8080
# open http://localhost:8080/index.html

# On the GN100, also start inference:
llama-server -m /path/to/nemotron-30b-q8.gguf -ngl 99 --port 8090
cd src && uvicorn orchestrator.main:app --host 0.0.0.0 --port 30001
```

## Track

Cultural Impact | Spark Hack Series NYC, Apr 10-12 2026
