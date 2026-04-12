# UX Audit — Session 45, Apr 12 ~03:30 ET

User-tester walkthrough of the click flow on James's `feature/sketch-overlay` `index.html`. Three concrete bugs found by reading the click handler code (`showCard()` line 4870) and the photo lookup logic (lines 4884-4897). All three are real, all three have load-bearing demo impact, all three are fixable in <30 min.

---

## Bug 1 — Building names are stubbed for everything except a hardcoded MARQUEE table

**Where:** `index.html` `showCard()` line 4870-4883.

**The code:**
```js
function showCard(building) {
  if (!featureFlags.storyCards) return;
  const card = document.getElementById('story-card');
  const marquee = MARQUEE[building.b];
  if (marquee) {
    document.getElementById('card-title').textContent = marquee.title;
    document.getElementById('card-year').textContent = `Built ${marquee.year}`;
    document.getElementById('card-body').textContent = marquee.body;
  } else {
    const era = getEra(building.y);
    document.getElementById('card-title').textContent = `BIN ${building.b}`;
    document.getElementById('card-year').textContent = building.y ? `Built ${building.y} / ${era.label}` : 'Construction year unknown';
    document.getElementById('card-body').textContent = `${building.h}m tall. ${era.label.toLowerCase()} construction. At the hackathon, clicking any building triggers Nemotron to generate a site-specific narrative using the building's metadata + surrounding historical context.`;
  }
  ...
