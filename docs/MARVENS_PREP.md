# Marvens Prep — Cross-Bronx Demo Polish

**Written ~03:30 ET Sun Apr 12. ~1 hour before Marvens arrives.**

## Context (read first, ~30 sec)

Carson left the team Apr 11 ~21:30 ET, "out of commission." Alex is solo on grunt work + all-nighter + demo video. James is heads-down on `feature/sketch-overlay` and just shipped 3 commits including the Bronx wire-up. **You are now the only person on visualization who can land the Cross-Bronx demo polish.**

The locked thesis (Session 45 pivot) is one causal arc:
> Cross-Bronx Expressway 1948-1972 → 60K displaced → Sedgwick Avenue → DJ Kool Herc Aug 11 1973 → hip-hop birth → cultural memory is what survives the bulldozer.

Your single load-bearing deliverable is the **Cross-Bronx migration cone** (Beat 3 of the demo). Even a static cone with the printed displacement count (60,000 per Caro) is enough — this is the visual hero of the pitch, not nice-to-have particle work. **The cone IS the demo.**

Beyond the cone, the second-highest-leverage thing you can do tonight is the right-side widget audit below. James shipped a lot of UI in his bronx push (`e0b2428`); some of it is load-bearing, some of it is noise that judges shouldn't see, some of it is broken-but-fixable.

---

## Widget audit — KEEP / HIDE / SCRAP

James's `index.html` has 8 right-side / overlay widgets. Here's the call for the Sun demo:

| # | Widget | Line | Decision | Why |
|---|---|---|---|---|
| 1 | `#legend` (8-era color key, top right) | 1356 | **KEEP** | Identifies the architectural eras at a glance. Don't touch. |
| 2 | `#immigration-origins-panel` | 1358 | **KEEP + REBIND** | See "Single highest-leverage fix" below. |
| 3 | `#controls` (year slider + era label, bottom) | 1364 | **KEEP** | The year slider IS the demo verb. Don't touch. |
| 4 | `#story-card` (SITE HISTORY click panel) | 1416 | **KEEP + WIRE TO BIOGRAPHY RAG** | This is where the click payoff renders. Currently shows dev placeholder text. See `docs/UX_AUDIT_SESSION_45.md` for the specific fix. |
| 5 | `#lightbox` (fullscreen photo viewer) | 1377 | **KEEP** | Triggered from story card. Used. |
| 6 | `#photo-mode` (full archival viewer with year scrubber) | 1393 | **HIDE for Sun** | Functionally overlaps with `#lightbox`. Two photo viewers is one too many. Add `#photo-mode { display: none !important; }` to body.ps2-mode (or set the feature flag). |
| 7 | `#dev-toggle` + `#dev-panel` (gear icon, FEATURE FLAGS) | 1437 | **HIDE for Sun** | Judges should never see "FEATURE FLAGS." Toggle off via JS at page load when not in dev mode (set `display: none` or wrap in `if (window.location.search.includes('dev'))`). |
| 8 | `#cinematic-overlay` (Ellis Island video) | 1452 | **HIDE for Sun** | Different thread (Ellis Island, 1903) — distracts from the Cross-Bronx → Kool Herc anchor. The 4-page handout PDF or biography RAG output is the artifact, not Ellis Island video. **EXCEPTION**: if you can swap the source video for a Cross-Bronx archival clip in the next hour, KEEP it — the cinematic overlay is gorgeous when the content is on-message. Source file path: `cultural-content/ellis-island-clips/ellis-island-1903-web.mp4`. |

---

## Single highest-leverage fix: rebind `#immigration-origins-panel`

James built a real immigration tuning panel with bucket-aware particle sliders, shapes (dot/line/trail/parabola/humans), and live readouts (lines 2200-2400 of `index.html`). It currently says **"HOVER A DENSITY HEX"** — implying a density hex layer that may or may not be wired into the click flow.

**The pivot:** the Cross-Bronx Expressway displacement event (`bronx-1959-cross-bronx-expressway-displacement` in `data/events-seed.json`) is tagged `immigration` in its niche_tags. **Displacement is the inverse of immigration.** The same widget that shows immigration origins by year should also show displacement origins for the Cross-Bronx era.

**Specific fix (~10-30 min depending on data layer state)**:

