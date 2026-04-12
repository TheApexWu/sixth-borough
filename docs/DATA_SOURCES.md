# NYC Open Data — Source References

Build-time reference for the data layer. All sources verified against `data.cityofnewyork.us` Apr 2026. License: NYC Open Data Terms of Use unless noted.

## What's actually loaded into the demo (Apr 12 ~03:30 ET, Session 45)

Four datasets are committed in the repo and joined by `src/biography/lookup.py` at runtime:

| Source | Where in repo | Used by |
|---|---|---|
| **NYC Building Footprints `5zhs-2jue`** (NYC OTI) — all 5 boroughs, ~1.05M buildings, LiDAR roof heights + construction year + BIN | `data/{manhattan,bronx,brooklyn,queens,staten}_compact.json` (262 MB total) | deck.gl renderer + biography RAG |
| **NYPL Milstein Picture Collection** — 750 georeferenced archival photos × 5 boroughs, 1900-1956 | `cultural-content/oldnyc/index.json` (James `bde0148`) | story card photo gallery + biography RAG nearby_photos |
| **Wikidata demolished NYC landmarks** — 295 records with name + built/demolished years + lat/lon | `data/demolished-landmarks.json` (sketch-overlay `277e8d9`) | biography RAG nearby_landmarks |
| **Hand-curated cultural events** — 19 events anchored on the Bronx hip-hop birth chain (Cross-Bronx 1959 → Puerto Rican migration → Loew's Paradise → Kool Herc 1973 → Wild Style → Beat Street) | `data/events-seed.json` (and pre-baked at `data/narration_cache.json` + `data/biography_cache.json`) | `/narrate` + `/biography` anchor events |
| **NYC Borough Boundaries `gthc-hcne`** (NYC DCP) — 5 polygon features for the red-outline overlay | `data/borough_boundaries.geojson` (3.2 MB) | deck.gl GeoJsonLayer |

Everything below is the broader architecture reference — datasets the schema is *designed for* but not yet wired in. Add to the loaded set above as time permits, or post-hack.

---

## Tier 1 — load-bearing for the data spine

### Building Footprints Historical Shape — `s5zg-yzea`
Historical building footprint geometry, every borough.
- **Why it matters:** has both `construction_year` and `demolition_year` as first-class fields. This is the literal time-machine data layer — query "every building that existed in year X" or "every building demolished between A and B" in one statement.
- **Schema:** `base_bbl`, `bin`, `construction_year`, `demolition_year`, `doitt_id`, `feature_code`, `geom_source`, `ground_elevation`, `height_roof`, `last_edited_date`, `last_status_type`, `mappluto_bbl`, `name`
- **Cadence:** weekly. Last updated Jan 23 2025.
- **Note:** prior versions retained per Local Law 106 of 2015.
- **URL:** https://data.cityofnewyork.us/Housing-Development/Building-Footprints-Historical-Shape/s5zg-yzea

### Building Footprints — `5zhs-2jue`
Modern building geometry, all five boroughs.
- **Scale:** 1,053,713 buildings citywide.
- **Inclusion:** buildings >400 sq ft and >12 ft tall, plus all buildings with a BIN.
- **Schema highlights:** BIN, BBL, ground elevation, roof height, construction year, feature type.
- **Cadence:** daily by NYC OTI, released weekly. Metadata last updated Oct 9 2025.
- **URL:** https://data.cityofnewyork.us/City-Government/Building-Footprints/5zhs-2jue

### PLUTO — `64uk-42ks`
Tax lot characteristics for every lot in NYC.
- **Scale:** all five boroughs, ~70 fields per lot.
- **Latest release:** 25v4 (January 2026).
- **Field highlights:** year built, building use, height, land use, lot dimensions, zoning, owner.
- **Historical PLUTO archive:** previously released versions on NYC DCP "Bytes of the Big Apple" portal back to 2002.
- **GitHub:** https://github.com/NYCPlanning/db-pluto
- **URL:** https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO-/64uk-42ks

### LPC Individual Landmark and Historic District Building Database — `7mgd-s57w`
NYC Landmarks Preservation Commission's authoritative cultural-heritage layer.
- **Scale:** ~36,000 buildings, drawn from 50+ years of LPC designation reports. Includes 1,408 individual landmarks, 125 interior landmarks, 12 scenic landmarks, and ~34,000 buildings within 141 historic districts.
- **Why it matters:** every entry is a pre-validated cultural reference point. Includes architect, era, style, designation date, designation report.
- **URL:** https://data.cityofnewyork.us/Housing-Development/LPC-Individual-Landmark-and-Historic-District-Buil/7mgd-s57w

### 1940s Tax Department Photographs — NYC Municipal Archives
Photographs of every single building in all five boroughs ca. 1940.
- **Scale:** 720,000 images. WPA-organized photography teams shot every property in NYC for the Department of Taxation between 1939 and 1941.
- **Why it matters:** for any historical building in our scope, this is the visual reference that makes the point cloud ghost layer possible without speculating.
- **Spatial organization:** by block + lot number — joinable directly to BBL in PLUTO and Footprints.
- **Access:** Free low-res (watermarked) via the Municipal Archives Online Gallery (Preservica) and the community map at 1940s.nyc. High-res files via DORIS (commercial / bulk terms TBD).
- **URLs:**
  - https://nycrecords.access.preservica.com/1940s-tax-photographs/
  - https://1940s.nyc/

### 1980s Tax Photographs — NYC Municipal Archives
Color photographs of every NYC building, 1983–1988.
- **Scale:** ~800,000 color images.
- **Why it matters:** for any era window after 1983, this is the closest visual reference to the actual era we're rendering. For the Bronx hip-hop birthplace window in particular, the 1980s color photos are era-aligned in a way the 1940s collection is not.
- **Access:** same portal family as the 1940s collection.

---

## Tier 2 — useful for specific niches and validation

### NYC Demolition Building — `j7h9-tb8p`
DOB demolition job applications, 94 columns, daily updated.
- **Coverage caveat:** post-2010 only. For pre-2010 demolitions, use `s5zg-yzea`'s `demolition_year` field instead.
- **Field highlights:** Job #, Borough, Job Type, Building Type, latitude, longitude, council district, census tract, dimensional data.
- **URL:** https://data.cityofnewyork.us/Housing-Development/NYC-Demolition-Building/j7h9-tb8p

### Historical DOB Permit Issuance — `bty7-2jhb`
Pre-DOB-NOW historical permits.
- **URL:** https://data.cityofnewyork.us/Housing-Development/Historical-DOB-Permit-Issuance/bty7-2jhb

### Historic Districts Map — `xbvj-gfnw`
Polygon boundaries of all 141 historic districts that have been calendared, heard, or designated by LPC.
- **Why it matters:** the niche filter UI can color the map by historic district to give users a sense of "this is the protected area, this is where things keep getting torn down."
- **URL:** https://data.cityofnewyork.us/Housing-Development/Historic-Districts-Map-/xbvj-gfnw

### LPC Designation Photo Collection
Authoritative photographs of NYC designated landmarks and historic districts. Cleaner than tax photos for landmark-quality buildings.
- **URL:** https://nyclandmarks.lunaimaging.com/luna/servlet/NYClandmarks~2~2

### Discover NYC Landmarks
LPC's interactive map with style/architect/era filters. Useful as a reference for the niche taxonomy schema (we can borrow the categories an expert agency already designed).
- **URL:** https://www.landmarks.nyc/

---

## Outside-NYC-Open-Data Sources

### NYPL Digital Collections API
- **Free** with token signup. **10,000 requests/day** per token.
- **Scale:** 1M+ machine-readable objects. Includes ~200,000 NYC photographs spanning 1870s–1970s, bulk taken 1910–1940.
- **High-res images:** `highResLink` field returns the original uncropped 8-bit TIFF (often >200MB), gated on rights status.
- **Geographic query gotcha:** the API doesn't natively support coordinate queries. Geographic info lives in MODS subject fields. Workaround: query by neighborhood / address terms, then join coordinates manually.
- **API docs:** https://api.repo.nypl.org/api_documentation_v1
- **Browse:** https://digitalcollections.nypl.org/

### OldNYC
Community-built map of geocoded historical NYC photos pulled from NYPL collections.
- **Why it matters:** the geographic-coordinate join that NYPL's API doesn't natively support has *already been done* by this project. Open source, can be ingested directly.
- **URL:** https://www.oldnyc.org/

### NYC Municipal Archives Online Gallery (Preservica)
Beyond the tax photos, also includes maps, blueprints, vital records, sound recordings, and motion pictures from the largest local government archive in North America.
- **URL:** https://nycrecords.access.preservica.com/

### Cornell University Hip Hop Collection
Specific to the demo niche. 250,000+ items established in 2007.
- **Holdings include:** Afrika Bambaataa personal archive, Joe Conzo Jr. photographs (the photographer of early Bronx hip-hop), Charlie Ahearn (director of *Wild Style*) archive, Buddy Esquire flyer collection, Grandmaster Caz papers, Bill Adler (Def Jam publicist) archive.
- **URL:** https://rmc.library.cornell.edu/hiphop/

---

## Open validation questions

Things to confirm before any of these sources is wired into a runtime ingest path.

1. **DORIS licensing for 1940s + 1980s tax photos.** Are watermarked low-res versions free for use beyond personal/research? What's the actual cost of bulk high-res access? Email DORIS at the contact form on archives.nyc to clarify.
2. **Historical Building Footprints earliest-year coverage.** Schema confirms `construction_year`, but how far back do records actually reach? NYC building records get spotty pre-1880. Query the dataset directly to find the floor.
3. **Historical PLUTO schema stability across versions.** The 2002 release and the 2026 release have different field sets. Check the `db-pluto` GitHub repo for version-by-version field diffs before relying on a specific historical year.
4. **Joe Conzo Jr. photo rights.** Archive is at Cornell but reproduction rights presumably his / his estate. For any Bronx-1973 visual reference that involves his images, contact required.

---

## How this maps to the four pillars

| Source | Time Machine | PS2 Aesthetic | Cultural Intelligence | Niche Discovery |
|---|---|---|---|---|
| Building Footprints Historical Shape (`s5zg-yzea`) | core | — | — | — |
| Building Footprints (`5zhs-2jue`) | base layer | — | — | — |
| PLUTO (`64uk-42ks`) | strong | — | supporting | supporting |
| 1940s Tax Photos | strong | core | supporting | supporting |
| 1980s Tax Photos | strong | core | supporting | supporting |
| LPC Landmark DB (`7mgd-s57w`) | supporting | — | core | strong |
| Historic Districts Map (`xbvj-gfnw`) | supporting | — | strong | supporting |
| LPC Designation Photo Collection | — | strong | strong | supporting |
| NYPL Digital Collections | supporting | strong | strong | strong |
| OldNYC | supporting | strong | strong | supporting |
| Cornell Hip Hop Collection | supporting | strong | core (hip-hop niche) | core (hip-hop niche) |
| Municipal Archives (Preservica) | strong | strong | strong | strong |

---

*Add to this file when you find a source worth referencing later. Keep entries terse — name, ID or URL, why it matters, schema highlights, access notes.*
