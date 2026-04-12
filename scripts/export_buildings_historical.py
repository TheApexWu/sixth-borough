"""
Export NYC Building Footprints HISTORICAL SHAPE to compact JSONs for the
deck.gl frontend, with both construction_year AND demolition_year so the
year slider can show buildings appearing AND disappearing.

DRAFT — Apr 11 ~23:30 ET, Session 43. The "V1 unlock" path.

Background:
- The Apr 10 NYC Open Data audit (`~/Desktop/sixth-borough-kickoff/docs/NYC_OPEN_DATA.md`)
  identified `s5zg-yzea` (Building Footprints Historical Shape) as Tier 1
  V1 must-have. It has BOTH `construction_year` AND `demolition_year` —
  the literal time-machine data layer. Every prior version retained per
  Local Law 106 of 2015.
- The current `manhattan_compact.json` schema is `{p, h, y, b}` and has
  ONLY construction year. When the user scrubs backward in James's slider,
  buildings disappear before they were built (correct), but demolished
  buildings do NOT reappear when scrubbed back to before their demolition
  (wrong — that's the entire point of the time machine).
- This script extends the schema to `{p, h, y, d, b}` where `d` is the
  optional demolition year (null/0 if still standing).
- The deck.gl filter then becomes:
      shouldRender(building, currentYear) {
        if (building.y > currentYear) return false;        // not built yet
        if (building.d && building.d < currentYear) return false; // demolished
        return true;
      }
- Buildings that have a non-null `d` are the "ghost" candidates — render
  them in faded/wireframe mode in the years between built and demolished
  to make the "what was here" beat visceral.

USAGE:
    1. Download the historical shape GeoJSON:
         curl -L -o data/nyc_buildings_historical.geojson \
           "https://data.cityofnewyork.us/api/geospatial/s5zg-yzea?method=export&format=GeoJSON"
       (size unknown — likely 1-2 GB since it includes all historical versions)

    2. Run the splitter:
         python scripts/export_buildings_historical.py

    3. Output: 5 borough files in the new {p, h, y, d, b} schema
         data/manhattan_historical.json
         data/bronx_historical.json
         ...
       Plus a manifest at data/borough_historical_manifest.json

NAMING NOTE: outputs are `*_historical.json` (not `*_compact.json`) so
they coexist with James's existing Manhattan compact file. The frontend
can opt into the historical layer by switching the fetch URL.

OPTIONAL FILTERS:
    --boroughs LIST   Only process these boroughs (default: all 5)
    --min-height N    Drop buildings with height_roof < N feet (default: 0)
    --demolished-only Only export buildings that have a demolition_year
                      (smallest possible output, ghost-layer only)
"""

import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_INPUT = DATA_DIR / "nyc_buildings_historical.geojson"

# Same borough code map as the live-only script. The historical dataset
# uses `base_bbl` which encodes borough as the first digit, but it also
# carries `boro` / `borocode` fields most of the time.
BOROUGH_BY_CODE = {
    "1": "manhattan",
    "2": "bronx",
    "3": "brooklyn",
    "4": "queens",
    "5": "staten",
}
CODE_BY_NAME = {v: k for k, v in BOROUGH_BY_CODE.items()}


def get_borough_code(props: dict) -> str | None:
    """Tolerate field-name drift across NYC export endpoints, including
    deriving the borough from base_bbl's first digit if no explicit field."""
    for key in ("boro_code", "borocode", "boro", "BORO_CODE", "BoroCode"):
        v = props.get(key)
        if v is not None:
            v = str(v).strip()
            if v in BOROUGH_BY_CODE:
                return v
    # Fallback: derive from base_bbl. BBL = Borough(1) + Block(5) + Lot(4).
    # First character is the borough code 1-5.
    bbl = props.get("base_bbl") or props.get("mappluto_bbl") or props.get("bbl")
    if bbl:
        first = str(bbl).strip()[:1]
        if first in BOROUGH_BY_CODE:
            return first
    return None