```

**The bug:** there's a `MARQUEE` lookup table keyed by BIN that has hand-curated titles for a small set of famous buildings. Every other building falls through to the `else` branch which titles the card `BIN 2008286` (literally the BIN number) and the body text is dev placeholder describing the FUTURE behavior of the demo, not the actual data. **A judge clicks any non-MARQUEE building and sees "BIN 2008286" as the building name and a meta-paragraph about how the demo "will" call Nemotron.**

**Why this is hard to fix the obvious way:** NYC Building Footprints (`5zhs-2jue`) does NOT have building names. It has BIN, BBL, year_built, height, polygon. Names live in OTHER datasets:
- LPC Individual Landmarks (only ~36K landmarked buildings, not every building)
- PLUTO has owner of record (a name, but it's the LLC, not the building name)
- demolished-landmarks.json has names (only for demolished)
- events-seed.json has titles for the 19 hand-curated cultural events

**The pragmatic fix (~10 min, no new data needed):**

Replace the `else` branch with semantic data the user can actually read:
```js
} else {
  const era = getEra(building.y);
  // Use a human label, not the BIN. The address is the most user-readable
  // identifier; if we don't have an address, use the era + dimensions.
  const label = building.address
    ? building.address
    : building.y
      ? `${era.label} building, built ${building.y}`
      : `${era.label} building`;
  document.getElementById('card-title').textContent = label;
  document.getElementById('card-year').textContent = building.y ? `${era.label} / ${building.y}` : era.label;
  // Show the structured facts the user can verify, not a meta description.
  const facts = [];
  if (building.h) facts.push(`${building.h} m tall (LiDAR)`);
  if (building.y) facts.push(`built ${building.y}`);
  facts.push(`BIN ${building.b}`);
  document.getElementById('card-body').textContent = facts.join(' · ');
}
```

**The proper fix (~30 min, wires the biography RAG):**

Replace the entire `else` branch with a call to the new biography endpoint. The endpoint serves cached responses in 11 ms for canonical buildings and 1m43s for cold buildings — the ~1.5 second pre-bake batch can warm the top 50 demo addresses tonight. See "Biography RAG wire-up" below.

---

## Bug 2 — Photo lookup fallback is too generous, surfaces irrelevant images

**Where:** `index.html` `showCard()` lines 4884-4897.

**The code:**
```js
// Attach nearby oldnyc photos, if any. Primary: within ±8y and 140m.
// Fallback: nearest in space regardless of year, within 800m — so a click
// never surfaces an empty gallery when the user is off a photo's exact year.
_cardPhotos = [];
_cardPhotoBuildingYear = building.y || currentYear;
_cardPhotoIdx = 0;
if (featureFlags.oldnycPhotos && building.p && oldnycPhotos.length) {
  const [clng, clat] = polygonCentroid(building.p);
  let hits = findPhotosNear(clng, clat, currentYear);
  if (!hits.length) {
    hits = findNearestPhotosSpatial(clng, clat, currentYear);
  }
  _cardPhotos = hits.slice(0, 6).map(h => h.photo);
}
```

**The bug:** James added a fallback "nearest photos within 800m REGARDLESS OF YEAR" so the gallery is never empty. This is well-intentioned but defeats the photo-as-evidence relationship: click a 1750 colonial building, get a 1950s street scene from 800m away because that's the closest pin. **The photos shown are spatially "near" but historically irrelevant** — exactly the bug Alex flagged in user-testing.

The NYPL Milstein collection is ~1900-1956 (mostly the 1939-1941 NYC tax-photo project). Most NYC buildings will have NO matching photos within ±8 years, so the fallback fires CONSTANTLY and shows year-mismatched imagery.

**Three fixes, in order of conservatism:**

### Option A (5 min, safest): tighten the spatial fallback

Change the 800m fallback to 200m AND require the photo year to be within ±20 years of the building's construction year (not the current slider year):

```js
if (featureFlags.oldnycPhotos && building.p && oldnycPhotos.length) {
  const [clng, clat] = polygonCentroid(building.p);
  let hits = findPhotosNear(clng, clat, currentYear);
  if (!hits.length) {
    // Fallback: within 200m AND within ±20 years of THE BUILDING'S construction
    // year (not the current slider year — slider can be at 2026 even when
    // clicking a 1920 building). Photos must still be archivally relevant.
    const buildingYear = building.y || currentYear;
    hits = findNearestPhotosSpatial(clng, clat, buildingYear)
      .filter(h => Math.abs(h.photo.year - buildingYear) <= 20)
      .filter(h => h.distance_m <= 200);
  }
  _cardPhotos = hits.slice(0, 6).map(h => h.photo);
}
```

### Option B (10 min, more honest): show the empty state on purpose

When there are no relevant photos, show a clean empty state instead of an irrelevant fallback:

```js
if (featureFlags.oldnycPhotos && building.p && oldnycPhotos.length) {
  const [clng, clat] = polygonCentroid(building.p);
  const hits = findPhotosNear(clng, clat, currentYear);
  if (hits.length) {
    _cardPhotos = hits.slice(0, 6).map(h => h.photo);
  } else {
    // Honest: no archival photo on file for this address ±8 years.
    // The card body will show this as a textual "no record" line.
    _cardPhotos = [];
  }
}
```

Then in `renderCardPhotos()`, when `_cardPhotos.length === 0`, show a small grey line: `"No archival photo on file for this address within ±8 years (NYPL Milstein Collection)."` This honors the forensic posture and the rubric's "could a real City Planner use this tomorrow" usability bar — the user trusts the system MORE when it admits absence than when it shows fake data.

### Option C (15 min, best for the demo): sort by year-relevance, then cap

Always return SOMETHING but rank by year-distance and cap at 200m AND show the year delta prominently:

```js
if (featureFlags.oldnycPhotos && building.p && oldnycPhotos.length) {
  const [clng, clat] = polygonCentroid(building.p);
  const buildingYear = building.y || currentYear;
  let hits = findNearestPhotosSpatial(clng, clat, buildingYear)
    .filter(h => h.distance_m <= 200);
  // Sort by year relevance first, then spatial proximity
  hits.sort((a, b) => {
    const aYearDelta = Math.abs(a.photo.year - buildingYear);
    const bYearDelta = Math.abs(b.photo.year - buildingYear);
    if (aYearDelta !== bYearDelta) return aYearDelta - bYearDelta;
    return a.distance_m - b.distance_m;
  });
  _cardPhotos = hits.slice(0, 6).map(h => h.photo);
}
```

The existing `renderCardPhotos()` already shows the year offset in the caption (line 4940-4945), so the user can SEE the delta. Option C trusts that text to do its job.

**Recommended: Option A for the demo (smallest diff, kills the worst case), then ship Option C post-hack.**

---

## Bug 3 — Card body fallback is dev placeholder text

**Where:** `index.html` `showCard()` line 4882.

**The code:**
```js
document.getElementById('card-body').textContent = `${building.h}m tall. ${era.label.toLowerCase()} construction. At the hackathon, clicking any building triggers Nemotron to generate a site-specific narrative using the building's metadata + surrounding historical context.`;
```

**The bug:** When the user clicks a non-MARQUEE building, the body text says "At the hackathon, clicking any building triggers Nemotron to generate..." — this is FUTURE TENSE describing what the demo WILL DO. A judge reads this and concludes: the LLM call is not actually wired into the click yet. (They'd be wrong — `/narrate` and `/biography` are both live. But the placeholder text makes the system look unfinished.)

**The fix is THE WHOLE POINT of tonight's biography RAG work**: replace the dev placeholder with a real call to `POST /biography` and render the 4-section markdown.

### Biography RAG wire-up (~20 min)

The endpoint is live on the GN100 at `http://127.0.0.1:30001/biography`. Cache hit returns in 11 ms. The Sedgwick canonical biography is already pre-baked. Wire it into the click handler:

