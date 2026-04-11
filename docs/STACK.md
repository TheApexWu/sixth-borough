# Sixth Borough — Pinned Stack

This document is the **single source of truth** for what tech we are using and why. If you're about to swap a piece of this stack, update this file first AND post in the team chat. Do not silently swap.

---

## The locked stack (as of Apr 11 ~15:30 ET)

| Layer | Pinned choice | Backup if it fails |
|---|---|---|
| Narration LLM | **NVIDIA Nemotron-3 Nano 30B (A3B variant)** from the NVIDIA Nemotron model family, Q8_K_XL GGUF, served via llama.cpp | Q4_K_M quantization (smaller, lower quality) |
| Narration runtime | **llama.cpp** built from source with `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="121"` for GB10's sm_121 | Ollama (slower path, used for stub fallback only) |
| Narration API | OpenAI-compatible `/v1/chat/completions` on **port `:8090`** (llama-server) wrapped by FastAPI orchestrator on **port `:30001`** for the real path; stub orchestrator on `:30000` as safety net | Same |
| Renderer (encounter mode, native, primary) | **Bevy 0.18.1** (Rust + wgpu) — Carson, on `renderer-rust` branch | **deck.gl + maplibre** browser path (James, on `feature/sketch-overlay`) as the breadth surface, also serves as fallback if native crashes |
| Renderer (lobby mode, web, breadth surface) | **deck.gl + maplibre** with year slider 1700-2026, 8 architectural eras, 750 NYPL Milstein photos georeferenced across 5 boroughs | Same |
| Renderer post-process | PS2-era constraint set: low-poly + vertex normals only + Sobel edge detection + palette quantization + fog falloff + affine warping | Same in both renderers |
| Ghost mesh format | **glb only** (low-poly Blender meshes, ~2K verts, vertex normals only). Single-format contract per `pointcloud-pipeline/README.md`. Loaded via Bevy's stock `SceneRoot(asset_server.load(GltfAssetLabel::Scene(0).from_asset(...)))` | Same |
| Migration flow primitive | **Sibling manifest pattern** at `assets/migration-flows/MANIFEST.json` (separate from ghost manifest). Cone with magnitude/spread/tilt/era encoding per `docs/MIGRATION_FLOW_PROTOTYPE.html` | Same |
| Asset authoring | **Blender** (Marvens) with vanilla glb export | — |
| Orchestrator | **Python (FastAPI)** with Pydantic models | — |
| Web build / WASM target | **Bevy → WASM via Trunk + Cloudflare Pages** (Carson, `renderer-rust` branch, `819a7f3` wasm + `54a431f` cicd) | Static deck.gl prototype as fallback |
| OS / runtime on box | DGX OS on the Acer Veriton GN100 | Provided, can't swap |

**Note on what was dropped (was previously pinned, no longer in the stack):**
- ~~`bevy_pointcloud` plugin~~ — dropped Apr 11 ~10:00 ET when Carson moved to glb-only single-format contract (`d6470aa`). Was the binding constraint pinning Bevy to 0.16; now removed.
- ~~PLY format~~ — dropped same time, glb is the single asset format.
- ~~OpenVAT vertex animation textures~~ — dropped when Marvens's deliverable shifted to "low-poly Blender ghosts" rather than animated point clouds. The ODESZA technique is reserved for post-hack v2.
- ~~Bevy 0.16~~ — Carson bumped to **0.18.1** in `renderer-rust` once the plugin constraint was gone.
- ~~Live VLM WebUI~~ — vision pipeline never started; not part of the submission.

---

## NVIDIA Nemotron-3 Nano 30B setup (the canonical path per NVIDIA's official playbook)

Source: NVIDIA `dgx-spark-playbooks/nvidia/nemotron/README.md`. Cached locally at `~/Desktop/spark-hack-cache/dgx-spark-playbooks/`.

**Why this matters for the rubric**: the Spark Hack judging breakdown awards **15 points for "The Stack"** based on whether the team uses a major NVIDIA library/tool — NeMo Models is explicitly listed as qualifying. Nemotron is NVIDIA's open model family and IS a NeMo model. The phrase **"NVIDIA Nemotron-3 Nano 30B from the NVIDIA Nemotron model family"** should appear in the demo video, the README, and any sponsor-facing pitch surface. Saying "Nemotron via llama.cpp" understates the rubric attribution. llama.cpp is the inference engine; **the model is the NVIDIA artifact**.

### Hardware
- DGX Spark with GB10 GPU
- ≥ 40 GB available GPU memory (model uses ~38 GB)
- ≥ 50 GB available storage

