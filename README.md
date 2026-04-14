# Sixth Borough

Cultural memory infrastructure for New York City, running entirely on local hardware.

## What It Does

A 3D time machine for every building in NYC. 1,082,831 structures across all five boroughs, extruded to real LiDAR roof heights, with a year scrubber from 1700 to 2026. Click any building and a 30B language model generates a biography from public NYC datasets. No cloud, no internet at runtime.

Ghost buildings remember what the city demolished: the Twin Towers rise in 1970 and vanish in 2001, Penn Station disappears in 1963, 117 Cross-Bronx tenements collapse year by year as Robert Moses displaces 60,000 people. 750 archival photos from the NYPL Milstein Division are pinned to the map. Immigration flows animate across centuries.

## Architecture

Two renderers consuming one shared data spine (building polygons, landmarks, ghost manifests, cultural content).

**Native renderer (this branch)** -- Bevy 0.18.1 + wgpu in Rust. Real 3D scene with directional lighting and shadows. Demolished buildings loaded as artist-authored .glb meshes via an ECS manifest system (each ghost is a Bevy entity with coordinate, era window, and niche tags). PS2-era post-process as GPU shaders. Shares 128 GB unified memory with a 30B language model on the DGX Spark. Includes a FastAPI orchestrator for biography generation via NVIDIA Nemotron-3 Nano 30B.

**Browser demo ([feature/sketch-overlay](https://github.com/TheApexWu/sixth-borough/tree/feature/sketch-overlay))** -- deck.gl + MapLibre in a single `index.html`. Extruded polygons on a flat map, 8 era color bands, immigration particle simulation, NYPL photo pins, Sobel sketch overlay. Runs on any laptop with a browser.

## Numbers

| | |
|---|---|
| Buildings | 1,082,831 |
| Ghost structures | 117 Cross-Bronx + WTC + Penn Station + Singer Building |
| Archival photos | 750 (NYPL Milstein Division) |
| Bridges / Stadiums | 8 / 8 (3 ghost) |
| Demolished landmarks | 295 (Wikidata) |
| Language model | NVIDIA Nemotron-3 Nano 30B (A3B, Q8_K_XL) |
| Inference | 29 tok/sec sustained on DGX Spark |
| Hardware | NVIDIA DGX Spark, 128 GB unified memory |

## Quick Start

```bash
# Browser demo (any machine)
git checkout feature/sketch-overlay
python3 -m http.server 8080
# open http://localhost:8080/index.html

# Native renderer + orchestrator (requires Rust toolchain)
cd renderer-rust && cargo run

# Orchestrator in stub mode (any laptop, no GPU)
pip install -r requirements.txt
./scripts/dev-stub.sh
# live on http://localhost:30000

# On the DGX Spark (real inference)
./scripts/start-llama-nano.sh
NARRATION_MODE=real LLAMA_SERVER_URL=http://127.0.0.1:8090 \
  python -m uvicorn src.orchestrator.main:app --host 0.0.0.0 --port 30001
```

## Stack

- Bevy 0.18.1 + wgpu (native renderer, Rust)
- deck.gl 9.1.4 + MapLibre GL 3.6.2 (browser demo)
- NVIDIA Nemotron-3 Nano 30B via llama.cpp
- FastAPI orchestrator (biography RAG, caching)
- Acer GN100 / NVIDIA DGX Spark / GB10 Grace Blackwell

Built at Spark Hack Series NYC, Apr 2026. Cultural Impact track winner + Most Likely to Become a Unicorn bounty.

Special thanks to [Carson Weeks](https://github.com/Cheatcodesam) (Rust renderer), [James Burke](https://github.com/lifesized) (cultural content), and Marvens Destine (hackathon networking).