```js
async function showCard(building) {
  if (!featureFlags.storyCards) return;
  const card = document.getElementById('story-card');
  const era = getEra(building.y);

  // Use the human-readable identifier (Bug 1 fix above)
  const label = building.address || (building.y ? `${era.label} building, built ${building.y}` : `${era.label} building`);
  document.getElementById('card-title').textContent = label;
  document.getElementById('card-year').textContent = building.y ? `${era.label} / ${building.y}` : era.label;

  // Show "loading" while the biography RAG is in flight
  document.getElementById('card-body').textContent = 'Loading building biography from local Nemotron...';
  card.style.display = 'block';

  // Call the biography endpoint with the BIN
  try {
    const resp = await fetch('http://127.0.0.1:30001/biography', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bin: building.b }),
    });
    if (resp.ok) {
      const data = await resp.json();
      // Render markdown as plain text for now (or pipe through marked.js if loaded)
      document.getElementById('card-body').textContent = data.narrative;
      // Tag the source so judges see the cache hit speed
      const footer = document.querySelector('#story-card .card-footer');
      if (footer) {
        const tag = data.backend === 'cache' ? '⚡ cached' : `${data.tokens_out} tokens · ${data.model}`;
        footer.textContent = `NARRATED BY NEMOTRON 3 NANO / GB10 BLACKWELL · ${tag}`;
      }
    } else {
      document.getElementById('card-body').textContent = `Building biography unavailable (HTTP ${resp.status}). BIN ${building.b}, built ${building.y || 'unknown'}.`;
    }
  } catch (err) {
    // Falls back to the structured facts on network error (also when running offline / no orch)
    const facts = [];
    if (building.h) facts.push(`${building.h} m tall (LiDAR)`);
    if (building.y) facts.push(`built ${building.y}`);
    facts.push(`BIN ${building.b}`);
    document.getElementById('card-body').textContent = facts.join(' · ');
  }

  // Photos still attached the same way (apply Bug 2 fix here)
  _cardPhotos = [];
  // ... rest of existing photo logic
}
```

**The cache hit visualization is a load-bearing pitch beat.** When the footer tag flips from `⚡ cached` (11 ms) on the first click of Sedgwick to `1024 tokens · Nemotron-3-Nano-30B-A3B-UD-Q8_K_XL.gguf` (~1m43s) on a cold building, the judge sees the local model actually doing work in real time. That's the demo proof.

---

## Pre-bake batch — kill latency for the top 20 demo addresses

The cache layer in `src/biography/router.py` writes back automatically on cache miss. Run a one-shot script to pre-bake the top 20 demo addresses tonight so the first click during the demo is always instant:

```python
# scripts/prebake_biographies.py
import httpx, json
PREBAKE_KEYS = [
    {"event_id": "bronx-1973-08-11-sedgwick"},  # Kool Herc anchor — already cached
    {"event_id": "bronx-1959-cross-bronx-expressway-displacement"},
    {"event_id": "bronx-1965-puerto-rican-migration"},
    {"event_id": "bronx-1923-loews-paradise"},
    {"event_id": "bronx-1968-bronx-opera-house"},
    # all 19 events from events-seed.json — pre-bake the lot
    {"event_id": "bronx-1974-cedar-park"},
    {"event_id": "bronx-1975-bronx-river-houses"},
    {"event_id": "bronx-1975-t-connection"},
    {"event_id": "bronx-1976-grandmaster-flash-quick-mix"},
    {"event_id": "bronx-1977-blackout-jul-13"},
    {"event_id": "bronx-1978-disco-fever"},
    {"event_id": "bronx-1979-rappers-delight"},
    {"event_id": "bronx-1980-cold-crush-brothers"},
    {"event_id": "bronx-1981-the-message"},
    {"event_id": "bronx-1982-wild-style-filming"},
    {"event_id": "bronx-1982-planet-rock"},
    {"event_id": "bronx-1983-rock-steady-roxy"},
    {"event_id": "bronx-1984-fashion-moda"},
    {"event_id": "bronx-1984-beat-street"},
]
for k in PREBAKE_KEYS:
    print(f"prebaking {k}...", flush=True)
    r = httpx.post("http://127.0.0.1:30001/biography", json=k, timeout=300)
    print(f"  {r.status_code} {len(r.text)} bytes")
```

