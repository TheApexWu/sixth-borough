# Build Decisions Log

Append-only log of build decisions made during the hackathon. When you make a non-obvious choice, write it here. Format:

```
## YYYY-MM-DD HH:MM — short title
**Decision:** what we chose
**Alternatives considered:** what we didn't choose
**Why:** the reason
**Owner:** who made the call
**Reversible by:** when this decision can still be undone
```

---

## 2026-04-10 evening — Track selection

**Decision:** Cultural Impact (one of three tracks).
**Alternatives considered:** Human Impact (too crowded), Environmental Impact (no native expertise on team).
**Why:** Sixth Borough's neighborhood-history thesis maps cleanly onto "preserve the history of unique neighborhoods." James's 8-era guided tour branch is already a working artifact in this space. Carson's Rust/wgpu renderer + Alex's narration loop complete the system.
**Owner:** Team consensus.
**Reversible by:** Friday night before submission form is touched. After Sat morning, we are committed.

---

## 2026-04-10 evening — Hardware framing

**Decision:** Treat the Acer Veriton GN100 as a single DGX Spark / GB10 box. Drop the earlier "GB10 oracle + Acer viewer" two-machine framing entirely.
**Alternatives considered:** Pretending we have two boxes (incoherent — the GN100 IS a DGX Spark, same chip).
**Why:** Research on Apr 9 confirmed the GN100 is the same GB10 Grace Blackwell silicon as the official DGX Spark, 128 GB unified memory, $2,999 retail. There is one machine. The pitch is "everything on one box, local-only" — that's stronger than the two-machine story anyway.
**Owner:** Alex.
**Reversible by:** Not reversible — the hardware is the hardware.

---

## 2026-04-10 evening — Narration model

**Decision:** Nemotron-3-Nano-30B-A3B (Q8 GGUF) via llama.cpp on the GN100, OpenAI-compatible API on port 30000.
**Alternatives considered:**
- Nemotron-Mini-4B-Instruct (smaller, faster, but less impressive on stage)
- Cloud APIs (zeros us on NVIDIA Stack score)
- NeMo Framework directly (now focused on speech, not the right tool)
- vLLM / TensorRT-LLM (more setup overhead than we have time for)
**Why:** This is the NVIDIA-recommended path per their own DGX Spark playbook. Uses an NVIDIA model (Nemotron) on NVIDIA hardware (GB10) via NVIDIA's documented setup. Earns points on both axes of the NVIDIA Ecosystem score. Fallback to Q4_K_M quantization if Q8 is too slow or won't fit.
**Owner:** Alex.
**Reversible by:** Sat noon. After that we're committed and the demo video has to use whichever model is running.

---

## 2026-04-10 evening — Renderer primary path

