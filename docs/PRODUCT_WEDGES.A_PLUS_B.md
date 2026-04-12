# Product Wedges — A+B Rewrite Draft (companion to PRODUCT_WEDGES.md)

> **Drafted Apr 11 ~16:30 ET. Held in working tree pending standup approval.** This rewrite collapses the original 5-buyer-segment table into a single thesis with **two output surfaces over one engine**. If validated at the 3-4 PM standup, this file replaces `PRODUCT_WEDGES.md` post-hackathon. For now both files coexist; the original stays canonical until the team signs off.
>
> **What changed from the original**: dropped 5 buyer segments → 2 named surfaces. Dropped "5 named personas" table → 2 named personas (Sofia Reyes, Dr. Alicia Vance). Added the unifying "one engine, two surfaces" frame. Folded ComfyUI (James's Apr 11 ~17:30 ET drop on `feature/sketch-overlay`) into Surface B. Kept the receipts thesis, the four data layers, and the rubric mapping unchanged.

---

## The thesis line (unchanged)

> **"We don't predict gentrification. We trace it from the receipts. Every particle is a person who moved, on record, in open data."**

## The new unifying line (added)

> **"Sixth Borough turns NYC's open record into both legal evidence and cultural memory — locally, on hardware the user owns, with no document ever leaving the room."**

This is the line for the Antler conversation, the Sun afternoon investor 1:1s, and the post-demo Q&A. It is NOT the cold open of the 90-second video — the locked thesis ("cultural memory infrastructure on local hardware") still leads the recorded pitch.

---

## One engine, two surfaces

Sixth Borough is one extraction engine (Nemotron-3 Nano 30B from the NVIDIA Nemotron model family + the four NYC Open Data layers + the 750-photo NYPL Milstein corpus + James's 8-era architectural taxonomy + the demolished landmarks layer) with two output skins. **The engine is identical for both surfaces. Only the output format and the buyer differ.**

| | Surface A — Forensic | Surface B — Reanimation |
|---|---|---|
| **What it produces** | A 4-page footnoted "building biography" PDF for any NYC address | A restylized archival video + locally-generated captions for any historical event |
| **ICP** | Tenant lawyers, Right to Counsel orgs, small RE litigation firms | NYPL, Bronx Historical Society, museum curators, doc filmmakers, university presses |
| **Named persona** | **Sofia Reyes**, tenant lawyer at Bronx Legal Services | **Dr. Alicia Vance**, preservation researcher at LPC |
| **Tomorrow-morning use** | Pulls every owner / violation / permit / demolition / eviction filing on a single block to build a holdover hearing in 30 seconds instead of 6 paralegal hours | Feeds an Ellis Island 1903 archival film + her LPC designation report into the box, gets back a stylized 90-second clip with footnoted captions for the museum opening |
| **Why local hardware** | Client confidentiality — confidential tenant files cannot be uploaded to OpenAI | Rights holders (NYPL, museums, estates) will not upload originals to a cloud service |
| **Engine call** | Nemotron extracts structured claims from DOB / LPC / court filings → renders to a templated PDF | Nemotron writes captions over ComfyUI-stylized footage (SD1.5 + 3DRenderStyle LoRA, on James's `feature/sketch-overlay` Comfy pipeline) |
| **NVIDIA stack used** | Nemotron 30B (NeMo Models) | Nemotron 30B + SD1.5 + LoRA (NeMo Models + Stable Diffusion stack on the same GB10 unified memory) |
| **Pricing** | $500-2000/mo per seat SaaS | $5-50K per project licensing |
| **Validation cycle** | 4 weeks (find one tenant lawyer, watch them use it on a real case) | 6 months (museum procurement) |
| **Why now** | NYC right-to-counsel just expanded — 20K new tenant cases/year need building histories | ComfyUI 3DRenderStyle + Nemotron captioning is a fresh capability nobody else is shipping |

## Why both, not pick one

These are not two products. They are **two skins on the same machine**, and they feed each other:

1. **Surface B is the brand layer that opens doors for Surface A.** Museums and historical societies are where the *primary documents lawyers need* are catalogued — LPC reports, oral history archives, neighborhood photo collections. A museum partnership for Surface B literally adds rows to Surface A's data spine.

2. **Surface A pays the rent that funds Surface B.** Cultural reanimation has a 6-month sales cycle and a procurement-officer buyer. Lawyers have a 4-week sales cycle and a hair-on-fire buyer. A pays for B's runway.

3. **Both require local inference, for different legal/contractual reasons.** This is the strongest version of the "why local hardware" pitch — it stops being an ideological flex and becomes the only legally compliant way to do the work.

4. **The same Nemotron extraction is doing both jobs.** Reading a court filing for Sofia and writing a caption for Alicia are the same operation: structured extraction over high-stakes historical documents that cannot leave the building.

---

## Four non-ML data layers (unchanged from original — both surfaces draw from these)

Each layer is a queryable historical truth, sourced entirely from public open data. None require a model. All are renderable in James's existing deck.gl/maplibre prototype + Carson's Bevy native client.

| Layer | Source | What it shows | Surface A use | Surface B use |
|---|---|---|---|---|
| **Demolitions** | DOB Job Filings (job_type DM) + Building Footprints Historical (`s5zg-yzea`) | Buildings lost, when, where → pin to OldNYC photos | "Adjacent demolitions in last 20 years" → tenant displacement claim or REIT acquisition risk | Photo-billboard ghosts at demolition sites for the museum installation |
| **Demographic shift** | ACS tract decennial 1970-2020 | Race / income / age / language at tract level over 50 years | Quantified displacement evidence for a holdover hearing | Density-shift particle field in the museum's Cross-Bronx exhibit |
| **Evictions** | NYC HCR / OCA eviction filings | Filings by tract/year → direct displacement signal | Pattern of filings on a block by a single landlord | Caro-style narrative anchor for the reanimation pipeline |
| **Alterations** | PLUTO `yearalter1` / `yearalter2` (`64uk-42ks`) | When buildings were renovated → proxy for capital flowing into a block | Capital-flow timeline for due diligence | "When did this block get re-skinned" for the oral history layer |

Plus James's already-shipped layers: 8-era architectural taxonomy (Colonial / Antebellum / Gilded / Golden / Deco / Midcentury / Postmodern / Glass), 750 NYPL Milstein photos × 5 boroughs, 295 Wikidata demolished landmarks, immigration arrivals 1719-2026.

---

## Marvens's role — Cross-Bronx as the canonical anchor for both surfaces

Cross-Bronx Expressway 1948-1972, ~60K displaced (Caro). Marvens's Sun deliverable (1-2 ghost meshes + 1 migration cone) is now load-bearing for **both** product surfaces:

- **For Surface A**: the Cross-Bronx cone is the visual hook in a Sofia Reyes demo of "this is what 60K displacement filings looks like across 24 years." The DOB demolition records + ACS tract delta + eviction filings sit underneath the cone as the receipts.
- **For Surface B**: the Cross-Bronx cone is the centerpiece of the museum installation Dr. Alicia Vance commissions. The cone's accompanying ComfyUI-stylized archival footage (Bronx fire engine clips, 1980s tenement demolition films) IS the licensable asset.

One canonical example. Two product surfaces. No double work.

---

## Two named usability personas (collapsed from 5)

The Spark Hack rubric explicitly asks: *"Could a real City Planner, or Factory Foreman actually use this tool to make a decision tomorrow?"*

| Persona | Tomorrow-morning use case | Surface |
|---|---|---|
| **Sofia Reyes**, tenant lawyer at Bronx Legal Services | Pulls every demolition + eviction filing + alteration record on a single block to build a displacement case for a holdover hearing — 30 seconds vs 6 paralegal hours | A |
| **Dr. Alicia Vance**, preservation researcher at the Landmarks Preservation Commission | Feeds an Ellis Island 1903 archival film into the box, gets back a stylized 90-second museum clip with locally-generated captions footnoted to LPC designation reports — for an exhibit opening next month | B |

These are illustrative archetypes, not real people, but they're concrete enough to drop into a Q&A answer. **For the demo, lead with Sofia Reyes.** She lands the cultural-impact-track ethics test cleanly, has the shortest path to revenue, and the displacement case framing pairs naturally with the Cross-Bronx anchor on screen. Mention Alicia second, as the brand-layer / museum-partnership story.

Dropped from the original five-persona table: Marcus Chen (REIT analyst), Jordan Park (ProPublica reporter), Riya Patel (insurance underwriter). **Reason:** five personas was variance, not signal. Pick the two you'd actually pitch to next week.

---

## Mapping to the Spark Hack judging rubric (refined)

| Category | What this doc contributes | Pts at stake |
|---|---|---|
| **Value & Impact → Insight Quality** | Cross-Bronx 60K Caro receipts, BUILDING_HISTORIC dataset, ACS tract delta, 8-era architectural taxonomy, 295 demolished landmarks — non-obvious and traceable | 10 |
| **Value & Impact → Usability** | Two named personas, each with a concrete tomorrow-morning decision the tool enables. Hits the rubric's exact "could a real City Planner use this tomorrow" test without spreading thin across 5 markets | 10 |
| **NVIDIA Ecosystem → The Stack** | Two NVIDIA models on one box: Nemotron 30B (NeMo Models, 15 pts) + SD1.5 + 3DRenderStyle LoRA via ComfyUI on the GB10. Both load locally into the same 128 GB unified memory | 15 |
| **NVIDIA Ecosystem → Spark Story** | "128 GB unified memory holds a 30B reasoning LLM AND SD1.5 image diffusion AND the renderer simultaneously. No team without unified memory can do this on one box. Both legal and museum customers require local inference for compliance / rights reasons." | 15 |
| **Frontier Factor → Creativity** | Six-dataset fusion + two NVIDIA models orchestrated on one box for two unrelated buyer segments | 10 |
| **Frontier Factor → Performance** | 29 tok/s sustained on Nemotron, ~8 minutes for a Phase 2 ComfyUI video pass on the GB10 | 10 |

Estimated rubric impact post-A+B-rewrite: **+3 to +5 pts** over the c62e87b baseline (~93/100), driven by the second NVIDIA model (ComfyUI) entering The Stack score and the sharper Usability narrative. New estimate: **~96-98 / 100** if ComfyUI demonstrably runs on the GN100 by Sun morning.

---

## What this does NOT change

- The locked 90s demo thesis ("cultural memory infrastructure on local hardware") stays the spine of the recorded pitch
- The four non-ML data layers are unchanged
- The Bronx hip-hop slice stays the cinematic anchor for the recorded video
- No predictive ML added — A is forensic, B is reanimation, neither forecasts
- Marvens still ships 1-2 ghost meshes + 1 Cross-Bronx migration cone for Sun. The deliverable is unchanged but now serves both pitches.
- The GB10 stays the showpiece. The local-first thesis is unchanged.
- James's `feature/sketch-overlay` branch is still the data spine. Carson's Bevy is still Mode B Encounter.

---

## Open questions to resolve at standup

1. **Does the team buy the "two surfaces, one engine" frame?** If yes, this file replaces `PRODUCT_WEDGES.md` post-hackathon. If no, this draft gets deleted and the original stays.
2. **Can ComfyUI demonstrably run on the GN100 by Sun morning?** James's `setup-comfy-linux.sh` lands at the venue tonight. If Phase 1 (stills) works by midnight, Surface B is real for the demo. If it doesn't, drop ComfyUI from the pitch and frame Surface B as "locally-generated captions over archival photos" instead of stylized video.
3. **Hand-curated Sofia Reyes building biography sample**: needs to exist as a literal PDF in `docs/samples/` by Sun morning. ~2 hours of work for Alex Sat night. This is the demoable artifact for Surface A.
4. **Antler 1:1 framing**: lead with the unifying line ("legal evidence + cultural memory") or lead with the unicorn-bounty line ("two products, one box, two markets, both compliance-locked to local inference")? Probably the second for Wouter / Marvens's Antler ally — it's more investable.
5. **Drop Bevy from post-hack scope?** If A+B is the product, Bevy is a demo prop, not a product component. James's deck.gl + Sofia's PDF + Alicia's video file is the entire post-hack stack. Decide post-hack, not at standup.

---

## Append-only changelog

- **Apr 11 ~16:30 ET** — drafted A+B rewrite as companion file. Original `PRODUCT_WEDGES.md` remains canonical pending team validation at 3-4 PM standup. Authors: Alex.
