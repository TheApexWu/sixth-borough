# Pitch Framings — Discussion Doc for Saturday Morning

**For:** Alex + Carson + James + Marvens
**When:** Saturday Apr 11 morning, before we lock the demo video script
**Goal:** Pick ONE framing for the 30-second elevator pitch + the demo video. Reinforce shared identity.

The Notion judging guide says the 30-second pitch should: hook → what it is → why it matters → how it's special → land. Five different framings below, each ~30 seconds. They are NOT mutually exclusive — the right answer is probably to pick one as the spine and steal a sentence from another for a closer.

**The fixed words that MUST appear in the recorded video** (per `docs/STACK.md` — these earn the 15-point Spark Story score; do not skip):
- "DGX Spark"
- "GB10 Grace Blackwell Superchip"
- "128 gigabytes of unified memory"
- "Nemotron"
- "running locally"
- "no internet connection at runtime"
- The unplug-cable line: *"Everything you're about to see runs on the box, with the cable on the floor, because computational ghosts need local hardware."*

---

## Framing A — "The Computational Ghost" (current thesis, sharpest)

> Every cool AI demo runs in the cloud. We pulled the cable. **Sixth Borough is a NYC time machine where you scrub a year slider through decades of a single neighborhood, watch the place re-render in PS2-era visuals, and listen to a local language model tell you what mattered there — entirely on this desktop, with no internet.** It's August 11, 1973 at 1520 Sedgwick Avenue and Kool Herc is about to invent hip-hop. The model that narrates that runs on the Acer GN100 in our hand. **Computational ghosts need local hardware.**

**Strengths:** unplug-cable demo IS the punchline; specific cinematic moment grounds it; sponsor scoring lines bake in; aligns with `docs/STACK.md` and the team-context doc verbatim.

**Risks:** if the unplug moment doesn't hit cleanly, the whole pitch deflates. Demands a reliable physical demo.

**Best for:** the demo video close. Strong as a default if we're picking the most consensus-friendly framing.

---

## Framing B — "Memory, Not Photorealism" (the aesthetic angle)

> **Photorealism is wrong for memory.** Nobody remembers a place the way Google sees it. We built **Sixth Borough — a NYC time machine that looks like the way you remember a neighborhood, not the way a satellite does.** PS2-era visuals, a local language model, a year slider, niche filters for hip-hop heads or queer history or demolished theaters. Stand at 1520 Sedgwick in 1973 and a model running on this desktop tells you what's about to happen. **The first time machine that looks like memory.**

**Strengths:** the "PS2 = memory" insight is non-obvious and immediately quotable. Plays well with judges who reward creative framing. Wins the Frontier Creativity score (10 pts) on its own.

**Risks:** doesn't lead with the local-LLM angle; you'd need to tuck NVIDIA stack words into the second sentence. Some judges may bounce off "aesthetic theory" as fluffy.

**Best for:** the part of the video where Carson talks about why PS2 shaders on Blackwell silicon is a deliberate choice, not a gimmick.

---

## Framing C — "Curator's Tool, Not Museum App" (the value angle)

> Every NYC neighborhood has a story spread across a dozen archives that don't talk to each other. **Sixth Borough is a curator's time machine — a guided computational walk through one neighborhood, in one era, that any teacher can lead a class through.** PS2-era visuals because memory isn't photorealistic. A local language model on a desktop because cultural context shouldn't depend on a billing account. We start with the Bronx, 1973–1985, the birth of hip-hop. **Plug it in anywhere. The internet is optional.**

**Strengths:** strongest on the Usability score (10 pts) — judges literally ask "could a real curator use this tomorrow?" Maps cleanly to a real go-to-market story (sell to museums, schools, cultural orgs).

**Risks:** the "curator/teacher" framing is a bit dry; loses some cinematic punch. Might undersell the engineering complexity.

**Best for:** the "so what?" close that earns the Value & Impact score. Probably the right answer to the judge question "what's the path to a real product?"

---

## Framing D — "The 1520 Sedgwick Cold Open" (cinematic / story-first)

