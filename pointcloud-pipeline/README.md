# Point Cloud Pipeline — Blender to Bevy Contract

This is the file format contract between Marvens (Blender authoring) and Carson (Bevy renderer ingest). Lock it before either side writes ingest code. After it's locked, both sides iterate independently — Marvens drops new ghosts into shared storage and bumps the manifest, Carson's renderer ingests on next launch.

---

## One format: GLB

Everything is **glTF Binary (.glb)**. Bevy 0.18 loads GLB natively — zero plugins, zero custom parsers. Blender's glTF export is its most battle-tested path. One format means one export workflow for Marvens and one ingest path for Carson.

### Format A — Static ghost (GLB)

For ghosts that don't move: building exteriors, frozen interior geometry, sculptural artifacts.

- **Container**: glb (binary glTF 2.0)
- **Blender export**: File → Export → glTF 2.0 (.glb), default settings. Use Principled BSDF materials only.
- **Point cloud look**: Use Geometry Nodes in Blender to scatter small icospheres (or cubes) on surfaces. Export the result as a standard mesh. The renderer sees a normal mesh — no special point cloud handling needed.
- **Alternatively**: Model as a standard mesh if the point cloud aesthetic isn't needed for that ghost. The renderer doesn't care — it loads any valid GLB.
- **Coordinate system**: Blender default export orientation (-Z forward, +Y up). Bevy's glTF loader handles the conversion automatically.
- **Poly budget**: Target 50K–200K triangles per ghost. Test against the renderer to find the sweet spot.
- **Bevy ingest**: `asset_server.load(GltfAssetLabel::Scene(0).from_asset("pointclouds/my-ghost.glb"))`
- **File extension**: `.glb`

### Format B — Animated ghost (GLB + OpenVAT) — STRETCH GOAL

For the ODESZA-style mechanic: drifting dust, pulsing shapes, cycling poses, animated breakdancer figures.