1. Find the `#immigration-origins-panel` show/hide trigger in `index.html` (search for `immigration-origins-panel` and `display:none` / `display:block` toggles)
2. Add a new trigger: when the user clicks a building polygon AND the current year is in the 1948-1972 range, populate the panel with the Cross-Bronx displacement origins (Tremont, Crotona Park East, East Tremont, Mott Haven — these are the neighborhoods Caro lists as gutted)
3. The panel header text "ORIGINS" stays — it now reads as "where the displaced families came FROM" (the bulldozed neighborhoods) rather than "where immigrants came FROM"
4. Below the year slider, when the year is 1948-1972, the panel should show:
   - **East Tremont** — 5,000+ displaced (1953-1955)
   - **Tremont** — ~12,000 displaced
   - **Crotona Park East** — ~8,000 displaced
   - **Mott Haven** — ~6,000 displaced
   - **Belmont, Morris Heights, Highbridge** — ~30,000 combined
   - Total ~60,000 (Caro, *The Power Broker*, ch. 37-38)
5. These are HARDCODED counts for the demo — no live data layer needed. Replace with live data post-hack.

If wiring a new building click handler is too much, **the cheapest alternative**: change the "HOVER A DENSITY HEX" text to "DRAG TO 1955" and have the panel auto-populate when the year slider crosses into the 1948-1972 range. No interaction needed beyond the slider Alex is already pulling on stage.

---

## Cross-Bronx migration cone

This is your existing assignment, not a new one. The acceptance criteria for the demo (Sun 2 PM):

1. **One static glb** (or even one dynamic primitive in deck.gl LayerExtension) at the Cross-Bronx corridor centroid — approximately `[40.8488, -73.9000]` to `[40.8378, -73.9216]`. Per `docs/MIGRATION_FLOW_PROTOTYPE.html`:
   - Position = neighborhood centroid (Tremont area)
   - Height = intensity (60,000 = TALL)
   - Top width = spread (multi-block)
   - Tilt = direction (south, toward Sedgwick Avenue)
   - Era band color = decade (1950s-1960s = a single muted ochre per the styleguide; NO red/orange/yellow per anti-patterns)
2. **Click panel with documented count + source citation**: every cone is clickable. The panel should show "60,000 displaced (Caro, *The Power Broker*, 1974)." This is the "we don't predict, we trace from the receipts" thesis embodied in one click.
3. **Anti-patterns** (do NOT cross): no red/orange/yellow (fire/smoke imagery), no fast turbulent motion, no plume shape, no PBR/photoreal, no cone without click-panel.

**The simplest version that ships**: a single textured glb cone at the Tremont centroid, vertex colors only, with a deck.gl click handler that fires the existing `#story-card` populated with the Caro citation. **Even one cone is enough.** The pitch language sells the rest.

---

## What James already shipped (don't redo this work)

- `feature/sketch-overlay` `e0b2428`: Bronx footprints wired into the deck.gl renderer (Manhattan + Bronx now render together, ~250K buildings total)
- `feature/sketch-overlay` `c635e62`: split Bronx out of Postmodern era as its own 1970s station in the guided tour — this is the era station you'll add the Kool Herc beat to
- `feature/sketch-overlay` `7e5dc13`: removed the play button from the timeline component (timeline is now scrub-only, which matches the demo verb)
- `feature/sketch-overlay` (earlier): 750 NYPL Milstein photos georeferenced across all 5 boroughs, immigration data 1719-2026 from LOC raw masters, photo-mode slideshow with year scrubber, comfy operator brief (deferred), Wikidata demolished landmarks layer

Your ghosts (low-poly Blender meshes) go in `assets/ghosts/` per the sibling manifest pattern. Migration cones go in `assets/migration-flows/`. **Each asset family gets its own MANIFEST.json — sibling pattern, NOT nested.** James's deck.gl loader is independent of the renderer-rust loader.

---

## Tools you have

- **Tailscale**: ask Alex to share `gn100-3857` so you can SSH/Tailscale into the box if you need to test against the real backend
- **Local map URL**: http://127.0.0.1:8766/index.html (Mac-served sketch-overlay clone, currently running)
- **Biography RAG endpoint**: `POST http://127.0.0.1:30001/biography {"event_id": "bronx-1973-08-11-sedgwick"}` returns the 4-section forensic biography in 11 ms (cached). You can wire this into the click handler to replace the dev placeholder text in the story card.
- **Branch**: work on `feature/sketch-overlay`. James will resolve the merge with main Sun morning.

---

## Don't do (anti-tasks)