**Run from the GN100** (where the orchestrator is). Each call takes ~1m30s on cold cache, ~10ms on warm. The full 19-event prebake takes ~30 minutes. Run it once, all 19 events become instant for the demo.

**Mirrors the existing `data/narration_cache.json` venue WiFi insurance pattern.**

---

## Bug 4 — biography lookup matches buildings without temporal filter

**Discovered while reading the prebake cache output (Session 45, Apr 12 ~03:45 ET).**

The structured retrieval in `src/biography/lookup.py` `find_building_near()` returns the spatially closest building to a query point regardless of when that building was constructed. So an event from 1974 can match a building constructed in 2008 — the lookup says "this is the nearest building to the event coordinates," not "this is the building that existed when the event happened."

**Concrete examples from the prebake cache:**

| Event | Year | Matched BIN | year_built | Distance | Verdict |
|---|---|---|---|---|---|
| `bronx-1973-08-11-sedgwick` | 1973 | 2008286 | **1920** | 14.6 m | ✓ correct |
| `bronx-1974-cedar-park` | 1974 | 2114829 | **2008** | 15.3 m | ✗ didn't exist in 1974 |
| `bronx-1978-disco-fever` | 1978 | 2115819 | **1992** | 29.9 m | ✗ didn't exist in 1978 |
| `bronx-1980-cold-crush-brothers` | 1980 | 2116225 | **2007** | 33.4 m | ✗ didn't exist in 1980 |
| `bronx-1979-rappers-delight` | 1979 | (none) | — | — | ✗ no spatial match within radius |

**Why this matters:** the biography RAG returns text like "the building with BIN 2114829 was constructed in 2008 (NYC Open Data Building Footprints, 5zhs-2jue) ... the anchor event Kool Herc moves outside to Cedar Park is recorded August 1974." The model dutifully cites 2008 as the construction year for a building it then ties to a 1974 event. **A judge reads this and concludes the data spine is broken.** The forensic posture demands these be temporally consistent.

### The fix (~10 min, two edits in `src/biography/lookup.py`)

