# Build Decisions Log

Append-only log of build decisions made during the hackathon. When you make a non-obvious choice, write it here. Format:

```
## YYYY-MM-DD HH:MM — short title
**Decision:** what we chose
**Alternatives considered:** what we didn't choose
**Why:** the reason
**Owner:** who made the call
**Reversible by:** when this decision can still be undone
```

---

## 2026-04-10 evening — Track selection

**Decision:** Cultural Impact (one of three tracks).
**Alternatives considered:** Human Impact (too crowded), Environmental Impact (no native expertise on team).
**Why:** Sixth Borough's neighborhood-history thesis maps cleanly onto "preserve the history of unique neighborhoods." James's 8-era guided tour branch is already a working artifact in this space. Carson's Rust/wgpu renderer + Alex's narration loop complete the system.
**Owner:** Team consensus.
**Reversible by:** Friday night before submission form is touched. After Sat morning, we are committed.

---

## 2026-04-10 evening — Hardware framing

**Decision:** Treat the Acer Veriton GN100 as a single DGX Spark / GB10 box. Drop the earlier "GB10 oracle + Acer viewer" two-machine framing entirely.
**Alternatives considered:** Pretending we have two boxes (incoherent — the GN100 IS a DGX Spark, same chip).
**Why:** Research on Apr 9 confirmed the GN100 is the same GB10 Grace Blackwell silicon as the official DGX Spark, 128 GB unified memory, $2,999 retail. There is one machine. The pitch is "everything on one box, local-only" — that's stronger than the two-machine story anyway.
**Owner:** Alex.
**Reversible by:** Not reversible — the hardware is the hardware.

---

## 2026-04-10 evening — Narration model

**Decision:** Nemotron-3-Nano-30B-A3B (Q8 GGUF) via llama.cpp on the GN100, OpenAI-compatible API on port 30000.
**Alternatives considered:**
- Nemotron-Mini-4B-Instruct (smaller, faster, but less impressive on stage)
- Cloud APIs (zeros us on NVIDIA Stack score)
- NeMo Framework directly (now focused on speech, not the right tool)
- vLLM / TensorRT-LLM (more setup overhead than we have time for)
**Why:** This is the NVIDIA-recommended path per their own DGX Spark playbook. Uses an NVIDIA model (Nemotron) on NVIDIA hardware (GB10) via NVIDIA's documented setup. Earns points on both axes of the NVIDIA Ecosystem score. Fallback to Q4_K_M quantization if Q8 is too slow or won't fit.
**Owner:** Alex.
**Reversible by:** Sat noon. After that we're committed and the demo video has to use whichever model is running.

---

## 2026-04-10 evening — Renderer primary path