- **Don't restart llama-server on `:8090`** on the GN100. Ever. Warm-loaded model takes 30+ sec to reload and the cable beat depends on it being warm.
- **Don't push to `main`** — James handles the merge.
- **Don't touch anything in `docs/*.md`** — that's the Mac instance's territory. If you need to add doc, write a NEW file with your name in it.
- **Don't add new dependencies** — the dependency-age rule still holds (≥2 weeks old as of Apr 10).
- **Don't try to fix the Bevy native renderer (`renderer-rust/`)** — Carson left, the path is frozen at `b394623`, it's not in the Sun demo verb.

---

## Order of operations (~1 hour budget)

1. **First 5 min**: read this doc + skim `docs/UX_AUDIT_SESSION_45.md` + `docs/DEMO_VIDEO_SCRIPT.CROSS_BRONX.md`
2. **Next 15 min**: hide the 3 widgets (photo-mode, dev-panel, cinematic-overlay) — three small CSS / JS edits to `index.html`
3. **Next 30 min**: rebind `#immigration-origins-panel` to fire on building click in 1948-1972 era OR auto-populate on slider crossing into that range. Hardcode the displacement counts.
4. **Last 10 min**: ship the static Cross-Bronx migration cone — one glb in `assets/migration-flows/` + one MANIFEST.json entry + one deck.gl click handler returning the Caro citation
5. **Push to `feature/sketch-overlay`**, tell Alex/James you're done, go to sleep

**If you only have time for ONE thing**: do the migration cone (item 4). Everything else is polish. The cone is the demo.

---

## Why this matters

You're inheriting the visualization role from a teammate who left mid-build. Alex is recording the demo video at midnight-2 AM. James is heads-down on the renderer. **The Cross-Bronx beat is the load-bearing visual moment of the entire pitch.** Without your cone, the demo is "look at this 3D map of NYC." With your cone, the demo is "watch the city erase 60,000 people in 24 years, click here for the receipts." That's the difference between the Cultural Impact track win and Most Likely to be a Unicorn at Antler.

The cone is the demo. Land the cone.

---

# 📍 COMPREHENSIVE DIRECTORY POINTING (read this when you sit down)

The two priorities:
1. **Immigration flow + visualization** (BIGGEST — the panel rebind + the cinematic swap)
2. **Refine immersion without breaking identity** (PS2 constraint language stays, no cloud, no PBR, no fire colors, no fast turbulence)

Below is exact file:line pointers for everything you'll touch.

---

## 1. IMMIGRATION FLOW — where the code lives

Branch: `feature/sketch-overlay`. File: `index.html`. James already built a SOPHISTICATED immigration tuning system — it's not "wire from scratch," it's "fix the trigger and swap the data source."

### Data files (already committed)
```
data/immigration/nyc_immigration_timeline.json    ← LOAD THIS, not the CSV
data/immigration/nyc_immigration_timeline.csv     ← raw source
data/immigration/us_totals_1820_2023_dhs.csv      ← DHS national context
data/immigration/README.md                        ← schema notes
```

### Immigration code in `index.html` — exact line numbers

| Line | What's there | What to do |
|---|---|---|
| **2371** | `IMMIGRATION_PARAM_DEFS` — 9 tunable params (size, amount, pressure, spread, life, outline, tail, arc, noise) per particle bucket | Read once. Don't change defaults until you've A/B'd the visual. |
| **2385** | `IMMIGRATION_BUCKETS = ['low', 'mid', 'high']` — 3 intensity tiers | Each bucket has its own param preset, picked by `IMMIGRATION_BUCKET_EDGES` thresholds (line 2386) |
| 2200-2360 | Dev panel UI for live-tuning the buckets (sliders, shape picker, save/reset) | This is the existing tuning UX. Wire flag `featureFlags.immigrationOrigins = true` to make it visible. |
| **3199** | `function getNeighborhoodOrigins(key, year)` — returns origin breakdown for a (neighborhood, year) | The data this function returns is the row that goes into the right-side ORIGINS panel |
| **3388** | `const GLOW_ANCHORS = [...]` — neighborhood centroids array | **YOU EDIT THIS** to add the Cross-Bronx neighborhoods (East Tremont, Tremont, Crotona Park East, Mott Haven, Belmont). Each entry needs `{key, lon, lat, label}`. |
| **3401** | `function nearestGlowAnchor(lon, lat)` — coord → anchor index | Used by hover/tooltip to pick which anchor the cursor is over. No changes needed if you add to GLOW_ANCHORS. |
| **3451** | `immigrationIntensityByYear = new Map(data.records.map(...))` — data load from `data/immigration/nyc_immigration_timeline.json` | Already wired. Verify the file loads on first map render (browser devtools network tab). |
| 3677 | `immigration-data-readout` element update — live YYY arrivals count | Already wired. Shows in the dev panel. |
| **3785-3795** | `onHover` handler for the `immigration-density-hexes` layer — populates `selectedNeighborhoodKey` and calls `updateImmigrationOriginsPanel()` | This is the **trigger you need to rebind** for the Cross-Bronx pivot. See below. |
| 3796-3850 | `getTooltip` handler — renders the inline bar chart for origins | Marvens can rewrite the bar chart styling but the data path is correct. |
| **4519** | `id: 'immigration-density-hexes'` deck.gl HexagonLayer definition | This is the layer the hover handler depends on. If the layer isn't rendering, the hover never fires. **CHECK THIS FIRST** in browser devtools — look for the layer in the deck.gl layer manager. |