`find_building_near()` should accept an optional `year` parameter and prefer buildings whose `year_built ≤ year`. Add a soft preference (don't hard-filter — sometimes the building was built shortly after and is still the right historical reference):

```python
def find_building_near(
    lat: float,
    lon: float,
    radius_m: float = 50.0,
    year: int | None = None,
) -> dict[str, Any] | None:
    """Find the nearest building polygon by centroid within radius_m. If
    a `year` is provided, soft-prefer buildings whose `year_built` is
    less than or equal to that year — anachronistic matches (a 2008
    building tied to a 1974 event) are pushed down the ranking even
    when they are spatially closest."""
    candidates = []
    for rec in _load_buildings_by_bin().values():
        d = _haversine_m(lat, lon, rec["centroid_lat"], rec["centroid_lon"])
        if d > radius_m:
            continue
        # Penalty for anachronistic matches: a building built AFTER the
        # event year is geometrically closer but historically wrong.
        # Score = distance + 100m penalty per decade of anachronism.
        anachronism_penalty = 0.0
        if year is not None and rec.get("year_built"):
            yb = rec["year_built"]
            if yb > year:
                anachronism_penalty = ((yb - year) / 10.0) * 100.0
        candidates.append((d + anachronism_penalty, d, rec))

    if not candidates:
        return None
    candidates.sort()
    _, true_d, best = candidates[0]
    return {**best, "distance_m": round(true_d, 1)}
```

Then in `assemble_record()` pass the event year through:

```python
if not building and lat is not None and lon is not None:
    # Pass the event year if we have one, so the lookup prefers
    # historically-consistent buildings over the spatially-nearest one.
    event_year = None
    if record.get("anchor_event"):
        event_year = record["anchor_event"].get("year") or record["anchor_event"].get("start_year")
    building = find_building_near(lat, lon, radius_m=80.0, year=event_year)
```

**After this fix**, re-run `scripts/prebake_biographies.py` to refresh the cache with temporally-consistent matches. The Sedgwick result stays the same (1920 ≤ 1973). The Cedar Park / Disco Fever / Cold Crush matches will either flip to older buildings nearby OR fall through to "no record" if no historically-consistent building is within radius — both more honest than the current ahistorical match.

---

## Bug 5 — MARQUEE table is 3 placeholders, not load-bearing copy

**Where:** `index.html` line 2597.

**The code:**
```js
const MARQUEE = {
  '1001389': { title: 'Empire State Building', year: 1931, body: 'Placeholder. James + Nemotron write the real narrative at the hackathon.' },
  '1013865': { title: 'Flatiron Building', year: 1902, body: 'Placeholder. Click any building to see this card. Carson/James: decide layout, animation, tone.' },
  '1066399': { title: 'One World Trade Center', year: 2014, body: 'Placeholder. The card system is scaffolded -- content, style, and interaction are open for the team.' },
};
```

**The bug:** even the 3 hand-curated marquee buildings have body text "Placeholder. James + Nemotron write the real narrative at the hackathon." A judge clicks the Empire State Building expecting to see the demo's killer feature and reads dev-team meta-commentary. **And 1520 Sedgwick — the entire pitch's anchor address — is NOT in the table at all.**

### Fix shipped (Session 45, Apr 12 ~03:45 ET)

Generated `cultural-content/marquee-bronx.json` with 8 BIN-keyed Bronx hip-hop birth chain entries (will expand to all 19 once the prebake batch completes). Each entry has a hand-written 1-2 sentence body in the forensic posture, not a placeholder. The Sedgwick anchor is included with BIN `2008286`.

**For James to wire (one fetch + merge into MARQUEE at startup):**

```js
// In the existing Promise.all data load block around line 2620:
fetch('cultural-content/marquee-bronx.json')
  .then(r => r.json())
  .then(data => {
    Object.assign(MARQUEE, data.marquee || {});
    console.log(`marquee: merged ${Object.keys(data.marquee || {}).length} hand-curated Bronx entries`);
  })
  .catch(err => console.warn('marquee-bronx.json failed to load:', err));
```

That's the entire integration. The Bronx hip-hop birth chain BINs now show real titles and forensic body copy. The 3 Manhattan placeholders (Empire State, Flatiron, One WTC) still show their placeholder text — replace them by hand if there's time, or let them fall back to the new biography RAG output (Bug 3 fix) when those BINs are clicked.

**File location:** `cultural-content/marquee-bronx.json` (sibling to `cultural-content/oldnyc/index.json`, on the same `feature/sketch-overlay` load path). Schema: `{_meta: {...}, marquee: {<bin>: {title, year, body, event_id, narration_seed, niche_tags, matched_year_built, distance_m}}}`.

---

## Optimization summary — using NYC Open Data better

Right now we have 4 datasets joined in `src/biography/lookup.py`:
1. NYC Building Footprints (5zhs-2jue) — BIN, polygon, height, year
2. NYPL Milstein photos — 750 georeferenced images
3. Wikidata demolished landmarks — 295 records with names
4. events-seed.json — 19 hand-curated cultural events

**The three things we are NOT yet doing that the open data supports:**

1. **Building NAMES from Wikidata demolished landmarks** — when a building polygon centroid matches a landmark name within ~50m, use the landmark name as the building title. ~5 min to wire into `lookup.py`. Lifts Bug 1 instantly for famous buildings.

2. **Address geocoding** — Building Footprints DOES have `base_bbl` (BBL = Borough/Block/Lot), which uniquely identifies the tax lot. The PLUTO dataset (`64uk-42ks`) has the street address keyed by BBL. We don't have PLUTO loaded, but we could either (a) load a PLUTO subset for the addresses on the Cross-Bronx corridor (~2 MB filtered subset, 30 min to pull), or (b) use the OSM Nominatim API to reverse-geocode each polygon centroid (one-shot batch on the 19 demo events, save to `data/event_addresses.json`). **Option (b) is faster for tonight.**

3. **Era taxonomy on the click result** — James has the 8-era taxonomy (Colonial / Antebellum / Gilded / Golden / Deco / Midcentury / Postmodern / Glass) keyed to construction year. The biography RAG isn't using it yet. Add `era` to the structured record in `lookup.py` so the Nemotron prompt includes "this is a [Postmodern] era building" in the context. **5 min in lookup.py + the prompt template.**

---

## Order of operations for James (when he's back at the keyboard)

1. **Bug 1 fix (Option B, biography RAG wire-up)** — replaces the placeholder text with real RAG output. Single highest-leverage UX fix tonight. ~20 min.
2. **Bug 2 fix (Option A)** — tightens the photo fallback to 200m + ±20y of building year. Kills the irrelevant-image complaint. ~5 min.
3. **Pre-bake batch** — run `scripts/prebake_biographies.py` on the GN100 in a tmux pane. ~30 min, fire-and-forget. Warms cache for all 19 demo events.
4. **(Optional) wire era into biography prompt** — 5 min, lifts the narrative quality.
5. **(Optional) reverse-geocode addresses** — 30 min, lifts Bug 1 for the Cross-Bronx corridor specifically.

**Items 1-3 are the must-haves. Items 4-5 are nice-to-haves for Sun morning rehearsal.**
