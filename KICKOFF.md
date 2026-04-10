# Sixth Borough — Kickoff Brief

*Drop this into your Claude Code session as priming context. Read once at the start, refer back as needed. If you change anything material in this doc, post it in the team chat so all four of us stay aligned.*

**Team:** Alex Wu · Carson Weeks · James Burke · **Marvens Destiné**
**Event:** Spark Hack Series NYC · Apr 10–12 2026 · 33 W 17th St
**Track:** Cultural Impact
**Hardware:** Acer Veriton GN100 (which IS a DGX Spark / GB10 Grace Blackwell box, 128 GB unified memory, one machine)
**Code freeze:** Sun Apr 12, 11:00 AM HARD
**Repo:** TheApexWu/sixth-borough (renaming from sixth-borough-draft at kickoff)

---

## Table of Contents

1. [TL;DR (30 seconds)](#tldr-30-seconds)
2. [The 4 Pillars (Core Identity)](#the-4-pillars-core-identity--do-not-break-these)
3. [How The Pillars Synthesize](#how-the-pillars-synthesize-the-product-loop)
4. [The Demo We're Shipping](#the-demo-were-shipping-the-3-min-video-story)
5. [Scope: IN vs OUT](#scope-what-we-build-vs-what-we-cut)
6. [The Stack (pinned)](#the-stack-pinned-dependency-age-rule-audited-apr-10-evening)
7. [Repo Skeleton](#repo-skeleton)
8. [Roles (Alex / Carson / James / Marvens)](#roles-who-owns-what)
9. [Risks + Mitigations](#risks--mitigations)
10. [Dual Pitch (NVIDIA vs Antler)](#dual-pitch-nvidia-judges-vs-antler-partners)
11. [Words That Must Appear In The Demo Video](#words-that-must-appear-in-the-demo-video)
12. [Sat 4:30 PM Progress Checkin Gate](#sat-430-pm-progress-checkin-gate)
13. [Sun 11 AM Submission Checklist](#sun-11-am-submission-checklist)
14. [Quick Start Commands](#quick-start-commands-on-the-gn100)
15. [Open Items](#open-items-dont-lose-track)
16. [The North Star](#the-north-star-one-sentence)

---

## TL;DR (30 seconds)

Sixth Borough is a **time machine for niche subcultures, covering all five boroughs of New York City**. You drop into any neighborhood across NYC, scrub a year slider through decades of history, and watch the place morph through eras in a deliberately PS2-style visual language that evokes memory rather than realism. You toggle a niche filter — hip-hop heads, queer history, demolished theaters, jazz, salsa, immigration flow — and the system surfaces only the cultural events, places, and people that matter to that lens, narrated in real time by a Nemotron-3-Nano language model running locally on the box. Everything runs on one machine with the ethernet cable on the floor. **The architecture is universal across all five boroughs.** The demo cinematic we're filming for the 3-min video is **one specific worked example**: the Bronx hip-hop birthplace lens, 1973–1985, anchored at 1520 Sedgwick Avenue — chosen because it's a single, mythologized, easy-to-narrate vertical slice that proves the system works. The visual identity layer (point cloud rendering of historical photos, era-conditioned PS2 post-process) is being driven by Marvens Destiné, who has shipped this kind of work at scale (ODESZA tour, 2M+ concert audience).

---

## The 4 Pillars (Core Identity — do not break these)

These are the four product-identity attributes that make Sixth Borough what it is. Every decision should preserve all four. If a proposed change breaks one of them, the change is wrong, not the pillar.

### Pillar 1 — TIME MACHINE
The primary user navigation is a **chronological year slider**. Not a feature on the side panel. The slider is the input modality — you move through space by clicking the map and through cultural depth by dragging time. Era boundaries are felt, not announced; the visual language morphs as you scrub. The methodological identity is **archaeological** — every year is a stratigraphic layer, every artifact is a record from a layered municipal/cultural archive, and the time machine literally is a dig.

### Pillar 2 — PS2 MEMORY AESTHETIC
Rendering is deliberately PS2-era: Sobel edge detection, palette quantization, vignette, low-poly textures, slight chromatic aberration. Era-conditioned — the renderer takes a year and returns a palette/post-process parameter set. **Marvens owns the visual identity for this pillar.** Point cloud rendering of historical photos (his ODESZA-tour technique) is the killer mechanic for "computational ghosts" — historical buildings as point cloud overlays on the modern coordinate. **The aesthetic is not retro for nostalgia. It's retro because memory looks like that.** Photorealism is a mismatch for cultural memory. Dream-logic visual styling is how the brain stores a place.

### Pillar 3 — CULTURAL INTELLIGENCE
The depth layer of meaning draped over the chronological bones. Every (place, year) has events, people, scenes, lineages, openings, deaths, inventions, demolitions, displacements. This is what makes the time machine *not empty*. It's also the layer that requires the most curation. The system architecturally supports a large cultural graph; the demo populates a vertical slice (Bronx hip-hop, 1973–1985) by hand.

### Pillar 4 — NICHE DISCOVERY
Filter-driven access for subcultural circles. The user picks a lens (hip-hop heads / queer history / demolished landmarks / immigration flow / jazz / salsa / theater) and the system surfaces only what's tagged for that lens. **This is the anti-overload mechanism.** Without niches, the time machine is a database that drowns the user. With niches, it's a discovery tool. It's also the wedge market — the first audience is one specific subculture, not "everyone who likes history."

### Why these four and not others
- **Open data is implicit in Pillar 3** — it's where the bones come from, but it's not a user-facing identity attribute
- **Hardware (DGX Spark, local-first) is the substrate, not a pillar** — it's how Pillars 1–4 run, not what they are
- **Archaeology is the methodology of Pillar 3** — the framing for how the data layer is built, lives inside Cultural Intelligence

---

## How The Pillars Synthesize (the product loop)

This is the actual user flow. Imagine watching it on stage Sunday.

```
USER drops a pin on the Bronx
       │
       ▼
Default view: modern Bronx, Sobel-rendered, 2026 palette
       │
       │ user drags time slider 2026 → 1960
       ▼
[Pillar 1: TIME MACHINE]
[Pillar 2: PS2 AESTHETIC + POINT CLOUD GHOSTS]
The renderer morphs era by era — palette desaturates, textures
degrade, the South Bronx burning visual cue kicks in around 1977,
demolished buildings come back as point cloud ghost overlays
as the slider passes their demolition years.

       │  pretty, but EMPTY — that's the point
       ▼
USER toggles "Hip-hop heads" niche filter ON
       │
       ▼
[Pillar 3: CULTURAL INTELLIGENCE]
[Pillar 4: NICHE DISCOVERY]
Pins start appearing as the slider passes their activation years:
   1973 — 1520 Sedgwick lights up
   1975 — T-Connection, Black Door, Webster PAL
   1977 — Bronx River Houses (Bambaataa)
   1978 — Disco Fever
   1979 — Sugar Hill marker
   1982 — Wild Style filming locations

       │
       ▼
As each pin lights, NEMOTRON-3-NANO (running locally on the GN100)
narrates the moment in 2-3 sentences, conditioned on:
   - the year
   - the niche (hip-hop voice, not generic history voice)
   - the specific event (its narration_seed)
   - the era visual mode

       │
       ▼
USER toggles "Hip-hop" off, toggles "Immigration flow" on
       │
       ▼
Same map, same slider, totally different pins. Cross Bronx
Expressway displacement, Operation Bootstrap waves, redlining.

       │
       ▼
USER toggles "Demolished theaters" on
       │
       ▼
The Loew's Boulevard, Bronx Opera House, Windsor Theater appear
as point cloud ghost overlays on the modern street view.
```

**The pitch line for this loop:** *"Every niche is a different lens. Same time machine, same place, infinite cultural depth, all running on one box with the cable on the floor."*

---

## The Demo We're Shipping (the 3-min video story)

The architecture is universal across all five boroughs of NYC. For the 3-minute submission video, we lock to ONE cinematic worked example to keep the story tight. The example is intentionally one of the most mythologized vertical slices in the city — it proves the system, but the system is not restricted to it.

**Cinematic worked example:** Bronx, 1973–1979, hip-hop birthplace lens. Chosen because it's specific, dated to a single address (1520 Sedgwick Avenue), narratively cinematic, and the kind of story judges remember. Other example slices the system supports out of the same architecture: Lower East Side immigration flow, Greenwich Village queer history, Harlem jazz lineage, Spanish Harlem salsa scene, Brooklyn industrial waterfront, Queens punk warehouses, Staten Island ferry-era working-class history.

**Beat by beat:**

1. **(0:00 – 0:30) Team intro.** Four names, four roles, one sentence each. Alex (orchestration + narration), Carson (Rust + wgpu engine), Marvens (3D / point cloud / visual identity), James (cultural curation + WebGL fallback).
2. **(0:30 – 1:00) Elevator pitch.** "Sixth Borough is a time machine for niche subcultures. We start with hip-hop in the Bronx — the most-mythologized scene in NYC, mapped to coordinates for the first time, rendered in the visual language of the era it belongs to. Everything runs on a single DGX Spark with no internet."
3. **(1:00 – 2:30) Live demo.**
   - Drop pin on the Bronx, modern view
   - Drag slider back to 1973
   - Watch the renderer morph era through Sobel + palette change + point cloud ghosts of demolished buildings appearing
   - Toggle "Hip-hop heads" filter
   - Click 1520 Sedgwick — Nemotron narrates the night Kool Herc invented the breakbeat
   - Drag forward through 1975 → 1979, watch additional pins light up
   - Quick toggle to "Immigration flow" to demonstrate the architecture handles other niches (don't dwell)
4. **(2:30 – 3:30) Build narration.**
   - Architecture: temporal cultural graph + era-conditioned PS2 renderer + point cloud ghost layer + niche-filtered narration loop
   - Hardware story: 128 GB unified memory holds the cultural graph, the Nemotron weights, the renderer scene, the point cloud assets, and the framebuffer in one address space
   - **The unplug-cable moment:** physically pull the ethernet cable, walk back, continue
   - Verbatim line: *"Everything you're about to see runs on the box, with the cable on the floor, because computational ghosts need local hardware."*
5. **(3:30 – 4:00) "So what?" close.**
   - "We built the wedge this weekend. The architecture is universal — every subculture is a new lens with the same renderer. Computational archaeology, niche by niche."

---

## Scope: What We Build vs What We Cut

### IN (architecture supports, demo populates)
- **Architectural support for all five boroughs of NYC.** The cultural events table, the renderer, the niche filter, and the narration loop are not borough-restricted. Any neighborhood can be added by extending the events JSON.
- Time slider with chronological era morphing on the renderer
- Niche filter UI with multiple toggleable lenses (hip-hop heads, queer history, demolished theaters, jazz, salsa, immigration flow, etc.)
- **Demo data slice (the worked example):** ~30 hand-curated hip-hop events from the Bronx, 1965–1985, anchored at 1520 Sedgwick Avenue
- **Architecture proof slices:** 1–2 events each for several other niches across multiple boroughs, to show the system is not restricted to one place or one lens
- Nemotron-3-Nano narration server on `:30000`, niche-conditioned prompt template
- PS2 post-process pipeline (Sobel + vignette + palette quant)
- **Point cloud ghost layer:** 3–5 demolished landmarks across the city rendered as point cloud overlays on the modern coordinate. Blender → point cloud export → renderer ingest pipeline. This is the killer Frontier Creativity move and the technique is exactly what Marvens has shipped at scale on the ODESZA tour.
- Unplug-cable physical demo
- Pre-recorded 30-second backup clip in case the live demo crashes
- README with architecture diagram + quick start
- 3–5 min YouTube demo video uploaded by Sun 10 AM
- Airtable submission by Sun 11 AM

### OUT (explicitly not in this weekend's scope)
- Live NYC Open Data ingestion pipeline at runtime (pitch as "the data layer scales next" — for the demo, the events JSON is hand-curated)
- Comprehensive coverage of all five boroughs in the seed data (architecture supports all five, the seed populates one cinematic slice + a handful of architecture-proof events from other boroughs)
- User accounts, save state, sharing, multiplayer
- Mobile responsiveness
- Calling any cloud LLM API for any reason (zeros us on NVIDIA Stack score)
- The OpenClaw bounty pivot (constrains the build, drops 5090 prize, not worth)
- Fine-tuning anything (we have 38 hours, use pretrained inference only)
- A real-time vision pipeline (Live VLM WebUI is dropped from scope unless Nemotron is up by Sat noon AND we have time)
- More than 5 demolished-building point clouds (quality > quantity)

---

## The Stack (pinned, dependency-age-rule audited Apr 10 evening)

| Layer | Tech | Notes |
|---|---|---|
| Hardware | Acer Veriton GN100 (DGX Spark / GB10 Grace Blackwell, 128 GB unified) | One machine, local-only |
| OS | DGX OS | Provided |
| Narration LLM | Nemotron-3-Nano-30B-A3B (Q8_K_XL GGUF) | NVIDIA model, 4 months old, ~38 GB |
| Narration runtime | llama.cpp built from source with `-DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES="121"` | Years old, mature |
| Narration API | OpenAI-compatible `/v1/chat/completions` on `:30000` | Standard |
| Renderer (primary) | Rust + wgpu (Carson) | Years old |
| Renderer (fallback) | WebGL + Three.js, James's `feature/sketch-overlay` branch | Years old, has 8-era cutscenes |
| Post-process | Sobel edges + vignette + palette quantization | Same in both renderer paths |
| **3D / Point cloud authoring** | **Blender (Marvens)** + custom export pipeline | Years old, Marvens's primary tool |
| **Point cloud runtime** | **PLY / SPLAT format ingested by the renderer** | Standard format, both Rust/wgpu and Three.js can render it |
| Cultural graph | Static JSON file (`data/events-bronx-hiphop-seed.json`) | Hand-curated, ~30 events for the demo |
| Niche filter UI | Toggle list / dropdown in the orchestrator frontend | Simple, one shipping niche + placeholder buttons |
| Orchestrator | Python (FastAPI) or Node — either is fine | Years old |
| Data source | NYC LPC, Wikimedia Commons, Bronx Historical Society (cited, not live-parsed) | Public domain / open data |

**Dependency age rule (announced at orientation):** every open source dependency must be ≥2 weeks old as of Apr 10 2026. NVIDIA / Nemotron stuff is exempt per orientation guidance. Audit complete — every item above passes (Blender is 20+ years old). If anyone wants to add a new dependency mid-build, **the new dep must be ≥2 weeks old or it doesn't ship.** No "I just found this perfect new library" at midnight.

---

## Repo Skeleton

```
sixth-borough/
├── KICKOFF.md              ← this file (read first)
├── README.md               ← project intro, thesis, quick start
├── ARCHITECTURE.md         ← system diagram + data flow
├── .gitignore
├── docs/
│   ├── EVENT_RULES.md      ← Spark Hack rules, scoring, deadlines, dependency age rule
│   ├── TEAM_CONTEXT.md     ← comprehensive priming context (older, supplanted by KICKOFF.md)
│   ├── STACK.md            ← pinned tech with verbatim setup commands
│   └── DECISIONS.md        ← decision log
├── data/
│   └── events-bronx-hiphop-seed.json   ← ~30 hand-curated cultural events for the demo
├── assets/
│   └── pointclouds/        ← Marvens's Blender point cloud exports (gitignored, large)
├── scripts/
│   ├── setup.sh            ← one-shot setup on the GN100
│   ├── start.sh            ← start narration server
│   └── test-narration.sh   ← API smoke test
├── pitch/
│   └── antler-90sec.md     ← the verbatim Antler unicorn pitch
├── src/                    ← application source
│   ├── renderer/           ← Carson's Rust + wgpu (or symlink to James's WebGL fallback)
│   ├── orchestrator/       ← Python/Node, time slider + niche filter UI + narration calls
│   └── data/               ← schema, niche taxonomy, era visual modes
└── pointcloud-pipeline/    ← Marvens's Blender → renderer export tooling
```

---

## Team — what each of us brings

This is a description of skills and natural areas of ownership, not a top-down task assignment. Specific work splits get worked out between us during build, in chat or in person. Use this section to know who to ping for what.

### Alex Wu
- Orchestration, LLM narration loop, prompt design
- Cultural events curation (hand-writing the seed JSON, sourcing historical references)
- Pitch writing, demo video script, Airtable submission
- General product direction, cross-team coordination

### Carson Weeks
- Rust + wgpu / Bevy renderer engineering
- PS2 post-process shaders (Sobel, vignette, palette quantization)
- Era-conditioned visual mode switching
- Point cloud ingest into the renderer
- Performance + frame rate optimization

### Marvens Destiné
- 3D / point cloud / visual identity (Blender, Cinema 4D, After Effects veteran)
- Point cloud pipeline for demolished-building ghost overlays — exactly the technique he shipped on the ODESZA Concert Visual Tour (June 2024, 2M+ concert audience)
- Visual polish, color palette + texture direction, era aesthetic calibration
- Antler relationships (he's an Antler member — useful for the unicorn bounty pursuit)
- Blender runs on his own laptop; point cloud assets export to the repo for the renderer to ingest

### James Burke
- Cultural curation + archaeology framing (his background)
- WebGL fallback path: the `feature/sketch-overlay` branch with 8-era cutscenes is real, working, and a credible safety net if the Rust renderer needs more time
- Historical photo / archive sourcing for the point clouds (knows what has good visual references)
- Cultural graph schema co-ownership

### How we coordinate
- **KICKOFF.md (this doc) is the shared single source of truth.** If anything material changes — scope, stack, demo content, decisions — update this file in place AND post in team chat so all four of us stay aligned.
- **DECISIONS.md** is an append-only log of build decisions. Add to it when you make a non-obvious call.
- **Sat 4:30 PM Progress Checkin** is the only scheduled feedback window. We sync as a team there.
- **Direct DM > all-hands** for fast questions during build.

---

## Risks + Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Nemotron-3-Nano 38 GB download fails on venue wifi | High | Critical (no narration = no demo) | Start FIRST after box checkout. Resumable. Phone hotspot fallback. Q4_K_M smaller fallback. Worst case: smaller Ollama model already on disk. |
| Carson's Rust/wgpu renderer doesn't compile or stabilize on the GN100 | Medium | High (no PS2 visual = weaker demo) | Sat 4 PM hard pivot to James's WebGL pipeline. Don't wait until Sat night. |
| Point cloud pipeline (Blender → renderer ingest) doesn't make it in time | Medium | Medium | Marvens picks ONE landmark to ship, not five. The mechanic only needs one working example for the demo. Pre-export Friday night if possible. |
| Time slider scope creep (try to support too many niches) | High | Medium (drains energy from the core loop) | ONE niche fully populated (hip-hop). Other niches are 1-2 placeholder events. Lock in DECISIONS.md. |
| Demo crashes live during the 3-min video record | Medium | Critical | Pre-record a 30-second backup clip Sat night. Use it as emergency cut-in. |
| Sun 11 AM submission upload fails on bad wifi | High | Critical (no submission = no judging) | Start the YouTube upload at 9 AM Sun, not 10:55. Use phone hotspot if needed. |
| Team forgets to say the Spark Story words on camera | Medium | High (loses 15 of 30 NVIDIA points) | Words list in this doc. Read aloud before each take. |
| Sleep deprivation by Sun morning destroys the pitch | High | High | Mandatory sleep windows: Sat 2-8 AM, Sun 2-8 AM. Non-negotiable. |
| OOM on the GN100 even with 128 GB headroom | Medium | Medium | Run `sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'`. UMA buffer cache caveat. |
| Cartewei integration framing unresolved | Low | Low (cosmetic) | Doesn't affect technical scope. Resolve after talking to James. |
| 4-person coordination overhead | Low | Low | Marvens joining late means one extra context-load. KICKOFF.md (this doc) is the inoculation. |

---

## Dual Pitch (NVIDIA judges vs Antler partners)

**Same product, two audiences, two pitches. Use the right one for the room.**

### For NVIDIA Systems Engineering judges
> "Sixth Borough is a temporal cultural graph database with niche-filtered query, an era-conditioned PS2 renderer with point cloud ghost overlays of demolished buildings, and a niche-conditioned narration loop, all running on one Acer Veriton GN100 with the ethernet cable on the floor. We use Nemotron-3-Nano-30B-A3B via llama.cpp on the GB10's sm_121 architecture. The 128 GB unified memory holds the cultural graph, the model weights, the renderer scene, the point cloud assets, and the framebuffer in one address space — no copies between GPU graphics and GPU inference. Pull the cable. The system keeps working. That's the point."

### For Antler partners (and any Antler folks Marvens introduces us to)
> "Sixth Borough is a discovery layer for cultural depth, built for niche subcultural circles. We start with hip-hop heads in the Bronx — the most-mythologized scene in NYC, mapped to coordinates for the first time, rendered in the visual language of the era. The wedge is one passionate subculture. The expansion is every other one — queer Village, downtown art, salsa Spanish Harlem, jazz Harlem, punk Bowery. Every new niche compounds the cultural graph and reuses the same renderer. The hardware story isn't a gimmick: a local-first cultural memory layer can ship as a physical museum kiosk, an in-car experience for tourism boards, or a private app for collectors who don't want their cultural fingerprint sitting in someone's training data. We're building the wedge this weekend on a DGX Spark because the system needs to hold the entire cultural graph + the renderer + the point cloud assets + the narration model on one box, with the cable on the floor. Computational ghosts need local hardware."

Full Antler pitch lives at `pitch/antler-90sec.md`.

---

## Words That MUST Appear In The Demo Video

These words have to be said on camera. If they're not said, we lose 15 of the 30 NVIDIA Ecosystem points. Read this list aloud before each take.

- "DGX Spark"
- "GB10 Grace Blackwell Superchip" (or "GB10 chip")
- "128 gigabytes of unified memory"
- "Nemotron-3-Nano"
- "running locally"
- "no internet connection at runtime"
- The unplug-cable line: *"Everything you're about to see runs on the box, with the cable on the floor, because computational ghosts need local hardware."*
- (New) **"point cloud"** — name the technique by name when showing the demolished building ghost overlays

---

## Sat 4:30 PM Progress Checkin Gate

This is the only scheduled mentor/judge feedback window of the weekend. Useful targets to have running by then so we can show real progress:

- Nemotron narration server up on `:30000` and responding to test prompts
- One renderer path running with a single scene + Sobel post-process
- Time slider working — drag year, scene visually morphs
- Niche filter UI exists with at least one fully wired niche
- A handful of hip-hop events in the seed data and one working narration call from a clicked pin
- At least one demolished-building point cloud loaded into the renderer
- Rough plan for the demo video locked

If we're not all the way there by 4:30, the Sat night → Sun morning push becomes "polish what works, drop what doesn't."

---

## Sun 11 AM Submission Checklist

In order, the things that must be true at 11:00 AM Sun:

1. ☐ Demo video uploaded to YouTube (unlisted), 3–5 min, contains all the Spark Story words above
2. ☐ Repo public on GitHub with README updated, architecture diagram, quick start, datasets cited, known limitations
3. ☐ Airtable form filled out with: team name, project description, Cultural Impact track selected, video URL, repo URL, deployed URL (or screen capture), team roster (4 names: Alex / Carson / James / Marvens)
4. ☐ Backup: at least one team member has the Airtable receipt screenshot
5. ☐ Pitch script for the in-person Hack Fair table rehearsed once
6. ☐ Hardware ready to walk to the Hack Fair station

**Start the YouTube upload at 9 AM Sun, not 10:55.** Bad wifi makes the upload the riskiest single moment of the morning.

---

## Quick Start Commands (on the GN100)

```bash
## clone the repo
git clone https://github.com/TheApexWu/sixth-borough.git
cd sixth-borough

## one-shot setup (downloads Nemotron weights ~38 GB, builds llama.cpp)
./scripts/setup.sh

## start the narration server (foreground, leave running in tmux)
./scripts/start.sh

## smoke test from another terminal
./scripts/test-narration.sh
```

If `setup.sh` fails on the model download, see `docs/STACK.md` for fallback to Q4_K_M and the manual steps.

For the **point cloud authoring pipeline**, Marvens runs Blender on his own laptop and exports PLY/SPLAT files into `assets/pointclouds/`. The renderer ingests them at runtime. Pipeline tooling (if any) lives in `pointcloud-pipeline/`.

---

## Open Items (don't lose track)

- **Cartewei framing:** unresolved, pending Alex's conversation with James in person at the venue. The architecture doesn't depend on Cartewei being mentioned, but if James wants to position Cartewei as the upstream data extraction layer for Sixth Borough, the events JSON file is exactly the kind of structured output Cartewei could produce. Decide and update DECISIONS.md once James weighs in.
- **Marvens onboarding:** he joined the team Apr 10 evening. The first 30 minutes Friday night should be Alex walking him through this KICKOFF.md doc + the 4 pillars + the demo cinematic. Once he's primed, he can spin up Blender immediately and start sourcing historical photos.
- **Marvens's Antler relationships:** he's a member of Antler. Find out which partners he knows. Most useful intros: Wouter Hiemstra (Alex already has prior context), the partner in charge of US-S26 evaluations.
- **Judge list:** unknown. Find out at check-in or in #spark-hack-nyc Discord.
- **Mentor list:** unknown. Same.
- **Power / room layout:** unknown. Find out at check-in.
- **Antler unicorn bounty active pursuit:** yes, lean in. Marvens is an inside ally — coordinate floor strategy with him.
- **OpenClaw bounty:** dropped per Apr 10 PM decision. Do not pivot back.
- **Pensar bounty (Least Likely to Get Hacked):** opportunistic only. If we have time Sat night, run Pensar on the build for the $500 + $500 credits. Don't reshape architecture for it.
- **BlenderBin (Marvens's startup):** acknowledge it as Marvens's day-job context. Sixth Borough is not a BlenderBin product. But if there's a clean cross-promotion (e.g., a Blender plugin from Sixth Borough's pipeline), worth a 2-line mention in the Antler pitch as "and Marvens runs his own Blender SaaS, BlenderBin." Don't force it.

---

## The North Star (one sentence)

**Sixth Borough is a time machine for niche subcultures, rendered in the visual language of memory, running on hardware that lets you pull the cable.**

If a decision feels confusing during the build, come back to that sentence and ask: does this make the time machine deeper, the niche discovery sharper, the PS2 aesthetic stronger, or the local-only thesis more credible? If yes, ship it. If no, cut it.

---

*Last updated: Apr 10 2026 evening, kickoff (Marvens added as 4th teammate). Update this file in place if anything material changes — do not let it drift.*
