# Demo Video Script — Cross-Bronx Anchored (Session 44 Pivot)

> **Drafted Apr 11 ~22:00 ET (Session 44, post-pivot, after Carson left).** This is the third companion script to `DEMO_VIDEO_SCRIPT.md` (original locked Apr 11 morning) and `DEMO_VIDEO_SCRIPT.A_PLUS_B.md` (Session 43 A+B rewrite). This version anchors the entire 90 seconds on the Cross-Bronx Expressway → 1520 Sedgwick → hip-hop birth causal arc, with the 3D map + year slider + migration cone as the visual hero.
>
> **Why this version exists**: Sessions 42 and 43 framed Sixth Borough as "cultural memory infrastructure on local hardware" and "one engine, two surfaces." Both true. But Alex's Session 44 pivot is sharper: instead of "look at all this NYC data with literary captions," the demo is a single causal arc anchored on a single address. Cross-Bronx Expressway 1948-1972 → 60K displaced → families pushed onto Sedgwick Avenue → 1520 Sedgwick rec room → August 11, 1973, DJ Kool Herc invents hip-hop → cultural memory is what survives the bulldozer. ONE story, ONE click, ONE chain.
>
> **What changed from the previous scripts**:
> - Cold open is unchanged (sponsor verbatim phrases stay locked)
> - The CLAIM beat is replaced with the MAP beat — describes the 3D map + year slider as a time machine you can drag, not as a chart
> - The DEMO beat is restructured: scrub year slider 1948→1972 to visually empty the Cross-Bronx corridor, fire the migration cone, THEN click 1520 Sedgwick for the narration. The drag is now the verb, not the click.
> - Q&A adds the unicorn-bounty number row (NYC right-to-counsel + Rule 1.6 + 20K cases + $600 paralegal cost)
> - Three off-stage 1:1 versions added: 90s stage / 2-min Antler / 30s civic
>
> **Status**: companion file held in working tree, not yet committed. Replaces both prior scripts if team validates Sun morning.

---

## The thesis (one sentence, locked Session 44)

> **Sixth Borough is a 3D map of New York City you can drag through time. Click any building, get a thirty-second footnoted dossier on its life — generated locally by NVIDIA Nemotron 30B, no internet at runtime. The hero example is 1520 Sedgwick Avenue: the rec room where DJ Kool Herc invented hip-hop, in a building that was full because Robert Moses's Cross-Bronx Expressway had displaced sixty thousand South Bronx families onto a few blocks of Sedgwick. We don't predict gentrification. We trace it from the receipts. Cultural memory is what survives the bulldozer.**

That's the spine. Every other line in this script comes back to it.

---

## The 90-second stage script

Sponsor verbatim phrases **bolded**. Per `docs/EVENT_RULES.md`, these earn the 15-point Spark Story score. Do not paraphrase. Word count target: ~225 spoken words at 140 wpm = ~95 sec, plus ~25 sec of silent visual beats (slider drag, cone fire, narration read) = ~95-105 sec total runtime.

### [OPENING — 12 sec. Stand next to the GN100. Tap the case on the second sentence.]

> "Sixth Borough is New York City's memory, localized in one box. One **DGX Spark**. One **GB10 Grace Blackwell Superchip**. **128 gigabytes of unified memory**. **Running locally**. **No internet connection at runtime**."

**Beat**: hardware tap is the most important physical action of the entire demo. When you say "this box," your hand must touch the GN100. Practice standing up.

### [THE MAP — 18 sec. Walk to the screen. The 3D map of NYC is already on display, year slider at 2026.]

> "This is every building in New York City, extruded to its real LiDAR-measured height, color-coded by architectural era. The slider at the bottom is the year. Drag it back to 1948."

