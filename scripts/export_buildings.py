"""
Export Manhattan buildings to a compact JSON for the deck.gl frontend.
Strips coordinate precision to 6 decimals to reduce file size.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_FILE = DATA_DIR / "manhattan_compact.json"

def main():
    print("Loading buildings...")
    with open(DATA_DIR / "manhattan_buildings.geojson") as f:
        data = json.load(f)

    buildings = []
    for feat in data["features"]:
        props = feat["properties"]
        geom = feat["geometry"]

        height = float(props.get("height_roof") or 0)
        year = props.get("construction_year")
        try:
            year = int(year) if year else 0
        except (ValueError, TypeError):
            year = 0

        if geom["type"] == "MultiPolygon":
            coords = geom["coordinates"][0][0]
        elif geom["type"] == "Polygon":
            coords = geom["coordinates"][0]
        else:
            continue

        # Trim coordinate precision (6 decimals = ~0.1m accuracy)
        coords = [[round(c[0], 6), round(c[1], 6)] for c in coords]

        buildings.append({
            "p": coords,           # polygon
            "h": round(height * 0.3048, 1),  # height in meters
            "y": year,             # construction year
            "b": props.get("bin", ""),
        })

    with open(OUT_FILE, "w") as f:
        json.dump(buildings, f, separators=(",", ":"))

    size_mb = OUT_FILE.stat().st_size / 1024 / 1024
    print(f"Exported {len(buildings)} buildings to {OUT_FILE} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    main()
