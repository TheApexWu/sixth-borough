# Point Cloud Pipeline — Blender to Bevy Contract

This is the file format contract between Marvens (Blender authoring) and Carson (Bevy renderer ingest). Lock it Friday night before either side writes ingest code. After it's locked, both sides iterate independently — Marvens drops new ghosts into shared storage and bumps the manifest, Carson's renderer ingests on next launch.

---

## Two formats, both supported from day one

### Format A — Static point cloud (PLY)

For ghosts that don't move: building exteriors, frozen interior geometry, sculptural artifacts.

- **Container**: PLY (Polygon File Format), binary, **little-endian**
- **Required vertex properties**: `x`, `y`, `z` (float32)
- **Optional vertex properties**: `red`, `green`, `blue` (uint8) — colored points; otherwise the renderer applies a per-niche palette
- **Coordinate system**: meters, Y-up, origin at the geographic anchor (the renderer translates to the BBL footprint at runtime)
- **Vertex count target**: 50K – 500K points per ghost. Lower = better frame budget. Higher = more visible detail. Test against the renderer to find the sweet spot.
- **Bevy ingest path**: `bevy_pointcloud` plugin (Potree-based, stable Rust)
- **File extension**: `.ply`

### Format B — Animated point cloud (glb + OpenVAT)

For Marvens's signature ODESZA-style mechanic: drifting dust, pulsing shapes, cycling poses, animated breakdancer figures, particle systems baked to GPU-side animation.