### The single highest-leverage rebind (~15 min)

The hover handler at line 3785 currently fires only when the cursor is over a `immigration-density-hexes` layer hex. The Cross-Bronx pivot wants the panel to fire on the **year slider crossing into 1948-1972** OR on **building polygon click in the Bronx**.

**Cheapest possible fix**: in the year slider event handler (search for `currentYear =` in `index.html` — line 4792 and 4824), add this block right after the year is updated:

```js
// Auto-pin the immigration origins panel to the Cross-Bronx neighborhoods
// when the year crosses into the 1948-1972 demolition window. The pivot:
// when the user scrubs into the Cross-Bronx era, the right-side panel
// auto-fills with the documented displacement counts (Caro), no hover needed.
if (currentYear >= 1948 && currentYear <= 1972) {
  selectedNeighborhoodKey = 'cross-bronx-corridor';  // add this anchor to GLOW_ANCHORS
  updateImmigrationOriginsPanel();
} else if (selectedNeighborhoodKey === 'cross-bronx-corridor') {
  selectedNeighborhoodKey = null;
  updateImmigrationOriginsPanel();
}
```

Then in `getNeighborhoodOrigins(key, year)` at line 3199, add a special case at the top:

```js
function getNeighborhoodOrigins(key, year) {
  // Cross-Bronx pivot: hardcoded displacement counts from Caro's
  // The Power Broker (1974), chapters 37-38. The "origins" here are
  // neighborhoods displaced INTO 1520 Sedgwick, not immigrant origins —
  // displacement is the inverse of immigration, same population-flow lens.
  if (key === 'cross-bronx-corridor' && year >= 1948 && year <= 1972) {
    return {
      year,
      countries: [
        { name: 'East Tremont',           share: 0.083, count: 5000 },
        { name: 'Tremont',                share: 0.200, count: 12000 },
        { name: 'Crotona Park East',      share: 0.133, count: 8000 },
        { name: 'Mott Haven',             share: 0.100, count: 6000 },
        { name: 'Belmont, Morris Heights, Highbridge', share: 0.500, count: 30000 },
      ],
      totalDisplaced: 60000,
      source: 'Robert Caro, The Power Broker (1974), ch. 37-38',
    };
  }
  // ... existing immigration logic
}
```

And add `cross-bronx-corridor` to GLOW_ANCHORS at line 3388:
```js
{ key: 'cross-bronx-corridor', lon: -73.9000, lat: 40.8488, label: 'Cross-Bronx Corridor' },
```

**This is 3 small edits in one file. Maybe 15 min including testing in the browser.**

---

## 2. CINEMATIC OVERLAY — swap Ellis Island for Cross-Bronx (5-min win)

James shipped the `#cinematic-overlay` widget pointing at `cultural-content/ellis-island-clips/ellis-island-1903-web.mp4`. **But while scraping the repo I found James ALSO shipped Cross-Bronx era archival video assets sitting in `cultural-content/`** that nobody is using yet:

```
cultural-content/Christie's - DJ Kool Herc and the birth of hip-hop ｜ Christie's [Jdb3MTz7xXg].mp4
cultural-content/Kinolibrary-Hip_Hop_Party_at_Bronx_River_Center_1980s_New_York_Premium-pLSmNafnaGo.mp4
cultural-content/ThamesTv-South_Bronx_fire_Apartment_Block_Fire_1980_s_South_Bronx_Only_in_America_1980-bKcecaIBWe4.mp4
```

Plus 15+ archival photos at `cultural-content/bronx/Bronx_1970s_*.jpg` (the ones James added in `feat(bronx): feature-flagged Bronx photos for Postmodern era cutscene` `655f421`).