### Step 1 — verify prereqs
```bash
git --version
cmake --version    # need 3.14+
nvcc --version     # CUDA toolkit
```

### Step 2 — install Hugging Face CLI
```bash
python3 -m venv nemotron-venv
source nemotron-venv/bin/activate
pip install -U "huggingface_hub[cli]"
hf version
```

### Step 3 — clone llama.cpp
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

### Step 4 — build with CUDA targeting GB10's sm_121
```bash
mkdir build && cd build
cmake .. -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="121" -DLLAMA_CURL=OFF
make -j8
```
Build takes ~5–10 minutes.

### Step 5 — download the GGUF weights (~38 GB)
```bash
hf download unsloth/Nemotron-3-Nano-30B-A3B-GGUF \
  Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf \
  --local-dir ~/models/nemotron3-gguf
```
**This is the single biggest network risk on bad wifi. Start it FIRST after box checkout. Download is resumable.**

### Step 6 — start the server (use the idempotent launcher)
```bash
./scripts/start-llama-nano.sh
```

Or manually (note port `:8090`, not `:30000` — `:30000` is reserved for the stub orchestrator on the same box):
```bash
./bin/llama-server \
  --model ~/models/nemotron3-gguf/Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf \
  --host 0.0.0.0 \
  --port 8090 \
  --n-gpu-layers 99 \
  --ctx-size 8192 \
  --jinja \
  --threads 8
```

### Step 7 — test the API
```bash
curl http://localhost:30000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nemotron",
    "messages": [{"role": "user", "content": "Describe Mott Haven in 1978 in two sentences."}],
    "max_tokens": 100
  }'
```

### Memory failure recovery
If you hit "CUDA out of memory" despite being within capacity, it's the UMA buffer cache issue. Run:
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

### If 38 GB is too much / takes too long
Drop to Q4_K_M quantization:
```bash
hf download unsloth/Nemotron-3-Nano-30B-A3B-GGUF \
  Nemotron-3-Nano-30B-A3B-Q4_K_M.gguf \
  --local-dir ~/models/nemotron3-gguf
```
Smaller download, lower output quality, same API.

---

## Renderer asset pipeline (Bevy 0.18.1 + Blender, glb-only)

The native renderer is **Bevy 0.18.1** (Rust, built on wgpu). Bevy was chosen over raw wgpu because the built-in animation graph, the mature first-party glTF loader, the ECS, and the WASM target give Marvens's Blender work a clean integration path without scene-graph plumbing from scratch.

### Why Bevy 0.18.1 (not 0.16)

The earlier 0.16 pin was driven by `bevy_pointcloud` plugin compatibility. Once the team moved to **glb-only single-format ghosts** (Apr 11 ~10:00 ET, commit `d6470aa`), `bevy_pointcloud` was no longer needed and the version constraint was lifted. Carson bumped to 0.18.1 in `renderer-rust` (`819a7f3` wasm + `54a431f` cicd) to get the latest WASM target and webgl2 support for the Cloudflare Pages deploy path.

### Blender → Bevy gold path (glb-only)

1. **Marvens authors in Blender.** City geometry, ghost meshes for demolished buildings, migration cone primitives — all in Blender.
2. **Vanilla glb export** for everything. Material constraint: **vertex normals only**, low poly (~2K verts per ghost), vertex colors for era band encoding, no procedural materials, no PBR.
3. **Drop into `assets/ghosts/`** for ghost meshes or `assets/migration-flows/` for migration cones. Add an entry to the corresponding `MANIFEST.json` (sibling pattern — one manifest per asset family, not nested).
4. **Carson reads from `MANIFEST.json`** in the Bevy ECS startup system, spawns one entity per asset via `SceneRoot(asset_server.load(GltfAssetLabel::Scene(0).from_asset(...)))`, and the rendering systems handle the rest.

### Sibling manifest pattern (locked Apr 11)

Each asset family gets its own manifest, not a unified one:

```
assets/ghosts/MANIFEST.json              # low-poly Blender ghosts (Marvens v1)
assets/migration-flows/MANIFEST.json     # migration cones (Marvens v1, Cross-Bronx canonical)
```

The two loaders are independent in the Bevy ECS startup phase. New asset families add new sibling manifests, not nested keys. Reasoning: keeps the JSON schemas independent so Marvens's two deliverables don't block each other, and lets the migration-flows loader evolve separately as the data layer grows.

### Why this collaboration model works

Marvens never touches Rust. Carson never touches Blender. The contract between them is `pointcloud-pipeline/README.md` (despite the legacy directory name; the format is glb-only now). Marvens drops a new ghost into shared storage + bumps the relevant manifest, Carson pulls and the renderer ingests it on next launch.

