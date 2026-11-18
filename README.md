# Sixth Borough

A 3D map of New York City's building footprints with a year slider. Buildings appear by construction year; demolished landmarks show while they stood. NVIDIA Nemotron-3 Nano 30B narrates via llama.cpp on an Acer GN100 (NVIDIA DGX Spark, GB10).

Built at NVIDIA Spark Hack NYC, 10-12 April 2026. Per the repo description: Cultural Impact Track winner and the Most Likely to Be Unicorn bounty.

## Team

- **Alex Wu** ([TheApexWu](https://github.com/TheApexWu)): lead engineer and architect. Orchestrator, GN100 llama.cpp setup, `/biography` endpoint, the browser app's five-borough load, ghost buildings, bridges, stadiums and year scrub, and the Bevy renderer on `risk`.
- **Carson Weeks** ([Cheatcodesam](https://github.com/Cheatcodesam)): Bevy scaffold and WASM build on `main`, llama.cpp narration backend.
- **James Burke** ([lifesized](https://github.com/lifesized)): guided tour, Sobel sketch overlay, NYPL OldNYC photo index, Wikidata demolished-landmark data, immigration data, cultural content.
- **Marvens Destine** ([A12-AA](https://github.com/A12-AA)): hackathon networking.

## Branches

| Branch | Holds | Last change |
|---|---|---|
| `main` | Orchestrator (stub and llama.cpp backends), data, Bevy 0.18.1 scaffold (test cube) | 14 Apr 2026 |
| `feature/sketch-overlay` | deck.gl browser app at hackathon end | 12 Apr 2026, 14:12 ET (`f788d18`); 14 Apr removed docs only |
| `nvidia-livestream` | Same app plus three livestream commits (`DEMO_MODE`, Manhattan content, outer-borough auto-load) | 6-7 May 2026 |
| `risk` | Fuller Bevy renderer, `renderer-rust-v2/` | 12 Apr 2026, 11:31 ET (`de3604b`) |
| `session-44/borough-expansion-bronx` | Orchestrator with `POST /biography`; not merged | 11 Apr 2026, 23:49 ET |

The repo doesn't record which renderer the judges saw.

## Numbers

Read from committed files on 18 Nov 2026; `tests/test_data_smoke.py` asserts the data figures on `main`.

| | Value | Source |
|---|---|---|
| Building footprints | 1,082,831 | `data/*_compact.json` |
| Geometry | 230.8 MB | same files |
| Archival photos | 750 (NYPL Milstein, via OldNYC) | `cultural-content/oldnyc/` |
| Demolished-building pins | 286 (Wikidata) | `data/demolished-landmarks.json` |
| Ghost landmarks | WTC 1, 2, 3 and 7; original Penn Station; Singer Building | `data/landmarks-infrastructure.json` |
| Bridges / stadiums | 8 / 8, 3 stadiums demolished | same file |
| Cross-Bronx ghosts | 117 placeholder blocks, removed 1948-1972 | generated in `index.html` |
| Year slider | 1719 to 2026 | `index.html` |
| Narrated events | 19, pre-generated 11 Apr (292.5 s, 0 failures) | `data/narration_cache.json` |
| Model | Nemotron-3-Nano-30B-A3B `UD-Q8_K_XL` GGUF, `-ngl 99` | `scripts/start-llama-nano.sh` |
| Generation speed | About 29 tok/s, one recorded run (798 tokens in 27.4 s) | GN100 snapshot, 11 Apr 2026 |
| Building heights | `height_roof` | NYC Building Footprints (`5zhs-2jue`) |

Model, data and photos are local. The page loads deck.gl 9.1.4, MapLibre GL 3.6.2 and GSAP 3.12.5 from unpkg.com, so the first load needs internet.

## Run it

Checkouts: `main` about 320 MB, `feature/sketch-overlay` about 520 MB.

**Browser app**

```bash
git clone https://github.com/TheApexWu/sixth-borough.git && cd sixth-borough
git checkout feature/sketch-overlay   # or nvidia-livestream
python3 -m http.server 8080           # open http://localhost:8080/
```

BK, QN and SI buttons load the outer boroughs; photo and Wikidata pins are in the Dev panel. Building clicks call `POST http://127.0.0.1:30001/biography` and fall back to curated text. The Liberty Island mesh and three Bronx hotspot videos are not in the repo.

**Orchestrator, stub mode** (no GPU, Python 3.11+)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
./scripts/dev-stub.sh                 # :30000; curl localhost:30000/health
```

**Real narration** (GB10 only): `scripts/setup-gn100.sh` builds llama.cpp for CUDA architecture 121 and downloads the GGUF from `unsloth/Nemotron-3-Nano-30B-A3B-GGUF`. Then:

```bash
./scripts/start-llama-nano.sh         # :8090 (start-gn100.sh collides with the stub on :30000)
NARRATION_MODE=real LLAMA_SERVER_URL=http://127.0.0.1:8090 \
  python -m uvicorn src.orchestrator.main:app --host 0.0.0.0 --port 30001
```

**Native renderer** (Rust): `cd renderer-rust && cargo run` on `main`; `cd renderer-rust-v2 && cargo run --release` on `risk`.

**Tests**

```bash
pytest                                                     # under a second
SIXTH_BOROUGH_FULL_DATA=1 pytest tests/test_data_smoke.py  # parses 231 MB; peaked at about 1.25 GB
```