**[Drag year slider from 2026 → 1948 in one continuous motion, ~5 seconds. Buildings appear and disappear at their actual construction and demolition dates. The 8-era color bands shift across the map. Don't narrate during the drag — let the map do the work.]**

**Why this beat works**: it shows the engine doing complex pipeline work (1+ million building polygons rendered against historical year filters in real time on the GB10's unified memory) without saying anything about the engine. The judge sees it move and infers the work. Verbs > adjectives.

### [THE CROSS-BRONX BEAT — 22 sec. Eye contact on the displacement number.]

> "1948. Robert Moses begins demolishing 159 buildings to push the Cross-Bronx Expressway through the South Bronx. Watch."

**[Drag year slider 1948 → 1972 slowly, ~6 seconds. The Cross-Bronx corridor visibly empties out — buildings vanishing from the map at their real demolition dates from NYC Building Footprints Historical Shape (`s5zg-yzea`). Marvens's migration cone fires: a particle stream flowing along the corridor toward Sedgwick Avenue, scaled to documented displacement counts. ~6 sec of pure visual.]**

> "Sixty thousand people displaced over twenty-four years. Every particle is a documented person. Real DOB demolition records. Real ACS census data. They were pushed onto a few blocks of Sedgwick Avenue."

**Why this beat works**: it's the moment a person stops thinking "cool data viz" and starts thinking "wait, what just happened to that neighborhood." The number 60,000 is from Caro's "The Power Broker" (1974). It's the most-cited displacement number in NYC urban renewal history. Use it without hedging.

### [THE CLICK — 25 sec. Move closer to the screen. Don't narrate the click.]

> "August 11, 1973. 1520 Sedgwick. The rec room of the building that was full because of the displacement you just watched."

**[Click the pin for `bronx-1973-08-11-sedgwick`. The Nemotron narration streams in on screen, generated live by the local 30B model. STAY SILENT for 8-12 seconds while the judges read. This is the most important silence of the entire demo.]**

> "That text was just generated by a 30-billion-parameter model from **NVIDIA's Nemotron model family**, running on this box, ten feet from you, in the last 30 seconds. The map you scrubbed, the cone you watched, the photo of the rec room, the model that wrote the narration — all local. Nothing left the room."

**Why this beat works**: the narration is the payoff after the visual setup. The visual setup made the displacement visceral; the narration humanizes it with one specific moment (a single rec room party). The "all local" line is the technical brag landed at the moment the audience is most receptive.

### [CLOSE — 13 sec. Tap the GN100 case again. Eye contact. Slow down. Land it.]

> "We don't predict gentrification. We trace it from the receipts. Hip-hop was born inside the trauma of urban renewal. Cultural memory is what survives the bulldozer.
>
> **Computational ghosts need local hardware**."

---

## Word count + timing

| Beat | Spoken words | Speak time @ 140 wpm | Silent visual time |
|---|---|---|---|
| Opening (hardware tap) | 33 | ~14 sec | — |
| The Map (slider intro) | 35 | ~15 sec | ~5 sec drag |
| The Cross-Bronx beat | 50 | ~21 sec | ~6 sec slider + cone |
| The Click | 60 | ~26 sec | ~8-12 sec narration read |
| Close | 32 | ~14 sec | — |
| **Total** | **210 spoken** | **~90 sec speak** | **~19-23 sec visual** |
| **Total runtime** | — | — | **~109-113 sec** |

**This runs ~110 sec, slightly over the 90 sec target.** Cut points if you need to land in 95 sec:
1. Drop the second clause of the Cross-Bronx beat ("Real DOB demolition records. Real ACS census data.") — saves ~6 sec
2. Cut the silent narration read from 12s → 8s — saves ~4 sec

Most likely the recorded video runs 100-105 sec. The Demo Video Instructions sub-page from Notion (still TBD) probably allows 90-180 sec. Assume 180 cap, target 100, leave headroom.

---

## Sponsor verbatim phrases checklist

Same as the original script. The recorded video MUST contain all of these to score the full 15 Spark Story points:

- [x] **DGX Spark** — opening
- [x] **GB10 Grace Blackwell Superchip** — opening
- [x] **128 gigabytes of unified memory** — opening
- [x] **Running locally** — opening
- [x] **No internet connection at runtime** — opening
- [x] **NVIDIA Nemotron** (model family attribution) — demo postscript ("from NVIDIA's Nemotron model family")
- [x] **Computational ghosts need local hardware** — close (the wedge line)

---

## Q&A pivots (the unicorn bounty answer is now baked in)

| Question | Answer |
|---|---|
| **"Who's the customer?"** | "First paying customer is NYC tenant lawyers. New York's right-to-counsel expansion in 2022 gave 20,000 new tenant cases per year guaranteed legal representation. Each case requires a building history that takes a paralegal 6 hours to assemble from 8 different city databases. That's $600 of paralegal time per case, $12 million a year of redundant labor across the legal aid system. We do it in 30 seconds for $500 a month per attorney seat. Why this has to run locally is not ideology, it's Rule 1.6 of the New York Rules of Professional Conduct — client confidentiality. Tenant attorneys cannot upload privileged files to OpenAI. Local inference is a regulatory requirement, not a feature." |
| **"Could a city planner use this tomorrow?"** | "Tomorrow morning a tenant lawyer in the South Bronx can build a Cross-Bronx Expressway displacement case with footnoted DOB and ACS citations in the time it took her to make coffee. That's the entire wedge. Cultural orgs are the brand layer that opens the door — same engine, same hardware, same data spine, $3,000 box that the Bronx Historical Society can buy on a grant." |
| **"Why local? Cloud is faster."** | "Cloud is legally impossible for our buyer. Tenant attorneys are bound by Rule 1.6 of the NY Rules of Professional Conduct — they cannot upload privileged client files to OpenAI or Anthropic. Insurance underwriters cannot put proprietary risk models through GPT-4. REIT diligence teams cannot send deal-stage files through cloud LLMs. Three buyers, all compliance-locked to local inference. We're the only stack that gives them open NYC data plus private document ingestion plus a 30B reasoning model on a $3,000 box." |
| **"What's the ML story? Are you doing prediction?"** | "We deliberately don't predict. Predicting gentrification IS gentrification. We trace what already happened from the public record. The ML is NVIDIA Nemotron 30B from the Nemotron model family doing structured retrieval over 6 NYC Open Data datasets — Building Footprints, Building Footprints Historical Shape with construction_year and demolition_year, ACS census, NYPL Milstein photos, LPC landmarks, DOB violations. Plus templated synthesis. No forecasting layer. Every claim cites a public dataset row." |
| **"Why two models? Isn't that overengineered?"** *(if ComfyUI lands)* | "Two models because we have two surfaces. Nemotron handles the language work — extraction over court filings, caption generation. Stable Diffusion 1.5 with a 3DRenderStyle LoRA via ComfyUI handles the visual restylization on the same GB10. Both load into the same 128 GB unified memory. No team without unified memory could load both models plus a renderer plus the open-data corpus on a single box without copying tensors across PCIe." |
| **"How does this scale?"** | "Horizontally, by neighborhood and by buyer. One $3,000 box per community. The Bronx model belongs to the Bronx. We don't need a billion-parameter model trained on the whole world — we need a 30B model trained on a square mile, paired with NYC Open Data, on a box any law firm or library can buy outright. Eighteen-month roadmap: 100 NYC tenant attorneys at $500/mo is $600K ARR, year two REIT and insurance in NYC is $5M ARR, year three is 5 cities at $25M ARR." |
| **"What are the numbers?"** | "**Twenty-nine tokens per second** sustained generation on a 30B Q8 reasoning model on local hardware. **Sixty megabytes** of browser-deliverable payload carries 175 years of NYC building biography across 5 boroughs. **128 gigabytes** unified memory holds Nemotron + the building footprint corpus + the renderer simultaneously. **Zero** network round trips at runtime. **One million fifty-three thousand seven hundred thirteen** buildings indexed from NYC Open Data Building Footprints `5zhs-2jue`. **Twenty thousand** new NYC tenant cases per year post-right-to-counsel. **Six hours** of paralegal time per case, currently. **Thirty seconds** of local inference, with Sixth Borough." |
| **"What about the other boroughs?"** | "All five are in the data spine. 750 NYPL Milstein archival photos georeferenced across all 5 boroughs, 150 each, 1900-1956. Manhattan and Bronx are 3D-extruded; the other three boroughs are loading. We're demoing the 1520 Sedgwick beat because it's the most cinematic single anchor, not because the architecture is Bronx-only." |
| **"Is this real or a demo?"** | "Real. Click any pin yourself." [Hand them the trackpad. Devastating move if the path is solid.] |

---

## Off-stage 1:1 framings

### Antler 2-minute version (memorize the first paragraph)

Use this with Wouter, Marvens's Antler ally, or any GP who walks up.

> "Sixth Borough is a forensic building intelligence engine that runs entirely on local NVIDIA hardware. The interface is a 3D map of New York City you can drag through time. Every building is extruded to its real LiDAR-measured roof height, color-coded by architectural era, and the year slider lets you scrub from 1700 to 2026. As you drag, buildings appear at construction year and disappear at demolition year. Migration cones fire along documented displacement corridors at the years displacement actually happened, scaled to real ACS census numbers. Click any building and you get a four-page footnoted dossier in 30 seconds — every owner since 1966, every demolition within a thousand feet, every alteration permit, every cultural event on that block, every displaced community, every historical photo. Generated locally by NVIDIA Nemotron 30B on the GB10 Grace Blackwell, no internet at runtime, no document leaving the room.
>
> First paying customer: NYC tenant lawyers. New York's right-to-counsel expansion in 2022 gave 20,000 new tenant cases per year guaranteed representation. Each case requires a building history that takes a paralegal 6 hours to assemble from 8 city databases. That's $600 of paralegal time per case, $12 million a year of redundant labor. We do it in 30 seconds for $500/month per seat.
>
> The reason this has to run locally is Rule 1.6 of the New York Rules of Professional Conduct — client confidentiality. Tenant attorneys cannot upload privileged case files to OpenAI. Same logic applies to insurance underwriters and REIT analysts. Three compliance-locked buyer segments, one engine.
>
> Why NVIDIA hardware specifically: the GB10's 128 GB unified memory holds the 30B reasoning model AND the 1.05 million record building footprint corpus AND the renderer state in one address space, zero PCIe round trips. The map renders interactive while the LLM does inference on the same box, sharing the same memory. Without unified memory you cannot do this on one box. The Acer Veriton GN100 is $3,000 retail — that price point matters because it's also within the grant budget of any small NYC cultural nonprofit.
>
> Hero example: 1520 Sedgwick Avenue. Robert Moses's Cross-Bronx Expressway displaced 60,000 South Bronx families starting in 1948. They were pushed onto a few blocks of Sedgwick. The crowding created the rec room party scene. August 11, 1973, DJ Kool Herc invented hip-hop in that rec room. Same engine that builds a tenant lawyer's evidence packet builds the cultural-memory printout for the Universal Hip Hop Museum. One product, two compliance-locked markets, one $3,000 box. Eighteen-month path: 100 NYC tenant attorneys at $500/month is $600K ARR. Year two REIT + insurance in NYC, $5M ARR. Year three 5 cities, $25M ARR.
>
> Founder is an NYU CS+Data Science grad from Queens. Shipped the 30B local stack in 36 hours on a box I'd never seen before. Technical credibility to build it, cultural literacy not to extract from the communities I'm telling stories about. Two hundred fifty K to land the first 100 attorneys and prove unit economics. That's the Antler check."

**~395 words, ~170 seconds at 140 wpm.** Memorize the first paragraph specifically — it's the "what is this" answer. The middle and end are connective tissue.

### Civic 30-second version

Use this with NYPL / Bronx Historical Society / civic-tech roamers.

> "Sixth Borough is a 3D map of New York City you can drag through time. Every building, every demolition, every displacement corridor, scrubbable from 1700 to today, all from public NYC datasets, rendered locally on a $3,000 Acer NVIDIA box. Click any building and a local model writes a footnoted history of the block in 30 seconds. The Bronx Historical Society can own the same hardware as a Wall Street REIT and run the same engine — same map, same data, same model — on a box they own outright, no upload to anyone's cloud. We don't extract community memory into a SaaS, we give the community the tool that produces the archive. Hero example is 1520 Sedgwick: Cross-Bronx Expressway, Kool Herc, hip-hop birthplace. Phase 2 partners we're approaching: Universal Hip Hop Museum, Cornell Hip Hop Collection, Bronx Historical Society. Computational ghosts need local hardware. The community keeps its own ghosts."

**~135 words, ~58 seconds.**

---

## Delivery notes (unchanged from prior scripts + 2 additions)

1. **The hardware tap is the most important physical action.** When you say "this box," touch the GN100. Practice standing up.
2. **Do not talk over the silent narration read.** The 8-12 seconds of judges reading the Nemotron output IS the demo. Stand still and let them read.
3. **Three lines need eye contact specifically:**
   - "Sixty thousand people displaced over twenty-four years"
   - "Nothing left the room"
   - "Computational ghosts need local hardware"
4. **No em dashes in delivery.** Replace every dash with a full stop and a breath.
5. **If Nemotron hangs at click time**, deploy the buy-time line:
   > "While that loads, this runs on the same hardware NVIDIA built for exactly this category of work. Local-first inference is the whole claim, and local-first means we own the latency too."
6. **NEW — the slider drag is the second-most-important physical action after the hardware tap.** Practice the drag from 2026 → 1948 → 1972 standing up. The drag should be ONE continuous motion, not stop-start. The visceral effect is in the continuity. Practice with the demo screen 3 times before recording.
7. **NEW — handing the trackpad to a judge is the close-of-Q&A move.** "Click any address yourself." Then physically push the trackpad toward them. This is the "is this real?" answer that wins by demonstration. Practice the gesture.

---

## If the demo breaks

Same priority list as the original script:
1. **WiFi flake** at venue — orchestrator unreachable. Mitigation: rehearse on the GN100's local screen via HDMI. Network is the secondary path, not the primary. (NEW: post-move the GN100 is on WiFi not ethernet, so the unplug-cable beat is broken — either plug ethernet back in, or skip the unplug.)
2. **llama-server crash** — orchestrator returns HTTP 502 with "Loading model". Wait 30 sec, retry. If still failing, restart with `bash scripts/start-llama-nano.sh` in the llama tmux session.
3. **Renderer crash** — Bevy or deck.gl. Mitigation: have BOTH paths warm. Judges don't care which renders, only that something does.
4. **Pre-baked narration cache** at `data/narration_cache.json` — 19 narrations, all `backend:"real"`, ready as fallback if the live model dies. The renderer can serve from the cache transparently.

**Hard fallback**: pre-recorded 30-second OBS capture of the working happy path. Record this BEFORE the live demo as insurance.

---

## What's NOT in the script (and why)

- "Time machine" → demoted to internal language only. Hook only, never the spine.
- "Cultural memory infrastructure" → poetry. Use it in the close, never the open. The lawyer beat is the open.
- The 5-buyer-segment table → cut. We pick one (lawyers), name it specifically, and cite the regulation.
- Bevy / Rust / llama.cpp / Tailscale tooling → judges don't care about toolchains. Answer if asked, never lead with it.
- ComfyUI / SD1.5 / 3DRenderStyle LoRA → only mention if it actually demonstrably runs at the demo. If it doesn't, drop the "two models" Q&A answer.
- "Five personas" (Sofia / Marcus / Alicia / Jordan / Riya) → cut. Sofia Reyes was a fictional rubric-coded archetype. Replace with the right-to-counsel population number ("20,000 cases per year").

---

## Roles for the recorded video

Carson is OUT. Marvens may or may not be available. James is on visualization content. Alex is doing the all-nighter and the recording.

| Beat | Who delivers | Why |
|---|---|---|
| Opening (hardware tap) | **Alex** | Founder voice, anchors the thesis |
| The Map (slider intro) | **Alex** | Same |
| The Cross-Bronx beat | **Alex** | Load-bearing — must be Alex for tonal consistency |
| The Click + narration | **Alex** | The narration speaks for itself; Alex stays silent during the read |
| Close | **Alex** | Founder lands the close |

**Recording reality**: Alex records solo. Single voice across the whole video. Optional: one-line cameo from James or Marvens in the close ("the community keeps its own ghosts" delivered by a teammate) IF they're at the venue tonight, otherwise drop.

---

## What to rehearse before recording (Sat night)

1. **Full script standing up, hardware tap, slider drag, twice through with stopwatch.** Should land 95-110 sec consistently.
2. **The slider drag specifically** — practice 5 times. Should be ONE continuous motion 2026 → 1948 → 1972, not stop-start. The visceral effect is in the continuity.
3. **Live click on `bronx-1973-08-11-sedgwick`** end to end on the GN100. Confirm `backend:"real"` in the dev tools. Confirm narration text appears on screen and is readable from 6 feet.
4. **The buy-time line** for if Nemotron hangs.
5. **Backup OBS recording** — 30 sec, no voice, just the visual happy path. Insurance against a Sun-AM crash.

---

## Append-only changelog

- **Apr 11 ~22:00 ET** — drafted Cross-Bronx-anchored rewrite as third companion file. Anchors entire 90s on the Cross-Bronx Expressway → 1520 Sedgwick → hip-hop chain. Map + slider + migration cone is the visual hero. Q&A bakes in the unicorn-bounty number row (NYC right-to-counsel + Rule 1.6 + 20K cases + $600 paralegal). Three off-stage 1:1 versions for stage / Antler / civic audiences. Authors: Alex (post-Carson-departure pivot, Session 44).