- **Container**: glb (binary glTF 2.0) + a separate VAT texture
- **Authoring tool**: [OpenVAT](https://github.com/sharpen3d/openvat) Blender addon
- **What OpenVAT does**: captures vertex animation from Blender's evaluated dependency graph (Geometry Nodes, modifiers, shapekeys, simulations) and bakes it into a Vertex Animation Texture (VAT) where each pixel encodes a vertex's position at a specific frame.
- **Output**: a base mesh GLB + a VAT texture (PNG16 recommended — 16-bit RGBA, good precision, wide compatibility)
- **Bevy ingest**: Carson writes a custom WGSL vertex shader (~50–100 lines) that samples the VAT per frame. Written once, works for all animated ghosts.
- **Loop length**: Keep loops short (1–3 seconds) for the demo. The renderer loops indefinitely; longer loops cost more texture memory.
- **Vertex count target**: 10K–100K vertices per animated ghost. Lower than static because VAT texture size scales with vertex count × frame count.
- **Transform note**: OpenVAT always encodes XYZ → RGB with Blender's default export orientation (-Z forward, +Y up). Carson handles the axis remap in the shader.
- **File extension**: `.glb` for the mesh, `.png` for the VAT texture (co-located, same slug)

**This is a stretch goal.** Only attempt after Format A ghosts are loading and the core demo flow works.

---

## File naming convention

```
<slug>.glb                     static ghost mesh
<slug>-anim.glb                animated ghost mesh (OpenVAT)
<slug>-anim-vat.png            animated ghost VAT texture (OpenVAT)
<slug>.preview.png             preview thumbnail (committed to git)
```

**Slug rules:**
- Lowercase, hyphenated
- Format: `<venue>-<year>`
- Be specific enough that future-Marvens can read the filename and know exactly what it is

**Examples:**
```
1520-sedgwick-rec-room-1973.glb
1520-sedgwick-rec-room-1973.preview.png

disco-fever-interior-1980.glb
disco-fever-interior-1980.preview.png

1520-sedgwick-rec-room-1973-anim.glb           (stretch)
1520-sedgwick-rec-room-1973-anim-vat.png       (stretch)
```

---

## Where files live

```
sixth-borough/
└── assets/
    └── pointclouds/
        ├── MANIFEST.json                              <-- committed (small)
        ├── 1520-sedgwick-rec-room-1973.preview.png    <-- committed
        ├── 1520-sedgwick-rec-room-1973.glb            <-- gitignored, sync via shared storage
        └── 1520-sedgwick-rec-room-1973-anim.glb       <-- gitignored (stretch)
```

**The .glb / .png (VAT) files are gitignored** (see root `.gitignore`). They're large, change often, and version control adds no value over a shared Drive/Dropbox. Marvens uploads to shared storage and bumps the manifest. The renderer reads the manifest, falls back gracefully if a referenced file is missing locally.

**The MANIFEST.json + preview PNGs ARE committed** so the team can see what exists at any given commit, and so the renderer build doesn't fail in CI or on a fresh clone.

---

## MANIFEST.json schema

The renderer reads `assets/pointclouds/MANIFEST.json` at startup. Each entry describes one ghost.

```json
{
  "version": 2,
  "ghosts": [
    {
      "slug": "1520-sedgwick-rec-room-1973",
      "title": "1520 Sedgwick Avenue Rec Room",
      "coordinate": [40.8398, -73.9210],
      "era_year": 1973,
      "era_window": [1973, 1979],
      "niche_tags": ["hip-hop"],
      "format": "glb",
      "file": "1520-sedgwick-rec-room-1973.glb",
      "preview": "1520-sedgwick-rec-room-1973.preview.png",
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
- `format` — `"glb"` for static, `"glb-vat"` for animated (stretch)
- `file` — relative to `assets/pointclouds/`
- `preview` — optional, shown if the actual file isn't synced locally
- `animated` — `true` for OpenVAT, `false` for static
- `source_attribution` — required for any photo-derived asset
- `notes` — optional, free text for the curator

---

## Marvens's export checklist (static ghost)

1. Model/sculpt the ghost in Blender
2. For point-cloud aesthetic: add a Geometry Nodes modifier that scatters small icospheres on the surface. Adjust density to taste.
3. Apply all modifiers
4. File → Export → glTF 2.0 (.glb)
   - Format: glTF Binary (.glb)
   - Include: Selected Objects (or the ghost collection)
   - Transform: defaults (Blender handles Y-up conversion)
   - Mesh: Apply Modifiers = ON
   - Material: keep it simple — Principled BSDF, solid colors or vertex colors
5. Drop the `.glb` in shared storage
6. Add an entry to `MANIFEST.json`, push the manifest

**That's it.** No special plugins, no special settings, no second format to remember.

---

## Authoring stack reference (for Marvens)

| Tool | Purpose | Where to get it |
|---|---|---|
| Blender | Authoring environment | blender.org (you already have it) |
| OpenVAT addon | Animated ghost encoding (stretch) | https://github.com/sharpen3d/openvat |
| AliceVision Meshroom | Photogrammetry from photos to mesh | https://alicevision.org/ |
| COLMAP | Alternative photogrammetry pipeline | https://colmap.github.io/ |
| Blender Photogrammetry Importer | Loads Meshroom/COLMAP output into Blender | https://github.com/SBCV/Blender-Addon-Photogrammetry-Importer |
| Joe Conzo Jr. archive (6,000+ images) | Source photographs for Bronx hip-hop ghosts | https://digital.library.cornell.edu/collections/conzo |
| 1940s.nyc | NYC Municipal Archives tax photos | https://1940s.nyc/ |

---

## Saturday sync with Marvens (~15 minutes)

1. **Sample round trip.** Marvens exports any placeholder GLB (a cube, a noise scatter — anything). Drops it in `assets/pointclouds/`, adds a manifest entry. Carson loads it in Bevy. If it renders, the pipeline works.
2. **Point cloud aesthetic.** Decide: scattered icospheres (geo nodes) vs. solid low-poly mesh vs. both. Quick visual test.
3. **Poly budget.** Carson eyeballs frame rate with the sample asset, sets a ceiling. Marvens stays under it.
4. **Shared storage.** Pick one: Google Drive, Dropbox, or USB stick at the venue. Share the link.
5. **Ghost count.** Realistic ceiling for the demo: 3–5 total, with 1520 Sedgwick rec room as the must-ship anchor.

Once the round trip works, both sides iterate independently for the rest of the day.

---

## Decisions locked

- [x] Single format: GLB (Bevy 0.18 native glTF loader, no plugins)
- [x] Coordinate system: Blender default export, Bevy handles conversion
- [x] Animated ghosts (OpenVAT) are a stretch goal, not P0
- [x] Color handling: bake vertex colors or materials in Blender. Renderer can override with per-niche palette at runtime if needed.
- [x] MANIFEST.json version bumped to 2 (format field changed from `"ply"` to `"glb"`)
