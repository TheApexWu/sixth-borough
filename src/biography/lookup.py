"""Structured retrieval over local NYC Open Data files.

Given a BIN, lat/lon, or event_id, joins the relevant rows from every local
data file we have and returns a flat dict ready for prompt synthesis.

NOT semantic RAG. NOT embeddings. Pure keyed lookup + lat/lon proximity. The
right shape for this problem because the user knows the address (or BIN), so
exact match + radius search is correct, not semantic similarity.

Drafted Apr 12 ~02:30 UTC, Session 45.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

# Repo root: this file is at src/biography/lookup.py, so 3 parents up.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
CULTURAL_DIR = REPO_ROOT / "cultural-content"

# Borough code → name (from base_bbl[0])
BOROUGH_BY_CODE = {
    "1": "manhattan",
    "2": "bronx",
    "3": "brooklyn",
    "4": "queens",
    "5": "staten",
}

# Files we know about. Missing files are gracefully skipped — the lookup
# returns whatever it can find. We do NOT fail the whole biography because
# Brooklyn data isn't on this box yet.
BUILDING_FILES = {
    "manhattan": DATA_DIR / "manhattan_compact.json",
    "bronx": DATA_DIR / "bronx_compact.json",
    "brooklyn": DATA_DIR / "brooklyn_compact.json",
    "queens": DATA_DIR / "queens_compact.json",
    "staten": DATA_DIR / "staten_compact.json",
}
EVENTS_FILE = DATA_DIR / "events-seed.json"
LANDMARKS_FILE = DATA_DIR / "demolished-landmarks.json"
OLDNYC_FILE = CULTURAL_DIR / "oldnyc" / "index.json"


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance between two lat/lon points in meters. Pure stdlib."""
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _polygon_centroid(coords: list[list[float]]) -> tuple[float, float]:
    """Centroid of a polygon's exterior ring. coords is [[lon, lat], ...].
    Returns (lat, lon). Naive average — fine for the small NYC building
    polygons we care about, where the difference vs proper area-weighted
    centroid is sub-meter."""
    if not coords:
        return (0.0, 0.0)
    avg_lon = sum(c[0] for c in coords) / len(coords)
    avg_lat = sum(c[1] for c in coords) / len(coords)
    return (avg_lat, avg_lon)


@lru_cache(maxsize=1)
def _load_buildings_by_bin() -> dict[str, dict[str, Any]]:
    """Load every available borough compact JSON, build a BIN -> record dict.
    Each record carries the original {p, h, y, b} fields plus a derived
    `centroid` (lat, lon) and `borough` name. Cached forever for one server
    process."""
    out: dict[str, dict[str, Any]] = {}
    for borough, path in BUILDING_FILES.items():
        if not path.exists():
            continue
        with open(path) as f:
            records = json.load(f)
        for r in records:
            bin_str = str(r.get("b", "")).strip()
            if not bin_str:
                continue
            centroid = _polygon_centroid(r.get("p", []))
            out[bin_str] = {
                "bin": bin_str,
                "polygon": r.get("p", []),
                "height_m": r.get("h"),
                "year_built": r.get("y"),
                "borough": borough,
                "centroid_lat": centroid[0],
                "centroid_lon": centroid[1],
                "_source_dataset": "NYC Open Data Building Footprints (5zhs-2jue)",
            }
    return out


@lru_cache(maxsize=1)
def _load_events() -> list[dict[str, Any]]:
    if not EVENTS_FILE.exists():
        return []
    with open(EVENTS_FILE) as f:
        d = json.load(f)
    return d.get("events", []) if isinstance(d, dict) else d


@lru_cache(maxsize=1)
def _load_landmarks() -> list[dict[str, Any]]:
    if not LANDMARKS_FILE.exists():
        return []
    with open(LANDMARKS_FILE) as f:
        d = json.load(f)
    return d if isinstance(d, list) else d.get("landmarks", d.get("features", []))


@lru_cache(maxsize=1)
def _load_oldnyc_photos() -> list[dict[str, Any]]:
    if not OLDNYC_FILE.exists():
        return []
    with open(OLDNYC_FILE) as f:
        d = json.load(f)
    return d if isinstance(d, list) else d.get("photos", d.get("records", []))


def find_building_by_bin(bin_str: str) -> dict[str, Any] | None:
    """Direct lookup by Building Identification Number (BIN)."""
    return _load_buildings_by_bin().get(str(bin_str).strip())


def find_building_near(lat: float, lon: float, radius_m: float = 50.0) -> dict[str, Any] | None:
    """Find the nearest building polygon by centroid within radius_m. Linear
    scan over the loaded buildings — for ~1M records this is ~0.5 sec on the
    GB10. Acceptable for an interactive lookup. Could be made O(log n) with a
    spatial index later if needed."""
    best = None
    best_d = radius_m + 1
    for rec in _load_buildings_by_bin().values():
        d = _haversine_m(lat, lon, rec["centroid_lat"], rec["centroid_lon"])
        if d < best_d:
            best_d = d
            best = {**rec, "distance_m": round(d, 1)}
    return best


def find_event_by_id(event_id: str) -> dict[str, Any] | None:
    """Look up an event in events-seed.json by ID."""
    for e in _load_events():
        if e.get("id") == event_id:
            return e
    return None


