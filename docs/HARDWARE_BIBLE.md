# Sixth Borough — Hardware & Model Bible (personal cheat sheet)

Your reference for every "wait what is actually running on what" question. Read top to bottom once, then scan only the section you need.

---

## 1. The Box (one sentence per layer)

| Layer | What it is | What to say out loud |
|---|---|---|
| Chassis | Acer Veriton GN100 | "Acer Veriton GN100" |
| Platform | NVIDIA DGX Spark | "DGX Spark" |
| Chip | NVIDIA GB10 Grace Blackwell Superchip | "GB10 Grace Blackwell Superchip" |
| Memory | 128 GB unified (Grace CPU and Blackwell GPU share one address space, no PCIe copy) | "128 gigabytes of unified memory" |
| CUDA arch | sm_121 (the reason `-DCMAKE_CUDA_ARCHITECTURES="121"` is in the llama.cpp build) | (build detail, not pitch) |
| OS | DGX OS (Ubuntu derivative NVIDIA ships with the box) | "DGX OS" |
| Network at runtime | **Ethernet cable on the floor** | "running locally, no internet connection" |

**The Spark Story (15 rubric pts)**: "The 30 billion parameter model, the 262 megabytes of NYC building polygons, the orchestrator, the renderer scene, and the open-data corpus all share one address space. On a non-unified architecture you would copy tensors across PCIe every inference call. On GB10 the Nemotron weights and the building data and the renderer state are literally the same memory."

---

## 2. The Model

| Field | Value |
|---|---|
| Family | **NVIDIA Nemotron** (NeMo Models category in the rubric) |
| Specific model | **Nemotron-3 Nano 30B (A3B variant)** |
| Quantization | Q8_K_XL GGUF (unsloth packaging) |
| File on disk | `~/models/nemotron3-gguf/Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf` (~38 GB) |
| Resident | All 99 layers on GPU (`-ngl 99`), full offload, no swap |
| Context | 8192 tokens (`-c 8192`) — fine for narration, can go to 1M if needed |
| Sustained throughput | ~29 tokens/sec on warm load |
| First-call latency | ~5 sec cold, then ~5-30 sec per biography depending on output length |
| Reasoning model gotcha | Puts CoT in `reasoning_content` not `content`. Fixed three ways: `/no_think` in system prompt, `chat_template_kwargs.thinking=False`, and explicit "begin with `## 1.`" instruction |

**The Stack score (15 rubric pts) attribution phrase, locked**:
> "NVIDIA Nemotron-3 Nano 30B from the NVIDIA Nemotron model family, running on NVIDIA DGX Spark hardware."

Saying "Nemotron via llama.cpp" understates the rubric. llama.cpp is the **engine**. The **model** is the NVIDIA artifact. Always name the model family.

---

## 3. The Runtime (llama.cpp, not Ollama)

```
~/llama.cpp/build/bin/llama-server
  -m ~/models/nemotron3-gguf/Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf
  --host 127.0.0.1
  --port 8090
  -ngl 99       # all layers on GPU
  -c 8192       # context window
  --jinja       # chat template support
```

- Built from source on the box with `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="121"` for sm_121
- Speaks the **OpenAI Chat Completions API** at `http://127.0.0.1:8090/v1/chat/completions`
- Lives in tmux session `llama` (`tmux attach -t llama`)
- Idempotent restart: `~/sixth-borough/scripts/start-llama-nano.sh`
- **Ollama is not used.** Anywhere in the docs that says "Ollama" is stale.

---

## 4. The Orchestrator (FastAPI, two endpoints, two ports)

```
src/orchestrator/main.py
  ├── POST /narrate    → src/orchestrator/narration_real.py → llama-server :8090
  ├── POST /biography  → src/biography/router.py → lookup + synthesize → llama-server :8090
  ├── GET  /events     → static read of data/events-seed.json
  ├── GET  /niches     → static taxonomy
  └── GET  /health     → which backend is wired
```

| Process | Port | Mode | tmux | Purpose |
|---|---|---|---|---|
| Real orchestrator | `:30001` | `NARRATION_MODE=real` | `orch` | The demo path |
| Stub orchestrator | `:30000` | templated narration, no LLM | `stub` | Safety net (could be killed post-submission, kept for paranoia) |

