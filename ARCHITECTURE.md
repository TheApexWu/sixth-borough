# Sixth Borough — Architecture

## System diagram

```
                    ┌─────────────────────────────────────────────────────┐
                    │       ACER VERITON GN100 (DGX SPARK / GB10)         │
                    │       128 GB unified memory · Blackwell GPU         │
                    │       sm_121 CUDA arch · runs entirely offline      │
                    └─────────────────────────────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 │                                 │
        ▼                                 ▼                                 ▼
┌──────────────────┐          ┌──────────────────┐               ┌──────────────────┐
│  RUST + wgpu     │          │  llama.cpp       │               │  Live VLM WebUI  │
│  RENDERER        │          │  NARRATION       │               │  VISION (opt)    │
│                  │          │  SERVER          │               │                  │
│  PS2 post-proc:  │  scene   │                  │  caption      │  Ollama backend  │
│  - Sobel edges   │  bytes   │  Nemotron-3-Nano │  request      │  Gemma 3 / Llama │
│  - Vignette      │ ───────► │  30B-A3B Q8 GGUF │ ◄──────────── │  Vision          │
│  - Palette quant │          │                  │               │                  │
│  - Era cutscenes │          │  :30000          │               │  :8090           │
│                  │          │  OpenAI API      │               │  WebRTC stream   │
└──────────────────┘          └──────────────────┘               └──────────────────┘
        ▲                                 ▲                                 ▲
        │                                 │                                 │
        └─────────────────────┬───────────┴─────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  ORCHESTRATOR    │
                    │  (Python/Node)   │
                    │                  │
                    │  - Loads era     │
                    │  - Drives tour   │
                    │  - Routes calls  │
                    │  - Caches state  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   USER (browser  │
                    │   on the box)    │
                    └──────────────────┘
```

## Data sources (all cached locally before code freeze)

- **NYC Open Data** — historical landmark records, zoning history, neighborhood boundaries
  - Cached at `assets/nyc-data/` (gitignored, downloaded once)
- **Wikimedia Commons** — historical photos of NYC neighborhoods by era
  - 24 photos already in James's `feature/sketch-overlay` branch
  - Cached at `assets/photos/` (gitignored)
- **Era metadata** — hand-curated by team, lives in `src/data/eras.json`

## Network topology

**At runtime: NONE.** The system is designed to run with the ethernet cable unplugged. The unplug-cable demo is the entire pitch — if anything in the system requires network at runtime, it goes in the trash.

**During build:** model weights and dataset assets are downloaded once, then cached. Once the box is set up, the cable comes out.

## Memory budget on the GN100 (128 GB unified)

| Component | Approximate footprint |
|---|---|
| Nemotron-3-Nano-30B-A3B Q8 GGUF | ~38 GB |
| Live VLM (Gemma 3 / Llama Vision via Ollama) | ~10 GB |
| Renderer scene + framebuffer | ~2 GB |
| Orchestrator + Python runtime | ~1 GB |
| OS + buffer cache | ~10 GB |
| **Total estimated** | **~61 GB** |
| **Headroom** | **~67 GB** |

If we hit OOM despite the headroom, the DGX Spark UMA caveat applies — flush the buffer cache:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

If we need to drop the VLM, the system still works narration-only.

## Failure modes & fallbacks

| Failure | Detection | Fallback |
|---|---|---|
| Rust/wgpu renderer doesn't compile or crashes | By Sat 4 PM Progress Checkin | Pivot to James's WebGL Sobel pipeline as primary visual |
| Nemotron-3-Nano-30B doesn't fit in memory or runs too slow | Test Friday night | Drop to Q4_K_M quantization (smaller download, lower quality) |
| Nemotron download (38 GB) fails on venue wifi | Watch download progress | Use phone hotspot, or fall back to a smaller Ollama model already on disk |
| Live VLM doesn't run alongside Nemotron | Memory check | Drop the vision pipeline entirely, narration-only is still a complete pitch |
| Demo crashes on stage | Rehearsal | Have a 30-second pre-recorded clip of the working loop ready as backup |