**Decision:** Carson's Rust + wgpu pipeline as primary. James's WebGL `feature/sketch-overlay` branch as fallback path, with the explicit decision point at Sat 4 PM Progress Checkin.
**Alternatives considered:**
- WebGL primary (proven to work, but doesn't tell the "native Blackwell" story as cleanly)
- Both at once (no time, would split focus)
**Why:** Native code on Blackwell silicon is a stronger Frontier Creativity story than "Three.js in a browser." But James's branch is real, working, and has the 8-era cutscene engine, so it's a credible safety net.
**Owner:** Alex + Carson + James.
**Reversible by:** Sat 4 PM hard. If Carson's renderer isn't stable by then, we pivot to WebGL and don't look back.

---

## 2026-04-10 evening — Product synthesis & 4 pillars locked

**Decision:** Sixth Borough is built around 4 core identity pillars: (1) Time Machine, (2) PS2 Memory Aesthetic, (3) Cultural Intelligence, (4) Niche Discovery. Chronology is the navigation primitive, niche filtering is the anti-overload mechanism, PS2 aesthetic is the substrate experience, cultural intelligence is the depth layer that makes the time machine not-empty.
**Alternatives considered:** treating cultural intelligence + niche discovery as a pivot away from the time machine framing (rejected — the team's mental model is preserved by adding these as additive layers, not replacements).
**Why:** A time machine without curation is just a database with a slider. A time machine with niche-filtered cultural depth is a discovery tool. The 4 pillars are mutually reinforcing — none of them is decorative.
**Owner:** Alex.
**Reversible by:** Not reversible without rewriting the product. These four are the identity. See `KICKOFF.md` for the full pillar definitions.

---

## 2026-04-10 evening — Demo cinematic locked

**Decision:** ONE neighborhood (Bronx), ONE era window (1973–1985), ONE fully-populated niche (hip-hop heads), anchored at 1520 Sedgwick Avenue. ~30 hand-curated events. 4–5 other niches present as placeholder toggles with 1–2 events each.
**Alternatives considered:** showing all 8 eras from James's branch (too diffuse for a 3-min video), demoing multiple neighborhoods (no time), demoing immigration flow as the cinematic centerpiece (rejected — too cliched, judges have seen it).
**Why:** The hip-hop birthplace is unbeatable as a 3-min demo story — specific, NYC-mythic, dated to a single address, narratively cinematic. The architecture is universal; the demo is one slice. The placeholder niches prove the architecture handles other lenses without dragging focus.
**Owner:** Alex.
**Reversible by:** Friday midnight. After Saturday morning, the events seed file is locked.

---

## 2026-04-10 evening — OpenClaw bounty dropped

**Decision:** Not pursuing the Most Impactful Use of OpenClaw bounty (RTX 5090).
**Alternatives considered:** building an OpenClaw "Walking Tour Coordinator" skill as a 2-3 hour Sat afternoon add-on.
**Why:** OpenClaw constrains the build to fit its skill model and pulls energy away from the core product. The cultural intelligence + niche discovery framing doesn't naturally fit a generic agent skill wrapper. The opportunity cost is higher than the prize value.
**Owner:** Alex.
**Reversible by:** Not reversible — committing to this decision frees Sat afternoon for the core loop.

---

## 2026-04-10 evening — Antler Unicorn bounty active priority

**Decision:** Actively pursue the Most Likely to Be a Unicorn bounty. Lean into the niche-discovery + B2B-but-cultural framing for any Antler conversation. Pitch verbatim lives in `pitch/antler-90sec.md`.
**Alternatives considered:** treating Antler bounty as opportunistic.
**Why:** Alex has prior Antler context (Mar 27 meeting with Wouter Hiemstra, Antler app submitted Mar 31). This isn't a cold pitch — it's a progress update on what he's been building since they last talked. Antler dinner + auto-acceptance to Founder in Residence is a real ROI for Alex's job/funding trajectory regardless of whether Sixth Borough wins the track.
**Owner:** Alex.
**Reversible by:** N/A — this is a posture, not a build constraint.

---

## 2026-04-10 evening — Dependency age rule passed

**Decision:** All planned dependencies are ≥2 weeks old as of Apr 10 2026. Audit complete.
**Alternatives considered:** swapping in newer cutting-edge libraries (rejected — would violate orientation rule).
**Why:** Per the orientation announcement at the kickoff, every open-source dependency must be at least 2 weeks old. NVIDIA / Nemotron stack is exempt and clear regardless. llama.cpp, Rust+wgpu, Three.js, Ollama, Nemotron-3-Nano GGUFs (4 months old), Live VLM WebUI (5 months old), etc. all pass. **Mid-build rule:** any new dependency added during the hackathon must also pass the ≥2-week check or it doesn't ship.
**Owner:** Alex (audit), Carson + James (compliance).
**Reversible by:** N/A — rule is external.

---

## 2026-04-10 evening — Carson + James mental model preservation

**Decision:** When syncing with Carson and James at the venue, frame the cultural intelligence + niche discovery layers as ADDITIVE to the existing time-machine PS2 framing, not as a pivot. Their work (Carson's renderer, James's 8-era cutscene engine) is unchanged. The new pieces are a data layer + a niche filter UI on top.
**Alternatives considered:** presenting it as a product reframe (rejected — risks confusing the team and breaking their build context).
**Why:** Carson and James have been operating under "time machine PS2 aesthetic" all week. The synthesis I'm proposing fits inside that framing — chronology is still the navigation, PS2 is still the substrate, the new dimensions (cultural intelligence layer + niche filter) live ON TOP of what they're already building. Talking to them as if the project changed will cost momentum.
**Owner:** Alex (the framing).
**Reversible by:** N/A — this is a communication discipline, not a build constraint.

---

## 2026-04-10 evening — Renderer engine: Bevy 0.16 (Rust + wgpu)

**Decision:** The Rust renderer is built on **Bevy 0.16**, not raw wgpu. Static point clouds ingest through the `bevy_pointcloud` plugin (Potree-based, stable Rust, PLY format). Animated point clouds use **OpenVAT** (Blender addon) → glb with embedded vertex animation texture, sampled by a custom WGSL vertex shader on the Bevy side.
**Alternatives considered:**
- Raw wgpu with hand-rolled scene graph (more control, but rebuilding what Bevy gives free; no time)
- Bevy 0.18 (latest, January 2026 release, but plugin ecosystem hasn't caught up — `bevy_pointcloud` plugin compat is the binding constraint)
- `bevy_gaussian_splatting` plugin (more "neural rendering" aesthetic, but requires nightly Rust for default features and adds risk)
- glTF morph targets only for animated point clouds (works but caps at low vertex counts; OpenVAT scales further)
**Why:** Bevy gives us a built-in animation graph (since 0.14, animation masks + additive blending added in 0.15), the mature first-party glTF loader, an ECS for the niche-filtered event entities, and a plugin ecosystem that includes static point cloud rendering out of the box. The key insight is that **Marvens authors everything in Blender** — city geometry, ghosts, animated point clouds — and Carson loads it via standard formats. Marvens never touches Rust; Carson never touches Blender. The contract between them is the file format spec in `pointcloud-pipeline/README.md`.

OpenVAT specifically is the right choice for the animated point cloud ghost layer because it's Blender-native, captures any vertex-level animation including Marvens's Geometry Nodes / Simulations work, encodes the result as a GPU texture that any engine with a basic vertex shader can sample, and is the same family of technique Marvens has shipped to 2M+ concert attendees on the ODESZA tour. The ~50–100 lines of WGSL Carson writes to sample the VAT is the only net-new shader work.

Bevy 0.16 (mid-2025) is pinned over 0.18 (January 2026) because the third-party plugin ecosystem — especially `bevy_pointcloud` — is most reliably aligned with 0.16. 0.18 is too new for safe hackathon plugin compat.
**Owner:** Carson + Alex + Marvens.
**Reversible by:** Friday midnight (engine pin), Sat morning (bump to 0.17 if Carson confirms plugin compat), not reversible after Sat morning.

---

## 2026-04-10 evening — Carson + Marvens paired ownership of asset format contract

**Decision:** Carson (`renderer-rust` branch) and Marvens (`pointcloud-pipeline` branch) **pair Friday night** to lock the file format contract that lives in `pointcloud-pipeline/README.md`. Once locked, they iterate independently for the rest of the weekend — Marvens drops new ghosts into shared storage and bumps `assets/pointclouds/MANIFEST.json`, Carson's renderer ingests on next launch.
**Alternatives considered:** treating Marvens as a passive asset producer who hands files over a wall (rejected — Marvens has shipped this exact technique at scale and his input on the format spec is high-value).
**Why:** Carson explicitly said he wants to work with Marvens on integration, not after it. Pairing on the format spec Friday night removes the highest-risk part of the collaboration (ambiguity about what the file looks like) before either of them writes any code that depends on the assumption.
**Owner:** Carson + Marvens (the contract), Alex (the meta-decision).
**Reversible by:** N/A — this is a coordination model, not a build constraint.

---

## (add new decisions below this line as they happen)
