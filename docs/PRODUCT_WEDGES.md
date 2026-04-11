# Product Wedges — Sellable Applications Beyond Museum Tour

> **Locked Apr 11 ~14:00 ET.** Sixth Borough's defensible wedge isn't the museum/tour-guide framing — it's the **non-ML historical-truth layer** sitting underneath the cultural memory experience. Every claim is traceable to an open data record. We don't predict; we trace.

The cultural memory ghost layer (NYPL photos + Nemotron narration + PS2 aesthetic) is the **emotional onramp** that makes the data layer memorable. The data layer is what people pay for.

For the data sources behind every wedge below, see `docs/DATA_SOURCES.md`. For the locked pitch thesis, see `docs/PITCH_FRAMINGS.md` and `docs/DEMO_VIDEO_SCRIPT.md`.

---

## The thesis line

> **"We don't predict gentrification. We trace it from the receipts. Every particle is a person who moved, on record, in open data."**

ML prediction is wrong for this problem space — predicting gentrification IS gentrification, and the room (Spark Hack judges + Antler GPs + community-data audience) will read predictive overlays as extraction theater. The defensible move is the opposite: surface the receipts that already exist, anchor them to historical events, and let the user draw their own conclusions.

This is also the framing that makes the GB10 sponsored-product flex coherent end-to-end: local hardware → local memory → local sovereignty → no model trained on community pain.

---

## Four non-ML data layers

Each layer is a queryable historical truth, sourced entirely from public open data. None require a model. All are renderable in James's existing deck.gl/maplibre prototype + Carson's Bevy native client without new infrastructure.

| Layer | Source | What it shows | Ghost mode expression |
|---|---|---|---|
| **Demolitions** | DOB Job Filings (job_type DM) + Building Footprints Historical (`s5zg-yzea`) | Buildings lost, when, where → pin to OldNYC photos for "what was here" | Photo-billboard ghosts at demolition sites, dated to permit issuance |
| **Demographic shift** | ACS tract decennial 1970-2020 | Race / income / age / language at tract level over 50 years | Density-shift particle field, time-scrubbable per decade |
| **Evictions** | NYC HCR / OCA eviction filings | Filings by tract/year → direct displacement signal | Filing-flag particles emerging at recorded addresses, decay over time |
| **Alterations** | PLUTO `yearalter1` / `yearalter2` (`64uk-42ks`) | When buildings were renovated → proxy for capital flowing into a block | Building re-skin animation tied to alteration year |

All four layers are additive on top of the existing OldNYC photo index (`cultural-content/oldnyc/index.json`) and the borough building compactor (`scripts/export_buildings.py`). No new data spine required.

---

## Marvens's role: particle effects as data tracers (not predictors)

The particle effect work Marvens is bringing to Sixth Borough can carry the data narrative if we frame each particle as a **documented historical movement**, not a forecast.

### Concrete particle expressions

1. **Displacement vectors** — at a demolished building site, particles emit FROM the site and flow to ACS-documented destination tracts where that community resettled. Anchored to a documented event:
   - Cross-Bronx Expressway 1948-1972 → south Bronx residents pushed to outer Bronx, north Manhattan, South Florida
   - Tompkins Square Riots 1988 → Lower East Side artists/working class displaced to outer boroughs
   - Atlantic Yards 2009 → Prospect Heights tenants displaced to Bed-Stuy, East NY
2. **Density shift** — particle density at a tract scales with population over time (1970→2020 ACS). Time-scrub the decade and watch density move. Pure census counts, no model.
3. **Era color coding** — particles inherit a PS2 palette band per source decade. The visual rhythm of "the 70s left here, the 90s arrived, the 2010s priced everyone out" is readable in 5 seconds.
4. **Anchored to receipts** — every particle stream is tied to a documented event. Click a stream → shows the ACS table + the photo + the news clipping.

### What Marvens actually needs to ship for Sun

One canonical example, not all 5 boroughs of particles:
- 1-2 ghost meshes per the visual direction contract (`docs/VISUAL_DIRECTION.md`)
- 1 displacement-vector particle prototype anchored to ONE historical event (Cross-Bronx is the strongest single anchor — most cinematic, best-documented, NYC-mythic)

Quality of the canonical example sells the framework. Volume comes after the hackathon.

---

## Sellable wedges

The cultural memory experience is the door. The data layer is the durable product. Five buyer segments, each defensible without ML:

