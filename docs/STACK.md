# Sixth Borough — Pinned Stack

This document is the **single source of truth** for what tech we are using and why. If you're about to swap a piece of this stack, update this file first AND post in the team chat. Do not silently swap.

---

## The decision (Friday night, lock by midnight)

| Layer | Pinned choice | Backup if it fails |
|---|---|---|
| Narration LLM | **Nemotron-3-Nano-30B-A3B** (Q8 GGUF) via **llama.cpp** | Q4_K_M quantization, or Ollama with `nemotron-mini` (4B) |
| Narration runtime | **llama.cpp** built from source with `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="121"` | Ollama (slower but easier) |
| Narration API | OpenAI-compatible `/v1/chat/completions` on port `:30000` | Same |
| Vision model (optional) | **Live VLM WebUI** + Ollama backend (Gemma 3 or Llama Vision) | Drop the vision pipeline entirely |
| Renderer | **Rust + wgpu** (Carson) | **WebGL + Three.js** sketch-overlay branch (James) |
| Renderer post-process | Sobel + vignette + palette quantization | Same in both paths |
| Orchestrator | Python (FastAPI) or Node | Either works |
| OS / runtime on box | DGX OS on the Acer Veriton GN100 | Provided, can't swap |

---

## Nemotron-3-Nano setup (the canonical path per NVIDIA's official playbook)

Source: NVIDIA `dgx-spark-playbooks/nvidia/nemotron/README.md`. Cached locally at `~/Desktop/spark-hack-cache/dgx-spark-playbooks/`.

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

### Step 6 — start the server
```bash
./bin/llama-server \
  --model ~/models/nemotron3-gguf/Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf \
  --host 0.0.0.0 \
  --port 30000 \
  --n-gpu-layers 99 \
  --ctx-size 8192 \
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

## Live VLM WebUI setup (optional vision pipeline)

Source: NVIDIA `dgx-spark-playbooks/nvidia/live-vlm-webui/README.md`. Cached locally.

### What it gives us
- Real-time WebRTC video streaming to a VLM backend
- OpenAI-compatible API
- Web UI at `https://<SPARK_IP>:8090`
- Backends: **Ollama** (recommended), vLLM, SGLang, NIM, or cloud APIs (we will use Ollama)

### Why we'd use it
The vision pipeline lets the narration model "see" the rendered scene. Instead of narrating from a hardcoded era description, the system can take a screenshot of the renderer output, ask the VLM "describe this scene," then feed that description into the Nemotron narration prompt for grounding. **This is a +10 Frontier Creativity move** ("vision models reading the rendered map") if we have time.

### Setup
1. Install Ollama on the Spark (per `nvidia/ollama/` playbook)
2. Pull a vision model: `ollama pull gemma3:vision` or `ollama pull llama3.2-vision`
3. Install Live VLM WebUI via pip
4. Start it pointing at Ollama on the box
5. Access at `https://localhost:8090`

### Commit decision
**Skip this entirely if Nemotron narration isn't running by Sat noon.** Vision is a stretch goal, not a core feature. Don't let it distract from the narration loop.

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
| GPT-4 / Claude / any cloud LLM API | **Zero points on the NVIDIA Stack score.** Local-only is the entire pitch. |
| NeMo Framework (the Python toolkit) | NeMo's modern focus is speech/ASR/TTS — not the right tool for our LLM narration use case. The NVIDIA-recommended path for LLM inference on DGX Spark is llama.cpp, per their own playbook. We use the playbook path. |
| TensorRT-LLM | More setup overhead than llama.cpp for the same outcome in 38 hours |
| vLLM | Higher throughput than we need; llama.cpp's OpenAI API is enough |
| Fine-tuning | We have 38 hours. Pretrained inference only. |
| OpenClaw | Only relevant for the OpenClaw bounty (RTX 5090). Cultural Impact track does not need it. |

---

## Cultural events schema (the data layer that drives niche discovery)

The cultural intelligence layer is a static JSON file at `data/events-bronx-hiphop-seed.json` (for the demo). Hand-curated, ~30 events. Schema:

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
- "Nemotron-3-Nano"
- "running locally"
- "no internet connection at runtime"
- The unplug-cable moment with the line: "*Everything you're about to see runs on the box, with the cable on the floor, because computational ghosts need local hardware.*"

If the recorded video does not contain these phrases, we lose 15 of the 30 NVIDIA Ecosystem points. Do not skip.