Cache layer in `src/biography/router.py`:
- `data/biography_cache.json` keyed by `bin:`, `event:`, or `latlon:`
- Cache hit returns in **~11 ms**
- Cache miss runs the full Nemotron pipeline and writes back
- Pre-baked at code-freeze for venue WiFi insurance

---

## 5. The Data (everything is on disk, nothing fetched at runtime)

| Source | File | Size | What it provides |
|---|---|---|---|
| NYC Building Footprints `5zhs-2jue` | `data/{manhattan,bronx,brooklyn,queens,staten}_compact.json` | 262 MB total, ~1.05M buildings | LiDAR roof heights + construction year + BIN + polygon, schema `{p,h,y,b}` |
| NYPL Milstein Picture Collection | `cultural-content/oldnyc/index.json` | 750 photos × 5 boroughs | Georeferenced archival photos 1900-1956 |
| Wikidata demolished landmarks | `data/demolished-landmarks.json` | 295 records | Built/demolished years + lat/lon |
| Hand-curated cultural events | `data/events-seed.json` | 19 events | Cross-Bronx → Kool Herc chain |
| NYC Borough Boundaries `gthc-hcne` | `data/borough_boundaries.geojson` | 3.2 MB, 5 polygons | Red outline overlay |
| Pre-baked narrations | `data/narration_cache.json` | 19 events | `/narrate` venue-WiFi insurance |
| Pre-baked biographies | `data/biography_cache.json` | growing | `/biography` warm cache |

The join is BIN-first, then haversine lat/lon proximity. No embeddings, no vector DB, no LangChain. All in `src/biography/lookup.py`.

---

## 6. The Click Flow (what happens when a judge clicks a building)

```
1. User clicks polygon in deck.gl + maplibre browser
2. Browser POSTs http://localhost:30001/biography {"bin": "2008286"}
3. router.py checks data/biography_cache.json — if hit, return in 11 ms
4. Cache miss path:
   a. lookup.py.assemble_record() resolves BIN against bronx_compact.json
      → height_m, year_built, polygon
   b. haversine within 200 m → 8 nearest NYPL Milstein photos
   c. haversine within 500 m → nearby cultural events
   d. haversine within 1 km → demolished Wikidata landmarks
   e. returns flat structured dict + dataset citations
5. synthesize.py builds the prompt:
   - SYSTEM: forensic historian, no speculation, /no_think directive
   - USER: structured record verbatim with field names preserved
6. POST :8090/v1/chat/completions with chat_template_kwargs.thinking=False
7. Nemotron returns 4-section markdown:
   ## 1. Identification
   ## 2. Physical history
   ## 3. Cultural significance
   ## 4. What the receipts prove
8. router.py writes the response to the cache
9. Browser overlays biography panel + photo strip + dataset citation row
```

**The verb is the year slider scrub. The wow beat is the Cross-Bronx empty-out. The payoff is the 1520 Sedgwick biography click.**

---

## 7. The Fallback Ladder

| Failure | Detection | Fallback |
|---|---|---|
| Building click feels slow | Stopwatch | Cache layer should hit in 11 ms; if not, the cache file is missing or BIN does not match — fall back to the pre-baked anchor events |
| `:8090` llama-server crashes | `tmux attach -t llama` shows error / `curl :8090/v1/models` fails | `~/sixth-borough/scripts/start-llama-nano.sh` (idempotent, ~30 sec restart) |
| `:30001` real orchestrator crashes | `curl :30001/health` fails | Stub orchestrator on `:30000` is alive as safety net |
| Both backends down + venue WiFi flakes | Smoke test | `data/narration_cache.json` + `data/biography_cache.json` serve from disk without any backend running |
| Demo crashes on stage | Live | Pre-recorded 30-sec OBS clip of the working loop |
| Tailscale flakes | Pre-demo | Demo runs on the GN100's local screen via HDMI, Tailscale is the secondary remote-debug path |

---

## 8. The Unplug Beat (the entire pitch in one gesture)

