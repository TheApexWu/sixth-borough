# Sixth Borough

A time machine for niche subcultures across all five boroughs of New York City. Built for Spark Hack Series NYC, Apr 10–12 2026.

Drop into any neighborhood, scrub a year slider through decades of history, toggle a niche filter (hip-hop heads, queer history, demolished theaters, jazz, salsa, immigration flow), and watch the place re-render in the visual language of its era while a local language model narrates what mattered there. Everything runs on one box with the ethernet cable on the floor.

**Track:** Cultural Impact
**Hardware:** Acer Veriton GN100 (DGX Spark / GB10 Grace Blackwell, 128 GB unified memory, runs entirely offline)
**Renderer:** Bevy 0.16 (Rust + wgpu) with PS2-style post-process and `bevy_pointcloud` for the demolished-building ghost layer
**Narration:** Nemotron-3-Nano-30B-A3B (Q8 GGUF) via llama.cpp on the GB10
**Asset authoring:** Blender (point cloud ghosts use OpenVAT for animated vertex-level animation)

See [`docs/STACK.md`](docs/STACK.md) for the pinned tech stack, [`ARCHITECTURE.md`](ARCHITECTURE.md) for the system diagram, and [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) for the NYC Open Data references.

Quick start and contribution workflow land in the next push.