**Decision:** Carson's Rust + wgpu pipeline as primary. James's WebGL `feature/sketch-overlay` branch as fallback path, with the explicit decision point at Sat 4 PM Progress Checkin.
**Alternatives considered:**
- WebGL primary (proven to work, but doesn't tell the "native Blackwell" story as cleanly)
- Both at once (no time, would split focus)
**Why:** Native code on Blackwell silicon is a stronger Frontier Creativity story than "Three.js in a browser." But James's branch is real, working, and has the 8-era cutscene engine, so it's a credible safety net.
**Owner:** Alex + Carson + James.
**Reversible by:** Sat 4 PM hard. If Carson's renderer isn't stable by then, we pivot to WebGL and don't look back.

---

## 2026-04-10 evening — Product synthesis & 4 pillars locked

**Decision:** Sixth Borough is built around 4 core identity pillars: (1) Time Machine, (2) PS2 Memory Aesthetic, (3) Cultural Intelligence, (4) Niche Discovery. Chronology is the navigation primitive, niche filtering is the anti-overload mechanism, PS2 aesthetic is the substrate experience, cultural intelligence is the depth layer that makes the time machine not-empty.
**Alternatives considered:** treating cultural intelligence + niche discovery as a pivot away from the time machine framing (rejected — the team's mental model is preserved by adding these as additive layers, not replacements).
**Why:** A time machine without curation is just a database with a slider. A time machine with niche-filtered cultural depth is a discovery tool. The 4 pillars are mutually reinforcing — none of them is decorative.
**Owner:** Alex.
**Reversible by:** Not reversible without rewriting the product. These four are the identity. See `KICKOFF.md` for the full pillar definitions.

---

## 2026-04-10 evening — Demo cinematic locked

**Decision:** ONE neighborhood (Bronx), ONE era window (1973–1985), ONE fully-populated niche (hip-hop heads), anchored at 1520 Sedgwick Avenue. ~30 hand-curated events. 4–5 other niches present as placeholder toggles with 1–2 events each.
**Alternatives considered:** showing all 8 eras from James's branch (too diffuse for a 3-min video), demoing multiple neighborhoods (no time), demoing immigration flow as the cinematic centerpiece (rejected — too cliched, judges have seen it).
**Why:** The hip-hop birthplace is unbeatable as a 3-min demo story — specific, NYC-mythic, dated to a single address, narratively cinematic. The architecture is universal; the demo is one slice. The placeholder niches prove the architecture handles other lenses without dragging focus.
**Owner:** Alex.
**Reversible by:** Friday midnight. After Saturday morning, the events seed file is locked.

---

## 2026-04-10 evening — OpenClaw bounty dropped

**Decision:** Not pursuing the Most Impactful Use of OpenClaw bounty (RTX 5090).
**Alternatives considered:** building an OpenClaw "Walking Tour Coordinator" skill as a 2-3 hour Sat afternoon add-on.
**Why:** OpenClaw constrains the build to fit its skill model and pulls energy away from the core product. The cultural intelligence + niche discovery framing doesn't naturally fit a generic agent skill wrapper. The opportunity cost is higher than the prize value.
**Owner:** Alex.
**Reversible by:** Not reversible — committing to this decision frees Sat afternoon for the core loop.

---

## 2026-04-10 evening — Antler Unicorn bounty active priority

**Decision:** Actively pursue the Most Likely to Be a Unicorn bounty. Lean into the niche-discovery + B2B-but-cultural framing for any Antler conversation. Pitch verbatim lives in `pitch/antler-90sec.md`.
**Alternatives considered:** treating Antler bounty as opportunistic.
**Why:** Alex has prior Antler context (Mar 27 meeting with Wouter Hiemstra, Antler app submitted Mar 31). This isn't a cold pitch — it's a progress update on what he's been building since they last talked. Antler dinner + auto-acceptance to Founder in Residence is a real ROI for Alex's job/funding trajectory regardless of whether Sixth Borough wins the track.
**Owner:** Alex.
**Reversible by:** N/A — this is a posture, not a build constraint.

---

## 2026-04-10 evening — Dependency age rule passed

**Decision:** All planned dependencies are ≥2 weeks old as of Apr 10 2026. Audit complete.
**Alternatives considered:** swapping in newer cutting-edge libraries (rejected — would violate orientation rule).
**Why:** Per the orientation announcement at the kickoff, every open-source dependency must be at least 2 weeks old. NVIDIA / Nemotron stack is exempt and clear regardless. llama.cpp, Rust+wgpu, Three.js, Ollama, Nemotron-3-Nano GGUFs (4 months old), Live VLM WebUI (5 months old), etc. all pass. **Mid-build rule:** any new dependency added during the hackathon must also pass the ≥2-week check or it doesn't ship.
**Owner:** Alex (audit), Carson + James (compliance).
**Reversible by:** N/A — rule is external.

---

## 2026-04-10 evening — Carson + James mental model preservation

**Decision:** When syncing with Carson and James at the venue, frame the cultural intelligence + niche discovery layers as ADDITIVE to the existing time-machine PS2 framing, not as a pivot. Their work (Carson's renderer, James's 8-era cutscene engine) is unchanged. The new pieces are a data layer + a niche filter UI on top.
**Alternatives considered:** presenting it as a product reframe (rejected — risks confusing the team and breaking their build context).
**Why:** Carson and James have been operating under "time machine PS2 aesthetic" all week. The synthesis I'm proposing fits inside that framing — chronology is still the navigation, PS2 is still the substrate, the new dimensions (cultural intelligence layer + niche filter) live ON TOP of what they're already building. Talking to them as if the project changed will cost momentum.
**Owner:** Alex (the framing).
**Reversible by:** N/A — this is a communication discipline, not a build constraint.

---

## 2026-04-10 evening — Renderer engine: Bevy 0.16 (Rust + wgpu)

**Decision:** The Rust renderer is built on **Bevy 0.16**, not raw wgpu. Static point clouds ingest through the `bevy_pointcloud` plugin (Potree-based, stable Rust, PLY format). Animated point clouds use **OpenVAT** (Blender addon) → glb with embedded vertex animation texture, sampled by a custom WGSL vertex shader on the Bevy side.
**Alternatives considered:**
- Raw wgpu with hand-rolled scene graph (more control, but rebuilding what Bevy gives free; no time)
- Bevy 0.18 (latest, January 2026 release, but plugin ecosystem hasn't caught up — `bevy_pointcloud` plugin compat is the binding constraint)
- `bevy_gaussian_splatting` plugin (more "neural rendering" aesthetic, but requires nightly Rust for default features and adds risk)
- glTF morph targets only for animated point clouds (works but caps at low vertex counts; OpenVAT scales further)
**Why:** Bevy gives us a built-in animation graph (since 0.14, animation masks + additive blending added in 0.15), the mature first-party glTF loader, an ECS for the niche-filtered event entities, and a plugin ecosystem that includes static point cloud rendering out of the box. The key insight is that **Marvens authors everything in Blender** — city geometry, ghosts, animated point clouds — and Carson loads it via standard formats. Marvens never touches Rust; Carson never touches Blender. The contract between them is the file format spec in `pointcloud-pipeline/README.md`.

OpenVAT specifically is the right choice for the animated point cloud ghost layer because it's Blender-native, captures any vertex-level animation including Marvens's Geometry Nodes / Simulations work, encodes the result as a GPU texture that any engine with a basic vertex shader can sample, and is the same family of technique Marvens has shipped to 2M+ concert attendees on the ODESZA tour. The ~50–100 lines of WGSL Carson writes to sample the VAT is the only net-new shader work.

Bevy 0.16 (mid-2025) is pinned over 0.18 (January 2026) because the third-party plugin ecosystem — especially `bevy_pointcloud` — is most reliably aligned with 0.16. 0.18 is too new for safe hackathon plugin compat.
**Owner:** Carson + Alex + Marvens.
**Reversible by:** Friday midnight (engine pin), Sat morning (bump to 0.17 if Carson confirms plugin compat), not reversible after Sat morning.

---

## 2026-04-10 evening — Carson + Marvens paired ownership of asset format contract

**Decision:** Carson (`renderer-rust` branch) and Marvens (`pointcloud-pipeline` branch) **pair Friday night** to lock the file format contract that lives in `pointcloud-pipeline/README.md`. Once locked, they iterate independently for the rest of the weekend — Marvens drops new ghosts into shared storage and bumps `assets/pointclouds/MANIFEST.json`, Carson's renderer ingests on next launch.
**Alternatives considered:** treating Marvens as a passive asset producer who hands files over a wall (rejected — Marvens has shipped this exact technique at scale and his input on the format spec is high-value).
**Why:** Carson explicitly said he wants to work with Marvens on integration, not after it. Pairing on the format spec Friday night removes the highest-risk part of the collaboration (ambiguity about what the file looks like) before either of them writes any code that depends on the assumption.
**Owner:** Carson + Marvens (the contract), Alex (the meta-decision).
**Reversible by:** N/A — this is a coordination model, not a build constraint.

---

## 2026-04-11 ~10:30 ET — Track A verified end-to-end

**Decision:** Track A (real Nemotron narration on GN100 via llama.cpp) is the demo path. Track B (Super 120B / NemoClaw / Ollama) is parked and not part of the submission.
**Alternatives considered:** holding Track B open as a parallel possibility (rejected — Carson's overnight smoke test on Nemotron-3-Nano-30B-A3B returned `backend:"real"` with period-accurate Bronx text on `bronx-1973-08-11-sedgwick`, so Track A is proven and Track B is now scope risk).
**Why:** Carson grinded overnight, self-onboarded to GN100 via the handoff doc, debugged a real Nemotron-3-Nano quirk (reasoning model puts output in `reasoning_content` when `max_tokens` is tight), shipped the fix in `4ce1930` (`narration_real.py` reasoning_content fallback + `LLAMA_MAX_TOKENS` 220→1024 + `main.py` `NarrationBackendError` → HTTP 502). The smoke test produced a 26.8 sec hold of beautiful sensory text on the Sedgwick event. The path works.
**Owner:** Carson (the fix), Alex (the lock).
**Reversible by:** Sat afternoon ONLY IF Track A breaks. After Sat 4 PM, this is the demo.

---

## 2026-04-11 ~10:00 ET — Glb-only asset format (drops PLY, drops bevy_pointcloud)

**Decision:** **glb is the single asset format** for static and animated point clouds. The earlier "PLY for static + glb for animated" dual-format contract is dropped.
**Alternatives considered:**
- Keeping PLY for static point clouds (rejected — adds surface area for no aesthetic gain on the Bronx demo)
- Keeping `bevy_pointcloud` plugin in the dependency tree (rejected — was the binding constraint pinning Bevy to 0.16, no longer needed once PLY is gone)
**Why:** Per Alex: "simple and better for the verts." Carson wrote the glb loader and made the call to drop PLY entirely (`d6470aa`). Two formats was always extra surface area. Single-format simplifies Marvens's authoring workflow (one Blender export, not two), simplifies Carson's renderer (one loader, not two), and unblocks a Bevy version bump if Carson wants it. `pointcloud-pipeline/README.md` already updated by Carson in `d6470aa` (removed PLY path, -65 lines).
**Owner:** Carson (the engineering call), Alex (the product call), Marvens (the workflow side, to be confirmed at venue).
**Reversible by:** N/A — already shipped to main and the dual-format scaffolding is gone.

**Stale docs that still reference PLY+glb dual** (post-standup cleanup, not blocking):
- `docs/DECISIONS.md` line ~124 (the Bevy 0.16 entry — the Bevy 0.16 pin reason is now stale, the plugin we pinned to is no longer in the build)
- `CONTRIBUTING.md` (pointcloud-pipeline branch description)
- `marvens-shot-list.md` (Alex's local doc, not in repo)

---

## 2026-04-11 morning — Pitch thesis locked: cultural memory infrastructure

**Decision:** The pitch thesis is **"cultural memory infrastructure that runs on the community's own hardware instead of someone else's cloud."** "Time machine" survives only as the door hook, never as the spine. The 90-second demo script + delivery notes + Q&A pivots + sponsor verbatim phrase placement live in `docs/DEMO_VIDEO_SCRIPT.md`.
**Alternatives considered:**
- Continuing with "time machine" as the spine (rejected — it's a hook, not a thesis; doesn't answer "so what" for judges or for Antler)
- Adding a predictive ML / "do more with the data" angle suggested by an outside participant (rejected — at 19 seed events there is no ML to do; predicting gentrification is gentrification; it would dilute the wedge)
- Leading with the PS2 aesthetic / Frontier Creativity angle (rejected — the aesthetic is a strength but not load-bearing on its own; the local-hardware claim is the only framing where the GB10 is load-bearing rather than decorative)
**Why:** This is the only framing where the hardware is the political claim, not a perf flex. NVIDIA Spark Hack judges + Antler GP in the room + a literal GB10 on the floor — the room is screaming "local hardware as a sovereignty claim." Every other team is either doing a cloud wrapper or using the GB10 as a benchmark. We're the only team where the hardware IS the thesis. This framing is also what makes Antler write a check (PixVerse is the cloud bet on the same generative-AI thesis; Sixth Borough is the local-hardware fork — same conviction, opposite infrastructure). The "time machine" framing is fine as a hook for the door but cannot carry the pitch. The "cultural memory infrastructure" reframe carries it.

The load-bearing claim, in Alex's words: *"Cultural memory is the most extractable resource a city has. Right now Google, Zillow, and OpenAI are extracting it for free. They flatten it. They surveil it. They charge per query. And they only know what got scraped. We built the opposite."*
**Owner:** Alex.
**Reversible by:** Standup confirmation. After Sat morning standup lock, this is the script we rehearse.

---

## 2026-04-11 morning — CORS middleware staged for main.py (uncommitted)

**Decision:** Pre-stage `fastapi.middleware.cors.CORSMiddleware` in `src/orchestrator/main.py` with `allow_origins=["*"]` so the future public WASM build at `sixthborough.nyc` can hit `api.sixthborough.nyc/narrate` cross-origin. Staged in working tree only, **not committed**, holding until Carson's Bevy→WASM build is verified green and the team decides to buy the domain.
**Alternatives considered:**
- Committing CORS now (rejected — restarts the live orchestrator on GN100 for no current benefit; introduces risk before the WASM path is proven)
- Not staging at all (rejected — leaves a 5-minute fire drill the moment WASM lands)
**Why:** CORS is harmless when there's no cross-origin caller, so the risk is asymmetric. Staging the diff costs nothing. Committing it without testing the live restart costs ~30 seconds of downtime if it goes wrong. The right move is "ready to ship, not yet shipped." When WASM is verified, `git add src/orchestrator/main.py && git commit && git push && restart orch tmux` is the activation path.
**Owner:** Alex (staged), Carson (will trigger by landing WASM).
**Reversible by:** `git checkout src/orchestrator/main.py` if we abandon the WASM path.

---

## 2026-04-11 ~11:37 ET — James shipped NYPL OldNYC index (5-borough cultural scaffold)

**Decision:** James's `bde0148` lands the cultural-data scaffold for all 5 boroughs in flight. 750 NYPL Milstein archival photos, 150 per borough (Bronx, Brooklyn, Manhattan, Queens, Staten Island), 1900-1956. Slim JSON index at `cultural-content/oldnyc/index.json` (221 KB, 750 records, schema `{id, boro, lat, lon, year, title, thumb, nypl_url}`), 26 MB of 600px thumbnails, generated by `scripts/build_oldnyc_index.py` (170 lines).
**Why:** This is the cultural memory data layer the audit below was about to recommend. James shipped it before the recommendation landed. The "all 5 boroughs" claim is now literally true in the repo: 150 georeferenced points × 5 boroughs = 750 clickable archival anchors with NYPL provenance.
**Owner:** James Burke.
**Reversible by:** N/A — already in main.

**Implications**:
- The borough expansion ask is now PARTIALLY ANSWERED before Alex even decides.
- The Option B recommendation below (curate ~30 cultural events across boroughs) is still valuable as the **narration-anchor** layer (the events seed file remains the click-to-narrate trigger), but James's OldNYC index gives the rendered scaffold layer for free.
- The renderer can now spawn 750 photo-billboard ghosts at real NYC coordinates without any new data work. Carson + Marvens can render these as low-poly billboards with the photo as albedo + Sobel edge detection — instant "ghost layer" across all 5 boroughs.
- The pitch can now credibly say "750 archival photos from the NYPL Milstein collection, anchored to real coordinates across all five boroughs, every one is a click-to-narrate ghost."

---

## 2026-04-11 ~midday — NYC borough expansion data audit (DECISION PENDING)

**Decision:** PENDING. Alex to decide post-standup whether to expand from Bronx-only to all 5 boroughs.

**The ask**: "Did we update Sixth Borough to include ALL borough data and building info? It'd be nice bonus to fully fulfill the entirety of NYC. First obtain more open data and the physical models of the buildings, validate/audit them, then we can decide to add them."

**Audit findings — datasets that exist, are free, cover all 5 boroughs**:

### Tier 1 — Geometric building data

| Dataset | Source | Size | Format | Vintage | Coverage | Notes |
|---|---|---|---|---|---|---|
| **TUM LoD2 CityGML** | gis.bgu.tum.de (TU Munich) | **2.4 GB compressed** | CityGML, KML, COLLADA, **glTF** | 2015-2017 | All 5 boroughs, **1,082,015 buildings**, 55 thematic attributes per building | **glTF native = Carson's stock Bevy loader can ingest. But 1M buildings is way past the demo budget.** Source: NYC Open Data + TUM enhancements. |
| **NYC Official 3D Building Model** | data.cityofnewyork.us / maps.nyc.gov | unknown | GML, Multipatch (Esri), DGN | 2014 base, last updated Sep 2023 | All 5 boroughs, hybrid LoD1+LoD2 (~100 iconic buildings in LoD2) | Less detailed than TUM but official. Download URLs: DA_WISE_GML.zip, DA_WISE_Multipatch.zip, DA_Wise_DGN.zip. |
| **NYC Building Footprints (active)** | data.cityofnewyork.us (`5zhs-2jue`) | varies | Shapefile, GeoJSON, file geodatabase, REST | Updated daily by OTI | All current buildings >400 sqft >12 ft, all 5 boroughs | Daily-updated. Attributes: BIN, BBL, construction year, ground elevation, roof height, feature code. 2D footprints. |
| **MapPLUTO** | nyc.gov/site/planning | 11-65 MB per borough | Shapefile | 22v2 (May 2022), newer releases possible | 870,000+ tax lots, 80+ attributes per lot, all 5 boroughs | Tabular metadata, not geometry. Pairs with footprints. |

### Tier 2 — Historical / demolished building data (the actual ghost-layer candidates)

| Dataset | Source | Size | Format | Coverage | Notes |
|---|---|---|---|---|---|
| **BUILDING_HISTORIC** | data.cityofnewyork.us (`ipkp-snf6`) | unknown | Shapefile, GeoJSON, file geodatabase | All 5 boroughs, demolished AND significantly altered buildings | **THIS IS THE GHOST LAYER DATASET.** Attributes: `OBJECTID`, `NAME`, `BIN`, `HEIGHT_ROOF`, `LAST_STATUS_TYPE` (demolition vs alteration), `CONSTRUCTION_YEAR`, `DEMOLITION_YEAR`, `ALTERATION_YEAR`, `BASE_BBL`, `MAPPLUTO_BBL`, `GEOM_SOURCE`, `GROUND_ELEVATION`. Maps directly onto the demolished-theaters niche. Records moved here from active footprints when demolished/altered. |
| **LPC Individual Landmark + Historic District Building Database** | data.cityofnewyork.us (`7mgd-s57w`) | tabular | CSV / API | All 5 boroughs, **36,000 buildings** (34K within 141 historic districts + 1,408 individual landmarks) | Pairs with BUILDING_HISTORIC for narrative grounding. 50+ years of LPC reports. |
| **Historic Districts (Map)** | data.cityofnewyork.us (`xbvj-gfnw`) | small | Shapefile | All 5 boroughs | The 141 historic districts as polygons. |

### Tier 3 — Cultural/historical archives (for the RAG roadmap line)

| Dataset | Source | Format | Coverage | Notes |
|---|---|---|---|---|
| **NYPL NYC Space/Time Directory** | spacetime.nypl.org | NDJSON, Data Package, APIs, georectified historical maps | **5,000+ digitized NYC street maps 1850-1950**, historical addresses, Building Inspector data, OldNYC photo locations, 18th century ward boundaries | **Phase 2 RAG source.** Cite on stage as "we ground every narration in NYPL's Space/Time Directory." DO NOT import today. The killer cultural memory data layer for post-hack. |

### Validation summary

- **License**: All datasets above are governed by NYC Open Data Terms of Use (free for non-commercial; commercial use OK with attribution). TUM redistribution adds no restrictions. **No license blockers.**
- **Format compatibility**: TUM model has glTF — Carson's existing `SceneRoot(asset_server.load(GltfAssetLabel::Scene(0)...))` could ingest individual building glTF files directly, no new loader needed. BUILDING_HISTORIC and footprints are 2D shapefiles/GeoJSON — would need extrusion (Blender → glb) before they're renderable, ~1 day Blender work for one borough's worth.
- **Vintage**: 2014-2017 is the freshest 3D data. Buildings demolished/built since then will be wrong. **For demolished buildings the staleness is a feature, not a bug** — we want the historical state, not 2026.
- **Scope reality check**: 1,082,015 buildings is NOT importable in 24 hours. Even loading TUM's glTF into Bevy at runtime would crush the GB10 frame budget. Carson's renderer at "loads manifest, spawns SceneRoots" handles tens-to-hundreds of entities, not a million.

### Three options for the ask

**Option A — DO NOTHING (Bronx only, future-roadmap line)**
- Ship as-is. Pitch the architecture as borough-agnostic. Cite NYC Open Data + NYPL Space/Time as Phase 2/3 in the script.
- Cost: 0 hours. Risk: judges ask "what about the other boroughs" and the answer is verbal-only.
- The 90s script already handles this with: *"Starting in the Bronx where hip-hop was born. The architecture is borough-agnostic."*

**Option B — CURATE EVENTS ACROSS BOROUGHS (no new geometry, just data layer)** ⭐ RECOMMENDED
- Hand-curate 5-10 cultural events per borough for `data/events-seed.json`. Push from 19 → ~50 events.
- Manhattan candidates: Stonewall Inn (1969), CBGB (1973-2006), Apollo Theater (1934 onwards), Loew's State Theatre (demolished 1987), Pennsylvania Station (demolished 1963), Studio 54 (1977), Tenement Museum site (1863).
- Brooklyn candidates: Brooklyn Navy Yard, Coney Island Steeplechase Park (demolished 1964), Wonder Wheel, Ebbets Field (demolished 1960), Eastern Parkway, Brownstone Brooklyn formation.
- Queens candidates: 1939 + 1964 World's Fair sites (Flushing Meadows), Long Island City warehouse-to-art transition, Steinway Mansion, Forest Hills Tennis Stadium.
- Staten Island candidates: St. George Ferry Terminal, Snug Harbor Cultural Center, Fresh Kills landfill (closed 2001), Conference House.
- Pitch upgrade: **"all 5 boroughs scaffolded"** instead of "Bronx demo." Click any pin in any borough → real narration.
- Cost: ~2 hours of curation. Can ship today before the noon checkpoint if started immediately.
- Risk: low. Infrastructure already handles multi-borough events. The renderer doesn't care which borough a coordinate is in.
- **This is the recommended add.**

**Option C — IMPORT THE TUM 3D MODEL (full geometric scaffold)**
- Download 2.4 GB TUM glTF. Spike into Carson's renderer. Try to make 1M buildings render at frame rate.
- Cost: 6-12 hours of pipeline work, probably blows the 24-hour budget. Likely crashes or chokes the GB10 at runtime.
- Risk: HIGH. Could derail the entire demo.
- **NOT recommended for this hackathon.** Recommended for Phase 2 / post-hack.

### Recommended decision

**Take Option B** (curate events across all 5 boroughs, ship today). **Defer Option C to Phase 2 roadmap line in the script.** Update the 90s script line from *"Starting in the Bronx where hip-hop was born"* to *"All five boroughs are seeded. We're demoing the Bronx hip-hop slice because it's the most cinematic."* That single phrase upgrade earns the "all of NYC" claim without any new geometry.

**Phase 2 roadmap addition (also recommended for the script)**: "Phase 2 grounds every narration in NYPL's NYC Space/Time Directory — 5,000+ georectified historical street maps 1850-1950, plus the BUILDING_HISTORIC dataset of every demolished building in the five boroughs."

**Owner of decision:** Alex (post-standup or now).
**Reversible by:** Sat noon if curating events. After that the seed file is locked.

---

## 2026-04-11 ~14:00 ET — Product wedge framing locked: receipts not predictions

**Decision:** The defensible product wedge underneath the cultural memory experience is a **non-ML historical-truth layer** assembled from public open data. We do NOT add predictive ML / gentrification forecasting / migration prediction to the build. Every claim is traceable to an open data record. The user-facing tagline: *"We don't predict gentrification. We trace it."* Full wedge breakdown (4 data layers + 5 sellable buyer segments + Marvens's particle role) lives in `docs/PRODUCT_WEDGES.md`.
**Alternatives considered:**
- Adding ML/prediction overlays for migration or gentrification forecasting (rejected — predicting gentrification IS gentrification; the room reads predictive overlays as extraction; weakens both the thesis and the political defensibility)
- Treating the project as a museum/tour-guide product only (rejected — caps buyer pool to grant-funded preservation orgs, doesn't justify Antler-grade investment thesis)
- Pivoting away from cultural memory toward pure real estate analytics (rejected — kills the emotional onramp that makes the data layer memorable; the cultural memory experience IS the marketing wedge for the data product)
**Why:** The room (Spark Hack judges + Antler GPs + community-data audience) is screaming for the opposite of cloud extraction. ML prediction layered on community displacement data IS the extraction we're claiming to fight. The defensible move is to surface receipts that already exist, anchor them to historical events, and let users draw their own conclusions. This is also the framing that makes the GB10 sponsored-product flex coherent end-to-end: local hardware → local memory → local sovereignty → no model trained on community pain. The four layers (demolitions, demographic shift, evictions, alterations) all live on top of the existing data spine — no new infrastructure required. Marvens's particle effects become data tracers (documented historical movements) rather than predictive overlays.
**Owner:** Alex.
**Reversible by:** N/A — this is a thesis-level commitment, not a build constraint. Reversing it would require rewriting the pitch and the moat story.

---

## 2026-04-11 ~14:00 ET — Visual direction doc locked (PS2 as constraint language)

**Decision:** PS2 aesthetic is a **constraint language for memory, not a 3D world the user walks through.** The map stays a flat social interface (Mode A — Lobby). PS2 only kicks in inside the ghost encounter (Mode B — Dungeon). Six SMT3 Nocturne reference images locked into `docs/refs/visual/` with NOTICE.md fair-use disclaimer. Full direction doc at `docs/VISUAL_DIRECTION.md`. Sent-ready HTML version with embedded reference images at `~/Desktop/sixth-borough-visual-direction.html`.
**Alternatives considered:**
- Pure 3D walkable world from the start (rejected — kills the social map interface that James shipped, multiplies asset budget, drowns the cultural data layer in geometry)
- PS2 styling on the map view itself (rejected — clashes with deck.gl/maplibre's clean cartographic register; map needs to read as data, not as game world)
- Skipping the visual reference doc and hoping verbal direction lands (rejected — Marvens needs concrete reference images to lock the constraint contract)
**Why:** The Mode A (lobby) ↔ Mode B (encounter) split lets each render style do what it's best at. The map is for browsing the city's data, the encounter is for being inside one specific memory. PS2 as a constraint language (low poly, vertex lighting, fog falloff, affine texture warping, 256×256 textures, vertex normals only) is what makes the ghosts feel like memories rather than 3D models — the constraints ARE the aesthetic argument. The visual direction doc gives Marvens a concrete spec without locking him into specific meshes.
**Owner:** Alex (the framing), Marvens (the meshes), Carson (the shader).
**Reversible by:** Sat afternoon if Marvens pushes back on the constraint set. After Sat night, the contract is locked.

---

## (add new decisions below this line as they happen)
