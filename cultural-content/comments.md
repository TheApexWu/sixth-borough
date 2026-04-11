Includes footage of the Bronx to fit with the Bronx deepdive.
- video of breakdancing, DJs, music and block parties, burning buildings
- images of buildings, environment, people, poverty, culture

## External assets

- **Ellis Island 3D model** (zip, ~149 MB) — hosted on Google Drive (too large for the repo):
  https://drive.google.com/file/d/124aYpsfN3TcRzhvMBgAY1h8vqvTRlOIJ/view?usp=sharing

## oldnyc/ — NYPL Milstein historical photo index (all 5 boroughs)

Shared archival photo resource, usable by any renderer path (James's WebGL
sketch-overlay, Carson's Rust/wgpu, the orchestrator, etc.). Wired at the asset
layer so branches only need to add their own hover/click/narration logic.

**Source:** NYPL Milstein Division tax photos, exposed via
https://www.oldnyc.org/data.json. The raw 75 MB dataset is gitignored
(`cultural-content/oldnyc/raw/`) — re-download with the build script below.

**Coverage (committed):** 750 photos, 150 per borough, years 1900–1990, evenly
sampled chronologically per borough. ~26 MB on disk.

**Folder layout:**
- `cultural-content/oldnyc/index.json` — slim index, one record per photo:
  `{ id, boro, lat, lon, year, title, thumb, nypl_url }`
- `cultural-content/oldnyc/thumbs/{photo_id}.jpg` — 600 px local thumbnails,
  offline-ready (satisfies the cable-off pillar from KICKOFF)
- `cultural-content/oldnyc/raw/data.json` — gitignored; only present locally
  after running the build script

**How to use from a renderer:**
1. Load `cultural-content/oldnyc/index.json` at startup
2. On hover/click at a lat/lng, find the nearest photo(s) within ~100 m AND
   within ±N years of the current slider year
3. Show `<img src="{record.thumb}">` + `record.title` + attribution line:
   *"NYPL Milstein Division via oldnyc.org"*
4. Click-through to full NYPL record via `record.nypl_url`

**To re-run the build** (resample, change year range, expand per-borough cap):
```
# one-time: download the raw dataset (75 MB, gitignored)
mkdir -p cultural-content/oldnyc/raw
curl -L https://www.oldnyc.org/data.json -o cultural-content/oldnyc/raw/data.json

# run the build (idempotent — skips existing thumbnails)
python3 scripts/build_oldnyc_index.py --help
python3 scripts/build_oldnyc_index.py                          # defaults: 1900–1990, 150/boro
python3 scripts/build_oldnyc_index.py --max-per-boro 300       # denser coverage (~1500 photos, ~75 MB)
python3 scripts/build_oldnyc_index.py --boroughs Bronx --year-min 1965 --year-max 1985 --max-per-boro 0
```

**Attribution requirement:** Milstein photos are public domain, but the demo
video + README + `docs/DATA_SOURCES.md` must credit *"NYPL Milstein Division
via oldnyc.org"*. Do not strip this.