> **August 11, 1973. Cindy Campbell's birthday party in the rec room of 1520 Sedgwick Avenue, the Bronx.** Her brother Clive, who calls himself DJ Kool Herc, isolates the percussion break of two records using two turntables and accidentally invents hip-hop. **Sixth Borough is the time machine that lets you stand in that rec room — and hear an AI running on the desktop in front of you tell you what's happening.** PS2 visuals because memory isn't HD. A 30-billion-parameter local model because cultural ghosts don't belong in someone else's data center. One neighborhood, one cinematic era, one box on the floor.

**Strengths:** strongest emotional opener; specific date + place + character + stake = a story, not a feature list. Judges remember stories. The hip-hop birthplace is unbeatable as a hook because it's specific, NYC-mythic, and culturally enormous.

**Risks:** longer; runs ~35 sec; have to trim to fit 30. Front-loads narrative at the expense of explaining what the product IS — judges might wait too long for the "so what."

**Best for:** the demo video cold open. Carries the most emotional weight.

---

## Framing E — "The Unified Memory Flex" (the engineering brag)

> We're running a 30-billion-parameter Nemotron model, a real-time renderer, and a vision pipeline simultaneously on a $2,999 desktop because the GB10's 128 gigabytes of unified memory means there's no copy between graphics and inference. **Sixth Borough is what you build when you take that constraint seriously: a NYC time machine with PS2-era visuals, a year slider through decades, niche filters, and a local AI narrator — all running on the box with the cable on the floor.** Computational ghosts need local hardware. **And we just built one.**

**Strengths:** maxes out the NVIDIA Stack score (15 pts) — judges literally said "tell us why DGX Spark specifically." This pitch ANSWERS that question word-for-word. Highest scoring ceiling on the technical axis.

**Risks:** front-loads the engineering brag, which can feel cold to non-engineer judges. Doesn't open with a story or an image — opens with a number.

**Best for:** the technical narration middle of the video where Alex explains the system architecture.

---

## Recommended hybrid for the demo video

**The hybrid that uses each framing for its strength:**

1. **Cold open (10 sec) — Framing D**: the 1520 Sedgwick story. Specific date, place, person, stake. No product mention yet.
2. **What it is (10 sec) — Framing A**: "Sixth Borough is a NYC time machine where you scrub a year slider, the place re-renders in PS2 visuals, and a local model narrates." Pull in the niche filter mention.
3. **The technical brag (5 sec) — Framing E one-liner**: "30-billion-parameter Nemotron, real-time Bevy renderer, all on a $2,999 desktop because of 128GB unified memory." Hits the Stack score word-for-word.
4. **The unplug moment (3 sec) — Framing A close**: walk to the box, pull the cable, walk back. "Everything you're about to see runs on the box with the cable on the floor."
5. **The land (2 sec) — Framing A or C**: "Computational ghosts need local hardware." OR "The first time machine that looks like memory." OR "Plug it in anywhere — the internet is optional."

Total: ~30 sec. Hits hook + product + stack + spark story + close. Earns points on all four scoring categories without feeling like a checklist.

---

## Discussion questions for Saturday morning standup

1. **Which framing resonates most as the SPINE?** A is the team-context default. D is the most cinematic. C is the most product-strategic. Pick one to anchor.
2. **Who delivers which 10-sec block?** Cold open is a single voice (Alex or Carson). Technical brag is the engineer voice. Close is the team voice (everyone on screen). Decide who.
3. **Are we comfortable with the unplug-cable moment?** It's worth 15 points but only if it works. If anyone has a concern about reliability, surface it now.
4. **Do we add a "James pillar" — the 8-era guided tour as the navigation primitive?** None of the framings above explicitly call it out. Might be worth mentioning that the year slider IS the navigation, not a feature.
5. **What's the ONE artifact we point to as the "non-obvious cultural insight"?** The judging rubric weights "Insight Quality" (10 pts) on whether we surface something specific and valuable, not generic. The 1520 Sedgwick rec room IS our answer if we pick D. Confirm.

---

## Operational notes

- This doc is **discussion fodder, not a final script**. We pick + edit + lock during the morning standup.
- Once the framing is locked, the narrator script for the demo video lives at `docs/DEMO_VIDEO_SCRIPT.md` (TBD).
- Slide deck owner: James (must lock Sat night per CONTRIBUTING.md — Sun afternoon conflict).
- The fixed-words list at the top of this doc is non-negotiable. Whichever framing wins, those phrases must appear verbatim.

*Drafted Apr 11 ~04:30 ET overnight. Discuss + decide Apr 11 morning.*