def find_nearby_oldnyc_photos(lat: float, lon: float, radius_m: float = 200.0, limit: int = 8) -> list[dict[str, Any]]:
    """Return the closest NYPL Milstein photos within radius_m, sorted by
    distance, capped at limit. Each result includes the original photo fields
    plus distance_m."""
    photos = _load_oldnyc_photos()
    out = []
    for p in photos:
        plat = p.get("lat")
        plon = p.get("lon")
        if plat is None or plon is None:
            continue
        d = _haversine_m(lat, lon, float(plat), float(plon))
        if d > radius_m:
            continue
        out.append({**p, "distance_m": round(d, 1)})
    out.sort(key=lambda x: x["distance_m"])
    return out[:limit]


def find_nearby_demolished_landmarks(lat: float, lon: float, radius_m: float = 1000.0, limit: int = 10) -> list[dict[str, Any]]:
    """Return demolished landmarks (Wikidata) within radius_m of the target.
    Wider radius than photos because landmarks are scarcer."""
    out = []
    for l in _load_landmarks():
        plat = l.get("lat")
        plon = l.get("lon")
        if plat is None or plon is None:
            continue
        d = _haversine_m(lat, lon, float(plat), float(plon))
        if d > radius_m:
            continue
        out.append({**l, "distance_m": round(d, 1)})
    out.sort(key=lambda x: x["distance_m"])
    return out[:limit]


def find_nearby_events(lat: float, lon: float, radius_m: float = 500.0, limit: int = 10) -> list[dict[str, Any]]:
    """Cultural events within radius_m. The events-seed.json events use
    `coordinate: [lat, lon]` as their primary schema."""
    out = []
    for e in _load_events():
        coord = e.get("coordinate")
        if isinstance(coord, (list, tuple)) and len(coord) >= 2:
            elat, elon = float(coord[0]), float(coord[1])
        else:
            elat = e.get("lat") or e.get("latitude")
            elon = e.get("lon") or e.get("lng") or e.get("longitude")
            if elat is None or elon is None:
                continue
            elat, elon = float(elat), float(elon)
        d = _haversine_m(lat, lon, elat, elon)
        if d > radius_m:
            continue
        out.append({**e, "distance_m": round(d, 1)})
    out.sort(key=lambda x: x["distance_m"])
    return out[:limit]


def assemble_record(*, bin: str | None = None, lat: float | None = None, lon: float | None = None, event_id: str | None = None) -> dict[str, Any]:
    """Top-level entry point. Resolves any of (bin, lat/lon, event_id) into a
    structured biography record by joining every available local dataset.

    Resolution priority: explicit BIN > event_id (uses event's lat/lon) > lat/lon.
    Returns a flat dict ready to feed into the synthesize prompt template.
    Missing data sources are silently skipped."""
    record: dict[str, Any] = {
        "query": {"bin": bin, "lat": lat, "lon": lon, "event_id": event_id},
        "building": None,
        "anchor_event": None,
        "nearby_photos": [],
        "nearby_landmarks": [],
        "nearby_events": [],
        "data_sources": [],
    }

    # Step 1: resolve to a building record
    building = None
    if bin:
        building = find_building_by_bin(bin)
        if building:
            record["data_sources"].append("NYC Open Data Building Footprints (5zhs-2jue) by BIN")

    if not building and event_id:
        ev = find_event_by_id(event_id)
        if ev:
            record["anchor_event"] = ev
            # events-seed.json uses {"coordinate": [lat, lon]} as the primary
            # schema; tolerate the alternate {lat, lon} / {latitude, longitude}
            # forms in case downstream callers post raw rows.
            coord = ev.get("coordinate")
            if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                lat, lon = float(coord[0]), float(coord[1])
            else:
                elat = ev.get("lat") or ev.get("latitude")
                elon = ev.get("lon") or ev.get("lng") or ev.get("longitude")
                if elat and elon:
                    lat, lon = float(elat), float(elon)
            record["data_sources"].append(f"data/events-seed.json event '{event_id}'")

    if not building and lat is not None and lon is not None:
        building = find_building_near(lat, lon, radius_m=80.0)
        if building:
            record["data_sources"].append(
                f"NYC Open Data Building Footprints (5zhs-2jue) by lat/lon proximity ({building.get('distance_m')} m)"
            )

    record["building"] = building

    # Step 2: derive search lat/lon for the radius queries
    search_lat, search_lon = lat, lon
    if building:
        search_lat = building["centroid_lat"]
        search_lon = building["centroid_lon"]

    if search_lat is None or search_lon is None:
        # Nothing to anchor on. Return what we have.
        return record

    # Step 3: enrich with radius queries (each is independent)
    photos = find_nearby_oldnyc_photos(search_lat, search_lon)
    if photos:
        record["nearby_photos"] = photos
        record["data_sources"].append(f"NYPL Milstein photo index (cultural-content/oldnyc/index.json) — {len(photos)} photos within 200m")

    landmarks = find_nearby_demolished_landmarks(search_lat, search_lon)
    if landmarks:
        record["nearby_landmarks"] = landmarks
        record["data_sources"].append(f"Wikidata demolished landmarks (data/demolished-landmarks.json) — {len(landmarks)} within 1km")

    events = find_nearby_events(search_lat, search_lon)
    if events:
        record["nearby_events"] = events
        record["data_sources"].append(f"Hand-curated cultural events (data/events-seed.json) — {len(events)} within 500m")

    return record
