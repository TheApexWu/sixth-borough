# Sixth Borough

Cultural memory infrastructure for New York City, running entirely on local hardware.

## What It Does

A 3D time machine for every building in NYC. 1,082,831 structures across all five boroughs, extruded to real LiDAR roof heights, with a year scrubber from 1700 to 2026. Click any building and a 30B language model generates a biography from public NYC datasets. No cloud, no internet at runtime.

Ghost buildings remember what the city demolished: the Twin Towers rise in 1970 and vanish in 2001, Penn Station disappears in 1963, 117 Cross-Bronx tenements collapse year by year as Robert Moses displaces 60,000 people. 750 archival photos from the NYPL Milstein Division are pinned to the map. Immigration flows animate across centuries.

## Architecture

Two renderers consuming one shared data spine (building polygons, landmarks, ghost manifests, cultural content).

**Browser demo** (`feature/sketch-overlay`) -- deck.gl + MapLibre in a single `index.html`. Extruded polygons on a flat map plane, time-gated construction/demolition, immigration particle simulation, archival photo pins, Sobel sketch overlay. Runs on any laptop. This is the proof of concept.

**Native renderer** (`renderer-rust-v2`) -- Bevy 0.18.1 + wgpu in Rust. Real 3D scene with lighting and shadows. Demolished buildings loaded as artist-authored .glb meshes via ECS manifest system. PS2-era post-process as GPU shaders. Shares 128 GB unified memory with a 30B language model on NVIDIA's DGX Spark. This is the production target -- scaffolding and asset pipeline built, pending full asset integration.

## Numbers

| | |
|---|---|
| Buildings | 1,082,831 |
| Ghost structures | 117 Cross-Bronx + WTC + Penn Station + Singer Building |
| Archival photos | 750 (NYPL Milstein Division) |
| Bridges / Stadiums | 8 / 8 (3 ghost) |
| Demolished landmarks | 295 (Wikidata) |
| Language model | NVIDIA Nemotron-3 Nano 30B |
| Inference | 29 tok/sec on DGX Spark |
| Hardware | NVIDIA DGX Spark, 128 GB unified memory |

## Quick Start

```bash
python3 -m http.server 8080
# open http://localhost:8080/index.html
```

## Stack

- deck.gl 9.1.4 + MapLibre GL 3.6.2 + GSAP 3.12.5 (browser)
- Bevy 0.18.1 + wgpu (native, Rust)
- NVIDIA Nemotron-3 Nano 30B via llama.cpp
- FastAPI orchestrator (biography RAG, caching)
- Acer GN100 / NVIDIA DGX Spark / GB10 Grace Blackwell

Built at Spark Hack Series NYC, Apr 2026. Cultural Impact track.
