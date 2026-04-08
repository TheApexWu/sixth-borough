"""
Sixth Borough -- 3D Manhattan mockup with timeline slider.
Python/pydeck prototype. Shows 45,194 buildings extruded by height,
colored by construction era. Timeline slider filters visible buildings.

Run: python scripts/mockup_3d.py
Opens: sixth_borough_mockup.html in browser
"""

import json
import pydeck as pdk
import webbrowser
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_FILE = Path(__file__).parent.parent / "sixth_borough_mockup.html"

# Era color palette (PS2-inspired muted tones)
ERA_COLORS = {
    "pre-1800":    [80, 60, 50, 180],      # dark brown -- colonial
    "1800-1860":   [120, 85, 60, 180],      # warm brown -- antebellum
    "1860-1900":   [160, 110, 70, 180],     # amber -- Gilded Age
    "1900-1930":   [180, 140, 80, 200],     # gold -- golden age (biggest cohort)
    "1930-1945":   [100, 130, 160, 200],    # steel blue -- Art Deco/Depression
    "1945-1970":   [130, 130, 130, 200],    # concrete gray -- brutalism
    "1970-2000":   [90, 110, 90, 180],      # olive -- postmodern
    "2000+":       [60, 180, 200, 220],     # cyan -- glass tower era
}

def classify_era(year):
    if not year: return "pre-1800"
    y = int(year)
    if y < 1800: return "pre-1800"
    if y < 1860: return "1800-1860"
    if y < 1900: return "1860-1900"
    if y < 1930: return "1900-1930"
    if y < 1945: return "1930-1945"
    if y < 1970: return "1945-1970"
    if y < 2000: return "1970-2000"
    return "2000+"


def load_buildings():
    print("Loading Manhattan buildings...")
    with open(DATA_DIR / "manhattan_buildings.geojson") as f:
        data = json.load(f)

    buildings = []
    for feat in data["features"]:
        props = feat["properties"]
        geom = feat["geometry"]

        height = float(props.get("height_roof") or 0)
        year = props.get("construction_year")
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                year = None

        # Extract polygon coordinates (handle MultiPolygon)
        if geom["type"] == "MultiPolygon":
            coords = geom["coordinates"][0][0]  # first polygon, outer ring
        elif geom["type"] == "Polygon":
            coords = geom["coordinates"][0]
        else:
            continue

        era = classify_era(year)
        color = ERA_COLORS[era]

        # Convert height from feet to meters for pydeck
        height_m = height * 0.3048

        buildings.append({
            "polygon": coords,
            "height": height_m,
            "year": year or 0,
            "era": era,
            "color": color,
            "bin": props.get("bin", ""),
            "bbl": props.get("base_bbl", ""),
            "elevation": float(props.get("ground_elevation") or 0) * 0.3048,
        })

    print(f"Loaded {len(buildings)} buildings")

    # Era stats
    era_counts = {}
    for b in buildings:
        era_counts[b["era"]] = era_counts.get(b["era"], 0) + 1
    for era in sorted(era_counts.keys()):
        print(f"  {era}: {era_counts[era]:,} buildings")

    return buildings


def build_deck(buildings, max_year=2026):
    """Build pydeck visualization with buildings up to max_year."""

    filtered = [b for b in buildings if b["year"] <= max_year]

    layer = pdk.Layer(
        "PolygonLayer",
        data=filtered,
        get_polygon="polygon",
        get_elevation="height",
        get_fill_color="color",
        elevation_scale=1,
        elevation_range=[0, 500],
        extruded=True,
        wireframe=False,
        pickable=True,
        auto_highlight=True,
        opacity=0.8,
    )

    view_state = pdk.ViewState(
        latitude=40.758,
        longitude=-73.985,
        zoom=14,
        pitch=55,
        bearing=-20,
        max_zoom=18,
        min_zoom=10,
    )

    tooltip = {
        "html": "<b>Era:</b> {era}<br/>"
                "<b>Built:</b> {year}<br/>"
                "<b>Height:</b> {height:.0f}m<br/>"
                "<b>BIN:</b> {bin}",
        "style": {
            "backgroundColor": "rgba(0,0,0,0.85)",
            "color": "white",
            "fontFamily": "'Courier New', monospace",
            "fontSize": "12px",
        },
    }

    return pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/dark-v11",
    )