---

## llama.cpp on the GN100 — gotchas

- The `-DCMAKE_CUDA_ARCHITECTURES="121"` flag is critical. The GB10 reports as sm_121. Other values won't compile correctly.
- `-DLLAMA_CURL=OFF` avoids a libcurl link error common on DGX OS.
- `--n-gpu-layers 99` means "all layers on GPU." Don't lower this unless you know the model isn't fitting.
- Context window can go up to 1M tokens (`--ctx-size 1048576`) but uses more memory. Default 8192 is fine for narration.
- The first inference call after startup is slow (~5 sec) as the model warms. Pre-warm before the demo.

---

## What we are NOT using (and why)

| Tech | Why not |
|---|---|
| GPT-4 / Claude / any cloud LLM API | **Zero points on the NVIDIA Stack score** per the rubric ("Merely calling GPT-4 via API gets 0 points here"). Local-only is the entire pitch. |
| NeMo Framework (the Python toolkit) | NeMo Framework's modern focus is speech/ASR/TTS — not the right tool for our LLM narration use case. The NVIDIA-recommended path for LLM inference on DGX Spark is llama.cpp serving NVIDIA Nemotron models, per their own playbook. We use the playbook path. **The model attribution to the NVIDIA Nemotron family still scores The Stack** — see the "NeMo Models" line in the rubric. |
| TensorRT-LLM | More setup overhead than llama.cpp for the same outcome in 38 hours |
| vLLM | Higher throughput than we need; llama.cpp's OpenAI API is enough |
| Fine-tuning | We have 38 hours. Pretrained inference only. |
| OpenClaw | Only relevant for the OpenClaw bounty (RTX 5090). Cultural Impact track does not need it. |
| Predictive ML / gentrification forecasting | Locked out by thesis (`docs/PRODUCT_WEDGES.md`): "we don't predict gentrification, we trace it from the receipts." Predictive overlays read as extraction theater to community-data audiences. |
| Vision pipeline (Live VLM WebUI / Ollama vision) | Was a stretch goal; never started; not part of submission. |

---

## Cultural events schema (the data layer that drives niche discovery)

The cultural intelligence layer is a static JSON file at `data/events-seed.json`. Hand-curated, **19 events** (Apr 11 ~14:50 ET, all 19 pre-baked through the real backend into `data/narration_cache.json` as venue-WiFi insurance). Schema:

```json
{
  "id": "bronx-1973-08-11-sedgwick",
  "coordinate": [40.8378, -73.9202],
  "start_year": 1973,
  "end_year": null,
  "niche_tags": ["hip-hop"],
  "title": "Kool Herc invents the breakbeat",
  "narration_seed": "August 11, 1973. Cindy Campbell's birthday party at 1520 Sedgwick Avenue rec room. Her brother Clive Campbell, DJ Kool Herc, isolates the percussion break of two records using two turntables. Hip-hop is born.",
  "era_visual_mode": "1970s-bronx-warm",
  "source_url": "https://en.wikipedia.org/wiki/1520_Sedgwick_Avenue",
  "importance_score": 100
}
```

**Field semantics:**
- `id`: stable string identifier (slug pattern: `borough-year-month-day-keyword` or `borough-year-keyword`)
- `coordinate`: `[lat, lng]` in WGS84. Approximate is fine for the demo, refine Sat morning.
- `start_year`, `end_year`: when the event/place is "active" on the time slider. `end_year: null` means "ongoing or instantaneous"
- `niche_tags`: array of niche identifiers — events with multiple tags appear under multiple filters
- `title`: short label (shown on the pin tooltip)
- `narration_seed`: the human-written hook that gets fed into Nemotron at runtime, with niche + era + nearby-events appended at inference time
- `era_visual_mode`: maps to a renderer post-process parameter set (palette + Sobel intensity + vignette warmth)
- `source_url`: provenance — what we cited
- `importance_score`: 0–100, used to prioritize pins when many overlap on the map at the same time

**Niche taxonomy (for the demo):**
- `hip-hop` — fully populated, ~25 events (the demo cinematic)
- `immigration` — placeholder, 2-3 events
- `demolished-theaters` — placeholder, 2 events
- `queer-history` — placeholder, 1-2 events
- `jazz` — placeholder, 1-2 events
- `salsa` — placeholder, 1-2 events

The placeholders prove the architecture handles other lenses without being the cinematic centerpiece.

---

## Niche-conditioned narration prompt template

