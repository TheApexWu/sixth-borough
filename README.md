# Sixth Borough

NYC's cultural memory infrastructure, localized in one box.

## Why

Every city has a memory. Most of it lives in filing cabinets, microfiche, and the heads of old-timers who are dying. Digitization without intelligence is just storage. Sixth Borough makes cultural memory visible, queryable, and local -- a sixth sense for the city.

NYC's right-to-counsel expansion guarantees legal representation for 20,000 new tenant cases per year. Every case needs a building history. A paralegal pulls from 8 databases for 6 hours. We do it in 30 seconds on a $3,000 box the firm owns outright. Rule 1.6 of the NY Rules of Professional Conduct requires client confidentiality -- tenant attorneys legally cannot upload case files to a cloud LLM. Local inference is the only compliant path.

## What It Does

3D map of 1,082,831 buildings across all five boroughs, extruded to real LiDAR roof heights, with an animated year scrubber from 1700 to 2026. Click any building and a 30-billion-parameter NVIDIA Nemotron model generates a forensic biography from four public NYC datasets. No cloud. No internet at runtime.

- **Ghost buildings**: Twin Towers rise in 1970 and vanish in 2001. Penn Station disappears in 1963. Singer Building gone by 1968. The machine remembers what the city demolished.
- **Cross-Bronx Expressway**: 117 green ghost tenements along the corridor vanish as you drag 1948 to 1972, replaced by the expressway road surface. 60,000 people displaced. Click any green building for the displacement-to-hip-hop story with archival photos.
- **Infrastructure**: 8 major bridges (Brooklyn through Verrazano) and 8 stadiums (including 3 ghost: Polo Grounds, Ebbets Field, original Yankee Stadium) rendered from a shared data layer.
- **Demolished landmarks**: 295 Wikidata pins across the city. White while standing, amber after demolition.
- **Archival photos**: 750 NYPL Milstein Division photos georeferenced to buildings.
- **Immigration flow**: Toggle-able animation of historical migration patterns by origin country and decade.
- **Guided tour**: 9-station era walk from Colonial (1760, Fraunces Tavern) through Glass Tower (2020, Hudson Yards), with a Bronx Burning station for the Cross-Bronx/hip-hop chain.

The demo traces one chain: Robert Moses displaced 60,000 South Bronx families onto Sedgwick Avenue. The density created the rec room party scene. DJ Kool Herc invented hip-hop at 1520 Sedgwick on August 11, 1973. Cultural memory is what survives the bulldozer.

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
| Cache hit latency | 11 ms |
| Hardware cost | $3,000 |

## Dual-Renderer Architecture

Two renderers, one data contract.

- **deck.gl (primary demo)**: Browser-based. PolygonLayer, GeoJsonLayer, ScatterplotLayer. Animated year scrubber, fly-to navigation, immigration flow toggle. Runs on any machine with a browser.
- **Bevy/Rust (native)**: GPU-native renderer on the `renderer-rust-v2` branch. Bevy 0.18.1 + wgpu. Real materials, shadows, higher fidelity. Runs natively on the GN100. Production path for scaling to 49K photos and full temporal animation.

Both renderers load from `data/landmarks-infrastructure.json` (bridges, stadiums, ghost buildings) and the 5 borough compact JSONs.

## Stack

- **Frontend**: deck.gl + MapLibre GL (year presets, fly-to buttons, draggable story cards)
- **Native renderer**: Bevy 0.18.1 + wgpu (Rust, renderer-rust-v2 branch)
- **Inference**: NVIDIA Nemotron-3 Nano 30B (A3B) on llama-server (llama.cpp, CUDA 12.8, cuBLAS, all 99 layers on GPU)
- **Orchestrator**: FastAPI on :30001 (biography RAG, caching, photo overlay)
- **Data**: 5 borough compacted JSONs, landmarks-infrastructure.json (bridges, stadiums, ghosts), demolished-landmarks.json (295 Wikidata pins), MARQUEE cultural content, Bronx archival photos, immigration flow data
- **Runtime**: Zero network dependencies. 128 GB unified memory. Everything on-device.

## Hardware

Acer GN100 / NVIDIA DGX Spark / GB10 Grace Blackwell Superchip / 128 GB unified LPDDR5X memory. Model weights (38 GB), building geometry (231 MB), orchestrator, and renderer share one address space with zero contention.

## Quick Start

```bash
python3 -m http.server 8080
# open http://localhost:8080/index.html
```

On the GN100, also start the inference backend:
```bash
# tmux session "llama"
llama-server -m /path/to/nemotron-30b-q8.gguf -ngl 99 --port 8090

# tmux session "orch"
cd src && uvicorn orchestrator.main:app --host 0.0.0.0 --port 30001
```

## Repo Structure

```
index.html                          -- deck.gl 3D map (all boroughs, ghost buildings, year scrubber, toggles)
data/                               -- compacted building geometry JSONs (5 boroughs)
data/landmarks-infrastructure.json  -- shared data: 8 bridges, 8 stadiums, 6 ghost buildings
data/demolished-landmarks.json      -- 295 Wikidata demolished landmark pins
cultural-content/                   -- archival photos, MARQUEE content, Bronx hip-hop assets
cultural-content/bronx/             -- Kool Herc, Bronx River party, South Bronx fire photos
cultural-content/oldnyc/            -- 750 NYPL Milstein photos + thumbnails
scripts/                            -- data pipelines, recompaction, export
src/                                -- FastAPI orchestrator, biography RAG, inference wiring
docs/                               -- hardware bible, pitch framings, operator briefs
handouts/                           -- demo script, pitch bible, infrastructure preview, recording runbook
```

## Demo Flow

1. Map opens at 2026 showing all five boroughs with bridges, stadiums, and landmark pins
2. Year presets (1948, 1970, 1973, 2001, 2026) or type any year -- animated scrub shows buildings appear/vanish
3. SEDGWICK button flies to Cross-Bronx corridor (green ghost buildings)
4. Drag 1948 to 1972: green tenements vanish section by section, grey expressway appears
5. Click any green building: hip-hop displacement story with 3 archival photos
6. WTC button flies to Lower Manhattan; Twin Towers rise at 1970, vanish past 2001
7. Click iconic buildings (Empire State, Chrysler, Grand Central) for MARQUEE story cards with NYPL photos
8. Immigration flow toggle animates migration patterns by origin country and decade
9. Building click triggers Nemotron biography (30 sec generation, 11 ms cache hit)

## Team

- Alex Wu -- lead, architecture, frontend, orchestrator, demo
- Carson Weeks -- Rust/Bevy native renderer, infrastructure
- James Burke -- data curation, cultural content, guided tour
- Marvens Destiné -- 3D visualization, point cloud pipeline

## Track

Cultural Impact | Bounty: Most Likely to Become a Unicorn

## Links

- GitHub: [TheApexWu/sixth-borough](https://github.com/TheApexWu/sixth-borough)
- Hardware: NVIDIA DGX Spark (Acer GN100)
- Model: NVIDIA Nemotron-3 Nano 30B (A3B variant)