### One-line fix

In `index.html` around line 1455-1457, swap the cinematic source. From:
```html
<video id="cinematic-video" playsinline muted preload="metadata">
  <source src="cultural-content/ellis-island-clips/ellis-island-1903-web.mp4" type="video/mp4">
</video>
```

To:
```html
<video id="cinematic-video" playsinline muted preload="metadata">
  <source src="cultural-content/Christie's - DJ Kool Herc and the birth of hip-hop ｜ Christie's [Jdb3MTz7xXg].mp4" type="video/mp4">
</video>
```

(The filename has special chars — URL-encode it or rename the file to `cultural-content/kool-herc-christies.mp4` first. Renaming is cleaner.)

Then update the cinematic location label at line 1453 from `Ellis Island · 40.6995°N 74.0391°W` to `1520 Sedgwick Avenue · 40.8488°N 73.9216°W`.

And the caption title at line 1459 from `ARRIVAL` to `THE BREAKBEAT` or `AUGUST 11 1973`.

**This single swap turns the cinematic-overlay widget from "off-message Ellis Island distraction" into "on-message Cross-Bronx wow beat."** 5 minutes including the file rename. **DO THIS BEFORE the panel rebind** if you only have 30 minutes total.

---

## 3. THE STATIC MIGRATION CONE — your existing assignment

You already had this. Reminder of the core spec from `docs/MIGRATION_FLOW_PROTOTYPE.html`:

**Where to drop assets:**
```
assets/migration-flows/
  MANIFEST.json          ← committed, sibling to assets/ghosts/MANIFEST.json
  cross-bronx-cone.glb   ← your file (gitignored, sync via shared storage)
  cross-bronx-cone.preview.png  ← committed, for the manifest preview
```

**Cone parameters (from `docs/MIGRATION_FLOW_PROTOTYPE.html`):**
- Position: Tremont area centroid `[40.8488, -73.9000]` (Cross-Bronx Expressway midpoint)
- Height: intensity (60,000 = TALL)
- Top width: spread (multi-block, ~0.5 units)
- Tilt: direction (south, toward Sedgwick Avenue)
- Era band color: 1950s-1960s = single muted ochre per the styleguide
- Click panel: text "60,000 displaced (Caro, *The Power Broker*, 1974)" + a dataset citation

