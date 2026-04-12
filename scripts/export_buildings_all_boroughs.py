"""
Export ALL FIVE NYC boroughs to compact JSONs for the deck.gl frontend.

DRAFT — Apr 11 ~23:30 ET, Session 43. Extends James's `export_buildings.py`
(Manhattan-only) to handle the full citywide Building Footprints dataset.

Background:
- James's original `export_buildings.py` is hardcoded to read
  `data/manhattan_buildings.geojson` and write `data/manhattan_compact.json`.
- That file (manhattan_buildings.geojson, 42 MB) was a Manhattan-only filtered
  download of NYC Open Data Building Footprints (`5zhs-2jue`), pulled by Alex
  Apr 7 2026.
- The kickoff audit doc (`~/Desktop/sixth-borough-kickoff/docs/NYC_OPEN_DATA.md`)
  flagged that the dataset is actually CITYWIDE — 1,053,713 buildings across
  all 5 boroughs — not Manhattan-only. Alex didn't realize at the time.
- This script reads the full citywide GeoJSON in one pass and writes 5
  borough-keyed compact JSONs in James's `{p, h, y, b}` schema.

USAGE:
    1. Download the citywide Building Footprints GeoJSON (~1 GB):
         curl -L -o data/nyc_buildings_citywide.geojson \
           "https://data.cityofnewyork.us/api/geospatial/5zhs-2jue?method=export&format=GeoJSON"
       (or download from the dataset page in a browser if curl is slow)

    2. Run the splitter:
         python scripts/export_buildings_all_boroughs.py

    3. Output: 5 files in data/, one per borough, plus a tiny manifest
         data/manhattan_compact.json
         data/bronx_compact.json
         data/brooklyn_compact.json
         data/queens_compact.json
         data/staten_compact.json
         data/borough_manifest.json    (per-borough counts + filesizes)

OPTIONAL DOWNSAMPLING (for browser delivery):
    --min-height N    Drop buildings with height_roof < N feet (default: 0)
    --boroughs LIST   Only process these boroughs (default: all 5)

EXAMPLES:
    # Full city, no filtering (largest output, ~1.3 GB total)
    python scripts/export_buildings_all_boroughs.py

    # Only Bronx (for the Sun demo expansion past Manhattan)
    python scripts/export_buildings_all_boroughs.py --boroughs bronx

    # All boroughs, drop walk-ups and garages (~50% reduction)
    python scripts/export_buildings_all_boroughs.py --min-height 33

    # Just Manhattan and Bronx, full density (the realistic Sun deliverable)
    python scripts/export_buildings_all_boroughs.py --boroughs manhattan,bronx
"""

import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_INPUT = DATA_DIR / "nyc_buildings_citywide.geojson"

# Building Footprints `5zhs-2jue` borough codes per NYC OTI metadata.
# The field is variously named "boro_code", "borocode", or "boro" depending
# on which export endpoint NYC Open Data hands you. We probe all three.
BOROUGH_BY_CODE = {
    "1": "manhattan",
    "2": "bronx",
    "3": "brooklyn",
    "4": "queens",
    "5": "staten",
}

# Inverse map for the --boroughs CLI filter.
CODE_BY_NAME = {v: k for k, v in BOROUGH_BY_CODE.items()}


def get_borough_code(props: dict) -> str | None:
    """Pull the borough code from a feature's properties, tolerating
    field-name drift across NYC Open Data export endpoints. Falls back
    to deriving the borough from base_bbl's first digit if no explicit
    field is present (the citywide 5zhs-2jue export drops boro_code in
    favor of base_bbl)."""
    for key in ("boro_code", "borocode", "boro", "BORO_CODE", "BoroCode"):
        v = props.get(key)
        if v is not None:
            v = str(v).strip()
            if v in BOROUGH_BY_CODE:
                return v
    # Fallback: BBL = Borough(1) + Block(5) + Lot(4). First char is borough 1-5.
    bbl = props.get("base_bbl") or props.get("mappluto_bbl") or props.get("bbl")
    if bbl:
        first = str(bbl).strip()[:1]
        if first in BOROUGH_BY_CODE:
            return first
    return None