When the user has a niche filter on and the time slider crosses an event's start_year, the orchestrator calls the Nemotron server with a prompt built from this template:

```
SYSTEM:
You are a cultural memory narrator. Your voice is grounded, specific, and
present-tense. You speak with the authority of someone who knows the {niche}
scene from the inside, not as a tourist or a textbook. Two to three sentences
per scene. No throat-clearing.

CONTEXT:
- Place: {neighborhood}, {borough}
- Year: {year}
- Era visual mode: {era_visual_mode}
- Active niche lens: {niche}
- Event: {title}
- Hook: {narration_seed}
- Recently active nearby events: {recent_nearby_titles}

USER:
Narrate this scene in 2-3 sentences for someone standing here right now,
filtered through the {niche} lens.
```

This template gives Nemotron enough structure that the niche voice stays consistent across scenes but enough flexibility that each narration feels alive. **Lock this template Friday night** and don't iterate on it during the build.

---

## Dependency age rule (announced at orientation Apr 10)

**Rule:** every open source dependency must be at least 2 weeks old as of Apr 10 2026. Cutoff date: **Mar 27 2026 or earlier.** NVIDIA / Nemotron stack is exempt per orientation guidance.

**Audit (completed Apr 10 evening):**

| Dependency | Created/Updated | Status |
|---|---|---|
| llama.cpp | Years old | ✅ Pass |
| Nemotron-3-Nano-30B-A3B base model | Dec 15 2025 (~4 months) | ✅ Pass (NVIDIA exempt anyway) |
| Nemotron-3-Nano GGUF Q8_K_XL (unsloth) | 4 months ago | ✅ Pass |
| Live VLM WebUI | Nov 4 2025 (~5 months) | ✅ Pass |
| Rust + wgpu | Years old | ✅ Pass |
| Bevy 0.18.1 | Released January 2026 (~3 months) | ✅ Pass |
| ~~`bevy_pointcloud`~~ | Dropped Apr 11 ~10:00 ET when team moved to glb-only (`d6470aa`) | n/a |
| ~~OpenVAT Blender addon~~ | Dropped Apr 11 ~14:00 ET when Marvens's deliverable shifted from animated point clouds to low-poly Blender ghosts | n/a |
| Blender (point cloud authoring) | 20+ years old | ✅ Pass |
| glTF / glb format | 2017 spec, years of tooling | ✅ Pass |
| AliceVision Meshroom (photogrammetry) | Years old | ✅ Pass |
| COLMAP (SfM/MVS) | Years old | ✅ Pass |
| Three.js (James's branch) | Years old | ✅ Pass |
| Ollama | Years old | ✅ Pass |
| GSAP | Years old | ✅ Pass |
| FastAPI | Years old | ✅ Pass |
| Hugging Face CLI | Years old | ✅ Pass |
| CUDA toolkit / nvcc | Years old | ✅ Pass |
| DGX Spark playbooks repo | Public for months | ✅ Pass |

**Mid-build rule:** if anyone wants to add a new dependency during the hackathon, the new dep must also be ≥2 weeks old. No "I just found this perfect new library" at midnight. Check the GitHub createdAt or HF upload date before installing.

---

## What gets said in the demo video (verbatim words to lock)

These words **must** appear in the recorded demo:

- "DGX Spark"
- "GB10 Grace Blackwell Superchip"
- "128 gigabytes of unified memory"
- **"NVIDIA Nemotron"** model family attribution (CRITICAL — see rubric note below)
- "running locally"
- "no internet connection at runtime"
- The unplug-cable moment with the line: "*Everything you're about to see runs on the box, with the cable on the floor, because computational ghosts need local hardware.*"

**Critical rubric note (Apr 11 ~15:30 ET pass)**: the phrase "Nemotron" alone does NOT lock the 15 NVIDIA Stack pts unambiguously. The rubric awards The Stack score on use of NVIDIA libraries/tools and explicitly lists **NeMo Models** as qualifying. Nemotron IS in the NeMo model family — but only if the team **names it as such**. The locked attribution phrase is:

> "NVIDIA Nemotron-3 Nano 30B from the NVIDIA Nemotron model family, running on NVIDIA DGX Spark hardware."

Or, slightly shorter for the demo postscript:

> "a 30-billion-parameter model from NVIDIA's Nemotron model family, running on this box."

Saying "Nemotron via llama.cpp" reads as "they're just using llama.cpp." Saying "from NVIDIA's Nemotron model family on NVIDIA DGX Spark" is what locks the rubric attribution.

If the recorded video does not contain these phrases, we lose 15 of the 30 NVIDIA Ecosystem points. Do not skip.