## The 4-pillar map (where each pillar lives in the architecture)

| Pillar | Where it lives | Components |
|---|---|---|
| **Time Machine** | Orchestrator + renderer | Year slider UI, era query against the events table, era-conditioned renderer state |
| **PS2 Memory Aesthetic** | Renderer | Sobel + vignette + palette quant post-process, era_visual_mode parameter map |
| **Cultural Intelligence** | Data layer + narration | `data/events-bronx-hiphop-seed.json`, niche-conditioned Nemotron prompt template |
| **Niche Discovery** | Orchestrator UI | Filter toggle list, niche → events query, niche → narration voice routing |

The four pillars are not parallel features. They are one product loop where:
1. The Time Machine is the navigation primitive (how the user moves)
2. The PS2 Aesthetic is the substrate experience (how the user feels the movement)
3. The Cultural Intelligence is the data depth (what makes movement meaningful)
4. Niche Discovery is the access mechanism (how the user controls information overload)

Removing any one of the four breaks the product. Adding a fifth would dilute the identity. Stop at four.

---

## Cultural events table (the data layer)

Events are stored as a JSON array in `data/events-bronx-hiphop-seed.json`. See `docs/STACK.md` for the field-level schema. The orchestrator loads the file at startup, indexes events by year and by niche tag, and serves queries:

- **Time slider drag → era events:** "give me all events where `start_year ≤ current_year ≤ (end_year ?? infinity)` AND `current_niche` is in `niche_tags`"
- **Pin click → narration:** "give me the narration_seed for event X, build a Nemotron prompt with the niche + era + nearby events context, return the generated text"

For the demo, ~30 hand-curated events. For the universal architecture pitch, "the data layer scales next via Cartewei or live NYC Open Data ingestion" (deferred work).

---

## Niche filter UI flow

```
USER opens Sixth Borough
       │
       ▼
Default state: time slider at 2026, no niche filter, modern view
       │
       │ user drags slider 2026 → 1973
       ▼
Renderer morphs through era_visual_modes (PS2 palette/post-process changes)
       │
       │ user clicks "Hip-hop heads" toggle in niche filter list
       ▼
Orchestrator queries events: hip-hop tag, year window 1965-1985
       │
       ▼
Pins appear/disappear on map as slider passes their start_years
       │
       │ user drags slider forward to 1973
       ▼
1520 Sedgwick pin lights up
       │
       │ user clicks the pin
       ▼
Orchestrator builds prompt:
  niche=hip-hop, year=1973, place=Bronx, event=Kool Herc breakbeat,
  narration_seed=..., recent_nearby=[...]
       │
       ▼
POST :30000/v1/chat/completions
       │
       ▼
Nemotron-3-Nano returns 2-3 sentence narration
       │
       ▼
Orchestrator overlays narration text on the renderer scene
       │
       │ user toggles "Hip-hop" off, "Immigration flow" on
       ▼
Same map, same year, totally different pin set (immigration events)
```

The toggle is the critical UX element. **Niche switching is what proves the architecture works on multiple lenses.** Even if only one niche is fully populated, the toggle has to feel real.

---

## Why this architecture wins points

- **Tech Execution (30 pts):** real systems work, multiple components, complete data flow, not a static dashboard
- **NVIDIA Stack (15 pts):** uses Nemotron-3-Nano (NVIDIA model) via the official NVIDIA-recommended path (llama.cpp on GB10 with sm_121)
- **Spark Story (15 pts):** unified memory + local-only inference + the unplug-cable demo
- **Insight (10 pts):** specific neighborhood + specific era + specific cultural artifact, not abstract gestures
- **Usability (10 pts):** a curator could lead a class through this tomorrow
- **Creativity (10 pts):** PS2-era visuals on Blackwell silicon is genuinely novel
- **Performance (10 pts):** cite frame rate + token/sec on a slide

