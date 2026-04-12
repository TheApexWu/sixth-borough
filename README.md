# Sixth Borough

NYC's cultural memory infrastructure, localized in one box.

## What It Does

3D map of 1,082,831 buildings across all five boroughs. Temporal slider spans 1700-2026 -- drag it and watch the city grow. Click any building for an AI-generated biography: who built it, who lived there, what happened. Ghost buildings (demolished structures like the original Penn Station and the Twin Towers) reappear as you scroll back in time. 750 archival photos from the NYPL overlay the map at their original locations.

## Key Numbers

| Metric | Value |
|--------|-------|
| Buildings rendered | 1,082,831 |
| Geometry data | 231 MB |
| Archival photos (NYPL) | 750 |
| Demolished landmarks | 295 |
| Inference speed | 29 tok/sec |
| Cache hit latency | 11 ms |
| Hardware cost | $3,000 |

## Stack

- **Frontend**: deck.gl + MapLibre GL (PolygonLayer, GeoJsonLayer, borough boundaries, lazy-loading)
- **Inference**: NVIDIA Nemotron-3 Nano 30B on llama-server (llama.cpp, CUDA, sm_121)
- **Orchestrator**: FastAPI (biography generation, caching, photo overlay)
- **Runtime**: Zero network dependencies. Everything runs on-device.

## Hardware

Acer GN100 / NVIDIA DGX Spark / GB10 Grace Blackwell Superchip / 128 GB unified LPDDR5X memory.

## Quick Start

```bash
python3 -m http.server 8090
# open http://localhost:8090
```

## Repo Structure

```
index.html            -- deck.gl 3D visualization (all 5 boroughs)
data/                 -- compacted building geometry JSONs
cultural-content/     -- biography cache, archival photo metadata
scripts/              -- data pipelines, export, curation
src/                  -- orchestrator, inference wiring
docs/                 -- hardware bible, operator briefs
handouts/             -- demo teleprompter, recording runbook
```

## Team

- Alex Wu
- Carson Weeks
- James Burke
- Marvens Destine

## Track

Cultural Impact

## Links

GitHub: [TheApexWu/sixth-borough](https://github.com/TheApexWu/sixth-borough)