def extract_compact_record(feat: dict, min_height_ft: float) -> dict | None:
    """Convert a single Building Footprints feature into James's compact
    `{p, h, y, b}` shape. Returns None if the record should be dropped
    (zero height, missing geometry, or below the min-height filter)."""
    props = feat.get("properties", {})
    geom = feat.get("geometry") or {}

    height_ft = props.get("height_roof")
    try:
        height_ft = float(height_ft) if height_ft is not None else 0.0
    except (ValueError, TypeError):
        height_ft = 0.0

    if height_ft < min_height_ft:
        return None

    year = props.get("construction_year") or props.get("cnstrct_yr")
    try:
        year = int(year) if year else 0
    except (ValueError, TypeError):
        year = 0

    if geom.get("type") == "MultiPolygon":
        coords = geom["coordinates"][0][0]
    elif geom.get("type") == "Polygon":
        coords = geom["coordinates"][0]
    else:
        return None

    if not coords:
        return None

    # Trim coordinate precision to 6 decimals (~0.1m) — same as James's
    # original Manhattan compactor for byte-for-byte schema compatibility.
    coords = [[round(c[0], 6), round(c[1], 6)] for c in coords]

    return {
        "p": coords,
        "h": round(height_ft * 0.3048, 1),  # feet → meters
        "y": year,
        "b": str(props.get("bin", "")),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Split NYC citywide Building Footprints into 5 borough compact JSONs"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to citywide GeoJSON (default: {DEFAULT_INPUT.relative_to(DATA_DIR.parent)})",
    )
    parser.add_argument(
        "--boroughs",
        type=str,
        default="manhattan,bronx,brooklyn,queens,staten",
        help="Comma-separated borough names to export (default: all 5)",
    )
    parser.add_argument(
        "--min-height",
        type=float,
        default=0.0,
        help="Drop buildings with height_roof < N feet (default: 0, no filter)",
    )
    args = parser.parse_args()

    wanted_boroughs = {b.strip().lower() for b in args.boroughs.split(",") if b.strip()}
    unknown = wanted_boroughs - set(CODE_BY_NAME)
    if unknown:
        print(f"unknown boroughs: {sorted(unknown)}", file=sys.stderr)
        print(f"valid: {sorted(CODE_BY_NAME)}", file=sys.stderr)
        sys.exit(1)

    if not args.input.exists():
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        print(f"\nDownload it first with:", file=sys.stderr)
        print(
            f'  curl -L -o {args.input} \\\n'
            f'    "https://data.cityofnewyork.us/api/geospatial/5zhs-2jue?method=export&format=GeoJSON"',
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Loading {args.input} ({args.input.stat().st_size / 1024 / 1024:.0f} MB)...")
    with open(args.input) as f:
        data = json.load(f)

    print(f"  {len(data['features'])} features in input")
    print(f"Splitting by borough into: {sorted(wanted_boroughs)}")
    if args.min_height > 0:
        print(f"  filtering height_roof >= {args.min_height} ft")

    by_borough: dict[str, list[dict]] = {b: [] for b in wanted_boroughs}
    skipped_no_borough = 0
    skipped_no_geom = 0
    skipped_below_min = 0

    for feat in data["features"]:
        code = get_borough_code(feat.get("properties", {}))
        if code is None:
            skipped_no_borough += 1
            continue
        borough = BOROUGH_BY_CODE[code]
        if borough not in wanted_boroughs:
            continue
        rec = extract_compact_record(feat, args.min_height)
        if rec is None:
            if args.min_height > 0:
                skipped_below_min += 1
            else:
                skipped_no_geom += 1
            continue
        by_borough[borough].append(rec)

    print()
    print(f"  skipped (no borough field): {skipped_no_borough}")
    print(f"  skipped (no geometry):       {skipped_no_geom}")
    if args.min_height > 0:
        print(f"  skipped (below min height):  {skipped_below_min}")

    manifest = {
        "_meta": {
            "source_dataset": "5zhs-2jue (NYC Building Footprints)",
            "source_owner": "NYC Office of Technology & Innovation",
            "schema": "{p: polygon coords, h: roof height meters, y: construction year, b: BIN}",
            "min_height_filter_ft": args.min_height,
            "generator": "scripts/export_buildings_all_boroughs.py",
        },
        "boroughs": {},
    }

    print()
    for borough, records in sorted(by_borough.items()):
        out_file = DATA_DIR / f"{borough}_compact.json"
        with open(out_file, "w") as f:
            json.dump(records, f, separators=(",", ":"))
        size_mb = out_file.stat().st_size / 1024 / 1024
        # Quick stats for the manifest
        heights = [r["h"] for r in records if r.get("h", 0) > 0]
        years = [r["y"] for r in records if r.get("y", 0) > 0]
        manifest["boroughs"][borough] = {
            "count": len(records),
            "size_mb": round(size_mb, 1),
            "height_coverage_pct": round(100 * len(heights) / max(len(records), 1), 1),
            "year_coverage_pct": round(100 * len(years) / max(len(records), 1), 1),
            "height_min_m": round(min(heights), 1) if heights else 0,
            "height_max_m": round(max(heights), 1) if heights else 0,
            "year_min": min(years) if years else 0,
            "year_max": max(years) if years else 0,
        }
        print(
            f"  {borough:10}  {len(records):>7,} buildings  "
            f"{size_mb:>6.1f} MB  "
            f"h: {manifest['boroughs'][borough]['height_coverage_pct']:>5.1f}%  "
            f"y: {manifest['boroughs'][borough]['year_coverage_pct']:>5.1f}%"
        )

    manifest_file = DATA_DIR / "borough_manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to {manifest_file}")
    print("Done.")


if __name__ == "__main__":
    main()