- **Container**: glb (binary glTF 2.0)
- **Authoring tool**: [OpenVAT](https://github.com/sharpen3d/openvat) Blender addon
- **What OpenVAT does**: captures vertex animation from Blender's evaluated dependency graph (works with Geometry Nodes, modifiers, shapekeys, simulations) and bakes it into a Vertex Animation Texture where each pixel encodes a vertex's position at a specific frame.
- **Output**: a base mesh + a VAT texture (RGBA float32 or RGBA16F, depending on precision needs) embedded in the glb
- **Bevy ingest path**: custom WGSL vertex shader on Carson's side samples the VAT per frame. ~50–100 lines of shader code, written once.
- **Loop length**: keep loops short (1–3 seconds) for the demo. The renderer can loop indefinitely; longer loops cost more texture memory.
- **Vertex count target**: 10K – 100K points per animated ghost. Lower than static because the VAT texture scales with vertex count × frame count.
- **File extension**: `.glb` (with `-anim` suffix in the slug; see naming below)

---

## File naming convention

```
<slug>-<year>.ply              static point cloud
<slug>-<year>-anim.glb         animated point cloud
<slug>-<year>.preview.png      preview thumbnail (committed to git)
```

**Slug rules:**
- Lowercase, hyphenated
- Include the venue and the era anchor year
- Be specific enough that future-Marvens can read the filename and remember exactly what it is

**Examples:**
```
1520-sedgwick-rec-room-1973.ply
1520-sedgwick-rec-room-1973.preview.png
1520-sedgwick-rec-room-1973-anim.glb       (stretch shot)

disco-fever-interior-1980.ply
disco-fever-interior-1980.preview.png

loews-paradise-lobby-1929.ply
loews-paradise-lobby-1929.preview.png
```

---

## Where files live

```
sixth-borough/
└── assets/
    └── pointclouds/
        ├── MANIFEST.json                       <-- committed (small)
        ├── 1520-sedgwick-rec-room-1973.preview.png   <-- committed
        ├── 1520-sedgwick-rec-room-1973.ply           <-- gitignored, sync via shared storage
        └── 1520-sedgwick-rec-room-1973-anim.glb      <-- gitignored
```

**The .ply / .glb / .splat files are gitignored** (see root `.gitignore`). They're large, change often, and version control adds no value over a shared Drive/Dropbox. Marvens uploads to shared storage and bumps the manifest. The renderer reads the manifest, falls back gracefully if a referenced file is missing locally.

**The MANIFEST.json + preview PNGs ARE committed** so the team can see what exists at any given commit, and so the renderer build doesn't fail in CI or on a fresh clone.

---

## MANIFEST.json schema

The renderer reads `assets/pointclouds/MANIFEST.json` at startup. Each entry describes one ghost.

```json
{
  "version": 1,
  "ghosts": [
    {
      "slug": "1520-sedgwick-rec-room-1973",
      "title": "1520 Sedgwick Avenue Rec Room",
      "neighborhood": "Bronx",
      "borough": "Bronx",
      "coordinate": [40.8398, -73.9210],
      "era_year": 1973,
      "era_window": [1973, 1979],
      "niche_tags": ["hip-hop"],
      "format": "ply",
      "file": "1520-sedgwick-rec-room-1973.ply",
      "preview": "1520-sedgwick-rec-room-1973.preview.png",
      "vertex_count": 180000,
      "animated": false,
      "source_attribution": "Photogrammetry from Joe Conzo Jr. archive (Cornell Hip Hop Collection), CC BY-NC where applicable",
      "notes": "Sparse multi-view reconstruction. Sweep is approximate."
    }
  ]
}
```

**Field semantics:**
- `slug` — must match the file name (without extension)
- `title` — human-readable label, shown on the renderer's debug overlay
- `coordinate` — `[lat, lng]` WGS84, where the ghost anchors on the modern street
- `era_year` — the canonical year for the ghost's narrative anchor
- `era_window` — `[start, end]` when the ghost should be visible on the time slider
- `niche_tags` — which niche filter(s) reveal this ghost
- `format` — `"ply"` or `"glb-vat"`
- `file` — relative to `assets/pointclouds/`
- `preview` — optional, shown if the actual file isn't synced locally
- `vertex_count` — informational, helps the renderer team triage perf
- `animated` — `true` for OpenVAT glb, `false` for static PLY
- `source_attribution` — required for any photo-derived asset (especially Joe Conzo / Cornell archive material)
- `notes` — optional, free text for the curator

---

## Authoring stack reference (for Marvens)

| Tool | Purpose | Where to get it |
|---|---|---|
| Blender | Authoring environment | blender.org (you already have it) |
| OpenVAT addon | Animated point cloud encoding | https://github.com/sharpen3d/openvat |
| AliceVision Meshroom | Photogrammetry from photos to point cloud | https://alicevision.org/ |
| COLMAP | Alternative photogrammetry pipeline | https://colmap.github.io/ |
| Blender Photogrammetry Importer | Loads Meshroom/COLMAP output into Blender | https://github.com/SBCV/Blender-Addon-Photogrammetry-Importer |
| Joe Conzo Jr. archive (free, geocoded, 6,000+ images) | Source photographs for Bronx hip-hop ghosts | https://digital.library.cornell.edu/collections/conzo |
| 1940s.nyc | NYC Municipal Archives tax photos (every NYC building ca. 1940) | https://1940s.nyc/ |

---

## The Friday night sync (~30 minutes, in person)

Both Carson and Marvens commit to nailing this together before either writes any code that depends on the contract:

1. **Vertex count target.** Carson tests `bevy_pointcloud` with a placeholder PLY, finds the frame budget ceiling. Pick a number both sides can hit.
2. **MANIFEST.json schema.** Walk through the example above. Add or remove fields based on what each side actually needs.
3. **Coordinate convention.** Confirm meters + Y-up, confirm the anchor-translation formula at the renderer side (BBL → world space).
4. **Sample asset round trip.** Marvens exports a placeholder PLY (anything — a cube, a noise field), drops it in `assets/pointclouds/`, bumps the manifest, Carson loads it. **This validates the entire pipeline before either side commits to a real shot.**
5. **Naming convention** examples written down in this README so neither side has to remember them later.

Once the contract is locked, both sides iterate independently for the rest of the weekend.

---

## Open questions to resolve at the Friday night sync

- [ ] Vertex count ceiling per ghost (Carson tests, then we pin a number)
- [ ] OpenVAT VAT texture format — RGBA float32 (precise, large) vs RGBA16F (smaller, fine for most cases)
- [ ] Renderer color handling: do we use baked vertex colors from the PLY, or apply a per-niche palette at render time? Probably the latter, but worth confirming.
- [ ] How many ghosts are realistic for the demo (recommended ceiling: 5–7 total, with the 1520 Sedgwick rec room as the must-ship anchor)
- [ ] Shared storage path (Google Drive, Dropbox, or a self-hosted bucket) — pick one Friday night, share the link in team chat