1. Demo runs normally with ethernet plugged in (so the box can talk to your laptop over the venue WiFi for the screen share, if needed)
2. At the climax line — "this entire system runs on the box, with the cable on the floor" — physically pull the ethernet cable
3. Click another building. The biography returns in 11 ms (cache hit) or 5-30 sec (cache miss). Either way, **no internet was used**.
4. The cable is sitting on the floor in front of the judges. The point lands.

The unplug works because:
- The model weights are on the local SSD
- The data is on the local SSD
- The orchestrator is local Python
- The renderer is a static HTML file served from the box itself
- Nothing in the runtime path crosses the LAN, much less the internet

---

## 9. Common Commands (paste-ready)

```bash
# attach to the box
ssh gn100

# verify model is loaded
curl -s http://127.0.0.1:8090/v1/models | python3 -m json.tool

# verify real orchestrator is healthy
curl -s http://127.0.0.1:30001/health

# canonical Sedgwick biography smoke test
curl -X POST http://127.0.0.1:30001/biography \
  -H "Content-Type: application/json" \
  -d '{"bin": "2008286"}' | python3 -m json.tool

# canonical Sedgwick narration smoke test
curl -X POST http://127.0.0.1:30001/narrate \
  -H "Content-Type: application/json" \
  -d '{"event_id":"bronx-1973-08-11-sedgwick","year":1973,"niche":"hip-hop","style":"forensic"}'

# tmux session map
tmux ls
# expect: llama, orch, prebake, stub

# attach to llama-server logs
tmux attach -t llama
# detach with Ctrl-b d

# restart llama-server (idempotent)
~/sixth-borough/scripts/start-llama-nano.sh

# OOM recovery (UMA buffer cache flush)
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'

# GPU live status
nvidia-smi
```

---

## 10. The Memory Budget (so you can answer "how much headroom")

| Component | Footprint |
|---|---|
| Nemotron-3 Nano 30B Q8_K_XL | ~38 GB |
| Renderer scene + framebuffer | ~2 GB |
| Orchestrator + Python runtime | ~1 GB |
| Open data corpus + caches | <1 GB |
| OS + buffer cache | ~10 GB |
| **Total** | **~52 GB** |
| **Headroom on 128 GB unified** | **~76 GB** |

5x headroom for additional concurrent models if a judge asks "could you run a vision model alongside?" Answer: yes, easily, and the unified memory is why.

---

## 11. The Pitch One-Liners (pick by audience)

**For NVIDIA judges (rubric-locked, all the magic words):**
> "NVIDIA Nemotron-3 Nano 30B from the NVIDIA Nemotron model family, running locally on a 128 GB DGX Spark with the ethernet cable on the floor, writing forensic biographies of any New York City building from public records — with zero cloud calls."

**For technical visitors:**
> "30 billion parameter local reasoning model joining four NYC public datasets via zero-dependency RAG, on a single DGX Spark, with the cable unplugged."

**For non-technical visitors:**
> "Click any building in New York City and a 30-billion-parameter AI writes its forensic biography from public records — running on the box at my feet, with the internet cable on the floor."

**The metaphysical naming defense (use only if someone asks why "Sixth Borough"):**
> "Sixth Borough is like a sixth sense — a metaphysical borough that lives in the hardware and preserves the city as a whole."

---

## 12. The Anti-Cheat (what we do NOT do, and why it matters)

| Thing we don't do | Why |
|---|---|
| GPT-4 / Claude / cloud LLM | Zero rubric points and the unplug beat dies |
| NeMo Framework | Wrong tool for LLM inference; NVIDIA's own playbook says llama.cpp for Nemotron on Spark |
| TensorRT-LLM | More setup than llama.cpp for the same outcome in 38 hours |
| Vector DB / FAISS / LangChain | 4 datasets join cleanly on BIN + haversine; embeddings would lose the citation chain |
| Predictive ML / gentrification forecast | Locked out by thesis: "we don't predict gentrification, we trace it from the receipts" |
| Fine-tuning | We have 38 hours; pretrained inference only |
| Ollama | Slower than llama.cpp, was never wired in, vestigial doc references only |

---

## 13. The Single Sentence If You Forget Everything Else

> A 30-billion-parameter NVIDIA Nemotron model writes the forensic biography of any New York City building from four public datasets, joined zero-dependency by BIN and lat/lon proximity, on a 128 GB DGX Spark with the cable on the floor.