### 1. Real estate due diligence ($$$)
**Buyer:** Buyers, brokers, REITs, family offices.
**Product:** "Pull a 50-year truth report on any block before you buy." Demolition history, alteration history, demographic shift, eviction filings, historic photo overlay — one report.
**Pricing:** Per-query (~$50-200), portfolio subscription, or white-label API for brokerage platforms.
**Why defensible:** the receipts are open data but the assembly + UX + provenance trail is hard. Compstak/Reonomy charge thousands for far less historical depth and zero cultural context.

### 2. Tenant orgs / legal aid (mission, distribution play)
**Buyer:** Right to Counsel orgs, tenant unions, legal aid clinics, Furman Center, community land trusts.
**Product:** Free tier + branded reports for organizing campaigns. Eviction filings overlayed on demolition permits + new construction in one view. Tells the displacement story for tenant lawyers and organizers.
**Pricing:** Free tier + grant funding + paid white-label for legal aid orgs.
**Why important:** distribution + credibility flywheel. These users become the political backstop that makes the receipts moat defensible. "Used by the Legal Aid Society" is the credential that lets us charge real estate firms more.

### 3. Journalists / academics (citation play)
**Buyer:** ProPublica, The City, Bloomberg CityLab, Furman Center, Pratt Center, Columbia urban planning, NYU Wagner.
**Product:** API access + queryable historical layer for stories.
**Pricing:** Tiered API subscription ($500-5000/yr) + free tier for non-profit newsrooms.
**Why defensible:** every citation strengthens the moat. "Cited by ProPublica" is a credential that compounds.

### 4. Preservation orgs (grant-funded buyer)
**Buyer:** Landmarks Preservation Commission, Historic Districts Council, neighborhood preservation societies.
**Product:** Historic photo + demolition + LPC database crosswalk for landmark advocacy. "What got demolished here, when, and why."
**Pricing:** Annual license + custom research projects.
**Why defensible:** the BUILDING_HISTORIC + LPC + NYPL photo joins are non-trivial and the audience already pays for less.

### 5. Insurance / underwriting (long-tail high-value)
**Buyer:** Property insurers, climate risk modelers, reinsurers.
**Product:** Building age + alteration history + neighborhood claims for risk assessment, anchored to the actual historical record rather than statistical proxies.
**Pricing:** Enterprise contract.
**Why defensible:** building age and alteration history are inputs every insurer wants but few have at parcel-level granularity for NYC.

---

## What this changes about the pitch

It doesn't replace the locked thesis — *"cultural memory infrastructure on local hardware"* stays the spine. The wedge story lives in the **post-demo Q&A and the Antler conversation**, not the 90-second video.

When a judge or VC asks *"what's the path to a real product?"*:

> *"The cultural memory experience is the door. The data layer underneath is the product. We've identified four queryable historical truth layers from NYC Open Data — demolitions, demographic shift, evictions, alterations — and five buyer segments that pay for receipts today but can't get them assembled like this. We don't predict gentrification. We trace it. Every particle in the demo is a documented historical movement, not a forecast."*

That's the answer that turns *"cool hackathon project"* into *"fundable wedge."*

---

## What this does NOT change

- The 90s demo script stays locked (`docs/DEMO_VIDEO_SCRIPT.md`)
- The four pillars stay locked (Time Machine, PS2 Memory Aesthetic, Cultural Intelligence, Niche Discovery)
- The Bronx hip-hop slice stays the cinematic anchor for the recorded video
- No ML / prediction work added to the build
- No new infrastructure required — the existing renderer + data spine handles all four layers
- Marvens still ships 1-2 ghost meshes for Sun. Particles are ONE canonical example, not a full system.
- The GB10 stays the showpiece. The local-first thesis is unchanged.

---

## Open questions to resolve post-hack

1. Which of the five buyer segments has the shortest path to first revenue? Best guess: real estate due diligence (highest willingness to pay) or preservation orgs (warmest intro path through LPC contacts).
2. Does the displacement-vector particle prototype need IRB / community-board sign-off if we name specific historical events? Probably yes for any community-facing release. For demo purposes, citing public historical events is fair use.
3. Where does the data layer live operationally — on the GB10 alongside narration, or in a separate cloud service? The local-first thesis says the GB10 stays the showpiece; the cloud service is the SaaS layer for the wedge customers. Two-tier deployment.
4. Antler conversation framing: lead with the wedge (5 buyer segments) or lead with the thesis (local hardware sovereignty)? Probably thesis first, wedge as the "and here's how it makes money" beat.

---

*Drafted Apr 11 ~14:00 ET at the venue, post-renderer-merge planning conversation. Locked the "no ML / receipts not predictions" framing + the four data layers + the five buyer segments. See companion entry in `docs/DECISIONS.md`.*