def extract_compact_record(
    feat: dict, min_height_ft: float, demolished_only: bool
) -> dict | None:
    """Convert a single Building Footprints Historical Shape feature into
    the extended `{p, h, y, d, b}` schema. Returns None if the record
    should be dropped."""
    props = feat.get("properties", {})
    geom = feat.get("geometry") or {}

    height_ft = props.get("height_roof")
    try:
        height_ft = float(height_ft) if height_ft is not None else 0.0
    except (ValueError, TypeError):
        height_ft = 0.0

    if height_ft < min_height_ft:
        return None

    year_built = props.get("construction_year")
    try:
        year_built = int(year_built) if year_built else 0
    except (ValueError, TypeError):
        year_built = 0

    year_demolished = props.get("demolition_year")
    try:
        year_demolished = int(year_demolished) if year_demolished else 0
    except (ValueError, TypeError):
        year_demolished = 0

    if demolished_only and not year_demolished:
        return None

    if geom.get("type") == "MultiPolygon":
        coords = geom["coordinates"][0][0]
    elif geom.get("type") == "Polygon":
        coords = geom["coordinates"][0]
    else:
        return None

    if not coords:
        return None

    coords = [[round(c[0], 6), round(c[1], 6)] for c in coords]

    rec = {
        "p": coords,
        "h": round(height_ft * 0.3048, 1),
        "y": year_built,
        "b": str(props.get("bin", "")),
    }
    # Only include `d` when set, to keep the file size down.
    if year_demolished:
        rec["d"] = year_demolished
    return rec


def main():
    parser = argparse.ArgumentParser(
        description="Split NYC Building Footprints Historical Shape into 5 borough JSONs with `d` (demolition year)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Path to historical GeoJSON (default: {DEFAULT_INPUT.relative_to(DATA_DIR.parent)})",
    )
    parser.add_argument(
        "--boroughs",
        type=str,
        default="manhattan,bronx,brooklyn,queens,staten",
    )
    parser.add_argument(
        "--min-height",
        type=float,
        default=0.0,
    )
    parser.add_argument(
        "--demolished-only",
        action="store_true",
        help="Only export buildings with non-null demolition_year (ghost layer only)",
    )
    args = parser.parse_args()

    wanted_boroughs = {b.strip().lower() for b in args.boroughs.split(",") if b.strip()}
    unknown = wanted_boroughs - set(CODE_BY_NAME)
    if unknown:
        print(f"unknown boroughs: {sorted(unknown)}", file=sys.stderr)
        sys.exit(1)

    if not args.input.exists():
        print(f"ERROR: input file not found: {args.input}", file=sys.stderr)
        print(f"\nDownload it first with:", file=sys.stderr)
        print(
            f'  curl -L -o {args.input} \\\n'
            f'    "https://data.cityofnewyork.us/api/geospatial/s5zg-yzea?method=export&format=GeoJSON"',
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
    if args.demolished_only:
        print(f"  filtering: demolished buildings only (ghost layer)")

    by_borough: dict[str, list[dict]] = {b: [] for b in wanted_boroughs}
    skipped_no_borough = 0
    skipped_no_geom = 0
    demolished_count = 0

    for feat in data["features"]:
        code = get_borough_code(feat.get("properties", {}))
        if code is None:
            skipped_no_borough += 1
            continue
        borough = BOROUGH_BY_CODE[code]
        if borough not in wanted_boroughs:
            continue
        rec = extract_compact_record(feat, args.min_height, args.demolished_only)
        if rec is None:
            skipped_no_geom += 1
            continue
        if "d" in rec:
            demolished_count += 1
        by_borough[borough].append(rec)

    print()
    print(f"  skipped (no borough field): {skipped_no_borough}")
    print(f"  skipped (no geometry / filtered):       {skipped_no_geom}")
    print(f"  records with demolition_year set: {demolished_count}")

    manifest = {
        "_meta": {
            "source_dataset": "s5zg-yzea (NYC Building Footprints Historical Shape)",
            "source_owner": "NYC Office of Technology & Innovation",
            "schema": "{p: polygon, h: roof height meters, y: construction year, d: demolition year (omitted if standing), b: BIN}",
            "min_height_filter_ft": args.min_height,
            "demolished_only": args.demolished_only,
            "generator": "scripts/export_buildings_historical.py",
        },
        "boroughs": {},
    }

    print()
    for borough, records in sorted(by_borough.items()):
        out_file = DATA_DIR / f"{borough}_historical.json"
        with open(out_file, "w") as f:
            json.dump(records, f, separators=(",", ":"))
        size_mb = out_file.stat().st_size / 1024 / 1024
        with_d = sum(1 for r in records if "d" in r)
        manifest["boroughs"][borough] = {
            "count": len(records),
            "demolished_count": with_d,
            "size_mb": round(size_mb, 1),
        }
        print(
            f"  {borough:10}  {len(records):>7,} buildings  "
            f"({with_d:>5,} with demolition_year)  "
            f"{size_mb:>6.1f} MB"
        )

    manifest_file = DATA_DIR / "borough_historical_manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest written to {manifest_file}")
    print("Done.")


if __name__ == "__main__":
    main()
