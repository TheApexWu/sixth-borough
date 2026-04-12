# Sixth Borough

NYC's cultural memory infrastructure, localized in one box.

## What It Does

3D map of 1,082,831 buildings across all five boroughs of New York City, extruded to real LiDAR roof heights, with an animated year scrubber from 1700 to 2026. Click any building and a 30-billion-parameter NVIDIA Nemotron model generates a forensic biography from four public NYC datasets. No cloud. No internet at runtime.

Ghost buildings (Twin Towers, Penn Station, Singer Building) reappear and vanish at their real construction and demolition years. 8 major bridges and 8 stadiums (5 active, 3 ghost) are rendered as landmark infrastructure from a shared data layer. 295 demolished landmarks from Wikidata are pinned across the city. 117 demolished tenements along the Cross-Bronx Expressway corridor glow green and disappear as you drag 1948 to 1972, replaced by the expressway road surface. 750 archival photos from the NYPL Milstein Division overlay the map at their original locations. An immigration flow toggle animates historical migration patterns by origin country and decade.

The demo traces one chain: Robert Moses displaced 60,000 South Bronx families onto Sedgwick Avenue. The density created the rec room party scene. DJ Kool Herc invented hip-hop at 1520 Sedgwick on August 11, 1973. Cultural memory is what survives the bulldozer.

## Key Numbers

| Metric | Value |
|--------|-------|
| Buildings rendered | 1,082,831 |
| Geometry data | 231 MB (recompacted) |
| Bridges | 8 (Brooklyn, Manhattan, Williamsburg, Queensboro, GW, Verrazano, Throgs Neck, Triboro) |
| Stadiums | 8 (5 active + 3 ghost: Old Yankee, Polo Grounds, Ebbets Field) |
| Archival photos (NYPL) | 750 |
| Demolished landmarks (Wikidata) | 295 |
| Cross-Bronx ghost buildings | 117 |
| Model | Nemotron-3 Nano 30B (Q8_K_XL) |
| Inference speed | 29 tok/sec |
| Cache hit latency | 11 ms |
| Hardware cost | $3,000 |

## Stack

- **Frontend**: deck.gl + MapLibre GL (PolygonLayer, GeoJsonLayer, borough boundaries, year presets, fly-to navigation)
- **Inference**: NVIDIA Nemotron-3 Nano 30B (A3B) on llama-server (llama.cpp, CUDA 12.8, cuBLAS, all 99 layers on GPU)
- **Orchestrator**: FastAPI on :30001 (biography generation, caching, photo overlay)
- **Data**: 5 borough compacted JSONs, ghost buildings (WTC + Cross-Bronx), landmarks-infrastructure.json (bridges, stadiums), demolished-landmarks.json (295 Wikidata pins), immigration flow data, MARQUEE cultural content, Bronx archival photos
- **Runtime**: Zero network dependencies. 128 GB unified memory. Everything runs on-device.

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
index.html                          -- deck.gl 3D visualization (all boroughs, ghost buildings, year scrubber, immigration toggle)
data/                               -- compacted building geometry JSONs (5 boroughs)
data/landmarks-infrastructure.json  -- 8 bridges, 8 stadiums (3 ghost), 6 ghost buildings
data/demolished-landmarks.json      -- 295 Wikidata demolished landmark pins
cultural-content/                   -- archival photos, MARQUEE content, Bronx hip-hop assets
cultural-content/immigration/       -- immigration flow data by origin country and decade
cultural-content/bronx/             -- Kool Herc, Bronx River party, South Bronx fire photos
scripts/                            -- data pipelines, recompaction, export
src/                                -- FastAPI orchestrator, biography RAG, inference wiring
docs/                               -- hardware bible, pitch framings, operator briefs
handouts/                           -- demo script, pitch bible, recording runbook
```

## Demo Flow

1. Map opens at 2026 showing all five boroughs with 8 bridges and 8 stadiums rendered
2. Year presets: click 1948, 1970, 1973, 2001, 2026 -- buildings and landmarks appear/vanish
3. SEDGWICK button flies to Cross-Bronx Expressway corridor (green ghost buildings)
4. Drag the year scrubber 1948 to 1972: green tenements vanish, grey expressway appears
5. Click any green building: hip-hop displacement story + archival photos
6. WTC button flies to Lower Manhattan; towers rise at 1970, vanish past 2001
7. Immigration flow toggle animates migration patterns by origin country and decade
8. Building click triggers Nemotron biography (30 sec generation, 11 ms cache hit)

## Team

- Alex Wu (lead, architecture, frontend, orchestrator)
- Carson Weeks (Rust/Bevy renderer, infrastructure)
- James Burke (data curation, cultural content, guided tour)
- Marvens Destiné (3D visualization, point cloud pipeline)

## Track

Cultural Impact | Bounty: Most Likely to Become a Unicorn

## Links

- GitHub: [TheApexWu/sixth-borough](https://github.com/TheApexWu/sixth-borough)
- Hardware: NVIDIA DGX Spark (Acer GN100)
- Model: NVIDIA Nemotron-3 Nano 30B (A3B variant)
