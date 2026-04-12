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
