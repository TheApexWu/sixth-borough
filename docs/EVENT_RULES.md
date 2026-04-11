# Spark Hack Series NYC — Event Rules + Judging Rubric

Apr 10–12 2026 · 33 W 17th St · **Cultural Impact** track · Hosted by NVIDIA, Acer, Antler

Source: https://concrete-panther-c83.notion.site/Spark-Hack-Series-New-York-Presented-by-NVIDIA-Acer-and-Antler-611f567d17cc8207881a0162071001c8 (full text pulled via Notion v3 API Apr 11 ~15:25 ET).

## Wifi
- 5th floor: `33-west 17-5th FL` / `collaboration5`
- 6th floor: `A Founder House` / `shipitalready`

## Submission
- Airtable (legacy from earlier session): https://airtable.com/appWQWPtBqDUhCPPj/shriBT3uu4JLtlSr7
- **NEW: official submission link "coming soon" on the Notion** — watch Discord `#spark-hack-nyc` for the drop. (Apr 11 ~15:25 ET status: not yet posted.)
- **Code freeze: Sun Apr 12 11:00 AM HARD**
- Discord channel: `#spark-hack-nyc`
- Required deliverables (per Notion): Submission Checklist sub-page exists; Demo Video Instructions sub-page exists. **Pull both before standup.**

## Tracks (3 total — choose one)

1. **Human Impact**: Health, safety, economic well-being of NY residents. Tools that improve individual lives, streamline access to social services, or promote economic equity.
2. **Environmental Impact**: Sustainability, urban resilience, smarter resource management. Optimize energy/waste/movement.
3. **Cultural Impact** ← **OURS**: *"Celebrating the soul of New York through arts, recreation, and community identity. Use data to make the city's rich cultural and recreational offerings more accessible, or to preserve the history of its unique neighborhoods."*

Each track defines a theme, NOT scope of idea. Teams free to build any solution using NYC open data.

## Judging Philosophy (verbatim from Notion)

> *"We are judging Systems Engineering. A winning project isn't just a slide deck or a simple API wrapper; it is a functioning system that ingests raw data, processes it locally using the Acer Veriton GN100 AI Mini Workstation, and produces a valuable result."*

## The Scoring Breakdown (100 Points Total)

### 1. Technical Execution & Completeness (30 pts)
*"Did they actually build a working, complex system?"*

- **Completeness (15 pts)**: Does the system successfully complete the full data workflow without crashing?
- **Technical Depth (15 pts)**: Is there significant engineering "under the hood"? Did they build a complex pipeline (e.g., **Simulation, RAG, Fine-Tuning, or Custom Logic**) rather than just a simple static dashboard or basic API wrapper?

### 2. NVIDIA Ecosystem & Spark Utility (30 pts)
*"Did they leverage the unique hardware and software provided?"*

- **The Stack (15 pts)**: Did they use at least one major NVIDIA library/tool? Examples listed: **NIMs, RAPIDS, cuOpt, Modulus, NeMo Models**. **CRITICAL**: *"Merely calling GPT-4 via API gets 0 points here."*
- **The "Spark Story" (15 pts)**: Can they articulate **why** this runs better on a DGX Spark? Examples listed: *"We used the 128GB Unified Memory to hold the video buffer and the LLM context simultaneously"* or *"We ran inference locally to ensure privacy/latency."*

### 3. Value & Impact (20 pts)
*"Is the solution actually useful?"*

- **Insight Quality (10 pts)**: Is the insight non-obvious and valuable? Example: *"Traffic jams happen at 5 PM"* is obvious. *"Rain causes specific stalls on this specific ramp"* is valuable.
- **Usability (10 pts)**: Could a real City Planner, or Factory Foreman actually use this tool to make a decision tomorrow?

### 4. The "Frontier" Factor (20 pts)
*"Did they push the boundaries?"*

- **Creativity (10 pts)**: Did they combine data or models in a novel way? Example: *"Using vision models to read traffic maps."*
- **Performance (10 pts)**: Did they optimize the system for speed or scale? Example: *"We optimized the simulation to run at 50x real-time speed."*

## Bounties

| Bounty | Prize | Status |
|---|---|---|
| **Most Impactful Use of OpenClaw** | RTX 5090 | **Not pursuing** — constrains build to OpenClaw Skills Hub model, doesn't fit cultural memory framing. Opportunity cost too high. |
| **Most Likely to Be a Unicorn** | Dinner with Antler team + **automatic acceptance to Founder in Residence program** | **Active priority.** PRODUCT_WEDGES.md was written for this. Marvens is the inside Antler ally. The receipts framing + 5 buyer segments is the Antler conversation. |
| **Least Likely to Get Hacked** | $500 cash + $500 Pensar credits | **Opportunistic** — run Pensar on the orchestrator pre-submission, fix what it surfaces. ~30 min if it works, free shot. Decide go/no-go at standup. |

## Rules of note

- **Calling GPT-4 / cloud LLM API = 0 pts on The Stack score** (rubric verbatim). Must use a major NVIDIA library/tool by name.
- Open source dependencies must be **≥2 weeks old** as of Apr 10 (orientation rule). Cutoff: Mar 27 2026. NVIDIA / Nemotron stack exempt.
- One submission per team. 3-5 min demo video (unlisted YouTube/Vimeo) required per Submission Checklist (sub-page TBP).

## How Sixth Borough scores against this rubric

See `ARCHITECTURE.md` "Why this architecture wins points" section for the full mapping. Estimated total: **84-96 / 100** depending on demo execution. Strongest beats: NVIDIA Spark Story (15/15 if we land the 128 GB unified memory + unplug-cable script), Insight Quality (Cross-Bronx 60K Caro receipts), Creativity (six-dataset fusion + PS2 constraint language on Blackwell silicon).

**The single rubric-critical fix made Apr 11 ~15:30 ET**: every doc now consistently names the model as **"NVIDIA Nemotron-3 Nano 30B (A3B variant) from the NVIDIA Nemotron model family"** instead of bare "Nemotron." Nemotron IS a NeMo Model — but only if the team names it as such. See `docs/DECISIONS.md` 2026-04-11 ~15:30 ET entry.