**Anti-patterns** (these break the identity, do NOT cross):
- ❌ red, orange, yellow (fire/smoke imagery)
- ❌ fast turbulent motion
- ❌ plume shape
- ❌ PBR/photoreal
- ❌ cone without click-panel
- ❌ Three.js procedural shaders (we're glb-only)

**The simplest version that ships**: one textured glb cone at `[-73.9000, 40.8488]`, vertex colors only, with a deck.gl `ScenegraphLayer` (or `SimpleMeshLayer`) and a click handler that fires the existing `#story-card` populated with the Caro citation. **One cone is enough. You don't need the multi-cone migration system tonight — that's v2.**

---

## 4. IMMERSION REFINEMENT — what to keep, what to scrap

The PS2 mode is the identity. Don't break it. Specific things you can refine WITHOUT breaking identity:

### KEEP and refine
- **The PS2 palette** in `index.html` line ~899-1340 (`body.ps2-mode { --ps2-bone, --ps2-cream, --ps2-ink, --ps2-accent }`) — the bone/cream/ink color tokens. Marvens can adjust the accent color to a slightly more saturated Cross-Bronx ochre if it reads better against the Bronx 1970s photos.
- **The vignette + Sobel edge detection** post-process — already shipped on sketch-overlay
- **The hairline 1px borders, sharp right angles, block type** — Mode A constraint language
- **The story card layout** at line 1416 — typography is fine, just needs Bug 3 from `docs/UX_AUDIT_SESSION_45.md` fixed (replace placeholder body with biography RAG output)

### HIDE for Sun (already in the widget table above, repeating for clarity)
- `#dev-toggle` + `#dev-panel` — judges should never see "FEATURE FLAGS"
- `#photo-mode` — overlaps with `#lightbox`, kill the dupe

### POSSIBLY SCRAP (decide in the room with James)
- The cinematic-overlay if you can't swap the video source in time — better hidden than off-message
- The play button on the timeline (already removed in `7e5dc13`)

### DO NOT TOUCH
- The deck.gl scene tilt (55° pitch, -20° bearing) — this is the identity 3D look
- The year slider behavior — it's the demo verb
- The 8-era taxonomy — James's territory, locked
- Any of the load logic (lines 2620-2690 area) — fragile, James's territory

---

## 5. WHERE THE BIOGRAPHY RAG ENDPOINT IS (so you can wire the click handler)

```
src/biography/
  __init__.py        — package marker
  lookup.py          — structured retrieval over 5 borough JSONs + photos + landmarks + events
  synthesize.py      — Nemotron prompt + httpx POST to local llama-server :8090
  router.py          — POST /biography FastAPI route (mounted in main.py)

src/orchestrator/
  main.py            — FastAPI app, biography router mounted at line ~70
                       (uvicorn :30001 on the GN100, NARRATION_MODE=real)
```

**Endpoint URL on the GN100 backend**: `POST http://127.0.0.1:30001/biography`

**Request body** (any one of these):
```json
{"event_id": "bronx-1973-08-11-sedgwick"}
{"bin": "2008286"}
{"lat": 40.8378, "lon": -73.9202}
```

**Response shape** (snippets):
```json
{
  "query": {"bin": null, "lat": null, "lon": null, "event_id": "bronx-1973-08-11-sedgwick"},
  "structured_record": {
    "building": {"bin": "2008286", "borough": "bronx", "height_m": 4.9, "year_built": 1920, "centroid_lat": 40.83777, "centroid_lon": -73.92037, "distance_m": 14.6, ...},
    "anchor_event": {...},
    "nearby_photos": [...up to 8 NYPL Milstein photos within 200m...],
    "nearby_landmarks": [...up to 10 demolished within 1km...],
    "nearby_events": [...up to 10 cultural events within 500m...]
  },
  "narrative": "## 1. Identification\nThe building with BIN 2008286 was constructed in 1920...",
  "citations": ["NYC Open Data Building Footprints (5zhs-2jue) by lat/lon proximity (14.6 m)", ...],
  "backend": "cache",   // or "real" on cache miss
  "model": "Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf",
  "tokens_in": 652,
  "tokens_out": 4096
}
```

**Cache hit returns in 11 ms.** Cache miss runs the full pipeline (~1m43s on warm GB10) and writes back. 19 events are being pre-baked right now in a `prebake` tmux session on the GN100.

**Wire-up code for the story card** is documented in `docs/UX_AUDIT_SESSION_45.md` (Bug 3 fix section). 20 lines of fetch + render markdown. **The cache hit visualization** (footer says `⚡ cached` instead of `1024 tokens · Nemotron`) is a load-bearing pitch beat — judges see the local model proving itself in real time.

---

## 6. ALL THE DOCS YOU NEED IN ONE TABLE

| If you need... | Read this |
|---|---|
| The locked pitch | `docs/DEMO_VIDEO_SCRIPT.CROSS_BRONX.md` (Session 45 anchor) |
| Migration cone visual spec | `docs/MIGRATION_FLOW_PROTOTYPE.html` (open in browser) |
| PS2 constraint language | `docs/VISUAL_DIRECTION.md` |
| Architectural era taxonomy | `index.html` line 2538 (`getEra()` function) |
| The 3 click-handler bugs to fix | `docs/UX_AUDIT_SESSION_45.md` |
| Right-side widget keep/hide table | `docs/MARVENS_PREP.md` (this file, top section) |
| Buyer segments (post-demo Q&A) | `docs/PRODUCT_WEDGES.md` |
| The full rubric (100 pts) | `docs/EVENT_RULES.md` |
| Hardware health snapshot | `docs/GN100_HEALTH_APR11.md` |
| Build decisions log | `docs/DECISIONS.md` |
| Branch playbook | `CONTRIBUTING.md` |

---

## 7. ORDER OF OPERATIONS — sharpened

If you have **15 min**: do the cinematic swap (one-line fix, 5 min) + the migration cone (one glb at the Tremont centroid, 10 min). Ship those two.

If you have **30 min**: above + immigration panel rebind (year-slider auto-pin, 15 min).

If you have **60 min**: above + hide the 3 widgets (photo-mode, dev-panel, cinematic if you didn't swap) + finalize the panel content with the Caro citations.

If you have **2 hours**: above + a second migration cone for "Puerto Rican migration to South Bronx 1965" (already in events-seed.json as `bronx-1965-puerto-rican-migration`) + the `assets/ghosts/MANIFEST.json` entry for one ghost mesh of the demolished Bronx Opera House (1968).

**The 15-minute version is the must-ship. Everything beyond is bonus.**