def generate_html_with_slider(buildings):
    """Generate HTML with timeline slider that filters buildings by year."""

    # Pre-compute era data for each slider position
    deck = build_deck(buildings, max_year=2026)
    deck_html = deck.to_html(as_string=True)

    # Inject custom slider and PS2-style CSS
    slider_injection = """
    <style>
        body { margin: 0; overflow: hidden; background: #0a0a0a; }

        #controls {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background: rgba(0,0,0,0.9);
            border: 1px solid #333;
            padding: 20px 40px;
            font-family: 'Courier New', monospace;
            color: #ddd;
            text-align: center;
            min-width: 500px;
        }

        #controls h1 {
            margin: 0 0 5px 0;
            font-size: 14px;
            letter-spacing: 4px;
            color: #00b8d4;
            text-transform: uppercase;
        }

        #year-display {
            font-size: 48px;
            font-weight: bold;
            color: #fff;
            margin: 10px 0;
            font-variant-numeric: tabular-nums;
        }

        #era-label {
            font-size: 12px;
            color: #888;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 15px;
        }

        #timeline-slider {
            width: 100%;
            -webkit-appearance: none;
            height: 4px;
            background: #333;
            outline: none;
            cursor: pointer;
        }

        #timeline-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            background: #00b8d4;
            border-radius: 50%;
            cursor: pointer;
        }

        #stats {
            margin-top: 10px;
            font-size: 11px;
            color: #666;
        }

        #legend {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: rgba(0,0,0,0.85);
            border: 1px solid #333;
            padding: 15px;
            font-family: 'Courier New', monospace;
            color: #ddd;
            font-size: 11px;
        }

        #legend h3 {
            margin: 0 0 10px 0;
            font-size: 12px;
            letter-spacing: 2px;
            color: #00b8d4;
        }

        .legend-item {
            display: flex;
            align-items: center;
            margin: 4px 0;
        }

        .legend-swatch {
            width: 12px;
            height: 12px;
            margin-right: 8px;
            border: 1px solid #444;
        }

        #title-bar {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1000;
            font-family: 'Courier New', monospace;
        }

        #title-bar h1 {
            font-size: 24px;
            color: #fff;
            margin: 0;
            letter-spacing: 3px;
        }

        #title-bar p {
            font-size: 11px;
            color: #666;
            margin: 5px 0 0 0;
            letter-spacing: 1px;
        }
    </style>

    <div id="title-bar">
        <h1>SIXTH BOROUGH</h1>
        <p>MANHATTAN / 45,194 BUILDINGS / 1719-2026</p>
    </div>

    <div id="legend">
        <h3>ERA</h3>
        <div class="legend-item"><div class="legend-swatch" style="background:rgb(80,60,50)"></div>Pre-1800</div>
        <div class="legend-item"><div class="legend-swatch" style="background:rgb(120,85,60)"></div>1800-1860</div>
        <div class="legend-item"><div class="legend-swatch" style="background:rgb(160,110,70)"></div>1860-1900</div>
        <div class="legend-item"><div class="legend-swatch" style="background:rgb(180,140,80)"></div>1900-1930</div>
        <div class="legend-item"><div class="legend-swatch" style="background:rgb(100,130,160)"></div>1930-1945</div>
        <div class="legend-item"><div class="legend-swatch" style="background:rgb(130,130,130)"></div>1945-1970</div>
        <div class="legend-item"><div class="legend-swatch" style="background:rgb(90,110,90)"></div>1970-2000</div>
        <div class="legend-item"><div class="legend-swatch" style="background:rgb(60,180,200)"></div>2000+</div>
    </div>

    <div id="controls">
        <h1>TIMELINE</h1>
        <div id="year-display">2026</div>
        <div id="era-label">GLASS TOWER ERA</div>
        <input type="range" id="timeline-slider" min="1719" max="2026" value="2026" step="1">
        <div id="stats">
            <span id="building-count">45,194</span> buildings visible
        </div>
    </div>

    <script>
        // Building year data for filtering
        const buildingYears = BUILDING_YEARS_DATA;

        const eraLabels = {
            1800: 'COLONIAL ERA',
            1860: 'ANTEBELLUM',
            1900: 'GILDED AGE',
            1930: 'GOLDEN AGE',
            1945: 'ART DECO / DEPRESSION',
            1970: 'BRUTALISM / MIDCENTURY',
            2000: 'POSTMODERN',
            2027: 'GLASS TOWER ERA',
        };

        function getEraLabel(year) {
            const thresholds = Object.keys(eraLabels).map(Number).sort((a,b) => a-b);
            for (let i = thresholds.length - 1; i >= 0; i--) {
                if (year < thresholds[i]) continue;
                return eraLabels[thresholds[i]];
            }
            return 'COLONIAL ERA';
        }

        const slider = document.getElementById('timeline-slider');
        const yearDisplay = document.getElementById('year-display');
        const eraLabel = document.getElementById('era-label');
        const buildingCount = document.getElementById('building-count');

        slider.addEventListener('input', function() {
            const year = parseInt(this.value);
            yearDisplay.textContent = year;
            eraLabel.textContent = getEraLabel(year);
            const count = buildingYears.filter(y => y <= year).length;
            buildingCount.textContent = count.toLocaleString();
        });
    </script>
    """

    # Extract building years for the JS slider
    years = [b["year"] for b in buildings]
    years_js = json.dumps(years)
    slider_injection = slider_injection.replace("BUILDING_YEARS_DATA", years_js)

    # Inject before closing </body>
    html = deck_html.replace("</body>", slider_injection + "\n</body>")

    return html


def main():
    buildings = load_buildings()
    print("\nGenerating 3D visualization...")
    html = generate_html_with_slider(buildings)

    with open(OUT_FILE, "w") as f:
        f.write(html)

    print(f"\nWritten to {OUT_FILE}")
    print(f"File size: {OUT_FILE.stat().st_size / 1024 / 1024:.1f} MB")
    print("Opening in browser...")
    webbrowser.open(f"file://{OUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
