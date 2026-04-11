# GN100 Health Snapshot — Apr 11 2026 ~14:50 ET

Moment-in-time reference for the Spark Hack standup. Pulled live via `ssh gn100`.

## Host

| Field | Value |
|---|---|
| Hostname | `gn100-3857` |
| User | `acergn100_7` (Carson admin, Alex via Tailscale) |
| Tailscale | `100.125.233.124` |
| SSH alias | `ssh gn100` (config in `~/.ssh/config`, IdentityFile `~/.ssh/id_ed25519`) |
| Uptime | 18h 34m |
| Load | 1.13 / 1.29 / 1.38 (settled, comfortable) |

## GB10 Grace Blackwell

| Metric | Value |
|---|---|
| Driver | NVIDIA 580.142 |
| CUDA | 13.0 |
| Temperature | 50 °C |
| Power draw | 17 W (cap not reported) |
| GPU utilization | 20 % |
| VRAM | Not reported (Grace Blackwell unified memory exposes N/A via nvidia-smi — normal) |

**The box is barely working.** 20% util at 17W means we have ~5× headroom for additional concurrent models if we wanted them. The "30B model on a desktop" flex understates how much headroom the GB10 actually has.

## Disk

| Mount | Size | Used | Avail | Use% |
|---|---|---|---|---|
| `/` (`/dev/nvme0n1p2`) | 3.7 TB | 161 GB | 3.4 TB | 5 % |

3.4 TB free. We could pre-bake another 1000 events and not move the needle.

## Memory

| Region | Total | Used | Free | Available | Buff/Cache |
|---|---|---|---|---|---|
| RAM | 119 GiB | 47 GiB | 856 MiB | **72 GiB** | 71 GiB |
| Swap | 15 GiB | **1.4 MiB** | — | — | — |

Zero memory pressure. Could run the renderer ON the GN100 if we wanted (we don't — the laptop demos better visually).

## Live services

| Port | Service | PID | Uptime | Status |
|---|---|---|---|---|
| `:8090` | `llama-server` (Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL) `-ngl 99 -c 8192 --jinja` | 1048573 | **6h 38m** | UP, 4.4% CPU, 1.5% MEM |
| `:30001` | Real orchestrator (`NARRATION_MODE=real`, `LLAMA_SERVER_URL=http://127.0.0.1:8090`) | 1079191 | since 12:21 ET | UP, **23 successful 200 OK** since start |
| `:30000` | Stub orchestrator (uvicorn) | 28941 | since AM | UP, fallback |
| Tmux | `llama`, `nemoclaw`, `ollama`, `orch`, `stub` | — | — | All alive |

## Inference performance (most recent llama-server task)

- **798 tokens generated in 27.4 sec** = **29.17 tok/s** sustained
- Prompt cache: 6 prompts, 542 MiB (well under 8 GiB / 8 K tok budget)
- Reasoning-budget: activated then naturally deactivated (no max_tokens truncation hits)
- No `NarrationBackendError` events, no 502s, no slot exhaustion warnings

29 tok/s on a 30B Q8 reasoning model means a typical 80-100 word narration finishes in 12-25 sec — fast enough for the demo to feel live without apologizing for latency.

## Smoke test confirmation (Apr 11 14:45 ET)

```bash
ssh gn100 'curl -s -X POST http://127.0.0.1:30001/narrate \
  -H "Content-Type: application/json" \
  -d "{\"event_id\":\"bronx-1973-08-11-sedgwick\",\"year\":1973,\"niche\":\"hip-hop\",\"style\":\"sensory\"}"'
```

Returns:

> *"August 11, 1973, the rec room of 1520 Sedgwick throbs with cheap perfume and the thump of a crowd pressing against graffiti-splashed brick. Clive Campbell spins two turntables, looping the drum break until the rhythm hangs in the stale air like a low-frequency hum you can feel in your chest."*

`backend:"real"`, 23.4s hold. End-to-end Track A verified.

## Pre-bake cache (Apr 11 14:53 ET)

`data/narration_cache.json` contains all 19 events pre-baked from the real backend. 4 min 53 sec total, 19/19 successful, average ~15s per narration. Insurance against venue WiFi flake during the Sun demo. Same model, same backend, just cached a few minutes earlier — preserves the "live local model" framing if used as a fallback.

## What's NOT broken (and was previously claimed to be)

The "real backend down since AM" line that propagated through Session 40 + 41 outbox + people memory was **wrong**. At minimum since 12:08 ET (when llama-server pid started), Track A has been live and serving real Nemotron narrations. Carson never took it down. Memory has been corrected.

## Don't touch list

- **`:8090` llama-server** — 6h 38m uptime, prompt cache warm, do NOT restart unless it actually breaks. Restart cost = ~30s reload + cache rebuild.
- **`:30001` real orchestrator** — serving the demo path. Restart only after confirming with Carson.
- **GN100 disk / kernel** — leave it alone, it's running.

## Quick commands for the standup

```bash
# Verify backend is alive
ssh gn100 'curl -s http://127.0.0.1:30001/health'

# Tail orchestrator log
ssh gn100 'tmux capture-pane -t orch -pS -30'

# Tail llama-server log
ssh gn100 'tmux capture-pane -t llama -pS -30'

# GPU snapshot
ssh gn100 'nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,power.draw --format=csv'
```

---

*Snapshot taken Apr 11 2026 ~14:50 ET, post-compact session 41 addendum, pre-standup. See `Session Bridge - Apr 11 Session 41.md` for the session context that produced this audit.*
