# Sixth Borough

3D Manhattan time machine for NVIDIA Spark Hack NYC (Apr 10-12, 2026).

45,194 buildings morph across eras (1719-2026) via timeline slider. PS2 aesthetic. Story cards narrated by Nemotron 3 Nano on GB10 Blackwell.

This is an art project as much as a technical one. The PS2 rendering isn't retro nostalgia -- low-fidelity forces the viewer to fill in gaps with their own memory and imagination. High-fidelity 3D maps make people evaluate accuracy. We want provocation, not precision. The goal is the moment someone drags the slider from 1900 to 2026 and watches their neighborhood materialize while particles of human movement swirl around it, and a story card tells them who lived there before them.

Emotion Engine to Grace Blackwell. Custom silicon creates iconic aesthetics.

## Quick Start

```bash
python3 -m http.server 8090
# open http://localhost:8090
```

## What's Here

- `index.html` -- deck.gl 3D visualization with height-grow timeline animation, era coloring, story card scaffold
- `data/manhattan_compact.json` -- 45,194 Manhattan buildings (BIN, height meters, construction year, polygon coords). 16MB.
- `scripts/export_buildings.py` -- converts raw GeoJSON to compact format
- `scripts/mockup_3d.py` -- early pydeck prototype (superseded by index.html)

## Current State

- Manhattan buildings downloaded + validated (45,194, 100% height_roof, 98% construction_year)
- deck.gl 3D mockup with height-grow timeline slider + era coloring + story card scaffold
- Manhattan PLUTO downloaded (78MB, 42,600 lots with yearbuilt/landuse)
- 3 marquee story cards scaffolded (Empire State, Flatiron, One WTC) with placeholder text

## Data Sources

- **NYC Building Footprints** (dataset 5zhs-2jue): 45,194 Manhattan buildings with height_roof, construction_year, BIN
- **MapPLUTO** (dataset 64uk-42ks): 42,600 Manhattan lots with yearbuilt, landuse (not yet integrated)

Raw GeoJSON files (42MB + 78MB) are gitignored. Download from NYC Open Data if needed:
```
https://data.cityofnewyork.us/api/geospatial/5zhs-2jue?method=export&type=GeoJSON&$where=base_bbl%20like%20%271%25%27
https://data.cityofnewyork.us/api/geospatial/64uk-42ks?method=export&type=GeoJSON&$where=borough=%27MN%27
```

## Architecture

**Python prototype (current):** deck.gl PolygonLayer, MapLibre basemap, timeline slider, story cards.

**Hackathon target:** Carson ports to Rust/Bevy/wgpu with PS2 shaders. Fallback: Three.js with custom PS2 GLSL.

**GB10 flex:** Concurrent Vulkan rendering + Nemotron 3 Nano inference on 128GB unified memory. The key demo: rendering the city AND generating narrative simultaneously on the same chip, no cloud, no latency.

## Team

- **Alex Wu** -- data pipeline, LLM narration, product vision
- **Carson Weeks** -- Rust renderer, PS2 shaders, GPU particles
- **James Burke** -- UX/story cards, historical content, visual identity, slide deck

## Key Features

### Height-Grow Animation
Buildings lerp from 0 to full height over a 3-year window around construction_year. Creates a "growing city" effect as you drag the timeline.

### Era Coloring
8 eras from Colonial (pre-1800, dark brown) to Glass Tower (2000+, cyan).

### Story Cards
Click any building for info. 3 marquee sites (Empire State, Flatiron, One WTC) have placeholder narratives. Nemotron generates the rest at demo time.

### Timeline
Range 1719-2026. PLAY button auto-scrolls at ~20 years/second.

## Hackathon Build Targets

These are the heavier tasks we tackle together at the venue with the GB10 hardware.

### PS2 Post-Processing Shader
Color quantization to 15-bit palette. Scanline overlay. Optional CRT barrel distortion. Vertex snapping for that polygon wobble. The aesthetic makes people feel something instead of just seeing data. Implemented as either a wgpu/WGSL compute pass (Rust path) or a Three.js fullscreen GLSL post-process (fallback path).

### Nemotron Narrative Pipeline
Real-time story generation per building click. Nemotron 3 Nano (4B) running locally on the GB10 via Ollama. Streaming inference piped into the story card UI. Prompt includes building metadata (year, era, neighborhood, height) plus historical context for marquee sites. The rest of Manhattan gets generated narratives -- the LLM becomes the historian.

### Particle Flow System -- Human Movement
Immigration waves rendered as GPU particle density streams flowing through Manhattan streets. Not data-driven in 36 hours -- historically evocative illustrations triggered by timeline position:
- **Ellis Island era (1890-1920)**: particles flowing from Lower Manhattan outward. Italian, Jewish, Irish waves.
- **Great Migration (1910-1970)**: particles from the South flowing into Harlem and Upper Manhattan.
- **Post-1965 Immigration Act**: Chinatown densifies, Washington Heights fills with Dominican families.
- **Gentrification reversal (2000s+)**: particles reverse direction as neighborhoods flip.

Color-coded by origin. James picks the waves and the color language. Carson builds the GPU compute shader renderer. Alex wires the timeline triggers. The particle system is what turns a building map into a living city.

### Demolished Buildings Ghost Layer
Buildings that no longer exist rendered as translucent wireframe at their original footprint. They appear as you scroll back in time and fade as the timeline passes their demolition date. The original Penn Station materializing and then vanishing is the kind of moment that wins Cultural Impact.

### Slide Deck + Demo Narrative
James locks the presentation Saturday night (he leaves Sunday). The opener script, the demo walkthrough, the closing pitch. This gets designed alongside the build, not after.

## GB10 Notes

- 128GB unified LPDDR5X. CPU ptr = GPU ptr. 273 GB/s bandwidth.
- Stock Vulkan driver may be broken. Fix: 580.105.08+, install libnvidia-gl-580.
- CUDA 13.0 + Vulkan concurrent. DON'T use CUDA 13.2 compat packages.
- DGX OS = Ubuntu 24.04.
- Nemotron 3 Nano: `ollama pull nemotron-3-nano:4b` (2.8GB, 73 tok/s on GB10)
- Build llama.cpp with `-DCMAKE_CUDA_ARCHITECTURES="121"` for GB10 (sm_121, not sm_120).

## Sponsor Alignment

NVIDIA: GB10, CUDA, Nemotron, TensorRT, Vulkan, NV-Embed.
Acer: GN100 dev machine + prize.
Antler: co-hosting. Face-time value.

Track 3: **Cultural Impact** -- "preserving neighborhood history." Exact fit.
